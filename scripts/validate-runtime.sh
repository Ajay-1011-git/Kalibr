#!/bin/bash
# Runtime validation script for Kalibr
# Checks that all services are healthy and accessible

set -e

echo "=== Kalibr Runtime Validation ==="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

function wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=1

    echo "Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            check "$service is healthy"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo ""
    echo -e "${RED}✗${NC} $service failed to start after $max_attempts attempts"
    return 1
}

echo "1. Checking Redis..."
docker compose ps redis | grep -q "Up" && check "Redis container running" || exit 1

echo ""
echo "2. Checking Backend..."
wait_for_service "http://localhost:8000/v1/health" "Backend API" || exit 1

echo ""
echo "3. Checking Frontend..."
wait_for_service "http://localhost:5173" "Frontend" || exit 1

echo ""
echo "4. Checking Celery Worker..."
docker compose ps worker | grep -q "Up" && check "Worker container running" || exit 1

echo ""
echo "5. Checking Celery Beat..."
docker compose ps beat | grep -q "Up" && check "Beat container running" || exit 1

echo ""
echo "6. Testing Backend API..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/v1/health)
echo "$HEALTH_RESPONSE" | grep -q "healthy" && check "Backend health endpoint responsive" || exit 1

echo ""
echo "7. Checking Environment Configuration..."
if [ -f ".env" ]; then
    check ".env file exists"
    grep -q "REDIS_URL=redis://redis:6379/0" .env && check "Redis URL configured for local container" || echo -e "${YELLOW}⚠${NC} Redis URL may need adjustment"
    grep -q "SUPABASE_URL" .env && check "Supabase URL configured" || echo -e "${YELLOW}⚠${NC} Supabase URL missing"
    grep -q "FIREBASE_PROJECT_ID" .env && check "Firebase configured" || echo -e "${YELLOW}⚠${NC} Firebase not configured"
else
    echo -e "${RED}✗${NC} .env file missing"
    exit 1
fi

echo ""
echo "8. Checking Frontend Environment..."
if [ -f "frontend/.env" ]; then
    check "frontend/.env file exists"
else
    echo -e "${YELLOW}⚠${NC} frontend/.env file missing"
fi

echo ""
echo -e "${GREEN}=== All Critical Services Operational ===${NC}"
echo ""
echo "Access points:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Health:    http://localhost:8000/v1/health"
