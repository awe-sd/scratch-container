#!/bin/sh
# gitaccess.sh — example for use outside the Docker agent image.
#
# Instead of writing a one-time token into git config (which expires in 1 hour
# and breaks `git push`), this installs a credential helper that fetches a fresh
# token from the token-vending sidecar on every git network operation.
#
# Usage (source this file or run it once per shell session):
#   source ./gitaccess.sh
#   # or: . ./gitaccess.sh
#
# Requirements:
#   - AGENT_ID env var set to your agent name (e.g. "tessera-container")
#   - AGENT_SECRET_FILE pointing to the file containing the agent secret,
#     or AGENT_SECRET set directly (less safe — visible in `ps`)
#   - TOKEN_VENDING_URL set to the sidecar URL (default: http://localhost:8080)
#   - curl and jq available
#
# The credential helper is written to ~/.local/bin/ on first run and reused
# on subsequent runs. git is configured in ~/.gitconfig with an empty-helper
# reset so that any system-level credential helpers (e.g. VS Code's) are
# bypassed without requiring GIT_CONFIG_NOSYSTEM=1 in every shell.

set -eu

TOKEN_VENDING_URL="${TOKEN_VENDING_URL:-http://localhost:8080}"

# Install the credential helper.
HELPER_PATH="${HOME}/.local/bin/git-credential-token-vending"
mkdir -p "$(dirname "$HELPER_PATH")"

cat > "$HELPER_PATH" << 'EOF'
#!/bin/sh
[ "$1" = "get" ] || exit 0
SECRET_FILE="${AGENT_SECRET_FILE:-/run/secrets/agent-secret}"
RESPONSE=$(curl -fsS \
  -H "X-Agent-Secret: $(cat "$SECRET_FILE")" \
  "${TOKEN_VENDING_URL:-http://localhost:8080}/token?agent=${AGENT_ID}")
printf 'username=x-access-token\n'
printf 'password=%s\n' "$(printf '%s' "$RESPONSE" | jq -r .token)"
EOF
chmod +x "$HELPER_PATH"

# Register the helper in ~/.gitconfig using the empty-helper reset trick:
#   credential.helper =        clears any previously registered helpers
#                              (including system-level ones like VS Code's)
#   credential.helper = <ours> adds ours as the only active helper
#
# This means git ignores /etc/gitconfig's credential entries without needing
# GIT_CONFIG_NOSYSTEM=1 in the environment of every git invocation.
git config --global --replace-all credential.helper ""
git config --global --add credential.helper "$HELPER_PATH"
