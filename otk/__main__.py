"""
otk — unified CLI entrypoint.

Examples
  otk tunnel ./public 8080
  otk aihot --since 24h
  otk wikilink ~/my-vault --apply
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def cmd_tunnel(args: argparse.Namespace) -> int:
    script = SCRIPTS / "cloudflared-quick-tunnel.sh"
    cmd = ["bash", str(script), args.directory, str(args.port)]
    return subprocess.call(cmd)


def cmd_aihot(args: argparse.Namespace) -> int:
    script = SCRIPTS / "aihot-daily-digest.py"
    cmd = [sys.executable, str(script)]
    if args.mode:
        cmd += ["--mode", args.mode]
    if args.since:
        cmd += ["--since", args.since]
    if args.take:
        cmd += ["--take", str(args.take)]
    if args.q:
        cmd += ["--q", args.q]
    if args.date:
        cmd += ["--date", args.date]
    if args.json:
        cmd += ["--json"]
    return subprocess.call(cmd)


def cmd_wikilink(args: argparse.Namespace) -> int:
    script = SCRIPTS / "obsidian-wikilink-repair.py"
    cmd = [sys.executable, str(script), args.vault]
    if args.apply:
        cmd += ["--apply"]
    if args.report:
        cmd += ["--report", args.report]
    return subprocess.call(cmd)


def main() -> int:
    p = argparse.ArgumentParser(prog="otk", description="opencli-toolkit CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_t = sub.add_parser("tunnel", help="serve a local dir on a public URL")
    p_t.add_argument("directory", nargs="?", default=os.getcwd())
    p_t.add_argument("port", nargs="?", type=int, default=8080)
    p_t.set_defaults(func=cmd_tunnel)

    p_a = sub.add_parser("aihot", help="fetch the daily AI-news digest")
    p_a.add_argument("--mode", choices=["selected", "all"])
    p_a.add_argument("--since", help="e.g. 24h, 6h")
    p_a.add_argument("--take", type=int, default=20)
    p_a.add_argument("--q", help="keyword filter")
    p_a.add_argument("--date", help="YYYY-MM-DD")
    p_a.add_argument("--json", action="store_true")
    p_a.set_defaults(func=cmd_aihot)

    p_w = sub.add_parser("wikilink", help="repair Obsidian [[wikilinks]]")
    p_w.add_argument("vault", help="path to vault root")
    p_w.add_argument("--apply", action="store_true")
    p_w.add_argument("--report", help="write report to this path")
    p_w.set_defaults(func=cmd_wikilink)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
