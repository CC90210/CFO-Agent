<#
.SYNOPSIS
  Atlas (CFO-Agent) quickstart for Windows PowerShell.

.DESCRIPTION
  Usage:
    irm https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.ps1 | iex

  Atlas ships through the unified OASIS AI Agent Factory installer hosted
  in CC90210/CEO-Agent. This shim just preselects the `atlas` profile so
  the user lands directly in Atlas's wizard with no extra clicks.

  When piped through iex (the typical case), positional flags get lost,
  so we set $env:OASIS_PROFILE before invoking the upstream irm|iex —
  that's the documented escape hatch the upstream installer reads.
#>

param(
    [switch]$AutoInstall,
    [switch]$NoAutoInstall
)

$ErrorActionPreference = 'Stop'

$Remote  = 'https://raw.githubusercontent.com/CC90210/CEO-Agent/main/install/quickstart.ps1'
$Profile = 'atlas'

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

Write-Host "Atlas (CFO Agent) - fetching unified installer" -ForegroundColor Green
Write-Host "  source: $Remote"  -ForegroundColor DarkGray
Write-Host "  profile: atlas (Personal CFO - Tax - Wealth - Research)" -ForegroundColor DarkGray
Write-Host ""

# Forward auto-install consent through the OASIS_* env vars (positional
# flags don't survive irm|iex; the upstream installer documents this).
if ($AutoInstall)   { $env:OASIS_AUTO_INSTALL    = '1' }
if ($NoAutoInstall) { $env:OASIS_NO_AUTO_INSTALL = '1' }
$env:OASIS_PROFILE = $Profile

# Fetch + invoke. Same pattern as the upstream README.
Invoke-RestMethod -Uri $Remote | Invoke-Expression
