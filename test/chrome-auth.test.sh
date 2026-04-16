#!/bin/bash
# Chrome Remote Debug Auto-Connect Test

TEST_DIR="$(mktemp -d)"
trap "rm -rf $TEST_DIR" EXIT

echo "=== Chrome Remote Debug Auto-Connect Tests ==="
echo ""

PASS=0
FAIL=0

# Test 1: Detection script exists
echo -n "Test 1: chrome-detect.sh exists... "
if [ -f "bin/chrome-detect.sh" ]; then
    echo "PASS"
    ((PASS++))
else
    echo "FAIL"
    ((FAIL++))
fi

# Test 2: Session script exists
echo -n "Test 2: chrome-session.sh exists... "
if [ -f "bin/chrome-session.sh" ]; then
    echo "PASS"
    ((PASS++))
else
    echo "FAIL"
    ((FAIL++))
fi

# Test 3: Fallback script exists
echo -n "Test 3: auth-fallback.sh exists... "
if [ -f "bin/auth-fallback.sh" ]; then
    echo "PASS"
    ((PASS++))
else
    echo "FAIL"
    ((FAIL++))
fi

# Test 4: Launch script has --user-data-dir
echo -n "Test 4: chrome-launch.sh has --user-data-dir... "
if grep -q "\-\-user-data-dir" bin/chrome-launch.sh 2>/dev/null; then
    echo "PASS"
    ((PASS++))
else
    echo "FAIL"
    ((FAIL++))
fi

# Test 5: MCP config has chrome-devtools
echo -n "Test 5: .mcp.json has chrome-devtools... "
if grep -q "chrome-devtools" .mcp.json 2>/dev/null; then
    echo "PASS"
    ((PASS++))
else
    echo "FAIL"
    ((FAIL++))
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
    exit 0
else
    exit 1
fi