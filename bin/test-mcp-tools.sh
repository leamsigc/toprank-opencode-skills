#!/bin/bash
# Test MCP tool availability

echo "=== MCP Configuration Test ==="
echo ""
echo "Checking .mcp.json..."
if [ -f ".mcp.json" ]; then
    echo "✓ .mcp.json exists"
    echo ""
    echo "Contents:"
    cat .mcp.json
    echo ""
else
    echo "✗ .mcp.json not found"
    exit 1
fi

echo ""
echo "=== Tool Detection ==="
echo "MCP tool naming pattern expected: mcp__adsagent__*"
echo ""
echo "Note: adsagent MCP server requires ADSAGENT_API_KEY environment variable."
echo "To test MCP tools, set ADSAGENT_API_KEY and restart opencode.ai"