#!/bin/bash

# AirLLMHost API Test Script

BASE_URL="http://localhost:1410"

echo "======================================"
echo "AirLLMHost API Test Script"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if echo "$response" | grep -q "error"; then
        echo -e "${RED}FAILED${NC}"
        echo "Response: $response"
    else
        echo -e "${GREEN}OK${NC}"
        echo "Response: $response"
    fi
    echo ""
}

# Check if server is running
echo "Checking server connection..."
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}ERROR: Cannot connect to server at $BASE_URL${NC}"
    echo "Make sure api_server.py is running:"
    echo "  python api_server.py --port 1410"
    exit 1
fi

echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Test endpoints
test_endpoint "Health Check" "GET" "/health" ""
test_endpoint "Model Info" "GET" "/info" ""

test_endpoint "Generate" "POST" "/generate" \
    '{"prompt": "What is Python?", "max_new_tokens": 50}'

test_endpoint "Single-Turn Chat" "POST" "/chat" \
    '{"message": "Hello! How are you?", "max_new_tokens": 50}'

test_endpoint "Multi-Turn Chat (Turn 1)" "POST" "/chat/session" \
    '{"session_id": "test_session", "message": "What is AI?", "max_new_tokens": 50}'

test_endpoint "Multi-Turn Chat (Turn 2)" "POST" "/chat/session" \
    '{"session_id": "test_session", "message": "Tell me more", "max_new_tokens": 50}'

test_endpoint "Get Session History" "GET" "/session/test_session" ""

test_endpoint "Clear Session" "DELETE" "/session/test_session" ""

echo "======================================"
echo "All tests completed!"
echo "======================================"
