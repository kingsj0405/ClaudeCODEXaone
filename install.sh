#!/usr/bin/env bash
# Manual installer for ClaudeCODEXaone.
# Use this only if `claude plugin marketplace add` is unavailable — the plugin route is preferred.
#
# Usage:
#   git clone https://github.com/kingsj0405/ClaudeCODEXaone.git
#   cd ClaudeCODEXaone
#   bash install.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude"

if [[ ! -d "$ROOT/plugins" ]]; then
  echo "Error: plugins/ not found at $ROOT — run this script from the repo root." >&2
  exit 1
fi

echo "=== ClaudeCODEXaone — manual install ==="
echo ""

mkdir -p "$DEST"/{agents,commands,scripts,skills}

for plugin in exaone-friendli workflow; do
  src="$ROOT/plugins/$plugin"
  [[ -d "$src" ]] || continue

  for kind in agents commands; do
    [[ -d "$src/$kind" ]] || continue
    for f in "$src/$kind"/*.md; do
      [[ -f "$f" ]] || continue
      cp "$f" "$DEST/$kind/"
      echo "  $plugin/$kind/$(basename "$f") -> ~/.claude/$kind/"
    done
  done

  if [[ -d "$src/scripts" ]]; then
    for f in "$src/scripts"/*; do
      [[ -f "$f" ]] || continue
      cp "$f" "$DEST/scripts/"
      chmod +x "$DEST/scripts/$(basename "$f")"
      echo "  $plugin/scripts/$(basename "$f") -> ~/.claude/scripts/"
    done
  fi

  if [[ -d "$src/skills" ]]; then
    for d in "$src/skills"/*/; do
      [[ -d "$d" ]] || continue
      name="$(basename "$d")"
      rm -rf "${DEST:?}/skills/$name"
      cp -R "$d" "$DEST/skills/$name"
      echo "  $plugin/skills/$name/ -> ~/.claude/skills/$name/"
    done
  fi
done

# Plugin-installed agents resolve as `<plugin>:<agent>`; agents copied straight into
# ~/.claude/agents/ have no namespace, so the prefix would fail to resolve. Strip it.
for f in "$DEST"/agents/*.md "$DEST"/commands/*.md; do
  [[ -f "$f" ]] || continue
  if grep -q 'exaone-friendli:' "$f"; then
    sed -i '' 's|exaone-friendli:||g' "$f" 2>/dev/null || sed -i 's|exaone-friendli:||g' "$f"
    echo "  patched $(basename "$f"): stripped 'exaone-friendli:' namespace"
  fi
done

# Agents reference ${CLAUDE_PLUGIN_ROOT}, which only exists under the plugin runtime.
for f in "$DEST"/agents/*.md; do
  [[ -f "$f" ]] || continue
  if grep -q 'CLAUDE_PLUGIN_ROOT' "$f"; then
    sed -i '' "s|\${CLAUDE_PLUGIN_ROOT}|${DEST}|g" "$f" 2>/dev/null \
      || sed -i "s|\${CLAUDE_PLUGIN_ROOT}|${DEST}|g" "$f"
    echo "  patched $(basename "$f"): CLAUDE_PLUGIN_ROOT -> $DEST"
  fi
done

echo ""
echo "Done. Available globally:"
echo "  /k-exaone        ask K-EXAONE 236B (FriendliAI)"
echo "  /council         multi-model round-based deliberation"
echo "  korean-report    skill: rewrite an English draft as a Korean report"
echo ""
echo "Next: configure the opencode provider at ~/.config/opencode/opencode.json"
echo "  Template: $ROOT/opencode.json.template"
