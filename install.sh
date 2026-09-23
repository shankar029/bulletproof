#!/usr/bin/env sh
# Installs the bulletproof skill + launcher for a terminal coding agent.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
#   sh install.sh <pi|claude|copilot>
#
# Env:
#   BULLETPROOF_REF        git ref (branch/tag) to install         (default: main)
#   BULLETPROOF_SRC        use a local checkout instead of download (for testing/offline)
#   BULLETPROOF_SKILL_ONLY when set (pi only), install just the skill + agents and skip
#                          the pi workflow layer (packages, config, extensions)
set -eu

REPO="shankar029/bulletproof"
REF="${BULLETPROOF_REF:-main}"
AGENT="${1:-}"

die() {
  echo "error: $*" >&2
  exit 1
}

case "$AGENT" in
pi | claude | copilot) ;;
"" | -h | --help | help)
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
  [ -z "$AGENT" ] && exit 1 || exit 0
  ;;
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
  command -v tar >/dev/null 2>&1 || die "tar is required"
  TMP="$(mktemp -d)"
  echo "-> downloading $REPO@$REF ..."
  # Generic archive form resolves a branch, tag, or commit SHA (refs/heads is branch-only).
  curl -fsSL "https://github.com/$REPO/archive/$REF.tar.gz" | tar -xz -C "$TMP" ||
    die "download/extract failed for ref '$REF'"
  # GitHub strips a leading 'v' from tag dir names, so find the extracted dir rather than guess.
  SRC="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [ -n "$SRC" ] && [ -f "$SRC/SKILL.md" ] || die "SKILL.md missing in archive (bad ref '$REF'?)"
fi

install_skill() { # $1 = skills root; installs <root>/bulletproof/{SKILL.md,references/,scripts/,assets/}
  dest="$1/bulletproof"
  mkdir -p "$dest"
  cp "$SRC/SKILL.md" "$dest/SKILL.md"
  rm -rf "$dest/references"
  cp -R "$SRC/references" "$dest/references"
  rm -rf "$dest/scripts" "$dest/assets"
  [ -d "$SRC/scripts" ] && cp -R "$SRC/scripts" "$dest/scripts"
  [ -d "$SRC/assets" ] && cp -R "$SRC/assets" "$dest/assets"
  echo "  - skill    -> $dest"
}
install_file() { # $1 = src file, $2 = dest file
  mkdir -p "$(dirname "$2")"
  cp "$1" "$2"
  echo "  - launcher -> $2"
}
install_agent() { # $1 = src agent .md, $2 = dest, $3 = skill dir to substitute for {{BULLETPROOF_SKILL_DIR}}
  mkdir -p "$(dirname "$2")"
  sed "s#{{BULLETPROOF_SKILL_DIR}}#$3#g" "$1" >"$2"
  echo "  - agent    -> $2"
}

# The pi workflow layer: the plugins, config, and hooks the bulletproof skill/agent
# assumes. Augments the user's ~/.pi/agent without clobbering their provider/model/theme.
install_pi_workflow() {
  PI_DIR="${HOME}/.pi/agent"
  mkdir -p "$PI_DIR"

  # fff "override" mode: the built-in tool NAMES grep/find/multi_grep resolve to the fast,
  # git-aware fff implementations, so every agent allowlist that already says "grep, find"
  # gets them with no frontmatter change - including subagents.
  if [ -f "$SRC/agent/pi-fff.json" ]; then
    cp -f "$SRC/agent/pi-fff.json" "$PI_DIR/pi-fff.json"
    echo "  - config   -> $PI_DIR/pi-fff.json"
  fi

  # search-guard extension: blocks repo-wide grep -r / find . before they run and bounds
  # every unbounded bash call with a default wall-clock timeout.
  if [ -d "$SRC/agent/extensions" ]; then
    mkdir -p "$PI_DIR/extensions"
    cp -Rf "$SRC/agent/extensions/." "$PI_DIR/extensions/"
    echo "  - hooks    -> $PI_DIR/extensions/"
  fi

  # Plugins. Install pi if it is missing, then install each pinned package.
  if ! command -v pi >/dev/null 2>&1; then
    echo "  - pi not found; installing @earendil-works/pi-coding-agent globally ..."
    if command -v npm >/dev/null 2>&1; then
      npm install -g --ignore-scripts @earendil-works/pi-coding-agent@latest ||
        echo "  ! pi install failed; install it manually, then re-run this installer"
    else
      echo "  ! npm not found - install Node.js >= 18 + npm, then re-run this installer"
    fi
  fi
  if command -v pi >/dev/null 2>&1 && [ -f "$SRC/agent/packages.txt" ]; then
    echo "  - installing pi plugins from packages.txt ..."
    while IFS= read -r line; do
      spec="${line%%#*}" # strip inline comment
      spec="$(printf '%s' "$spec" | tr -d '[:space:]')"
      [ -z "$spec" ] && continue
      echo "    + $spec"
      pi install "$spec" || echo "    ! failed: $spec (install manually with: pi install $spec)"
    done <"$SRC/agent/packages.txt"
    # pi-browser-debug drives Chrome through Playwright - fetch its Chromium binary.
    if grep -q 'pi-browser-debug' "$SRC/agent/packages.txt"; then
      echo "  - installing Playwright Chromium for pi-browser-debug ..."
      (cd "$PI_DIR/npm" 2>/dev/null && npx --yes playwright install chromium) ||
        echo "    ! Playwright Chromium install failed; run 'npx playwright install chromium' manually"
    fi
  else
    echo "  ! skipped plugin install (pi unavailable); run 'pi install <spec>' per agent/packages.txt"
  fi
}

