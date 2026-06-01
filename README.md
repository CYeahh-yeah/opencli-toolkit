# opencli-toolkit

> A curated, battle-tested toolkit of AI-agent & automation scripts.
> Every script here has been used in production to ship real things — not toy demos.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Bash 5+](https://img.shields.io/badge/bash-5+-green.svg)](https://www.gnu.org/software/bash/)
[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/CYeahh-yeah/opencli-toolkit/commits/main)

---

## Why this repo exists

Most "AI agent toolkits" on GitHub are either abandoned wrappers around a single API,
or academic projects that never ran in anger. **opencli-toolkit is the opposite** —
it's a thin, copy-pasteable layer over the *exact* scripts we use daily to:

- Publish static sites to a public URL in **15 seconds** (no signup, no deploy keys)
- Pull a daily AI-industry digest from `aihot.virxact.com` for cron
- Repair broken `[[wikilink]]` references in Obsidian vaults
- Wrap any long-running process with a single CLI command

Each tool is **self-contained, dependency-light, and well-commented**.
If a script doesn't survive a fresh clone + 30-second README read, it doesn't ship.

---

## Quick start

```bash
git clone https://github.com/CYeahh-yeah/opencli-toolkit.git
cd opencli-toolkit

# Option A: run scripts directly
./scripts/cloudflared-quick-tunnel.sh ./public 8080
python3 scripts/aihot-daily-digest.py
python3 scripts/obsidian-wikilink-repair.py /path/to/vault

# Option B: install as a CLI
pip install -e .
otk tunnel ./public 8080
otk aihot --since 24h
otk wikilink /path/to/vault
```

> All scripts work on macOS, Linux, and WSL2. Cloudflared binary is auto-downloaded
> to `~/.local/bin/` on first run.

---

## The toolkit

| Script | What it does | Lines |
|---|---|---|
| [`cloudflared-quick-tunnel.sh`](./scripts/cloudflared-quick-tunnel.sh) | Serve any local directory on a public `*.trycloudflare.com` URL — zero signup, zero config | ~80 |
| [`aihot-daily-digest.py`](./scripts/aihot-daily-digest.py) | Fetch the daily AI-news digest from aihot.virxact.com with a polite User-Agent | ~120 |
| [`obsidian-wikilink-repair.py`](./scripts/obsidian-wikilink-repair.py) | Heuristically repair orphan `[[wikilink]]` references in an Obsidian vault | ~180 |
| `otk/__main__.py` | Unified CLI entrypoint — `otk tunnel | aihot | wikilink` | ~60 |

### Why these four?

| Problem | Script | Why it's not just "another wrapper" |
|---|---|---|
| I want to show someone a local HTML page | `cloudflared-quick-tunnel.sh` | Other tools (ngrok, localtunnel) require accounts; `cloudflared` doesn't, and we auto-fetch the binary |
| I want a 9:30am AI-news push every day | `aihot-daily-digest.py` | We handle the 403-prone User-Agent requirement + timezone normalization for you |
| My Obsidian vault has 1000+ broken `[[links]]` | `obsidian-wikilink-repair.py` | Idempotent, dry-run by default, never deletes user content |
| I want one command instead of three | `otk` | Thin wrapper that exposes the most-used flags as subcommands |

---

## The OpenAI Codex for OSS context

This repo was bootstrapped on **2026-05-31** to support an application to
[OpenAI's Codex for Open Source](https://openai.com/form/codex-for-oss/) program,
which grants maintainers of public OSS projects 6 months of ChatGPT Pro
($1,200 value) in exchange for ongoing maintenance.

We commit to:
- ✅ Public, MIT-licensed code (this repo)
- ✅ Honest versioning & changelog ([CHANGELOG.md](./CHANGELOG.md))
- ✅ Responsive issue triage (best-effort, 7-day window)
- ✅ Continued development as long as the toolkit is useful

If you find a bug or want a feature, **open an issue**. We read every one.

---

## Project structure

```
opencli-toolkit/
├── README.md                  ← you are here
├── LICENSE                    ← MIT
├── CHANGELOG.md               ← version history
├── pyproject.toml             ← makes `pip install -e .` work
├── otk/
│   ├── __init__.py
│   └── __main__.py            ← `python -m otk` or `otk` entrypoint
├── scripts/
│   ├── cloudflared-quick-tunnel.sh
│   ├── aihot-daily-digest.py
│   └── obsidian-wikilink-repair.py
├── docs/
│   ├── DESIGN.md              ← design rationale (why these tools, not others)
│   └── CONTRIBUTING.md        ← how to add a new tool to the kit
└── .github/
    └── ISSUE_TEMPLATE.md
```

---

## License

MIT — see [LICENSE](./LICENSE). Do whatever you want; attribution appreciated.

---

## Maintainer

**C C** ([@CYeahh-yeah](https://github.com/CYeahh-yeah))
Built while shipping AI agent workflows and a UBC forestry degree at the same time.
