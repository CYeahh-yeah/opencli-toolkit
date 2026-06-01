#!/usr/bin/env python3
"""
obsidian-wikilink-repair.py
---------------------------------------------------------------
Heuristically repair orphan [[wikilink]] references inside an
Obsidian vault. Designed to be safe, idempotent, and dry-run by
default — never deletes user content.

Use cases
  - Notes exported from a different system with broken wiki links
  - Vaults that lost the leading `[[` on a batch import
  - Mass-rename of a tag that left dangling references

Usage
  python3 obsidian-wikilink-repair.py /path/to/vault
  python3 obsidian-wikilink-repair.py /path/to/vault --apply
  python3 obsidian-wikilink-repair.py /path/to/vault --report out.txt
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path

# A stray `]]\n` at the very start of a note usually means the
# leading `[[Term]]` and its title line were dropped during import.
STRAY_CLOSE = re.compile(r"^]]\s*\n", re.MULTILINE)
WIKILINK = re.compile(r"\[\[([^\]\n]+?)\]\]")


def scan_file(path: Path) -> dict:
    """Return repair actions for a single file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {"_skip": True, "reason": "unreadable"}

    actions: list[str] = []
    new_text = text

    # 1. Stray `]]\n` at the start — re-attach a leading `[[Concept]]` line
    m = STRAY_CLOSE.match(text)
    if m:
        # Heuristic: title = the first [[Concept]] we find after the stray
        first_link = WIKILINK.search(text, pos=m.end())
        concept = first_link.group(1).strip() if first_link else path.stem
        new_text = f"[[{concept}]]\n# {concept}\n\n" + text[m.end():]
        actions.append(f"re-attach leading [[{concept}]] + H1 title")

    if not actions:
        return {"_skip": True, "reason": "no-repair-needed"}

    return {
        "_skip": False,
        "actions": actions,
        "old_size": len(text),
        "new_size": len(new_text),
        "new_text": new_text,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Repair orphan Obsidian [[wikilinks]]")
    p.add_argument("vault", help="path to Obsidian vault root")
    p.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    p.add_argument("--report", help="write a diff report to this path")
    p.add_argument("--ext", default=".md", help="file extension to scan (default .md)")
    args = p.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        print(f"error: not a directory: {vault}", file=sys.stderr)
        return 2

    fixed = skipped = errors = 0
    report_lines: list[str] = []

    for root, _dirs, files in os.walk(vault):
        # Skip Obsidian system dirs
        root_p = Path(root)
        if any(part.startswith(".") for part in root_p.parts[len(vault.parts):]):
            continue
        for name in files:
            if not name.endswith(args.ext):
                continue
            path = root_p / name
            result = scan_file(path)
            if result.get("_skip"):
                skipped += 1
                continue
            if result.get("_error"):
                errors += 1
                report_lines.append(f"ERROR  {path}: {result['_error']}")
                continue

            actions = ", ".join(result["actions"])
            report_lines.append(f"FIX    {path}\n        {actions}")
            fixed += 1

            if args.apply:
                path.write_text(result["new_text"], encoding="utf-8")

    summary = (
        f"\n{'APPLIED' if args.apply else 'DRY-RUN'}  fixed={fixed}  "
        f"skipped={skipped}  errors={errors}\n"
        f"  (re-run with --apply to write changes)\n"
    )
    print(summary)

    if args.report:
        Path(args.report).write_text(
            "\n".join(report_lines) + "\n" + summary, encoding="utf-8"
        )
        print(f"report written: {args.report}")
    elif report_lines:
        # Print first 20 lines as preview
        for line in report_lines[:20]:
            print(line)
        if len(report_lines) > 20:
            print(f"... ({len(report_lines) - 20} more)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
