"""Tests for cfo/claude_auth.py.

Run: python -m unittest tests.test_claude_auth -v

Mirrors the test coverage of Bravo's scripts/test_c_suite_context.js
auth section. If this drifts from Bravo's behavior, the two bridges
will retry inconsistently on auth/quota errors.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from cfo.claude_auth import (  # noqa: E402
    build_claude_spawn_env,
    is_claude_auth_or_quota_failure,
    check_claude_auth_paths,
)


class TestBuildClaudeSpawnEnv(unittest.TestCase):
    """Subscription-first auth: API key stripped by default, kept on retry."""

    def test_default_strips_api_key(self):
        env = build_claude_spawn_env(
            base={"ANTHROPIC_API_KEY": "sk-ant-fake", "PATH": "/usr/bin", "FOO": "bar"},
        )
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertEqual(env["FOO"], "bar")

    def test_force_api_key_preserves_key(self):
        env = build_claude_spawn_env(
            force_api_key=True,
            base={"ANTHROPIC_API_KEY": "sk-ant-fake", "PATH": "/usr/bin"},
        )
        self.assertEqual(env["ANTHROPIC_API_KEY"], "sk-ant-fake")

    def test_extras_override_base(self):
        env = build_claude_spawn_env(
            base={"CI": "false", "PATH": "/usr/bin"},
            extras={"CI": "true", "NONINTERACTIVE": "true"},
        )
        self.assertEqual(env["CI"], "true")
        self.assertEqual(env["NONINTERACTIVE"], "true")
        self.assertEqual(env["PATH"], "/usr/bin")

    def test_extras_does_not_re_add_api_key(self):
        # Even if extras tries to re-add ANTHROPIC_API_KEY, default
        # behavior should still strip it. This protects against a
        # caller mistakenly passing it through extras.
        env = build_claude_spawn_env(
            base={"PATH": "/usr/bin"},
            extras={"ANTHROPIC_API_KEY": "sk-leak"},
        )
        self.assertNotIn("ANTHROPIC_API_KEY", env)

    def test_no_args_returns_dict(self):
        # Should not crash; uses os.environ as base
        env = build_claude_spawn_env()
        self.assertIsInstance(env, dict)


class TestIsClaudeAuthOrQuotaFailure(unittest.TestCase):
    """Pattern matching for retry decision."""

    def test_exit_zero_never_failure(self):
        self.assertFalse(is_claude_auth_or_quota_failure("any output", 0))
        self.assertFalse(is_claude_auth_or_quota_failure("OAuth token has expired", 0))

    def test_auth_patterns_match(self):
        self.assertTrue(is_claude_auth_or_quota_failure("authentication_error: bad token", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("OAuth token has expired", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("HTTP 401 Unauthorized", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("Invalid API key provided", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("Please obtain a new token", 1))

    def test_quota_patterns_match(self):
        self.assertTrue(is_claude_auth_or_quota_failure("You have hit usage limit for today", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("rate limit exceeded", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("quota exceeded for this account", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("429 too many requests", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("reached your weekly limit", 1))

    def test_unrelated_errors_dont_match(self):
        self.assertFalse(is_claude_auth_or_quota_failure("TypeError: foo is undefined", 1))
        self.assertFalse(is_claude_auth_or_quota_failure("Network unreachable", 1))
        self.assertFalse(is_claude_auth_or_quota_failure("FileNotFoundError", 1))

    def test_empty_or_none_output(self):
        self.assertFalse(is_claude_auth_or_quota_failure("", 1))
        self.assertFalse(is_claude_auth_or_quota_failure(None, 1))  # type: ignore[arg-type]

    def test_case_insensitive(self):
        self.assertTrue(is_claude_auth_or_quota_failure("OAUTH TOKEN HAS EXPIRED", 1))
        self.assertTrue(is_claude_auth_or_quota_failure("Quota Exceeded", 1))


class TestCheckClaudeAuthPaths(unittest.TestCase):
    """Detect subscription OAuth + API key on a fake home dir."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="atlas-auth-test-")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_claude_dir_no_oauth(self):
        result = check_claude_auth_paths(home=self.tmp, env={})
        self.assertFalse(result["hasOAuth"])
        self.assertIsNone(result["oauthPath"])
        self.assertFalse(result["hasApiKey"])
        self.assertTrue(result["claudeDir"].endswith(".claude"))

    def test_real_path_credentials_json_with_dot(self):
        """Real Claude Code OAuth file is .credentials.json (leading dot)."""
        claude_dir = Path(self.tmp) / ".claude"
        claude_dir.mkdir()
        cred_file = claude_dir / ".credentials.json"
        cred_file.write_text('{"token":"xyz"}', encoding="utf-8")

        result = check_claude_auth_paths(home=self.tmp, env={})
        self.assertTrue(result["hasOAuth"])
        self.assertTrue(result["oauthPath"].endswith(".credentials.json"))

    def test_empty_credentials_file_rejected(self):
        """Empty file is not counted — OAuth must be present AND non-empty."""
        claude_dir = Path(self.tmp) / ".claude"
        claude_dir.mkdir()
        (claude_dir / ".credentials.json").write_text("", encoding="utf-8")

        result = check_claude_auth_paths(home=self.tmp, env={})
        self.assertFalse(result["hasOAuth"])

    def test_legacy_credentials_json_fallback(self):
        """If only the no-dot variant exists, still detect it (defense-in-depth)."""
        claude_dir = Path(self.tmp) / ".claude"
        claude_dir.mkdir()
        legacy = claude_dir / "credentials.json"
        legacy.write_text('{"token":"old"}', encoding="utf-8")

        result = check_claude_auth_paths(home=self.tmp, env={})
        self.assertTrue(result["hasOAuth"])
        self.assertTrue(result["oauthPath"].endswith("credentials.json"))

    def test_api_key_in_env(self):
        result = check_claude_auth_paths(
            home=self.tmp,
            env={"ANTHROPIC_API_KEY": "sk-ant-test"},
        )
        self.assertTrue(result["hasApiKey"])

    def test_blank_api_key_rejected(self):
        result = check_claude_auth_paths(
            home=self.tmp,
            env={"ANTHROPIC_API_KEY": ""},
        )
        self.assertFalse(result["hasApiKey"])

    def test_uses_os_environ_when_env_omitted(self):
        # Smoke test — should not crash. Real-world ANTHROPIC_API_KEY
        # may or may not be set; result should still be a valid dict.
        result = check_claude_auth_paths(home=self.tmp)
        self.assertIn("hasOAuth", result)
        self.assertIn("hasApiKey", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
