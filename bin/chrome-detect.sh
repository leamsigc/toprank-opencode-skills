#!/usr/bin/env bash
# Detect Chrome remote debugging connection
# Returns: JSON with {connected: bool, port: int, ws_url: string}
# Usage: source bin/chrome-detect.sh && check_chrome

PORT="${CHROME_REMOTE_DEBUGGING_PORT:-9222}"
HOST="${CHROME_REMOTE_DEBUGGING_HOST:-localhost}"

check_chrome() {
    response=$(curl -s -w "%{http_code}" "http://${HOST}:${PORT}/json" 2>/dev/null || echo "000")

    if [[ "$response" == "200" ]]; then
        ws_url=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0].get('webSocketDebuggerUrl',''))" 2>/dev/null || echo "")
        connected="true"
    else
        connected="false"
    fi
}

is_connected() {
    check_chrome
    [[ "$connected" == "true" ]]
}