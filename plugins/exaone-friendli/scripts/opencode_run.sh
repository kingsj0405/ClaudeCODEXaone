#!/usr/bin/env bash

# Thin wrapper around `opencode run` for non-interactive invocation.
#
# Usage:
#   bash scripts/opencode_run.sh "<prompt>" [extra opencode flags...]
#
# Examples:
#   bash scripts/opencode_run.sh "Explain closures in Go"
#   bash scripts/opencode_run.sh --format json "List files in src/"
#   bash scripts/opencode_run.sh --model friendli/LGAI-EXAONE/K-EXAONE-236B-A23B "..."
#
# Env overrides:
#   OPENCODE_MODEL              Override the default model
#                               (default: friendli/LGAI-EXAONE/K-EXAONE-236B-A23B)
#   OPENCODE_BIN                Override opencode binary path (default: `opencode` on PATH)
#   OPENCODE_INSECURE_TLS=1     Disable Node TLS certificate verification.
#                               ONLY for networks behind a TLS-inspecting corporate proxy
#                               that injects its own root CA. Off by default: turning it on
#                               makes every opencode request vulnerable to interception.
#                               Prefer pointing NODE_EXTRA_CA_CERTS at your proxy's root CA.

set -euo pipefail

MODEL="${OPENCODE_MODEL:-friendli/LGAI-EXAONE/K-EXAONE-236B-A23B}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"

if [[ $# -eq 0 ]]; then
  echo "Usage: bash scripts/opencode_run.sh \"<prompt>\" [extra opencode flags...]" >&2
  exit 2
fi

if ! command -v "$OPENCODE_BIN" >/dev/null 2>&1; then
  echo "Error: opencode CLI not found (looked for '$OPENCODE_BIN')." >&2
  echo "Install it with: npm install -g opencode-ai" >&2
  exit 127
fi

# If the caller already passed --model anywhere, do not inject our default.
inject_model=1
for arg in "$@"; do
  case "$arg" in
    --model|-m|--model=*|-m=*) inject_model=0 ;;
  esac
done

if [[ "$inject_model" -eq 1 ]]; then
  set -- --model "$MODEL" "$@"
fi

if [[ "${OPENCODE_INSECURE_TLS:-0}" == "1" ]]; then
  echo "warning: OPENCODE_INSECURE_TLS=1 — TLS certificate verification disabled" >&2
  export NODE_TLS_REJECT_UNAUTHORIZED=0
fi

exec "$OPENCODE_BIN" run "$@"
