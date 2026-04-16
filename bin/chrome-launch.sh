#!/usr/bin/env bash
# Launch Chrome with remote debugging for Chrome 136+
# Chrome 136+ requires explicit --user-data-dir

PORT="${CHROME_REMOTE_DEBUGGING_PORT:-9222}"
CHROME_PATH="${CHROME_PATH:-google-chrome}"
PROFILE_DIR="${CHROME_PROFILE_DIR:-$HOME/.config/google-chrome/remote-debug}"

# Create profile directory if it doesn't exist
mkdir -p "$PROFILE_DIR"

# Launch Chrome with remote debugging
exec "$CHROME_PATH" \
    --remote-debugging-port="$PORT" \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    "$@"