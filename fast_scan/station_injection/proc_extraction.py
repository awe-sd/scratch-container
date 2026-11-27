"""Turn a staged Snowflake Scripting procedure file into ONE read-only SELECT.

Shared by validate_fast_scan_v2.py and validate_validation_fast_scan_v2.py. Works on SQL
structure, never on comment text:

  CREATE [OR REPLACE] TEMPORARY TABLE T AS <select>        -> CTE  T AS (<select>)
  CREATE [OR REPLACE] TEMPORARY TABLE T (cols); INSERT INTO T <select>;
      DELETE FROM T WHERE <cond>; ...                       -> CTE chain ending in T
  INSERT INTO <final_target> (cols) <select>               -> the closing SELECT (INSERT dropped,
      trailing "WHERE NOT EXISTS (... <final_target> ...)" guard dropped)

Everything else (IF blocks, SELECT INTO, run-log writes, the post-insert DELETE/INSERT into
other tables) is NOT replayed; it is listed in Extracted.not_replayed so callers can say so.
Any expected stage that is missing, out of order, or unexpected raises ProcExtractionError.
"""

import re
from dataclasses import dataclass, field

# Tolerate temp-table DDL spellings; the stage name is group 1.
_CREATE_TMP = re.compile(
    r"^CREATE\s+(?:OR\s+REPLACE\s+)?(?:LOCAL\s+|GLOBAL\s+|VOLATILE\s+)?TEMP(?:ORARY)?\s+TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][\w$.]*)\s*", re.I)
_BIND = re.compile(r"(?<!:):([A-Za-z_]\w*)")
_DECLARE_DEFAULT = re.compile(r"^\s*(v_\w+)\s+[A-Za-z]+(?:\([\d,\s]+\))?\s*:=\s*('[^']*'|-?\d+(?:\.\d+)?)\s*;", re.I | re.M)


class ProcExtractionError(ValueError):
    pass


class StageNotFound(ProcExtractionError):
    pass


class UnboundParameter(ProcExtractionError):
    pass


class UnsupportedStageStatement(ProcExtractionError):
    pass


@dataclass
class Extracted:
    query: str                      # one SELECT; may still contain :binds until bind() is applied
    stages: list = field(default_factory=list)       # stage names replayed, in order
    final_target: str = ""
    declared_defaults: dict = field(default_factory=dict)   # v_x := literal in DECLARE
    not_replayed: list = field(default_factory=list)  # one-line labels of skipped statements


def procedure_body(sql_text: str, source: str = "<sql>") -> str:
    """Body between the procedure's AS '<newline> ... <newline>'; with '' unescaped."""
    m = re.search(r"\bAS\s+'[ \t]*\n", sql_text)
    if not m:
        raise ProcExtractionError(f"{source}: no procedure body opening (AS ') found")
    end = sql_text.rfind("\n';")
    if end < m.end():
        raise ProcExtractionError(f"{source}: no procedure body closing (';) found")
    return sql_text[m.end():end].replace("''", "'")


def strip_line_comments(text: str) -> str:
    out = []
    for line in text.split("\n"):
        i = line.find("--")
        while i != -1 and line[:i].count("'") % 2 == 1:   # -- inside a string literal
            i = line.find("--", i + 2)
        out.append(line if i == -1 else line[:i])
    return "\n".join(out)


def split_statements(text: str) -> list:
    stmts, buf, quote = [], [], None
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == ";":
            stmts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        stmts.append(tail)
    return [s for s in stmts if s]


