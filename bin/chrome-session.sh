#!/usr/bin/env bash
# CDP Session management - reuses existing Chrome connection
# Supports session persistence across multiple invocations

SESSION_DIR="${CDP_SESSION_DIR:-$HOME/.toprank/cdp-sessions}"
mkdir -p "$SESSION_DIR"

# Session file stores connection info
SESSION_FILE="$SESSION_DIR/current.json"

get_session() {
    # Return existing session if still valid
    if [[ -f "$SESSION_FILE" ]]; then
        cat "$SESSION_FILE"
    else
        echo '{"valid": false}'
    fi
}

connect() {
    # Establish new CDP connection
    source bin/chrome-detect.sh 2>/dev/null
    
    if [[ "$connected" == "true" ]]; then
        # Save session for reuse
        cat > "$SESSION_FILE" <<EOF
{
  "valid": true,
  "port": ${PORT},
  "ws_url": "${ws_url}",
  "connected_at": "$(date -Iseconds)"
}
EOF
        echo "Session established"
    else
        echo "Failed to connect to Chrome"
        return 1
    fi
}

disconnect() {
    # Clear session
    rm -f "$SESSION_FILE"
}

case "${1:-}" in
    get_session) get_session ;;
    connect) connect ;;
    disconnect) disconnect ;;
    *) echo "Usage: chrome-session.sh {get_session|connect|disconnect}" ;;
esac