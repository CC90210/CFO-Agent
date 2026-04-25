#!/usr/bin/env bash
# Atlas (CFO-Agent) quickstart — one-line installer for macOS / Linux / WSL.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.sh | bash
#
# Atlas ships through the unified OASIS AI Agent Factory installer hosted in
# CC90210/CEO-Agent. This shim just preselects --profile atlas so the user
# lands directly in Atlas's wizard with no extra clicks.

set -euo pipefail

REMOTE="https://raw.githubusercontent.com/CC90210/CEO-Agent/main/install/quickstart.sh"
PROFILE="atlas"

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    C_GREEN=$'\033[1;32m'; C_DIM=$'\033[2m'; C_RESET=$'\033[0m'
else
    C_GREEN=''; C_DIM=''; C_RESET=''
fi

printf '%sAtlas (CFO Agent) — fetching unified installer%s\n' "$C_GREEN" "$C_RESET"
printf '%s  source: %s%s\n' "$C_DIM" "$REMOTE" "$C_RESET"
printf '%s  profile: atlas (Personal CFO · Tax · Wealth · Research)%s\n\n' "$C_DIM" "$C_RESET"

if ! command -v curl >/dev/null 2>&1; then
    echo "curl not found. Install curl, then re-run." >&2
    exit 1
fi

# Pass --profile through to the upstream installer; forward any extra flags.
curl -sSL "$REMOTE" | bash -s -- --profile "$PROFILE" "$@"
