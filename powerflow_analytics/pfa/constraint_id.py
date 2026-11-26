"""Constraint identity: (FROMNUM, TONUM, CKT, CTGLABEL), written "FROM-TO-CKT@CTG"."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ConstraintId:
    fromnum: int
    tonum: int
    ckt: str
    ctglabel: str

    @classmethod
    def parse(cls, key: str) -> "ConstraintId":
        """Split on the first two '-' and the first '@' (a CTG may itself contain '-', '@' or spaces); no stripping."""
        parts = str(key).split("-", 2)
        if len(parts) != 3 or "@" not in parts[2]:
            raise ValueError(f"malformed constraint key {key!r}; expected 'FROM-TO-CKT@CTG'")
        ckt, _, ctg = parts[2].partition("@")
        try:
            return cls(int(parts[0]), int(parts[1]), ckt, ctg)
        except ValueError:
            raise ValueError(f"malformed constraint key {key!r}: FROM/TO must be integers") from None

    @property
    def line_key(self) -> str:
        return f"{self.fromnum}-{self.tonum}-{self.ckt}"

    def __str__(self) -> str:
        return f"{self.line_key}@{self.ctglabel}"


def constraint_key(df: pd.DataFrame) -> pd.Series:
    return (
        df["FROMNUM"].astype(int).astype(str)
        + "-" + df["TONUM"].astype(int).astype(str)
        + "-" + df["CKT"].astype(str).str.strip()
        + "@" + df["CTGLABEL"].astype(str).str.strip()
    )


def resolve(cache, spec: str) -> ConstraintId:
    """`spec` is a full key or a bare line LABEL; a label resolves to its dominant binding contingency in outctgviol2."""
    from .analysis.constraints import BINDING_PCT

    if "@" in spec:
        return ConstraintId.parse(spec)
    branch = cache.load("outbranch2", columns=["FROMNUM", "TONUM", "CKT", "LABEL"])
    ov = cache.load("outctgviol2", columns=["FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT"])
    m = branch[branch["LABEL"].astype(str) == str(spec)].drop_duplicates(["FROMNUM", "TONUM", "CKT"])
    if m.empty:
        raise ValueError(f"line label {spec!r} not found in cached outbranch2")
    if len(m) > 1:
        print(f"  note: label {spec!r} maps to {len(m)} FROMNUM/TONUM/CKT combos; "
              f"using the first ({m.iloc[0][['FROMNUM','TONUM','CKT']].to_dict()})")
    row = m.iloc[0]
    fromnum, tonum, ckt = int(row.FROMNUM), int(row.TONUM), str(row.CKT)
    sub = ov[(ov.FROMNUM == fromnum) & (ov.TONUM == tonum) & (ov.CKT == ckt)]
    bind = sub[sub.LIMVIOLPCT >= BINDING_PCT]
    if bind.empty:
        raise ValueError(f"no binding runs found for {spec!r} ({fromnum}-{tonum}-{ckt})")
    ctg = bind.groupby("CTGLABEL").size().sort_values(ascending=False).index[0]
    return ConstraintId(fromnum, tonum, ckt, ctg)
