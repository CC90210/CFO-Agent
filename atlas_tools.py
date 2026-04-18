"""
atlas_tools.py
--------------
Tool-use layer for Atlas-on-Telegram. Gives the Claude chat fallback the same
read/grep/run powers Atlas has from the Claude Code terminal, so CC can hold a
natural conversation on his phone and have Atlas actually DO things (read
brain/USER.md, grep the tax docs, run the networth snapshot, fetch live news)
instead of only talking about them.

Design
------
- Every tool is idempotent and read-only by default. No arbitrary bash, no file
  writes from Telegram — those remain IDE-only for safety.
- Every tool logs its invocation so CC can audit what Atlas did on his phone.
- Path arguments are sandboxed to the project root — no ../../.ssh/id_rsa.
- Tools wrap the existing `_run_*` dispatchers in telegram_bridge.py, so no
  duplicated logic.

Tool roster
-----------
  read_file(path)           Read any project file by relative path
  grep(pattern, path?)      Search the codebase (ripgrep-style)
  list_files(pattern)       Glob the project (e.g. "brain/*.md")
  run_cfo(command, args?)   Invoke a CFO command: runway/networth/status/
                            taxes/receipts/picks/deepdive/news/macro/brain
  read_pick(filename)       Read a saved stock pick from data/picks/
  read_memory(filename)     Read a file from the auto-memory folder
  web_search(query)         Native Anthropic web search

Anthropic tool-use loop
-----------------------
Call `run_with_tools(client, system, messages)` — it handles the full
tool_use → tool_result loop internally and returns the final assistant text.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("atlas.tools")

_ROOT = Path(__file__).resolve().parent
_MEMORY_ROOT = Path(
    r"C:\Users\User\.claude\projects\c--Users-User-APPS-CFO-Agent\memory"
)
_MAX_READ_CHARS = 20_000  # clip big files — Telegram + token budget


# ─────────────────────────────────────────────────────────────────────────────
#  Path sandbox — prevents reading outside project root or memory folder
# ─────────────────────────────────────────────────────────────────────────────


def _safe_resolve(rel_path: str, root: Path) -> Path:
    """Resolve a relative path inside a root. Raise if it escapes."""
    target = (root / rel_path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise PermissionError(
            f"Path {rel_path!r} escapes sandbox {root}"
        ) from exc
    return target


# ─────────────────────────────────────────────────────────────────────────────
#  Individual tool handlers — each returns a string suitable for Claude
# ─────────────────────────────────────────────────────────────────────────────


def _tool_read_file(path: str) -> str:
    target = _safe_resolve(path, _ROOT)
    if not target.exists():
        return f"File not found: {path}"
    if not target.is_file():
        return f"Not a file: {path}"
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return f"Read error: {exc}"
    if len(text) > _MAX_READ_CHARS:
        text = (
            text[:_MAX_READ_CHARS]
            + f"\n\n[...clipped {len(text) - _MAX_READ_CHARS} chars; use grep for specifics]"
        )
    logger.info("tool:read_file %s (%d chars)", path, len(text))
    return text


def _tool_grep(pattern: str, path: str = ".") -> str:
    import re

    target = _safe_resolve(path, _ROOT)
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        return f"Bad regex: {exc}"

    matches: list[str] = []
    files = [target] if target.is_file() else target.rglob("*")
    for f in files:
        if not f.is_file():
            continue
        # Skip obvious binaries and junk
        if f.suffix in {".pyc", ".jpg", ".png", ".db", ".sqlite", ".zip"}:
            continue
        if any(p in f.parts for p in {"__pycache__", ".git", "node_modules", "archive"}):
            continue
        try:
            for i, line in enumerate(
                f.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if regex.search(line):
                    rel = f.relative_to(_ROOT)
                    matches.append(f"{rel}:{i}: {line.strip()[:200]}")
                    if len(matches) >= 80:
                        matches.append("[...truncated at 80 matches]")
                        logger.info("tool:grep %r -> 80+ matches", pattern)
                        return "\n".join(matches)
        except Exception:  # noqa: BLE001
            continue
    logger.info("tool:grep %r -> %d matches", pattern, len(matches))
    return "\n".join(matches) if matches else f"No matches for {pattern!r}"


def _tool_list_files(pattern: str) -> str:
    if pattern.startswith("/") or ".." in pattern:
        return "Pattern must be a relative glob within the project root."
    results = sorted(str(p.relative_to(_ROOT)) for p in _ROOT.glob(pattern))
    logger.info("tool:list_files %s -> %d", pattern, len(results))
    return "\n".join(results[:200]) if results else f"No files match {pattern!r}"


def _tool_run_cfo(command: str, args: dict | None = None) -> str:
    """
    Invoke one of the existing Atlas CFO dispatchers. Imported lazily to avoid
    circular imports with telegram_bridge.
    """
    from telegram_bridge import (
        _run_runway,
        _run_networth,
        _run_status,
        _run_taxes,
        _run_receipts,
        _run_picks,
        _run_deepdive,
        _run_news,
        _run_macro,
        _run_brain,
    )

    args = args or {}
    logger.info("tool:run_cfo %s %s", command, args)

    try:
        if command == "runway":
            return _run_runway()
        if command == "networth":
            return _run_networth()
        if command == "status":
            return _run_status()
        if command == "taxes":
            return _run_taxes()
        if command == "receipts":
            since_raw = args.get("since")
            since = date.fromisoformat(since_raw) if since_raw else None
            return _run_receipts(since)
        if command == "picks":
            query = args.get("query", "best opportunities right now")
            n = int(args.get("n", 3))
            return _run_picks(query, n)
        if command == "deepdive":
            ticker = args.get("ticker", "")
            if not ticker:
                return "deepdive needs a ticker (e.g. NVDA)"
            return _run_deepdive(ticker)
        if command == "news":
            return _run_news(args.get("query", "financial markets"))
        if command == "macro":
            return _run_macro()
        if command == "brain":
            filename = args.get("filename", "")
            if not filename:
                return "brain needs a filename (e.g. USER.md)"
            return _run_brain(filename)
        return f"Unknown CFO command: {command}"
    except Exception as exc:  # noqa: BLE001
        logger.exception("tool:run_cfo failed for %s", command)
        return f"CFO command {command!r} error: {exc}"


def _tool_read_pick(filename: str) -> str:
    picks_dir = _ROOT / "data" / "picks"
    target = _safe_resolve(filename, picks_dir)
    if not target.exists():
        available = sorted(p.name for p in picks_dir.glob("*.md"))
        return f"Pick not found: {filename}\n\nAvailable:\n" + "\n".join(available[-15:])
    return target.read_text(encoding="utf-8", errors="replace")[:_MAX_READ_CHARS]


def _tool_read_agent_pulse(agent: str) -> str:
    """Read another agent's latest pulse (read-only). For cross-agent awareness."""
    import json as _json

    paths = {
        "bravo": [Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json")],
        "ceo": [Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json")],
        "maven": [
            Path(r"C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json"),
            Path(r"C:\Users\User\Marketing-Agent\data\pulse\cmo_pulse.json"),
            Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\cmo_pulse.json"),
        ],
        "cmo": [
            Path(r"C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json"),
            Path(r"C:\Users\User\Marketing-Agent\data\pulse\cmo_pulse.json"),
            Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\cmo_pulse.json"),
        ],
        "cfo": [_ROOT / "data" / "pulse" / "cfo_pulse.json"],
        "atlas": [_ROOT / "data" / "pulse" / "cfo_pulse.json"],
    }
    targets = paths.get(agent.lower())
    if not targets:
        return f"Unknown agent {agent!r}. Use: atlas|bravo|maven (or cfo|ceo|cmo)."
    for path in targets:
        if path.exists():
            try:
                data = _json.loads(path.read_text(encoding="utf-8"))
                return f"Source: {path}\n\n" + _json.dumps(data, indent=2, default=str)
            except Exception as exc:  # noqa: BLE001
                return f"Read error on {path}: {exc}"
    return f"{agent} has not published a pulse yet at any of: " + ", ".join(str(p) for p in targets)


def _tool_read_memory(filename: str) -> str:
    if not _MEMORY_ROOT.exists():
        return f"Memory folder not found: {_MEMORY_ROOT}"
    target = _safe_resolve(filename, _MEMORY_ROOT)
    if not target.exists():
        available = sorted(p.name for p in _MEMORY_ROOT.glob("*.md"))
        return f"Memory not found: {filename}\n\nAvailable:\n" + "\n".join(available)
    return target.read_text(encoding="utf-8", errors="replace")[:_MAX_READ_CHARS]


# ─────────────────────────────────────────────────────────────────────────────
#  Tool registry + Anthropic JSON schemas
# ─────────────────────────────────────────────────────────────────────────────

_HANDLERS: dict[str, Callable[..., str]] = {
    "read_file": lambda **kw: _tool_read_file(kw["path"]),
    "grep": lambda **kw: _tool_grep(kw["pattern"], kw.get("path", ".")),
    "list_files": lambda **kw: _tool_list_files(kw["pattern"]),
    "run_cfo": lambda **kw: _tool_run_cfo(kw["command"], kw.get("args")),
    "read_pick": lambda **kw: _tool_read_pick(kw["filename"]),
    "read_memory": lambda **kw: _tool_read_memory(kw["filename"]),
    "read_agent_pulse": lambda **kw: _tool_read_agent_pulse(kw["agent"]),
}


def tool_schemas() -> list[dict]:
    """Claude tool_use schemas. Keep descriptions concise — Claude reads them."""
    return [
        {
            "name": "read_file",
            "description": (
                "Read any file inside the CFO-Agent project by relative path. "
                "Use for brain/USER.md, docs/*.md, code files, data/*.json. "
                "Files >20K chars are clipped — use grep for huge files."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root, e.g. 'brain/USER.md'",
                    }
                },
                "required": ["path"],
            },
        },
        {
            "name": "grep",
            "description": (
                "Search the codebase for a regex pattern. Returns matching lines "
                "with file:line:content. Case-insensitive. Max 80 matches."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex (Python re syntax)"},
                    "path": {
                        "type": "string",
                        "description": "Optional relative path; defaults to whole project",
                    },
                },
                "required": ["pattern"],
            },
        },
        {
            "name": "list_files",
            "description": "Glob project files, e.g. 'brain/*.md' or 'data/picks/*.md'.",
            "input_schema": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        },
        {
            "name": "run_cfo",
            "description": (
                "Invoke a CFO command. Returns the same output CC would see "
                "from `python main.py <command>`."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": [
                            "runway", "networth", "status", "taxes", "receipts",
                            "picks", "deepdive", "news", "macro", "brain",
                        ],
                    },
                    "args": {
                        "type": "object",
                        "description": (
                            "Command-specific args: picks needs {query, n}, "
                            "deepdive needs {ticker}, news needs {query}, "
                            "receipts optional {since: 'YYYY-MM-DD'}, brain {filename}."
                        ),
                    },
                },
                "required": ["command"],
            },
        },
        {
            "name": "read_pick",
            "description": "Read a saved stock pick from data/picks/, e.g. '2026-04-16_ENB_enbridge.md'.",
            "input_schema": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
        {
            "name": "read_memory",
            "description": (
                "Read a file from Atlas's auto-memory folder, e.g. 'user_financial_profile.md'. "
                "Use this to ground answers in CC's documented state."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
        {
            "name": "read_agent_pulse",
            "description": (
                "Read another agent's latest pulse file (read-only). "
                "Use for cross-agent awareness: check Bravo's client state, "
                "Maven's ad-spend request, or Atlas's own published state. "
                "Agent argument: 'atlas' | 'bravo' | 'maven' (or cfo/ceo/cmo aliases)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["atlas", "bravo", "maven", "cfo", "ceo", "cmo"],
                    }
                },
                "required": ["agent"],
            },
        },
        # Native Anthropic web search — same tool the IDE uses.
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 6},
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  Tool-use conversation loop
# ─────────────────────────────────────────────────────────────────────────────


