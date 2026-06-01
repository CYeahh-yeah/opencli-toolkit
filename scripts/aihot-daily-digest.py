#!/usr/bin/env python3
"""
aihot-daily-digest.py
---------------------------------------------------------------
Fetch the AI-industry digest from aihot.virxact.com.

Why this exists
  The aihot public API returns 403 to most user-agents (it gates
  bots). This script ships a polite, browser-shaped User-Agent and
  handles the timezone normalization so you can pipe the output
  straight into `cron` -> Telegram/email/WeChat.

Usage
  python3 aihot-daily-digest.py                  # latest daily
  python3 aihot-daily-digest.py --since 24h      # last 24h
  python3 aihot-daily-digest.py --mode selected  # curated pool
  python3 aihot-daily-digest.py --date 2026-05-30
  python3 aihot-daily-digest.py --json           # raw JSON output
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_BASE = "https://aihot.virxact.com/api/public"
# This UA is required — bare Python/curl get 403.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36 aihot-skill/0.2.0")

# Beijing time — aihot timestamps are CST
CST = timezone(timedelta(hours=8))


def fetch(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"_error": "not_found", "_hint": "Daily not yet published (08:00 BJT)"}
        if e.code == 429:
            return {"_error": "rate_limited", "_hint": "600 req/min cap; back off"}
        return {"_error": f"http_{e.code}", "_hint": str(e)}


def parse_since(s: str) -> str:
    """Accept human-friendly ('24h', '6h', '30m', '7d') or pass through ISO timestamps."""
    import re
    m = re.fullmatch(r"(\d+)([smhd])", s.strip())
    if not m:
        return s  # assume already an ISO timestamp
    n, unit = int(m.group(1)), m.group(2)
    delta = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit] * n
    return (datetime.now(timezone.utc) - timedelta(seconds=delta)).isoformat(timespec="seconds")


def humanize_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(CST)
    except Exception:
        return iso
    delta = datetime.now(CST) - dt
    if delta.days >= 1:
        return f"{delta.days}d ago"
    h = delta.seconds // 3600
    if h >= 1:
        return f"{h}h ago"
    m = delta.seconds // 60
    return f"{m}m ago" if m > 0 else "just now"


def render_items(items: list[dict]) -> str:
    if not items:
        return "(no items)"
    lines = []
    for i, it in enumerate(items, 1):
        title = it.get("title") or it.get("name") or "(untitled)"
        url = it.get("url") or it.get("link") or ""
        ts = it.get("published_at") or it.get("created_at") or ""
        ago = humanize_time(ts) if ts else ""
        line = f"{i}. **{title}**"
        if ago:
            line += f"  _{ago}_"
        if url:
            line += f"\n   {url}"
        lines.append(line)
    return "\n\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="aihot daily/selected digest")
    p.add_argument("--mode", choices=["selected", "all"], help="items mode")
    # We use --since= instead of --since to avoid the leading-digit argparse quirk.
    p.add_argument("--since", help="e.g. 24h, 6h, 30m. USE --since=24h form (equals sign).")
    p.add_argument("--take", type=int, default=20, help="max items (default 20)")
    p.add_argument("--q", help="keyword filter")
    p.add_argument("--date", help="YYYY-MM-DD for /daily/{date}")
    p.add_argument("--json", action="store_true", help="emit raw JSON")
    args = p.parse_args()

    # Route: --date -> specific daily; else items
    if args.date:
        data = fetch(f"daily/{args.date}")
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        print(f"# AI Daily · {args.date}\n")
        items = data.get("items") or data.get("data") or []
        print(render_items(items))
        return 0

    params: dict = {"take": args.take}
    if args.mode:
        params["mode"] = args.mode
    if args.since:
        params["since"] = parse_since(args.since)
    if args.q:
        params["q"] = args.q

    data = fetch("items", params)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if data.get("_error"):
        print(f"[aihot] {data['_error']} — {data.get('_hint','')}", file=sys.stderr)
        return 1

    items = data.get("items") or data.get("data") or data.get("results") or []
    if not items and isinstance(data, list):
        items = data
    print(f"# aihot digest  · {len(items)} items\n")
    print(render_items(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