# Generate the system prompt used by --append-system-prompt (the installer ships the agent
# file + slash launcher, but not the system-prompt form), then install a `bpi` shell
# function so the drift-proof agent can be launched without typing the full flag.
install_bpi() {
  bp_agent="${HOME}/.pi/agent/agents/bulletproof.md"
  bp_sys="${HOME}/.pi/agent/prompts/bulletproof.system.md"
  if [ -f "$bp_agent" ]; then
    # Strip the YAML frontmatter (everything up to and including the second '---').
    awk 'BEGIN{fm=0}/^---$/{fm++;next}fm>=2' "$bp_agent" >"$bp_sys"
    echo "  - sysprompt-> $bp_sys"
  else
    echo "  ! agents/bulletproof.md not found; skipped bulletproof.system.md generation"
    return
  fi

  # Idempotently add the `bpi` function to the user's shell profile(s).
  add_bpi_to_profile() { # $1 = profile file
    prof="$1"
    [ -f "$prof" ] || : >"$prof"
    if grep -q '>>> bulletproof bpi >>>' "$prof" 2>/dev/null; then
      echo "  - bpi already present in $(basename "$prof")"
      return
    fi
    cat >>"$prof" <<'BPI'

# >>> bulletproof bpi >>>
# Run the drift-proof bulletproof agent: bpi "<req>" | bpi --fast "..." | bpi --full "..."
bpi() {
  sys="${HOME}/.pi/agent/prompts/bulletproof.system.md"
  pfx=""
  case "$1" in
    --fast|-Fast|fast) pfx="mode: fast"; shift ;;
    --full|-Full|full) pfx="mode: full"; shift ;;
  esac
  text="$*"
  [ -n "$pfx" ] && text="$(printf '%s\n%s' "$pfx" "$text")"
  if [ -z "$text" ]; then pi --append-system-prompt "$sys"
  else pi --append-system-prompt "$sys" "$text"; fi
}
# <<< bulletproof bpi <<<
BPI
    echo "  - bpi func -> $(basename "$prof")"
  }
  add_bpi_to_profile "${HOME}/.bashrc"
  [ -f "${HOME}/.zshrc" ] && add_bpi_to_profile "${HOME}/.zshrc"
}

case "$AGENT" in
pi)
  install_skill "${HOME}/.agents/skills"
  install_file "$SRC/launchers/pi/prompts/bulletproof.md" "${HOME}/.pi/agent/prompts/bulletproof.md"
  for a in "$SRC"/launchers/pi/agents/*.md; do
    install_agent "$a" "${HOME}/.pi/agent/agents/$(basename "$a")" "${HOME}/.agents/skills/bulletproof"
  done
  if [ -z "${BULLETPROOF_SKILL_ONLY:-}" ]; then
    echo "-> installing pi workflow layer (plugins, config, hooks) ..."
    install_pi_workflow
  else
    echo "-> BULLETPROOF_SKILL_ONLY set: skipping the pi workflow layer"
  fi
  echo "-> wiring the bpi launcher (system prompt + shell function) ..."
  install_bpi
  HINT="run   /bulletproof <requirement>   (or /skill:bulletproof), the bpi command, or launch the bulletproof agent"
  ;;
claude)
  install_skill "${HOME}/.claude/skills"
  install_file "$SRC/launchers/claude/commands/bulletproof.md" "${HOME}/.claude/commands/bulletproof.md"
  HINT="run   /bulletproof <requirement>"
  ;;
copilot)
  install_skill "${HOME}/.copilot"
  install_file "$SRC/launchers/copilot/agents/bulletproof.agent.md" "${HOME}/.copilot/agents/bulletproof.agent.md"
  HINT="start copilot --agent bulletproof"
  ;;
esac

echo "OK: bulletproof installed for $AGENT"
echo "    next: $HINT"
if [ "$AGENT" = pi ]; then
  echo "    tip:  reload your shell (. ~/.bashrc) once, then:  bpi \"<requirement>\"  (or bpi --fast / --full)"
fi
