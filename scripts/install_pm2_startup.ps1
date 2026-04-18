# scripts/install_pm2_startup.ps1
# ---------------------------------------------------------------------------
# Registers a Windows Task Scheduler entry that runs `pm2 resurrect` at user
# login, bringing Atlas (and any other pm2-managed app, like Bravo) back up
# automatically after Windows reboots.
#
# No admin required — registers at user level only.
#
# Run ONCE:
#   powershell -ExecutionPolicy Bypass -File scripts\install_pm2_startup.ps1
#
# Verify:
#   schtasks /query /tn "PM2 Resurrect on Login"
#
# Remove:
#   schtasks /delete /tn "PM2 Resurrect on Login" /f
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$taskName = 'PM2 Resurrect on Login'
$pm2Cmd = (Get-Command pm2.cmd -ErrorAction SilentlyContinue).Source

if (-not $pm2Cmd) {
    Write-Host "ERROR: pm2.cmd not found on PATH. Install pm2 globally first:" -ForegroundColor Red
    Write-Host "  npm install -g pm2" -ForegroundColor White
    exit 1
}

Write-Host "[1/3] Found pm2 at: $pm2Cmd" -ForegroundColor Cyan

# Build the action — run pm2 resurrect in the background, log output for debugging
$logDir = Join-Path $env:USERPROFILE '.pm2\startup-log'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$action = New-ScheduledTaskAction `
    -Execute 'cmd.exe' `
    -Argument "/c `"$pm2Cmd resurrect > `"$logDir\resurrect-out.log`" 2> `"$logDir\resurrect-err.log`"`""

# Trigger on any logon for this user (60-second delay so PATH + network are ready)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERDOMAIN\$env:USERNAME
$trigger.Delay = 'PT60S'

# Settings: don't stop if on batteries, run even if missed, no time limit
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

# Principal: run as the logged-in user, no elevation
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERDOMAIN\$env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Write-Host "[2/3] Registering scheduled task: $taskName" -ForegroundColor Cyan

# Remove any existing task with this name, then register the new one
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description 'Resurrect pm2-managed processes (Atlas CFO, Bravo) after user login' | Out-Null

Write-Host "[3/3] Done. Task will run at your next login." -ForegroundColor Green
Write-Host ""
Write-Host "Verify now:" -ForegroundColor Yellow
Write-Host "  schtasks /query /tn `"$taskName`"" -ForegroundColor White
Write-Host ""
Write-Host "First real test: reboot Windows. After login, wait 60s then run:" -ForegroundColor Yellow
Write-Host "  pm2 status" -ForegroundColor White
Write-Host "You should see atlas-telegram + bravo-* already online." -ForegroundColor White
