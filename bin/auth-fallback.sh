#!/usr/bin/env bash
# Auth fallback: Chrome CDP primary, environment variables backup
# Tries Chrome connection first, then falls back to API key from env

# Primary: Try Chrome CDP connection
connect_chrome() {
    source bin/chrome-detect.sh 2>/dev/null
    
    if [[ "$connected" == "true" ]]; then
        echo "Using Chrome CDP authentication"
        return 0
    fi
    return 1
}

# Fallback: Use environment variable
connect_env() {
    if [[ -n "$ADSAGENT_API_KEY" ]]; then
        echo "Using ADSAGENT_API_KEY from environment"
        export AUTH_METHOD="env"
        return 0
    fi
    return 1
}

# Main: Try Chrome first, then fallback
authenticate() {
    if connect_chrome; then
        export AUTH_METHOD="chrome"
        export AUTH_CHROME_PORT="${CHROME_REMOTE_DEBUGGING_PORT:-9222}"
    elif connect_env; then
        # Already set AUTH_METHOD in connect_env
        :
    else
        echo "ERROR: No valid authentication method available"
        echo "- Chrome not running with remote debugging"
        echo "- ADSAGENT_API_KEY not set"
        return 1
    fi
    
    echo "Authenticated via: $AUTH_METHOD"
}

case "${1:-}" in
    authenticate) authenticate ;;
    connect_chrome) connect_chrome ;;
    connect_env) connect_env ;;
    *) echo "Usage: auth-fallback.sh {authenticate|connect_chrome|connect_env}" ;;
esac