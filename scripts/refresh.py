"""
scripts/refresh.py
------------------
One-command refresh for Atlas's self-awareness layer. Runs at session start
(or any time CC wants to re-ground Atlas) to rebuild:

  1. brain/CAPABILITIES.md    — what Atlas can do (skills, tools, commands, modules)
  2. memory/MEMORY.md         — auto-regenerated index with frontmatter validation
  3. data/pulse/cfo_pulse.json — current liquid cash, tax reserve, spend gate

Any failure is reported but doesn't halt the others — partial refresh is
better than no refresh when one data source is offline.

Usage:
  python scripts/refresh.py              # full refresh
  python scripts/refresh.py --check      # CI mode: exit 1 on any drift/error
  python scripts/refresh.py --capabilities-only
  python scripts/refresh.py --memory-only
  python scripts/refresh.py --pulse-only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> int:
    """Run a subcommand, stream output. Return exit code."""
    print(f"\n>>> {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if anything is stale or invalid (no writes)")
    parser.add_argument("--capabilities-only", action="store_true")
    parser.add_argument("--memory-only", action="store_true")
    parser.add_argument("--pulse-only", action="store_true")
    args = parser.parse_args()

    do_all = not (args.capabilities_only or args.memory_only or args.pulse_only)
    errors = 0

    if do_all or args.capabilities_only:
        cmd = [sys.executable, "scripts/build_capabilities.py"]
        if args.check:
            cmd.append("--check")
        if _run(cmd) != 0:
            errors += 1

    if do_all or args.memory_only:
        cmd = [sys.executable, "scripts/validate_memory.py"]
        if args.check:
            cmd.append("--check")
        cmd.append("--quiet" if do_all else "--quiet" if False else "")
        cmd = [c for c in cmd if c]  # drop empties
        if _run(cmd) != 0:
            errors += 1

    if do_all or args.pulse_only:
        # Pulse is always rebuilt from live data; --check is not meaningful here
        if not args.check:
            if _run([sys.executable, "-m", "cfo.pulse"]) != 0:
                errors += 1

    print()
    if errors:
        print(f"[refresh] {errors} step(s) failed.")
        return 1
    print("[refresh] all systems re-grounded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
