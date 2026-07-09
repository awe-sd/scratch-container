# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a scratch/sandbox container, not a single-purpose project. There is no one major goal — the user tests different ideas here before branching mature ones out into their own dedicated repos. Expect loosely related, in-progress subfolders (e.g. `branch_tracking/`) rather than one coherent codebase. Don't assume subfolders share dependencies, conventions, or a common architecture unless they clearly do.

## Git / credential setup

- `gitaccess.sh` — for use *outside* the Docker agent image. Installs a git credential helper (`~/.local/bin/git-credential-token-vending`) that fetches a fresh token from a token-vending sidecar (`TOKEN_VENDING_URL`, default `http://localhost:8080`) on every git network operation, using `AGENT_ID` and `AGENT_SECRET_FILE`/`AGENT_SECRET`. Source it once per shell: `. ./gitaccess.sh`. Only works over HTTPS remotes (`https://github.com/...`), not `git@github.com:...` SSH URLs.
- `startup.sh` — entrypoint wrapper intended for the Docker agent image itself. Points git at a tmpfs-backed config (`GIT_CONFIG_GLOBAL=/tmp/.gitconfig`) so vended tokens never touch persistent disk, sets `user.name`/`user.email` from `AGENT_GIT_NAME`/`AGENT_GIT_EMAIL`, then `exec`s the given command.

## Independent repos cloned elsewhere

Other Appian Way repos (`LocalSkills`, `awconnect`) have been cloned under `/home/node/` rather than inside this repo, since they are independent projects with their own git history — keep it that way rather than nesting other repos' `.git` directories under this one.

## Python environment

`.venv` here is a `uv`-managed virtualenv (`uv venv`) local to this repo. `awconnect` is installed into it in editable mode from the separate `/home/node/awconnect` checkout (`uv pip install -e /home/node/awconnect`) — edits to that checkout are picked up immediately without reinstalling.

**Always run Python through `uv`** (`uv run script.py`, `uv run python -c ...`, `uv pip install ...`), never a bare `python`/`pip`. A minimal `pyproject.toml` marks this directory as the uv project root, so plain `uv run ...` from here (or any subfolder) resolves to this repo's `.venv` automatically — no `VIRTUAL_ENV=` override needed. If a container-wide `VIRTUAL_ENV` env var is set to something else, `uv run` still prefers the project `.venv` because `pyproject.toml` is present; only `uv pip install` without a preceding `uv run` can be redirected by a stray `VIRTUAL_ENV`, so prefer `uv run python -m pip install ...` or `uv add`/`uv pip install` from this directory if that ever resurfaces.

## Subprojects

- `branch_tracking/` — in-progress transmission-branch tracking table design (ERCOT / `isomarketid = 6`). See its own `CLAUDE.md` for details specific to that work.