def _balanced_paren_end(text: str, open_idx: int) -> int:
    depth, quote = 0, None
    for i in range(open_idx, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ProcExtractionError("unbalanced parentheses")


def _split_top_level_commas(text: str) -> list:
    parts, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _py_literal(text: str):
    if text.startswith("'"):
        return text[1:-1]
    return float(text) if "." in text else int(text)


_NOISE = re.compile(r"^(DECLARE\s+)?v_\w+\s+\w+(\(.*\))?(\s*:=.*)?$|^END(\s+IF)?$|^BEGIN$", re.I | re.S)


def _label(stmt: str) -> str:
    return re.sub(r"\s+", " ", stmt)[:70]


def extract_readonly_query(sql_text: str, expected_stages: list, final_target: str,
                           source: str = "<sql>", upto_stage: str = None) -> Extracted:
    """expected_stages: stage temp-table names in the order the procedure builds them.
    upto_stage: instead of the final INSERT's SELECT, return SELECT * FROM <that stage>."""
    body = strip_line_comments(procedure_body(sql_text, source))
    if re.search(r"/\*", body):
        raise ProcExtractionError(f"{source}: block comments are not supported by the extractor")
    stmts = split_statements(body)
    declared = {k.lower(): _py_literal(v) for k, v in _DECLARE_DEFAULT.findall(body)}

    stage_ctes = {}      # name -> list of (cte_name, column_list or None, select_text)
    stage_order = []
    declared_cols = {}   # name -> columns for CREATE T (cols) form
    final_select = None
    not_replayed = []
    target_re = re.compile(r"^INSERT\s+INTO\s+" + re.escape(final_target) + r"\s*\(", re.I)

    for stmt in stmts:
        m = _CREATE_TMP.match(stmt)
        if m and final_select is None:
            name = m.group(1).upper()
            rest = stmt[m.end():]
            if re.match(r"AS\b", rest, re.I):
                select = rest[2:].strip()
                stage_ctes[name] = [(name, None, select)]
            elif rest.startswith("("):
                close = _balanced_paren_end(rest, 0)
                cols = [c.split()[0] for c in _split_top_level_commas(rest[1:close])]
                declared_cols[name] = cols
                stage_ctes[name] = []
            else:
                raise ProcExtractionError(f"{source}: stage {name}: unsupported CREATE TEMPORARY TABLE form")
            stage_order.append(name)
            continue
        m = re.match(r"^INSERT\s+INTO\s+([A-Za-z_][\w$.]*)\s+(?=WITH\b|SELECT\b)", stmt, re.I)
        if m and m.group(1).upper() in stage_ctes and final_select is None:
            name = m.group(1).upper()
            parts, select = stage_ctes[name], stmt[m.end():].strip()
            if parts:   # a later INSERT appends rows, as it does when the procedure runs
                parts.append((f"{name}__{len(parts)}", None,
                              f"SELECT * FROM {parts[-1][0]}\nUNION ALL\nSELECT * FROM (\n{select}\n)"))
            else:
                parts.append((f"{name}__0", declared_cols[name], select))
            continue
        m = re.match(r"^INSERT\s+INTO\s+([A-Za-z_][\w$.]*)\s*\(", stmt, re.I)
        if m and m.group(1).upper() in stage_ctes and final_select is None:
            name = m.group(1).upper()
            if name not in declared_cols:
                raise UnsupportedStageStatement(
                    f"{source}: {_label(stmt)!r} lists columns for stage {name}, which is created with AS SELECT; "
                    "the extractor can only map a column list onto a stage declared with CREATE TABLE T (cols)")
            close = _balanced_paren_end(stmt, stmt.index("("))
            listed = [c.strip().strip('"').upper() for c in _split_top_level_commas(stmt[stmt.index("(") + 1:close])]
            select = stmt[close + 1:].strip()
            if not re.match(r"(WITH|SELECT)\b", select, re.I):
                raise UnsupportedStageStatement(f"{source}: {_label(stmt)!r}: INSERT column list not followed by WITH/SELECT")
            unknown = [c for c in listed if c not in {d.upper() for d in declared_cols[name]}]
            if unknown:
                raise ProcExtractionError(f"{source}: INSERT INTO {name} lists unknown column(s) {unknown}")
            picks = ", ".join(c if c.upper() in listed else f"NULL AS {c}" for c in declared_cols[name])
            mapped = f"SELECT {picks} FROM (\n{select}\n) AS _ins({', '.join(listed)})"
            parts = stage_ctes[name]
            if parts:
                parts.append((f"{name}__{len(parts)}", None,
                              f"SELECT * FROM {parts[-1][0]}\nUNION ALL\nSELECT * FROM (\n{mapped}\n)"))
            else:
                parts.append((f"{name}__0", declared_cols[name], mapped))
            continue
        m = re.match(r"^(?:UPDATE|MERGE\s+INTO)\s+([A-Za-z_][\w$.]*)", stmt, re.I)
        if m and m.group(1).upper() in stage_ctes and final_select is None:
            raise UnsupportedStageStatement(
                f"{source}: {_label(stmt)!r} modifies stage {m.group(1).upper()}; the extractor replays only "
                "INSERT and DELETE on stage tables, so this procedure cannot be validated until it is supported")
        m = re.match(r"^DELETE\s+FROM\s+([A-Za-z_][\w$.]*)\s+WHERE\s+(.*)$", stmt, re.I | re.S)
        if m and m.group(1).upper() in declared_cols and final_select is None:
            name = m.group(1).upper()
            parts = stage_ctes[name]
            if not parts:
                raise ProcExtractionError(f"{source}: stage {name}: DELETE before any INSERT")
            prev = parts[-1][0]
            parts.append((f"{name}__{len(parts)}", None,
                          f"SELECT * FROM {prev} WHERE NOT COALESCE(({m.group(2).strip()}), FALSE)"))
            continue
        if target_re.match(stmt):
            if final_select is not None:
                raise ProcExtractionError(f"{source}: more than one INSERT INTO {final_target}")
            open_idx = stmt.index("(")
            close = _balanced_paren_end(stmt, open_idx)
            final_select = stmt[close + 1:].strip()
            continue
        if not _NOISE.match(stmt):
            not_replayed.append(_label(stmt))

    if re.search(r"\bEXECUTE\s+IMMEDIATE\b|\bLOOP\b|\bWHILE\b|\bCALL\b", body, re.I):
        not_replayed.append("dynamic SQL / loop / CALL present in the procedure body")

    missing = [s for s in expected_stages if s.upper() not in stage_order]
    if missing:
        raise StageNotFound(
            f"{source}: stage {missing[0]!r} not found (no CREATE [OR REPLACE] TEMPORARY TABLE "
            f"{missing[0]} before the final INSERT INTO {final_target}); found stages: {stage_order}")
    if [s.upper() for s in expected_stages] != stage_order:
        raise ProcExtractionError(
            f"{source}: stages found {stage_order} differ from expected order "
            f"{[s.upper() for s in expected_stages]}; update the validator after reviewing the procedure")
    if final_select is None:
        raise StageNotFound(f"{source}: final 'INSERT INTO {final_target} (...) <select>' not found")
    if not re.match(r"(WITH|SELECT)\b", final_select, re.I):
        raise ProcExtractionError(f"{source}: final INSERT INTO {final_target} is not followed by WITH/SELECT")

    ctes = []
    for name in stage_order:
        parts = stage_ctes[name]
        if not parts:
            raise StageNotFound(f"{source}: stage {name!r} is created but never populated by INSERT INTO {name}")
        for i, (cte, cols, select) in enumerate(parts):
            last = i == len(parts) - 1
            cname = name if last else cte
            col_list = f"({', '.join(cols)})" if cols else ""
            ctes.append(f"{cname}{col_list} AS (\n{select}\n)")

    if upto_stage:
        if upto_stage.upper() not in stage_order:
            raise StageNotFound(f"{source}: stage {upto_stage!r} not found for upto_stage")
        query = "WITH " + ",\n".join(ctes) + f"\nSELECT * FROM {upto_stage}"
    else:
        guard = None
        for g in re.finditer(r"\bWHERE\s+NOT\s+EXISTS\s*\(", final_select, re.I):
            guard = g
        if guard is not None:
            tail = final_select[guard.start():]
            paren = guard.end() - 1 - guard.start()
            if _balanced_paren_end(tail, paren) == len(tail.rstrip()) - 1 and final_target.split(".")[-1].upper() in tail.upper():
                final_select = final_select[:guard.start()].rstrip()
        if not ctes:
            query = final_select
        elif final_select.upper().startswith("WITH"):
            query = "WITH " + ",\n".join(ctes) + ",\n" + final_select[4:].lstrip()
        else:
            query = "WITH " + ",\n".join(ctes) + "\n" + final_select
    return Extracted(query=query.strip(), stages=stage_order, final_target=final_target,
                     declared_defaults=declared, not_replayed=not_replayed)


def sql_literal(val) -> str:
    if val is None or (isinstance(val, float) and val != val) or str(val) in ("<NA>", "NaT", "nan"):
        return "NULL"
    if type(val).__name__ in ("bool", "bool_"):
        return "TRUE" if val else "FALSE"
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    return str(val)


def bind(query: str, values: dict) -> str:
    """Replace every :name with a literal; raise UnboundParameter listing any left over."""
    lookup = {k.lower(): v for k, v in values.items()}
    missing = sorted({m.lower() for m in _BIND.findall(query)} - set(lookup))
    if missing:
        raise UnboundParameter(f"no value supplied for bind variable(s): {missing}")
    return _BIND.sub(lambda m: sql_literal(lookup[m.group(1).lower()]), query)


def stub_cte(query: str, cte_name: str, stub_select: str) -> str:
    """Replace a named CTE's body (validation-run workaround for a source this role can't
    read), keeping the name and paren wrapper so downstream joins still compile."""
    marker = f"{cte_name} AS ("
    if marker not in query:
        raise StageNotFound(f"CTE {cte_name!r} not found in the extracted query; cannot stub it")
    open_idx = query.index(marker) + len(marker) - 1
    close_idx = _balanced_paren_end(query, open_idx)
    return query[: open_idx + 1] + f"\n        {stub_select}\n    " + query[close_idx:]


def describe_coverage(ex: Extracted, source: str) -> str:
    lines = [f"Coverage for {source}:",
             f"  replayed read-only (as CTEs, in order): {', '.join(ex.stages) or '(none)'}, then the SELECT of INSERT INTO {ex.final_target}",
             "  dropped on purpose: the INSERT itself and its WHERE NOT EXISTS guard (V1 rows for this config already exist)"]
    if ex.not_replayed:
        lines.append("  NOT replayed (procedural / write statements; their results are not checked here):")
        lines += [f"    - {s}" for s in ex.not_replayed]
    return "\n".join(lines)
