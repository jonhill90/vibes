#!/bin/bash
# End-to-end test for Task 2: Source Creation Validation Fix

echo "=========================================="
echo "Task 2: Source Creation Validation Test"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8003"

echo "Test 1: Create source with title (upload type)"
echo "----------------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/sources" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "upload", "title": "E2E Test Upload Source"}')
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [ "$HTTP_CODE" = "201" ]; then
    echo "✅ PASS: HTTP 201 Created"
    SOURCE_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    echo "Created source ID: $SOURCE_ID"
else
    echo "❌ FAIL: Expected HTTP 201, got $HTTP_CODE"
    echo "$BODY"
    exit 1
fi
echo ""

echo "Test 2: Verify title is returned in response"
echo "----------------------------------------------"
TITLE=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('title', 'MISSING'))" 2>/dev/null)
if [ "$TITLE" = "E2E Test Upload Source" ]; then
    echo "✅ PASS: Title correctly returned: $TITLE"
else
    echo "❌ FAIL: Title mismatch. Expected 'E2E Test Upload Source', got '$TITLE'"
    exit 1
fi
echo ""

echo "Test 3: Reject invalid source_type enum"
echo "----------------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/sources" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "document", "title": "Should Fail"}')
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$HTTP_CODE" = "422" ]; then
    echo "✅ PASS: HTTP 422 Unprocessable Entity (correctly rejected invalid enum)"
else
    echo "❌ FAIL: Expected HTTP 422, got $HTTP_CODE"
    exit 1
fi
echo ""

echo "Test 4: Create source without title (backwards compatible)"
echo "----------------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/sources" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "upload"}')
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [ "$HTTP_CODE" = "201" ]; then
    echo "✅ PASS: HTTP 201 Created (title optional)"
    TITLE=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('title'))" 2>/dev/null)
    if [ "$TITLE" = "None" ]; then
        echo "✅ PASS: Title is null (as expected)"
    else
        echo "⚠️  WARNING: Title is not null: $TITLE"
    fi
else
    echo "❌ FAIL: Expected HTTP 201, got $HTTP_CODE"
    exit 1
fi
echo ""

echo "Test 5: List sources and verify title extraction"
echo "----------------------------------------------"
RESPONSE=$(curl -s "$BASE_URL/api/sources")
COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['sources']))" 2>/dev/null)
if [ "$COUNT" -gt "0" ]; then
    echo "✅ PASS: Retrieved $COUNT sources"
    echo "Sample source with title:"
    echo "$RESPONSE" | python3 -c "import sys, json; sources = json.load(sys.stdin)['sources']; print(json.dumps([s for s in sources if s.get('title')][:1], indent=2))" 2>/dev/null
else
    echo "❌ FAIL: No sources returned"
    exit 1
fi
echo ""

echo "=========================================="
echo "All tests passed! ✅"
echo "Task 2: Source Creation Validation FIXED"
echo "=========================================="
