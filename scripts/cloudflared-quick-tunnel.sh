#!/usr/bin/env bash
# cloudflared-quick-tunnel.sh
# ---------------------------------------------------------------
# Serve any local directory on a public *.trycloudflare.com URL
# in 15 seconds. No signup, no auth token, no deploy keys.
#
# Usage:
#   ./cloudflared-quick-tunnel.sh [LOCAL_DIR] [PORT]
#   ./cloudflared-quick-tunnel.sh              # serve CWD on 8080
#   ./cloudflared-quick-tunnel.sh ./public 9000
#
# First run will auto-download cloudflared to ~/.local/bin/
# ---------------------------------------------------------------
set -euo pipefail

LOCAL_DIR="${1:-$(pwd)}"
PORT="${2:-8080}"
CLOUDFLARED="${HOME}/.local/bin/cloudflared"
GITHUB_RELEASE="https://github.com/cloudflare/cloudflared/releases/latest/download"

log()  { printf "\033[1;36m[otk]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[otk]\033[0m %s\n" "$*" >&2; }
fail() { printf "\033[1;31m[otk]\033[0m %s\n" "$*" >&2; exit 1; }

# 1. Validate inputs
[ -d "$LOCAL_DIR" ] || fail "Local directory not found: $LOCAL_DIR"
command -v python3 >/dev/null || fail "python3 is required"

# 2. Install cloudflared on first run
if ! command -v cloudflared >/dev/null && [ ! -x "$CLOUDFLARED" ]; then
  log "First run — downloading cloudflared to $CLOUDFLARED ..."
  mkdir -p "$(dirname "$CLOUDFLARED")"
  curl -fsSL -o "$CLOUDFLARED" \
    "${GITHUB_RELEASE}/cloudflared-linux-amd64"
  chmod +x "$CLOUDFLARED"
  log "Downloaded: $("$CLOUDFLARED" --version 2>&1 | head -1)"
fi

CLOUDFLARED_BIN="${CLOUDFLARED}"
[ -x "$CLOUDFLARED_BIN" ] || CLOUDFLARED_BIN="$(command -v cloudflared)"

# 3. Start a local HTTP server in the background
log "Starting local HTTP server: $LOCAL_DIR on port $PORT"
( cd "$LOCAL_DIR" && python3 -m http.server "$PORT" ) >/tmp/otk-http.log 2>&1 &
HTTP_PID=$!
trap 'kill $HTTP_PID 2>/dev/null || true' EXIT

# Give the server a moment to bind
sleep 1

# 4. Launch the cloudflare quick-tunnel
log "Launching cloudflared quick tunnel (Ctrl-C to stop) ..."
exec "$CLOUDFLARED_BIN" tunnel --no-autoupdate --url "http://localhost:${PORT}"
