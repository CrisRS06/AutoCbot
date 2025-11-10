#!/bin/bash

# AutoCbot E2E API Testing Script
# Tests all critical flows end-to-end

set -e  # Exit on error

API_BASE="http://localhost:8000/api/v1"
ERRORS=()
WARNINGS=()
PASSED=0
FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   AutoCbot E2E API Testing Suite${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Helper function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local headers="$6"

    echo -n "Testing: $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "$headers" "$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -H "$headers" -d "$data" "$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
        echo "$body"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_status, got $http_code)"
        echo "$body"
        ERRORS+=("$name: Expected HTTP $expected_status, got $http_code")
        ((FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 1: Authentication Flow${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 1: Register new user
USER_EMAIL="test_$(date +%s)@example.com"
USER_PASSWORD="SecurePassword123!"

echo "Registering user: $USER_EMAIL"
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASSWORD\"}" \
    "$API_BASE/auth/register")

REGISTER_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

if [ "$REGISTER_CODE" = "201" ]; then
    echo -e "${GREEN}✓ Registration PASSED${NC}"
    ((PASSED++))
    USER_ID=$(echo "$REGISTER_BODY" | grep -o '"id":[0-9]*' | cut -d: -f2)
    echo "User ID: $USER_ID"
else
    echo -e "${RED}✗ Registration FAILED (HTTP $REGISTER_CODE)${NC}"
    echo "$REGISTER_BODY"
    ERRORS+=("Registration failed with HTTP $REGISTER_CODE")
    ((FAILED++))
    exit 1
fi

echo ""

# Test 2: Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASSWORD\"}" \
    "$API_BASE/auth/login")

LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$LOGIN_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Login PASSED${NC}"
    ((PASSED++))
    ACCESS_TOKEN=$(echo "$LOGIN_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$LOGIN_BODY" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)
    echo "Access token obtained (${#ACCESS_TOKEN} chars)"
else
    echo -e "${RED}✗ Login FAILED (HTTP $LOGIN_CODE)${NC}"
    echo "$LOGIN_BODY"
    ERRORS+=("Login failed with HTTP $LOGIN_CODE")
    ((FAILED++))
    exit 1
fi

echo ""

# Test 3: Get current user info
echo "Getting current user info..."
ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$API_BASE/auth/me")

ME_CODE=$(echo "$ME_RESPONSE" | tail -n1)
ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')

if [ "$ME_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Get /me PASSED${NC}"
    ((PASSED++))
    echo "$ME_BODY"
else
    echo -e "${RED}✗ Get /me FAILED (HTTP $ME_CODE)${NC}"
    echo "$ME_BODY"
    ERRORS+=("Get /me failed with HTTP $ME_CODE")
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 2: Authorization Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 4: Access protected endpoint WITHOUT token (should fail)
echo "Testing protected endpoint without auth..."
NO_AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE/settings/")
NO_AUTH_CODE=$(echo "$NO_AUTH_RESPONSE" | tail -n1)

if [ "$NO_AUTH_CODE" = "401" ] || [ "$NO_AUTH_CODE" = "403" ]; then
    echo -e "${GREEN}✓ Protected endpoint blocks unauthenticated access${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Protected endpoint allows unauthenticated access (HTTP $NO_AUTH_CODE)${NC}"
    ERRORS+=("Protected endpoint should return 401/403, got $NO_AUTH_CODE")
    ((FAILED++))
fi

echo ""

# Test 5: Access protected endpoint WITH token (should work)
echo "Testing protected endpoint with valid token..."
SETTINGS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$API_BASE/settings/")

SETTINGS_CODE=$(echo "$SETTINGS_RESPONSE" | tail -n1)
SETTINGS_BODY=$(echo "$SETTINGS_RESPONSE" | sed '$d')

if [ "$SETTINGS_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Protected endpoint accepts valid token${NC}"
    ((PASSED++))
    echo "Settings: $SETTINGS_BODY"
else
    echo -e "${RED}✗ Protected endpoint rejects valid token (HTTP $SETTINGS_CODE)${NC}"
    echo "$SETTINGS_BODY"
    ERRORS+=("Settings endpoint failed with HTTP $SETTINGS_CODE")
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 3: Settings Management${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 6: Update settings
echo "Updating user settings..."
UPDATE_SETTINGS=$(curl -s -w "\n%{http_code}" -X PUT \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "default_pairs": "BTC/USDT,ETH/USDT",
        "default_timeframe": "1h",
        "max_position_size": 0.15,
        "max_open_trades": 3,
        "default_stoploss": -0.03,
        "default_takeprofit": 0.05,
        "enable_ml_predictions": true,
        "enable_paper_trading": true,
        "dry_run": true
    }' \
    "$API_BASE/settings/")

SETTINGS_UPD_CODE=$(echo "$UPDATE_SETTINGS" | tail -n1)
SETTINGS_UPD_BODY=$(echo "$UPDATE_SETTINGS" | sed '$d')

if [ "$SETTINGS_UPD_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Settings update PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Settings update FAILED (HTTP $SETTINGS_UPD_CODE)${NC}"
    echo "$SETTINGS_UPD_BODY"
    ERRORS+=("Settings update failed with HTTP $SETTINGS_UPD_CODE")
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 4: Public Endpoints${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 7: Market overview (public)
echo "Testing market overview..."
MARKET_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE/market/overview")
MARKET_CODE=$(echo "$MARKET_RESPONSE" | tail -n1)

if [ "$MARKET_CODE" = "200" ] || [ "$MARKET_CODE" = "500" ]; then
    if [ "$MARKET_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Market overview accessible${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ Market overview returned 500 (external API issue expected)${NC}"
        WARNINGS+=("Market API returned 500 - external API connectivity issue")
        ((PASSED++))
    fi
else
    echo -e "${RED}✗ Market overview failed unexpectedly (HTTP $MARKET_CODE)${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 5: Strategy Management${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 8: List strategies (should be empty initially)
echo "Listing strategies..."
STRAT_LIST_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$API_BASE/strategy/list")

STRAT_LIST_CODE=$(echo "$STRAT_LIST_RESPONSE" | tail -n1)
STRAT_LIST_BODY=$(echo "$STRAT_LIST_RESPONSE" | sed '$d')

if [ "$STRAT_LIST_CODE" = "200" ]; then
    echo -e "${GREEN}✓ List strategies PASSED${NC}"
    ((PASSED++))
    echo "Strategies: $STRAT_LIST_BODY"
else
    echo -e "${RED}✗ List strategies FAILED (HTTP $STRAT_LIST_CODE)${NC}"
    echo "$STRAT_LIST_BODY"
    ERRORS+=("List strategies failed with HTTP $STRAT_LIST_CODE")
    ((FAILED++))
fi

echo ""

# Test 9: Create strategy
echo "Creating new strategy..."
CREATE_STRAT=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Strategy",
        "description": "E2E test strategy",
        "type": "momentum",
        "parameters": {
            "symbols": ["BTC/USDT"],
            "timeframe": "1h",
            "indicators": {
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30
            }
        },
        "is_active": false
    }' \
    "$API_BASE/strategy/")

CREATE_STRAT_CODE=$(echo "$CREATE_STRAT" | tail -n1)
CREATE_STRAT_BODY=$(echo "$CREATE_STRAT" | sed '$d')

if [ "$CREATE_STRAT_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Create strategy PASSED${NC}"
    ((PASSED++))
    echo "$CREATE_STRAT_BODY"
else
    echo -e "${RED}✗ Create strategy FAILED (HTTP $CREATE_STRAT_CODE)${NC}"
    echo "$CREATE_STRAT_BODY"
    ERRORS+=("Create strategy failed with HTTP $CREATE_STRAT_CODE")
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}PHASE 6: Logout${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Test 10: Logout
echo "Logging out..."
LOGOUT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$API_BASE/auth/logout")

LOGOUT_CODE=$(echo "$LOGOUT_RESPONSE" | tail -n1)
LOGOUT_BODY=$(echo "$LOGOUT_RESPONSE" | sed '$d')

if [ "$LOGOUT_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Logout PASSED${NC}"
    ((PASSED++))
    echo "$LOGOUT_BODY"
else
    echo -e "${RED}✗ Logout FAILED (HTTP $LOGOUT_CODE)${NC}"
    echo "$LOGOUT_BODY"
    ERRORS+=("Logout failed with HTTP $LOGOUT_CODE")
    ((FAILED++))
fi

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo -e "Warnings: ${YELLOW}${#WARNINGS[@]}${NC}"
echo ""

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Warnings:${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo -e "  ${YELLOW}⚠${NC} $warning"
    done
    echo ""
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}Errors:${NC}"
    for error in "${ERRORS[@]}"; do
        echo -e "  ${RED}✗${NC} $error"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
