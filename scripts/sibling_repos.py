"""Shared sibling-agent repo path resolver.

Bravo, Maven (CMO-Agent), Atlas (CFO-Agent), and Aura each live in
their own repo. Cross-agent operations — agent_inbox cross-repo posting,
ceo_dashboard subprocessing to Maven's late_tool, future Atlas runway
queries — all need to know where each sibling lives on disk.

Single source of truth so the same paths/env-overrides aren't duplicated
across multiple scripts. Override per machine via env vars in
.env.agents (or process env): BRAVO_REPO, MAVEN_REPO, ATLAS_REPO, AURA_REPO.

Public API:
    SIBLING_CANDIDATES -- dict[str, list[Path]] of all known-good locations
                          per agent on the current platform (first hit wins).
                          Mirrors Bravo bridge V15.7's loadLocalSiblingPaths().
    SIBLING_REPOS      -- dict[str, Path] keyed by lowercased agent name —
                          resolves to env-var override (if set) or to the
                          first existing candidate (or first candidate as
                          a non-existent default).
    repo_for(name) -> Path | None
    script_in(agent, *parts) -> Path | None
        Returns Path to a script in a sibling repo, or None if the repo
        isn't installed on this machine (caller should fall back gracefully).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _platform_candidates() -> dict[str, list[str]]:
    """Per-machine sibling repo CANDIDATES. First-existing wins.

    Mac branch tracks Bravo's V15.7 loadLocalSiblingPaths() so the
    cross-agent contract stays in lockstep. Windows branch keeps the
    canonical paths CC has hardcoded across his agent fleet.
    """
    if sys.platform == "darwin":
        home = str(Path.home())
        return {
            "bravo": [
                f"{home}/Downloads/business-empire-agent",  # Bravo V15.7 reference
                f"{home}/CEO-Agent",
                f"{home}/Business-Empire-Agent",
            ],
            "maven": [
                f"{home}/CMO-Agent",
                f"{home}/APPS/CMO-Agent",
            ],
            "atlas": [
                f"{home}/Desktop/CFO-Agent",
                f"{home}/APPS/CFO-Agent",
                f"{home}/CFO-Agent",
            ],
            "aura": [
                f"{home}/AURA",
                f"{home}/Aura",
            ],
        }
    # Windows defaults — canonical layout, do NOT change without coordinating
    # with Bravo + Maven bridges.
    return {
        "bravo": [r"C:\Users\User\Business-Empire-Agent"],
        "maven": [r"C:\Users\User\CMO-Agent"],
        "atlas": [r"C:\Users\User\APPS\CFO-Agent"],
        "aura":  [r"C:\Users\User\AURA"],
    }


SIBLING_CANDIDATES: dict[str, list[Path]] = {
    name: [Path(p) for p in paths] for name, paths in _platform_candidates().items()
}


def _resolve_repo(agent: str, env_var: str) -> Path:
    """Pick the canonical repo path for an agent.

    Order: env var override > first existing candidate > first candidate
    as fallback (so Path is never None at module level).
    """
    override = os.environ.get(env_var, "").strip()
    if override:
        return Path(override)
    for cand in SIBLING_CANDIDATES.get(agent, []):
        if cand.exists():
            return cand
    candidates = SIBLING_CANDIDATES.get(agent, [])
    return candidates[0] if candidates else Path()


SIBLING_REPOS: dict[str, Path] = {
    "bravo": _resolve_repo("bravo", "BRAVO_REPO"),
    "maven": _resolve_repo("maven", "MAVEN_REPO"),
    "atlas": _resolve_repo("atlas", "ATLAS_REPO"),
    "aura":  _resolve_repo("aura",  "AURA_REPO"),
}


def repo_for(name: str) -> Path | None:
    """Return the repo path for a sibling agent if it exists on disk.

    Returns None for unknown names or for repos not present on this
    machine — callers MUST handle the None case (graceful degradation).
    """
    repo = SIBLING_REPOS.get(name.lower())
    if repo and repo.exists():
        return repo
    return None


def script_in(agent: str, *parts: str) -> Path | None:
    """Resolve a path inside a sibling agent's repo.

    Example:
        script_in("maven", "scripts", "late_tool.py")
        # -> Path("C:/Users/User/CMO-Agent/scripts/late_tool.py")

    Returns None if the agent's repo isn't installed.
    """
    repo = repo_for(agent)
    if repo is None:
        return None
    return repo.joinpath(*parts)