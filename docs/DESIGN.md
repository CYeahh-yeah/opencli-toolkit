# Design rationale

> Why these tools, and not other ones.

This document is the engineering companion to the README. It exists
so future contributors (and future me) understand the **decisions
behind the code**, not just the code itself.

---

## The 80/20 of an agent toolkit

A typical "AI agent toolkit" on GitHub contains 200 scripts, of which
3 are useful. We do the opposite: ship **3-5 well-tested tools** that
each cover a real recurring need. Every script in this repo answers
yes to **all** of:

1. **Used in production at least once** by a maintainer
2. **Self-contained** — no hidden config files, no env-var acrobatics
3. **Idempotent or safe-by-default** (dry-run, no destructive ops)
4. **Under 200 lines** (forces us to think about what to cut)

If a tool fails any of these, it doesn't ship.

---

## Tool-by-tool rationale

### 1. `cloudflared-quick-tunnel.sh`

**Problem.** I want to show a static HTML report to a friend / boss /
client, *right now*, without ngrok auth, without surge.sh tokens,
without signing up for Vercel.

**Why cloudflared quick tunnels.** `cloudflared tunnel --url` gives
you a public `*.trycloudflare.com` URL for any local port, with
**no signup and no auth token**. The catch is that the binary
isn't on most systems, so we auto-download to `~/.local/bin/`.

**What we explicitly don't do.**
- Don't pin a cloudflared version (they auto-update; we follow)
- Don't run a daemon (this is a one-shot tool)
- Don't accept a custom domain (use `cloudflared tunnel login` for that)

### 2. `aihot-daily-digest.py`

**Problem.** `https://aihot.virxact.com` is the best Chinese-language
AI news digest on the web, but the API gates non-browser User-Agents
with a 403.

**Why a wrapper.** A 3-line script would work, but the *real* value
is in the edge-case handling: timezone normalization (BJT), relative
time rendering ("3h ago"), graceful 404 ("daily not yet published"),
and a 429 backoff hint.

**What we explicitly don't do.**
- Don't scrape the HTML (they have a public API; respect it)
- Don't cache (the user controls their own cron cache)
- Don't render to a specific messenger format (just print markdown)

### 3. `obsidian-wikilink-repair.py`

**Problem.** Bulk-importing notes from another system (Notion,
Bear, Roam) often strips the leading `[[` of a wiki link, leaving
stray `]]` markers. Manual fixing of 100+ notes is soul-crushing.

**Why a script.** A regex-based repair is 80% correct, and the
remaining 20% needs human review anyway. So we ship a **dry-run
by default** tool that shows diffs, and only writes on `--apply`.

**Safety guarantees.**
- Never deletes files
- Never modifies a file that doesn't match the heuristic
- Emits a report you can grep / git-diff

### 4. `otk` CLI entrypoint

**Why bother with a CLI** when the scripts are runnable directly?
Two reasons: (a) discoverability — `otk --help` lists what's
available; (b) one consistent way to pass flags across the kit,
instead of remembering per-script argument names.

---

## What we won't add (and why)

| Rejected idea | Why |
|---|---|
| A LLM-call helper script | That's a library, not a script. Use LiteLLM, LangChain, etc. |
| A Telegram/Discord/WeChat pusher | 3 messengers × 3 auth flows = 9 implementations. Out of scope. |
| A docker-compose stack | We optimize for "clone + run on a laptop" |
| A web UI | The scripts are 30 seconds each. A web UI is 30 hours. |
| Auto-update to the latest version | ratchet = better. Pin in `pyproject.toml`. |

---

## Versioning policy

- **0.x** — API may change. Use `>=0.1,<0.2` if you depend on it.
- **1.0** — when (a) all 4 core scripts are stable for 6+ months
  and (b) we have at least 3 external contributors.

---

## License

MIT. Do whatever you want; attribution appreciated.
