"""
scripts/install_service.py
--------------------------
Helper to install Atlas as a Windows auto-start service.

Three options are offered:

  Option 1: Windows Task Scheduler
    Registers a task that starts run_atlas.py on user login.
    Uses schtasks.exe (built into Windows, no admin required for user tasks).

  Option 2: Startup Folder shortcut (batch file)
    Creates start_atlas.bat in the Windows Startup folder.
    Simplest option — runs when the user logs in.

  Option 3: PowerShell background job
    Registers a persistent background job via PowerShell.
    Useful for running in a terminal session without a visible window.

Usage
-----
  python scripts/install_service.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────

# The trading-agent project root (one level above this script)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_PYTHON_EXE = sys.executable
_ENTRY_POINT = _PROJECT_ROOT / "run_atlas.py"
_BAT_FILE = _PROJECT_ROOT / "start_atlas.bat"
_PS1_FILE = _PROJECT_ROOT / "start_atlas.ps1"

_TASK_NAME = "AtlasTradingAgent"

# Windows Startup folder — runs for the current user on login
_STARTUP_FOLDER = Path(
    os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
)


# ─────────────────────────────────────────────────────────────────────────────
#  Option 1: Task Scheduler
# ─────────────────────────────────────────────────────────────────────────────


def install_task_scheduler() -> None:
    """
    Register Atlas as a Windows Task Scheduler task that runs on user logon.
    The task runs with the current user's permissions — no admin required.
    """
    print("\nOption 1: Windows Task Scheduler")
    print("=" * 50)

    # Build the action: python run_atlas.py, working dir = project root
    cmd = [
        "schtasks",
        "/Create",
        "/TN", _TASK_NAME,
        "/TR", f'"{_PYTHON_EXE}" "{_ENTRY_POINT}"',
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F",  # Force overwrite if task already exists
    ]

    print(f"Task name:  {_TASK_NAME}")
    print(f"Python:     {_PYTHON_EXE}")
    print(f"Script:     {_ENTRY_POINT}")
    print(f"Trigger:    On logon")
    print()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("Task created successfully.")
            print()
            print("To verify: Open Task Scheduler and look for 'AtlasTradingAgent'")
            print("To remove: schtasks /Delete /TN AtlasTradingAgent /F")
        else:
            print(f"schtasks failed (code {result.returncode}):")
            print(result.stderr or result.stdout)
            print()
            print("Manual alternative — run this command yourself:")
            print(" ".join(cmd))
    except FileNotFoundError:
        print("schtasks.exe not found — you may not be on Windows.")
        print("Manual command:")
        print(" ".join(cmd))


# ─────────────────────────────────────────────────────────────────────────────
#  Option 2: Startup folder batch file
# ─────────────────────────────────────────────────────────────────────────────


def create_startup_bat() -> None:
    """
    Write start_atlas.bat and offer to copy it to the Windows Startup folder.
    The batch file launches Atlas in a minimised window on login.
    """
    print("\nOption 2: Windows Startup Folder (Batch File)")
    print("=" * 50)

    bat_content = (
        "@echo off\n"
        f"cd /d \"{_PROJECT_ROOT}\"\n"
        f"\"{_PYTHON_EXE}\" \"{_ENTRY_POINT}\"\n"
    )

    _BAT_FILE.write_text(bat_content, encoding="utf-8")
    print(f"Batch file created: {_BAT_FILE}")

    # Offer to copy to Startup folder
    if _STARTUP_FOLDER.exists():
        startup_bat = _STARTUP_FOLDER / "start_atlas.bat"
        try:
            import shutil
            shutil.copy2(_BAT_FILE, startup_bat)
            print(f"Copied to Startup folder: {startup_bat}")
            print()
            print("Atlas will now start automatically when you log into Windows.")
            print(f"To remove: delete {startup_bat}")
        except Exception as exc:  # noqa: BLE001
            print(f"Could not copy to Startup folder: {exc}")
            print()
            print("Manual step: copy this file to your Startup folder:")
            print(f"  Source: {_BAT_FILE}")
            print(f"  Destination: {_STARTUP_FOLDER}")
    else:
        print()
        print("Startup folder not found at expected path.")
        print("Manual step: copy this file to your Windows Startup folder:")
        print(f"  {_BAT_FILE}")
        print()
        print("To find your Startup folder: press Win+R, type 'shell:startup', press Enter")


# ─────────────────────────────────────────────────────────────────────────────
#  Option 3: PowerShell background job script
# ─────────────────────────────────────────────────────────────────────────────


def create_powershell_script() -> None:
    """
    Write start_atlas.ps1 that runs Atlas as a PowerShell background job.
    Useful for keeping Atlas running in a terminal session without blocking it.
    """
    print("\nOption 3: PowerShell Background Job")
    print("=" * 50)

    ps1_content = (
        "# start_atlas.ps1\n"
        "# Starts Atlas Trading Agent as a PowerShell background job.\n"
        "# Usage: .\\start_atlas.ps1\n"
        "\n"
        f"$projectRoot = \"{_PROJECT_ROOT}\"\n"
        f"$pythonExe = \"{_PYTHON_EXE}\"\n"
        f"$entryPoint = \"{_ENTRY_POINT}\"\n"
        "\n"
        "$job = Start-Job -Name 'AtlasTradingAgent' -ScriptBlock {\n"
        "    param($root, $python, $script)\n"
        "    Set-Location $root\n"
        "    & $python $script\n"
        "} -ArgumentList $projectRoot, $pythonExe, $entryPoint\n"
        "\n"
        "Write-Host \"Atlas started as background job (ID: $($job.Id))\"\n"
        "Write-Host \"To view output: Receive-Job -Name AtlasTradingAgent\"\n"
        "Write-Host \"To stop:        Stop-Job -Name AtlasTradingAgent\"\n"
        "Write-Host \"To check status: Get-Job -Name AtlasTradingAgent\"\n"
    )

    _PS1_FILE.write_text(ps1_content, encoding="utf-8")
    print(f"PowerShell script created: {_PS1_FILE}")
    print()
    print("To run:")
    print(f"  powershell -ExecutionPolicy Bypass -File \"{_PS1_FILE}\"")
    print()
    print("To check if Atlas is running:")
    print("  Get-Job -Name AtlasTradingAgent")
    print()
    print("To stop Atlas:")
    print("  Stop-Job -Name AtlasTradingAgent")
    print()
    print("Note: background jobs end when the PowerShell session closes.")
    print("For true persistence, use Option 1 (Task Scheduler) instead.")


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Atlas Trading Agent — Windows Service Installer         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Project root : {_PROJECT_ROOT}")
    print(f"Python       : {_PYTHON_EXE}")
    print(f"Entry point  : {_ENTRY_POINT}")
    print()

    if not _ENTRY_POINT.exists():
        print(f"ERROR: Entry point not found: {_ENTRY_POINT}")
        print("Run this script from the trading-agent project root.")
        sys.exit(1)

    print("Select an installation method:")
    print("  1 — Task Scheduler (recommended: runs on logon, persistent)")
    print("  2 — Startup Folder batch file (simplest, runs on logon)")
    print("  3 — PowerShell background job (manual start, no persistence)")
    print("  a — Install all three")
    print("  q — Quit")
    print()

    choice = input("Your choice: ").strip().lower()

    if choice == "1":
        install_task_scheduler()
    elif choice == "2":
        create_startup_bat()
    elif choice == "3":
        create_powershell_script()
    elif choice == "a":
        install_task_scheduler()
        create_startup_bat()
        create_powershell_script()
    elif choice == "q":
        print("Quit.")
        return
    else:
        print(f"Unknown choice: {choice}")
        sys.exit(1)

    print()
    print("Done. To start Atlas right now:")
    print(f"  python \"{_ENTRY_POINT}\"")


if __name__ == "__main__":
    main()
