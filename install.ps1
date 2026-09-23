#!/usr/bin/env pwsh
# Installs the bulletproof skill + launcher for a terminal coding agent (Windows / PowerShell).
#
# Usage:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) pi
#   ./install.ps1 <pi|claude|copilot>
#
# Env:
#   BULLETPROOF_REF        git ref (branch/tag) to install         (default: main)
#   BULLETPROOF_SRC        use a local checkout instead of download (for testing/offline)
#   BULLETPROOF_SKILL_ONLY when set (pi only), install just the skill + agents and skip
#                          the pi workflow layer (packages, config, extensions)
param(
  [Parameter(Position = 0)]
  [ValidateSet('pi', 'claude', 'copilot')]
  [string]$Agent
)
$ErrorActionPreference = 'Stop'
$Repo = 'shankar029/bulletproof'
$Ref = if ($env:BULLETPROOF_REF) { $env:BULLETPROOF_REF } else { 'main' }

if (-not $Agent) {
  Write-Host 'Usage: install.ps1 <pi|claude|copilot>'
  exit 1
}

$tmp = $null
try {
  if ($env:BULLETPROOF_SRC) {
    $src = $env:BULLETPROOF_SRC
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { throw "BULLETPROOF_SRC=$src has no SKILL.md" }
    Write-Host "-> using local source: $src"
  }
  else {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('bulletproof-' + [guid]::NewGuid())
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $zip = Join-Path $tmp 'src.zip'
    Write-Host "-> downloading $Repo@$Ref ..."
    # Generic archive form resolves a branch, tag, or commit SHA (refs/heads is branch-only).
    Invoke-WebRequest -Uri "https://github.com/$Repo/archive/$Ref.zip" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    # GitHub strips a leading 'v' from tag dir names, so take the extracted dir rather than guess.
    $src = (Get-ChildItem -Path $tmp -Directory | Select-Object -First 1).FullName
    if (-not $src -or -not (Test-Path (Join-Path $src 'SKILL.md'))) { throw "SKILL.md missing in archive (bad ref '$Ref'?)" }
  }

  function Install-Skill($skillsRoot) {
    $dest = Join-Path $skillsRoot 'bulletproof'
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $src 'SKILL.md') (Join-Path $dest 'SKILL.md') -Force
    foreach ($part in @('references', 'scripts', 'assets')) {
      $from = Join-Path $src $part
      if (Test-Path $from) {
        $to = Join-Path $dest $part
        if (Test-Path $to) { Remove-Item $to -Recurse -Force }
        Copy-Item $from $to -Recurse -Force
      }
    }
    Write-Host "  - skill    -> $dest"
  }
  function Install-File($from, $to) {
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    Copy-Item $from $to -Force
    Write-Host "  - launcher -> $to"
  }
  function Install-Agent($from, $to, $skillDir) {
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    (Get-Content $from -Raw).Replace('{{BULLETPROOF_SKILL_DIR}}', $skillDir) | Set-Content $to -NoNewline
    Write-Host "  - agent    -> $to"
  }

  # The pi workflow layer: the plugins, config, and hooks the bulletproof skill/agent
  # assumes. Augments ~/.pi/agent without clobbering the user's provider/model/theme.
  function Install-PiWorkflow {
    $piDir = Join-Path $HOME '.pi/agent'
    New-Item -ItemType Directory -Force -Path $piDir | Out-Null

    # fff "override" mode: the built-in tool NAMES grep/find/multi_grep resolve to the fast,
    # git-aware fff implementations - every allowlist that already says "grep, find" gets them.
    $fff = Join-Path $src 'agent/pi-fff.json'
    if (Test-Path $fff) {
      Copy-Item $fff (Join-Path $piDir 'pi-fff.json') -Force
      Write-Host "  - config   -> $(Join-Path $piDir 'pi-fff.json')"
    }

    # search-guard extension: blocks repo-wide grep -r / find . before they run and bounds
    # every unbounded bash call with a default wall-clock timeout.
    $ext = Join-Path $src 'agent/extensions'
    if (Test-Path $ext) {
      $extDest = Join-Path $piDir 'extensions'
      New-Item -ItemType Directory -Force -Path $extDest | Out-Null
      Copy-Item (Join-Path $ext '*') $extDest -Recurse -Force
      Write-Host "  - hooks    -> $extDest"
    }

    # Plugins. Install pi if it is missing, then install each pinned package.
    if (-not (Get-Command pi -ErrorAction SilentlyContinue)) {
      Write-Host '  - pi not found; installing @earendil-works/pi-coding-agent globally ...'
      if (Get-Command npm -ErrorAction SilentlyContinue) {
        try { npm install -g --ignore-scripts '@earendil-works/pi-coding-agent@latest' }
        catch { Write-Host '  ! pi install failed; install it manually, then re-run this installer' }
      }
      else { Write-Host '  ! npm not found - install Node.js >= 18 + npm, then re-run this installer' }
    }
    $pkgFile = Join-Path $src 'agent/packages.txt'
    if ((Get-Command pi -ErrorAction SilentlyContinue) -and (Test-Path $pkgFile)) {
      Write-Host '  - installing pi plugins from packages.txt ...'
      $pluginFailures = @()
      foreach ($raw in Get-Content $pkgFile) {
        $spec = ($raw -replace '#.*$', '').Trim()
        if (-not $spec) { continue }
        Write-Host "    + $spec"
        pi install $spec
        if ($LASTEXITCODE -ne 0) { Write-Host "    ! failed: $spec"; $pluginFailures += $spec }
      }
      # pi-browser-debug drives Chrome through Playwright - fetch its Chromium binary.
      if (Select-String -Path $pkgFile -Pattern 'pi-browser-debug' -Quiet) {
        Write-Host '  - installing Playwright Chromium for pi-browser-debug ...'
        $npmDir = Join-Path $piDir 'npm'
        try { Push-Location $npmDir; npx --yes playwright install chromium; Pop-Location }
        catch { Write-Host "    ! Playwright Chromium install failed; run 'npx playwright install chromium' manually" }
      }
      if ($pluginFailures.Count -gt 0) {
        Write-Host "  ! some plugins did NOT install: $($pluginFailures -join ' ')"
        Write-Host '    retry each with: pi install <spec>'
      }
    }
    else {
      Write-Host '  ! skipped plugin install (pi unavailable); run pi install <spec> per agent/packages.txt'
    }
  }

  # Generate the system prompt used by --append-system-prompt (the installer ships the agent
  # file + slash launcher, but not the system-prompt form), then install a `bpi` function into
  # $PROFILE so the drift-proof agent can be launched without typing the full flag.
  function Install-Bpi {
    $bpAgent = Join-Path $HOME '.pi/agent/agents/bulletproof.md'
    $bpSys = Join-Path $HOME '.pi/agent/prompts/bulletproof.system.md'
    if (Test-Path $bpAgent) {
      # Strip the YAML frontmatter (everything up to and including the second '---').
      $lines = Get-Content $bpAgent
      $fm = 0; $body = New-Object System.Collections.Generic.List[string]
      foreach ($l in $lines) {
        if ($fm -lt 2) { if ($l -eq '---') { $fm++ }; continue }
        $body.Add($l)
      }
      Set-Content -Path $bpSys -Value $body
      Write-Host "  - sysprompt-> $bpSys"
    }
    else {
      Write-Host '  ! agents/bulletproof.md not found; skipped bulletproof.system.md generation'
      return
    }

    # Idempotently add the `bpi` function to the PowerShell profile.
    $prof = $PROFILE.CurrentUserAllHosts
    New-Item -ItemType Directory -Force -Path (Split-Path $prof) | Out-Null
    if ((Test-Path $prof) -and (Select-String -Path $prof -Pattern '>>> bulletproof bpi >>>' -Quiet)) {
      Write-Host '  - bpi already present in $PROFILE'
      return
    }
    $block = @'

# >>> bulletproof bpi >>>
# Run the drift-proof bulletproof agent: bpi "<req>" | bpi -Fast "..." | bpi -Full "..."
function bpi {
  param([switch]$Fast, [switch]$Full)
  $sys = Join-Path $HOME '.pi/agent/prompts/bulletproof.system.md'
  $text = ($args -join ' ')
  if ($Fast) { $text = "mode: fast`n$text" }
  elseif ($Full) { $text = "mode: full`n$text" }
  if ([string]::IsNullOrWhiteSpace($text)) { pi --append-system-prompt $sys }
  else { pi --append-system-prompt $sys $text }
}
# <<< bulletproof bpi <<<
'@
    Add-Content -Path $prof -Value $block
    Write-Host '  - bpi func -> $PROFILE'
  }

  switch ($Agent) {
    'pi' {
      Install-Skill (Join-Path $HOME '.agents/skills')
      Install-File (Join-Path $src 'launchers/pi/prompts/bulletproof.md') (Join-Path $HOME '.pi/agent/prompts/bulletproof.md')
      $skillDir = (Join-Path $HOME '.agents/skills/bulletproof') -replace '\\','/'
      Get-ChildItem (Join-Path $src 'launchers/pi/agents') -Filter *.md | ForEach-Object {
        Install-Agent $_.FullName (Join-Path $HOME (".pi/agent/agents/" + $_.Name)) $skillDir
      }
      if (-not $env:BULLETPROOF_SKILL_ONLY) {
        Write-Host '-> installing pi workflow layer (plugins, config, hooks) ...'
        Install-PiWorkflow
      }
      else {
        Write-Host '-> BULLETPROOF_SKILL_ONLY set: skipping the pi workflow layer'
      }
      Write-Host '-> wiring the bpi launcher (system prompt + shell function) ...'
      Install-Bpi
      $hint = 'run   /bulletproof <requirement>   (or /skill:bulletproof), the bpi command, or launch the bulletproof agent'
    }
    'claude' {
      Install-Skill (Join-Path $HOME '.claude/skills')
      Install-File (Join-Path $src 'launchers/claude/commands/bulletproof.md') (Join-Path $HOME '.claude/commands/bulletproof.md')
      $hint = 'run   /bulletproof <requirement>'
    }
    'copilot' {
      Install-Skill (Join-Path $HOME '.copilot')
      Install-File (Join-Path $src 'launchers/copilot/agents/bulletproof.agent.md') (Join-Path $HOME '.copilot/agents/bulletproof.agent.md')
      $hint = 'start copilot --agent bulletproof'
    }
  }
  Write-Host "OK: bulletproof installed for $Agent"
  Write-Host "    next: $hint"
  if ($Agent -eq 'pi' -and -not $env:BULLETPROOF_SKILL_ONLY) {
    Write-Host "    auth: run 'pi' then '/login' to authenticate your provider (secrets are never stored)"
    Write-Host "    check: 'pi list' shows the installed plugins"
  }
  if ($Agent -eq 'pi') {
    Write-Host '    tip:  reload your shell (. $PROFILE) once, then:  bpi "<requirement>"  (or bpi -Fast / -Full)'
  }
}
finally {
  if ($tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
