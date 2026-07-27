#!/usr/bin/env sh
# Installs the bulletproof skill + launcher for a terminal coding agent.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
#   sh install.sh <pi|claude|copilot>
#
# Env:
#   BULLETPROOF_REF   git ref (branch/tag) to install         (default: main)
#   BULLETPROOF_SRC   use a local checkout instead of download (for testing/offline)
set -eu

REPO="shankar029/bulletproof"
REF="${BULLETPROOF_REF:-main}"
AGENT="${1:-}"

die() { echo "error: $*" >&2; exit 1; }

case "$AGENT" in
  pi|claude|copilot) ;;
  ""|-h|--help|help)
    cat >&2 <<EOF
Install the bulletproof skill for a terminal coding agent.

Usage: install.sh <agent>
  agent:  pi | claude | copilot

Examples:
  curl -fsSL https://raw.githubusercontent.com/$REPO/$REF/install.sh | sh -s -- pi
  BULLETPROOF_REF=v0.1.0 sh install.sh claude

Env:
  BULLETPROOF_REF   git ref to install (default: main)
  BULLETPROOF_SRC   install from a local checkout instead of downloading
EOF
    [ -z "$AGENT" ] && exit 1 || exit 0 ;;
  *) die "unknown agent '$AGENT' (expected: pi | claude | copilot)" ;;
esac

TMP=""
cleanup() { [ -n "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT INT TERM

if [ -n "${BULLETPROOF_SRC:-}" ]; then
  SRC="$BULLETPROOF_SRC"
  [ -f "$SRC/SKILL.md" ] || die "BULLETPROOF_SRC=$SRC has no SKILL.md"
  echo "-> using local source: $SRC"
else
  command -v curl >/dev/null 2>&1 || die "curl is required"
  command -v tar  >/dev/null 2>&1 || die "tar is required"
  TMP="$(mktemp -d)"
  echo "-> downloading $REPO@$REF ..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$REF.tar.gz" | tar -xz -C "$TMP" \
    || die "download/extract failed for ref '$REF'"
  SRC="$TMP/bulletproof-$REF"
  [ -f "$SRC/SKILL.md" ] || die "SKILL.md missing in archive (bad ref '$REF'?)"
fi

install_skill() { # $1 = skills root; installs <root>/bulletproof/{SKILL.md,references/}
  dest="$1/bulletproof"
  mkdir -p "$dest"
  cp "$SRC/SKILL.md" "$dest/SKILL.md"
  rm -rf "$dest/references"
  cp -R "$SRC/references" "$dest/references"
  echo "  - skill    -> $dest"
}
install_file() { # $1 = src file, $2 = dest file
  mkdir -p "$(dirname "$2")"
  cp "$1" "$2"
  echo "  - launcher -> $2"
}

case "$AGENT" in
  pi)
    install_skill "${HOME}/.agents/skills"
    install_file "$SRC/launchers/pi/prompts/bulletproof.md" "${HOME}/.pi/agent/prompts/bulletproof.md"
    HINT="run   /bulletproof <requirement>   (or /skill:bulletproof)" ;;
  claude)
    install_skill "${HOME}/.claude/skills"
    install_file "$SRC/launchers/claude/commands/bulletproof.md" "${HOME}/.claude/commands/bulletproof.md"
    HINT="run   /bulletproof <requirement>" ;;
  copilot)
    install_skill "${HOME}/.copilot"
    install_file "$SRC/launchers/copilot/agents/bulletproof.agent.md" "${HOME}/.copilot/agents/bulletproof.agent.md"
    HINT="start copilot --agent bulletproof" ;;
esac

echo "OK: bulletproof installed for $AGENT"
echo "    next: $HINT"
