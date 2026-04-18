"""
scripts/build_capabilities.py
-----------------------------
Atlas capability registry generator.

Scans the codebase and builds a SINGLE source of truth for "what Atlas can
do" at `brain/CAPABILITIES.md`. Runs every session so the registry never
drifts from the actual code.

Sources scanned:
  1. skills/<name>/SKILL.md         → frontmatter (name, description, triggers, tier)
  2. telegram_bridge.py             → CommandHandler registrations + docstrings
  3. atlas_tools.py                 → tool_schemas() for Claude tool-use surface
  4. cfo/*.py, research/*.py        → module __doc__ for domain modules
  5. main.py                        → argparse subcommands

Output: brain/CAPABILITIES.md — grouped by layer (user-facing, internal),
with routing hints so Atlas knows when to invoke each capability.

Usage:
  python scripts/build_capabilities.py              # write brain/CAPABILITIES.md
  python scripts/build_capabilities.py --check      # non-zero exit if stale
  python scripts/build_capabilities.py --print      # stdout only, don't write
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_CAPABILITIES_PATH = _ROOT / "brain" / "CAPABILITIES.md"


# ─────────────────────────────────────────────────────────────────────────────
#  Parsing helpers
# ─────────────────────────────────────────────────────────────────────────────


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML-style frontmatter bounded by --- lines. Returns {} if absent."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_block = parts[1].strip()
    result: dict[str, Any] = {}
    current_key: str | None = None
    for line in fm_block.splitlines():
        if not line.strip():
            continue
        if line.startswith(" ") and current_key:
            # Continuation of previous value
            result[current_key] = str(result[current_key]) + " " + line.strip()
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                # Inline list: [a, b, c]
                items = [x.strip() for x in val[1:-1].split(",") if x.strip()]
                result[key] = items
            elif val == ">":
                result[key] = ""
                current_key = key
            else:
                result[key] = val
                current_key = key
    return result


def _module_docstring(py_path: Path) -> str:
    """Return the module-level docstring, or empty string if none."""
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree) or ""
        return doc.strip()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
#  Source scanners
# ─────────────────────────────────────────────────────────────────────────────


def scan_skills() -> list[dict]:
    skills_dir = _ROOT / "skills"
    out: list[dict] = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if not fm.get("name"):
            continue
        out.append({
            "name": fm.get("name", skill_dir.name),
            "description": fm.get("description", "").strip(),
            "triggers": fm.get("triggers", []),
            "tier": fm.get("tier", "unspecified"),
            "path": f"skills/{skill_dir.name}/SKILL.md",
        })
    return out


def scan_telegram_commands() -> list[dict]:
    """Extract slash commands registered in telegram_bridge.py.

    Command descriptions come from the `_HELP_TEXT` constant (which is what
    CC actually sees when he types /help) rather than method docstrings,
    since the handlers don't have docstrings.
    """
    bridge = (_ROOT / "telegram_bridge.py").read_text(encoding="utf-8")

    # Build description lookup from _HELP_TEXT — lines like "/runway   description"
    help_descs: dict[str, str] = {}
    help_match = re.search(r'_HELP_TEXT\s*=\s*"""(.+?)"""', bridge, re.DOTALL)
    if help_match:
        for line in help_match.group(1).splitlines():
            # Matches: "/cmd   description" or "/cmd <arg> description" or "/cmd TICK description"
            m = re.match(r"\s*/(\w+)(?:\s+<[^>]+>|\s+[A-Z]{2,})?\s+(.+)$", line)
            if m:
                help_descs[m.group(1)] = m.group(2).strip()

    out: list[dict] = []
    # Match: app.add_handler(CommandHandler("name", self.cmd_name))
    for m in re.finditer(
        r'CommandHandler\(\s*"(\w+)",\s*self\.cmd_(\w+)\s*\)', bridge
    ):
        cmd, handler = m.group(1), m.group(2)
        out.append({
            "command": f"/{cmd}",
            "handler": f"cmd_{handler}",
            "description": help_descs.get(cmd, ""),
        })
    return out


def scan_atlas_tools() -> list[dict]:
    """Read atlas_tools.py tool_schemas() to list the Claude tool-use surface."""
    try:
        sys.path.insert(0, str(_ROOT))
        from atlas_tools import tool_schemas  # type: ignore
    except Exception as exc:
        return [{"name": "ERROR", "description": f"Could not import atlas_tools: {exc}"}]

    out: list[dict] = []
    for s in tool_schemas():
        name = s.get("name", "?")
        if s.get("type") == "web_search_20250305":
            out.append({"name": name, "description": "Native Anthropic web search", "kind": "anthropic"})
            continue
        out.append({
            "name": name,
            "description": s.get("description", "").strip().split("\n")[0],
            "kind": "local",
        })
    return out


def scan_modules(subdir: str) -> list[dict]:
    """Return {name, docstring, path} for every non-__init__ .py under subdir."""
    base = _ROOT / subdir
    out: list[dict] = []
    for py in sorted(base.glob("*.py")):
        if py.name == "__init__.py":
            continue
        doc = _module_docstring(py)
        # Collapse docstring to first non-empty paragraph
        summary = ""
        for line in doc.splitlines():
            line = line.strip()
            if line and not line.startswith("---") and not line.startswith("===") and line not in {subdir + "/" + py.name, f"{subdir}/{py.name}"}:
                summary = line
                break
        out.append({
            "name": py.stem,
            "summary": summary[:140],
            "path": f"{subdir}/{py.name}",
        })
    return out


def scan_main_commands() -> list[dict]:
    """Extract argparse subcommand names from main.py."""
    text = (_ROOT / "main.py").read_text(encoding="utf-8")
    out: list[dict] = []
    # Match: sub.add_parser("name", help="...")
    for m in re.finditer(r'add_parser\(\s*"(\w[\w-]*)"\s*(?:,\s*help\s*=\s*["\'](.+?)["\'])?', text):
        out.append({"command": f"python main.py {m.group(1)}", "description": (m.group(2) or "").strip()})
    return out


# ─────────────────────────────────────────────────────────────────────────────
#  Output builder
# ─────────────────────────────────────────────────────────────────────────────


_PREAMBLE = """# ATLAS CAPABILITIES — auto-generated registry

