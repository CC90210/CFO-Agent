r"""
validate_graph.py — Obsidian graph integrity checker for the CFO-Agent vault.

Scans every .md file in the vault (respecting .obsidian/app.json ignore filters),
parses wikilinks, reports:
  - Total wikilinks + file-level distribution
  - Broken targets (wikilink points to a file that doesn't exist in the vault)
  - Orphans (files in brain/, memory/, or skills/<X>/SKILL.md with zero incoming wikilinks)
  - Top connectors (files with most outgoing wikilinks)

Correctly handles:
  - Markdown-table pipe escapes: [[target\|alias]] treated as [[target|alias]]
  - Code-block exclusion: wikilinks inside fenced ``` blocks or `inline code` are ignored
  - Path-style and stem-style wikilinks: [[folder/sub/File]] and [[File]]
  - Multiple SKILL.md files with identical stems resolve correctly via path-first.

Usage:
    python scripts/validate_graph.py                  # summary report
    python scripts/validate_graph.py --broken-only    # only broken links
    python scripts/validate_graph.py --orphans-only   # only orphan nodes

Exits nonzero if broken links are found (useful for pre-commit integration).

Addresses CAPABILITY_GAPS.md Gap #4 (Obsidian graph orphan scanner).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

DEFAULT_IGNORE = {
    "node_modules", ".venv", ".claude", ".agents", ".cursor", ".git",
    ".rules", ".gemini", ".playwright-mcp", ".vscode", "tmp",
    "remotion-content", "archive",
}


def load_obsidian_ignores(vault: pathlib.Path) -> set[str]:
    app_json = vault / ".obsidian" / "app.json"
    ignores = set(DEFAULT_IGNORE)
    if app_json.exists():
        try:
            cfg = json.loads(app_json.read_text(encoding="utf-8"))
            for entry in cfg.get("userIgnoreFilters", []):
                ignores.add(entry.rstrip("/").rstrip("\\"))
        except json.JSONDecodeError:
            pass
    return ignores


def strip_code(content: str) -> str:
    """Remove fenced code blocks and inline code spans so we don't parse wikilinks inside them."""
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`\n]+`", "", content)
    return content


def normalize_table_escapes(content: str) -> str:
    r"""Replace markdown-table \| escape with plain |, so wikilink parser sees [[x|y]]."""
    return content.replace(r"\|", "|")


WIKILINK_RE = re.compile(r"\[\[(?P<target>[^\]|]+)(?:\|[^\]]+)?\]\]")


def collect_md(vault: pathlib.Path, ignores: set[str]) -> list[pathlib.Path]:
    files = []
    for p in vault.rglob("*.md"):
        if set(p.parts) & ignores:
            continue
        files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vault", default=".", help="Vault root (default: cwd)")
    ap.add_argument("--broken-only", action="store_true")
    ap.add_argument("--orphans-only", action="store_true")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).resolve()
    ignores = load_obsidian_ignores(vault)
    md_files = collect_md(vault, ignores)

    by_stem: dict[str, list[pathlib.Path]] = {}
    for p in md_files:
        by_stem.setdefault(p.stem, []).append(p)

    broken: list[tuple[pathlib.Path, str]] = []
    outgoing: dict[pathlib.Path, int] = {}
    incoming: dict[pathlib.Path, int] = {p: 0 for p in md_files}
    total = 0

    for p in md_files:
        try:
            raw = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        clean = normalize_table_escapes(strip_code(raw))
        links = WIKILINK_RE.findall(clean)
        total += len(links)
        if links:
            outgoing[p] = len(links)
        for target in links:
            t = target.strip().replace("\\", "/")
            base = t.split("/")[-1]
            resolved: pathlib.Path | None = None
            # 1) Path-first from vault root (absolute vault path)
            cand_with = vault / (t + ".md")
            cand_bare = vault / t
            if cand_with.exists():
                resolved = cand_with
            elif cand_bare.exists() and cand_bare.suffix == ".md":
                resolved = cand_bare
            # 2) Obsidian-style fuzzy: find any vault file whose relative path ends with target.md
            if resolved is None:
                target_suffix = t + ".md"
                for q in md_files:
                    rel = str(q.relative_to(vault)).replace("\\", "/")
                    if rel.endswith(target_suffix) and (
                        rel == target_suffix
                        or rel.endswith("/" + target_suffix)
                    ):
                        resolved = q
                        break
            # 3) Stem fallback (only if no slash in target)
            if resolved is None and "/" not in t and base in by_stem:
                resolved = by_stem[base][0]
            if resolved is None:
                broken.append((p, target))
            else:
                incoming[resolved] = incoming.get(resolved, 0) + 1

    def is_key(p: pathlib.Path) -> bool:
        parts = p.parts
        return (
            "brain" in parts
            or "memory" in parts
            or ("skills" in parts and p.name == "SKILL.md")
        )

    orphans = sorted(
        [p for p, n in incoming.items() if n == 0 and is_key(p)],
        key=str,
    )

    if args.broken_only:
        for p, t in broken:
            print(f"BROKEN: {p} -> [[{t}]]")
        return 1 if broken else 0

    if args.orphans_only:
        for p in orphans:
            print(f"ORPHAN: {p}")
        return 1 if orphans else 0

    # Summary
    print(f"Files scanned: {len(md_files)}")
    print(f"Total wikilinks: {total}")
    print(f"Files with wikilinks: {len(outgoing)}")
    print(f"Broken wikilinks: {len(broken)}")
    for p, t in broken:
        print(f"  BROKEN: {p} -> [[{t}]]")

    print(f"\nOrphans (brain/memory/skills): {len(orphans)}")
    for p in orphans[:30]:
        print(f"  ORPHAN: {p}")

    print("\nTop 15 connectors:")
    top = sorted(outgoing.items(), key=lambda kv: -kv[1])[:15]
    for p, n in top:
        print(f"  {n:3d}  {p}")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
