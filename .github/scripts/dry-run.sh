#!/usr/bin/env sh
# CI dry-run of install.sh with stubbed pi/npx and an isolated HOME.
# Usage: dry-run.sh <full|skill-only>
set -eu

MODE="${1:-full}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

STUB="$(mktemp -d)/bin"
mkdir -p "$STUB"
printf '#!/usr/bin/env sh\necho "[pi] $*" >> "$PI_CALLS"\n' >"$STUB/pi"
printf '#!/usr/bin/env sh\necho "[npx] $*" >> "$PI_CALLS"\n' >"$STUB/npx"
chmod +x "$STUB/pi" "$STUB/npx"

H="$(mktemp -d)"
CALLS="$(mktemp)"
mkdir -p "$H/.pi/agent/npm" # a real `pi install` creates this

fail() {
  echo "FAIL: $1"
  exit 1
}

if [ "$MODE" = skill-only ]; then
  PATH="$STUB:$PATH" HOME="$H" PI_CALLS="$CALLS" BULLETPROOF_SRC="$REPO" \
    BULLETPROOF_SKILL_ONLY=1 sh "$REPO/install.sh" pi
  [ ! -f "$H/.pi/agent/pi-fff.json" ] || fail "layer not skipped"
  [ ! -s "$CALLS" ] || fail "plugins installed under skill-only"
  grep -q '>>> bulletproof bpi >>>' "$H/.bashrc" || fail "bpi should still wire"
  echo "skill-only dry-run: all assertions passed"
  exit 0
fi

PATH="$STUB:$PATH" HOME="$H" PI_CALLS="$CALLS" BULLETPROOF_SRC="$REPO" sh "$REPO/install.sh" pi
[ -f "$H/.pi/agent/pi-fff.json" ] || fail "pi-fff.json not copied"
[ -f "$H/.pi/agent/extensions/search-guard/index.ts" ] || fail "search-guard not copied"
[ "$(grep -c '\[pi\] install npm:' "$CALLS")" -eq 9 ] || fail "expected 9 plugin installs"
grep -q 'playwright install chromium' "$CALLS" || fail "playwright not invoked"
[ -f "$H/.pi/agent/prompts/bulletproof.system.md" ] || fail "system prompt not generated"
if head -1 "$H/.pi/agent/prompts/bulletproof.system.md" | grep -q '^---$'; then
  fail "frontmatter leaked into system prompt"
fi
grep -q '>>> bulletproof bpi >>>' "$H/.bashrc" || fail "bpi not wired"
echo "install.sh full dry-run: all assertions passed"
