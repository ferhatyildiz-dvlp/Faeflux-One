#!/bin/bash

# Faeflux One - Quick Development Start Script
# Starts both backend and frontend in development mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Faeflux One Development Servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}📡 Starting Backend API (FastAPI)...${NC}"
cd "$SCRIPT_DIR/apps/api"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Run ./install.sh first${NC}"
    exit 1
fi

source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Run ./install.sh first${NC}"
    exit 1
fi

echo -e "${BLUE}Backend starting on http://localhost:8000${NC}"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}🌐 Starting Frontend (Next.js)...${NC}"
cd "$SCRIPT_DIR/apps/web"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    pnpm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  .env.local not found. Creating default...${NC}"
    cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
fi

echo -e "${BLUE}Frontend starting on http://localhost:3000${NC}"
pnpm dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Servers started!${NC}"
echo -e "${BLUE}  • Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}  • Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}  • API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID

