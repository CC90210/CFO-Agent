"""Invoke self-test in-process and write the report to data/selftest.log."""
from __future__ import annotations
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

out_path = _ROOT / "data" / "selftest_run.log"
out_path.parent.mkdir(parents=True, exist_ok=True)

# Write a "started" marker first so we can tell whether the subprocess died.
out_path.write_text("[selftest:started]\n", encoding="utf-8")

try:
    from scripts.self_test import main as st_main
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        rc = st_main([])
    body = buf.getvalue()
    body += f"\n[selftest:exit={rc}]\n"
    out_path.write_text(body, encoding="utf-8")
    sys.exit(rc)
except SystemExit:
    raise
except Exception:  # noqa: BLE001
    out_path.write_text("[selftest:crashed]\n" + traceback.format_exc(), encoding="utf-8")
    sys.exit(2)
