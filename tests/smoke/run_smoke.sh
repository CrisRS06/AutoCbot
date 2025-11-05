#!/bin/bash
# ==================================================
# AutoCbot Smoke Test Runner
# ==================================================
# Quick health check - runs all smoke tests
# Time Budget: < 30 seconds total
# ==================================================

set -e  # Exit on error

echo "🔥 AutoCbot Smoke Tests"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not installed${NC}"
    echo "Install with: pip install -r tests/requirements.txt"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

# Check if services are running
echo -e "${YELLOW}Checking services...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend not running on localhost:8000${NC}"
    echo "Start with: docker-compose up -d backend"
    exit 1
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not running (tests will skip frontend checks)${NC}"
fi

echo ""
echo "Running smoke tests..."
echo "================================"
echo ""

# Run smoke tests with pytest
pytest tests/smoke/ \
    -v \
    -m smoke \
    --tb=short \
    --color=yes \
    --timeout=5 \
    -x

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    echo "================================"
    exit 0
else
    echo ""
    echo "================================"
    echo -e "${RED}❌ Smoke tests failed${NC}"
    echo "================================"
    exit 1
fi