> **Do not edit by hand.** Regenerated by `scripts/build_capabilities.py` on every session start. Edits survive only until the next build.
> When adding a new skill / tool / command, add it to the source (skills/, atlas_tools.py, telegram_bridge.py, or main.py) — this file updates automatically.

This is Atlas's single source of truth for *what it can do*. Atlas reads this at session start to ground intent routing: given a user question, which capability handles it?

"""


def build_registry(
    skills: list[dict],
    telegram_cmds: list[dict],
    tools: list[dict],
    cfo_modules: list[dict],
    research_modules: list[dict],
    main_cmds: list[dict],
) -> str:
    out = [_PREAMBLE]
    out.append(f"**Built:** {date.today().isoformat()}  |  Source files: {len(skills)} skills, "
               f"{len(telegram_cmds)} Telegram commands, {len(tools)} Claude tools, "
               f"{len(cfo_modules)} CFO modules, {len(research_modules)} research modules.\n")

    # ── USER-FACING LAYER ────────────────────────────────────────────────────
    out.append("## Layer 1 — User-facing surfaces (how CC talks to Atlas)\n")

    out.append("### Telegram slash commands\n")
    out.append("Direct function dispatch — no Claude classifier, no tokens burned.\n")
    out.append("| Command | Does | Python handler |")
    out.append("|---|---|---|")
    for c in sorted(telegram_cmds, key=lambda x: x["command"]):
        out.append(f"| `{c['command']}` | {c['description'] or '(no description)'} | `{c['handler']}` |")
    out.append("")

    out.append("### CLI commands (terminal)\n")
    out.append("| Command | Does |")
    out.append("|---|---|")
    for c in sorted(main_cmds, key=lambda x: x["command"]):
        out.append(f"| `{c['command']}` | {c['description'] or '(see main.py)'} |")
    out.append("")

    # ── INTERNAL LAYER: CLAUDE TOOLS ─────────────────────────────────────────
    out.append("## Layer 2 — Claude tool-use surface (IDE-parity on Telegram)\n")
    out.append("These are the tools Atlas calls mid-conversation when a user asks something that needs a file read, grep, CFO command, saved pick, memory lookup, or web search.\n")
    out.append("| Tool | Kind | Purpose |")
    out.append("|---|---|---|")
    for t in sorted(tools, key=lambda x: x["name"]):
        out.append(f"| `{t['name']}` | {t.get('kind', '?')} | {t['description'] or '(no description)'} |")
    out.append("")

    # ── INTERNAL LAYER: SKILLS ───────────────────────────────────────────────
    out.append("## Layer 3 — Skill library (domain expertise)\n")
    out.append("Each skill is a focused playbook. When CC's question matches a skill's `triggers`, Atlas loads that skill's knowledge to ground its answer.\n")
    out.append("| Skill | Tier | Triggers | Description |")
    out.append("|---|---|---|---|")
    for s in sorted(skills, key=lambda x: x["name"]):
        triggers = ", ".join(s["triggers"][:6]) + ("…" if len(s["triggers"]) > 6 else "")
        desc = re.sub(r"\s+", " ", s["description"])[:120]
        out.append(f"| `{s['name']}` | {s['tier']} | {triggers or '—'} | {desc} |")
    out.append("")

    # ── INTERNAL LAYER: MODULES ──────────────────────────────────────────────
    out.append("## Layer 4 — Python modules (engines under the hood)\n")

    out.append("### CFO modules (`cfo/`)\n")
    out.append("| Module | Purpose |")
    out.append("|---|---|")
    for m in cfo_modules:
        out.append(f"| `{m['path']}` | {m['summary'] or '(see docstring)'} |")
    out.append("")

    out.append("### Research modules (`research/`)\n")
    out.append("| Module | Purpose |")
    out.append("|---|---|")
    for m in research_modules:
        out.append(f"| `{m['path']}` | {m['summary'] or '(see docstring)'} |")
    out.append("")

    # ── ROUTING DECISION MATRIX ──────────────────────────────────────────────
    out.append("## Layer 5 — Routing decision matrix\n")
    out.append("When a user message arrives, Atlas routes it by:\n")
    out.append("1. **Slash command?** → Direct Python dispatch (Layer 1 Telegram table). Zero Claude tokens.")
    out.append("2. **Natural language?** → Intent classifier picks `runway|networth|picks|deepdive|receipts|taxes|news|macro|status|chat`.")
    out.append("3. **Chat intent?** → Chat fallback with Layer 2 tool-use. Atlas may call `read_file`, `grep`, `list_files`, `run_cfo`, `read_pick`, `read_memory`, or `web_search` silently before answering.")
    out.append("4. **Needs domain depth?** → Relevant skill(s) from Layer 3 ground the answer.")
    out.append("5. **Needs backend work (Python impl, deep debugging, pre-ship review)?** → Delegate to Codex via `/codex:*` plugin (see `CLAUDE.md` Codex Dual-AI section).")
    out.append("6. **About clients / content / outreach / revenue ops?** → NOT Atlas's lane. Point CC to Bravo.")
    out.append("")

    out.append("## Layer 6 — Cross-agent handoffs\n")
    out.append("- **Atlas → Bravo:** read-only. Atlas reads `ceo_pulse.json` for MRR, clients, pipeline, spend commitments.")
    out.append("- **Atlas → Codex:** delegate via `scripts/codex-companion.mjs` for backend implementation, deep debugging, adversarial code review.")
    out.append("- **Atlas ↔ CC:** the ONLY agent that writes decisions. Both Atlas and Bravo only advise; CC clicks buttons.")
    out.append("")
    out.append("See `brain/AGENT_ORCHESTRATION.md` for the full contract.\n")

    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
#  Runner
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit 1 if output differs from file")
    parser.add_argument("--print", action="store_true", help="Print to stdout instead of writing")
    args = parser.parse_args()

    skills = scan_skills()
    tg_cmds = scan_telegram_commands()
    tools = scan_atlas_tools()
    cfo_mods = scan_modules("cfo")
    research_mods = scan_modules("research")
    main_cmds = scan_main_commands()

    text = build_registry(skills, tg_cmds, tools, cfo_mods, research_mods, main_cmds)

    if args.print:
        print(text)
        return 0

    if args.check:
        existing = _CAPABILITIES_PATH.read_text(encoding="utf-8") if _CAPABILITIES_PATH.exists() else ""
        if existing.strip() == text.strip():
            print(f"[capabilities] up-to-date ({_CAPABILITIES_PATH})")
            return 0
        print(f"[capabilities] STALE — regenerate with: python scripts/build_capabilities.py")
        return 1

    _CAPABILITIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CAPABILITIES_PATH.write_text(text, encoding="utf-8")
    print(
        f"[capabilities] wrote {_CAPABILITIES_PATH}\n"
        f"  {len(skills)} skills, {len(tg_cmds)} Telegram commands, "
        f"{len(tools)} Claude tools, {len(cfo_mods)} CFO modules, "
        f"{len(research_mods)} research modules, {len(main_cmds)} CLI commands"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
