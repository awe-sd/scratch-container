#!/bin/sh
set -eu

# Point git at a tmpfs-backed config so the vended token never touches
# persistent disk — GIT_CONFIG_GLOBAL is inherited by exec'd child processes.
export GIT_CONFIG_GLOBAL=/tmp/.gitconfig

git config --global credential.helper /usr/local/bin/git-credential-token-vending
git config --global user.name "${AGENT_GIT_NAME}"
git config --global user.email "${AGENT_GIT_EMAIL}"

exec "$@"
