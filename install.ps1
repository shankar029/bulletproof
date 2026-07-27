#!/usr/bin/env pwsh
# Installs the bulletproof skill + launcher for a terminal coding agent (Windows / PowerShell).
#
# Usage:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) pi
#   ./install.ps1 <pi|claude|copilot>
#
# Env:
#   BULLETPROOF_REF   git ref (branch/tag) to install         (default: main)
#   BULLETPROOF_SRC   use a local checkout instead of download (for testing/offline)
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
    Invoke-WebRequest -Uri "https://github.com/$Repo/archive/refs/heads/$Ref.zip" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $src = Join-Path $tmp "bulletproof-$Ref"
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { throw "SKILL.md missing in archive (bad ref '$Ref'?)" }
  }

  function Install-Skill($skillsRoot) {
    $dest = Join-Path $skillsRoot 'bulletproof'
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $src 'SKILL.md') (Join-Path $dest 'SKILL.md') -Force
    $refDest = Join-Path $dest 'references'
    if (Test-Path $refDest) { Remove-Item $refDest -Recurse -Force }
    Copy-Item (Join-Path $src 'references') $refDest -Recurse -Force
    Write-Host "  - skill    -> $dest"
  }
  function Install-File($from, $to) {
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    Copy-Item $from $to -Force
    Write-Host "  - launcher -> $to"
  }

  switch ($Agent) {
    'pi' {
      Install-Skill (Join-Path $HOME '.agents/skills')
      Install-File (Join-Path $src 'launchers/pi/prompts/bulletproof.md') (Join-Path $HOME '.pi/agent/prompts/bulletproof.md')
      $hint = 'run   /bulletproof <requirement>   (or /skill:bulletproof)'
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
}
finally {
  if ($tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