def run_with_tools(
    client: Any,
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int = 2048,
    max_iterations: int = 6,
) -> str:
    """
    Run a Claude conversation with tool use enabled. Loops until Claude's
    response has no more tool_use blocks, then returns the final text.

    Parameters
    ----------
    client      Anthropic client instance
    model       Model ID (e.g. 'claude-opus-4-7')
    system      System prompt (Atlas CFO identity + USER.md excerpt)
    messages    Conversation so far [{role, content}, ...]
    max_tokens  Per-response cap
    max_iterations  Safety cap on tool-use loops
    """
    # Make a working copy — we mutate as Claude + tools go back and forth
    convo = list(messages)
    tools = tool_schemas()

    for iteration in range(max_iterations):
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=convo,
        )

        # If Claude is done, extract final text and return
        if resp.stop_reason != "tool_use":
            for block in reversed(resp.content):
                if getattr(block, "type", None) == "text":
                    return block.text
            return "(Atlas produced no text output)"

        # Claude wants to call tools — append assistant turn, run each tool,
        # then append a user turn with the tool_result blocks
        convo.append({"role": "assistant", "content": resp.content})

        tool_results: list[dict] = []
        for block in resp.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            name = block.name
            tool_input = block.input or {}
            # web_search is handled by Anthropic server-side — no local handler
            if name == "web_search":
                continue
            handler = _HANDLERS.get(name)
            if handler is None:
                output = f"Unknown tool: {name}"
            else:
                try:
                    output = handler(**tool_input)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("tool %s failed", name)
                    output = f"Tool error: {exc}"
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output[:12_000],  # clip very long returns
                }
            )

        if not tool_results:
            # No local tool results (e.g. only web_search fired) — let Claude continue
            convo.append({"role": "user", "content": "Continue."})
        else:
            convo.append({"role": "user", "content": tool_results})

    return "(Atlas hit tool-iteration cap without finalizing — try again)"
