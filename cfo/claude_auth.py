"""Claude Code CLI auth-priority helpers (Python).

Python mirror of Bravo's scripts/c_suite_context.js auth helpers.
Atlas's Telegram bridge spawns the `claude` CLI as a subprocess
(rather than calling the Anthropic SDK directly) so it can use CC's
Claude Code subscription OAuth token instead of paid API billing.

Auth priority:
  1. Claude Code subscription OAuth (free under CC's plan, registered
     by `claude setup-token`, stored at ~/.claude/.credentials.json)
  2. ANTHROPIC_API_KEY (paid metered, fallback only)

CROSS-LANGUAGE SYNC (CRITICAL):
This file MUST stay behaviorally identical to:
  Business-Empire-Agent/scripts/c_suite_context.js
    (Node module — used by Bravo's bridge + future Bravo CLI tools)

If Anthropic changes the auth-failure or quota-error patterns, the
regex below MUST be updated in lockstep with that file's
_AUTH_FAIL_PATTERN. Same applies to the OAuth file path detection.
The two implementations diverge only in language idiom — Python
vs Node — never in behavior.

Public API:
    build_claude_spawn_env(force_api_key=False, base=None, extras=None)
        Returns a dict suitable for subprocess.run/Popen env=. Default
        strips ANTHROPIC_API_KEY so claude CLI uses OAuth. Pass
        force_api_key=True on the retry path to enable paid fallback.

    is_claude_auth_or_quota_failure(raw_output, exit_code) -> bool
        Returns True when stderr/stdout looks like an auth error or
        quota/rate-limit. Caller should retry with force_api_key=True.

    check_claude_auth_paths(home=None, env=None) -> dict
        Returns {hasOAuth, oauthPath, hasApiKey, claudeDir}. Used at
        boot to verify both auth paths are usable before any user
        query lands.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Mapping, Optional


# Pattern matches BOTH auth errors and quota/rate-limit errors. Same
# regex as scripts/c_suite_context.js — kept in sync deliberately. If
# this ever drifts, the bridges will retry inconsistently.
_AUTH_FAIL_PATTERN = re.compile(
    r"authentication_error|"
    r"OAuth token has expired|"
    r"401|"
    r"Invalid API key|"
    r"Please obtain a new token|"
    r"usage limit|"
    r"rate limit|"
    r"quota exceeded|"
    r"reached your.*limit|"
    r"429",
    re.IGNORECASE,
)


def build_claude_spawn_env(
    force_api_key: bool = False,
    base: Optional[Mapping[str, str]] = None,
    extras: Optional[Mapping[str, str]] = None,
) -> dict[str, str]:
    """Return a child-process env that respects subscription-first auth.

    Default behavior (force_api_key=False): strips ANTHROPIC_API_KEY so
    the claude CLI falls through to the OAuth token. Pass force_api_key
    =True on the retry path to enable the paid fallback.
    """
    if base is None:
        base = os.environ
    env: dict[str, str] = dict(base)
    if extras:
        env.update(extras)
    if not force_api_key:
        # Strip the key so claude CLI uses the OAuth subscription token.
        env.pop("ANTHROPIC_API_KEY", None)
    return env


def is_claude_auth_or_quota_failure(raw_output: str, exit_code: int) -> bool:
    """True when the CLI failed in a way the caller should retry on the
    API-key fallback path.
    """
    if exit_code == 0:
        return False
    if not raw_output:
        return False
    return bool(_AUTH_FAIL_PATTERN.search(raw_output))


def check_claude_auth_paths(
    home: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """Detect which auth paths are usable on this machine.

    Returns:
        {
          "hasOAuth":   bool,           # subscription OAuth file present + non-empty
          "oauthPath":  str | None,     # full path to the file (or None)
          "hasApiKey":  bool,           # ANTHROPIC_API_KEY in env, non-empty
          "claudeDir":  str,            # ~/.claude path (for log messages)
        }
    """
    if env is None:
        env = os.environ
    if home is None:
        home = os.environ.get("HOME") or os.environ.get("USERPROFILE") or ""

    claude_dir = Path(home) / ".claude"
    # Real path is .credentials.json (leading dot — verified 2026-04-27).
    # Legacy candidate kept for defense-in-depth in case the storage
    # layout changes in a future Claude Code release.
    candidates = [
        claude_dir / ".credentials.json",
        claude_dir / "credentials.json",
    ]

    oauth_path: Optional[str] = None
    for candidate in candidates:
        try:
            if candidate.stat().st_size > 0:
                oauth_path = str(candidate)
                break
        except (FileNotFoundError, OSError):
            continue

    api_key = env.get("ANTHROPIC_API_KEY") or ""

    return {
        "hasOAuth": oauth_path is not None,
        "oauthPath": oauth_path,
        "hasApiKey": bool(api_key),
        "claudeDir": str(claude_dir),
    }
