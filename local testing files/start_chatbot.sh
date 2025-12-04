#!/bin/bash

# 🤖 A2A-MCP Chatbot UI Starter Script
# Easy one-command startup for the entire system

echo "======================================================================"
echo "  🤖 Starting A2A-MCP Chatbot System"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/genaienv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv genaienv && source genaienv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Please create .env with OPENAI_API_KEY"
fi

# Load API key
export OPENAI_API_KEY=$(grep OPENAI_API_KEY "$SCRIPT_DIR/.env" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    echo "Please set it in .env or export it manually"
    exit 1
fi

echo -e "${GREEN}✅ API key loaded${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found!${NC}"
    echo "Please install Node.js and npm from https://nodejs.org/"
    exit 1
fi

# Install React dependencies if needed
if [ ! -d "$SCRIPT_DIR/react/node_modules" ]; then
    echo -e "${BLUE}📦 Installing React dependencies...${NC}"
    cd "$SCRIPT_DIR/react"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ npm install failed${NC}"
        exit 1
    fi
    cd "$SCRIPT_DIR"
fi

echo -e "${GREEN}✅ Dependencies ready${NC}"

# Install Python dependencies
source "$SCRIPT_DIR/genaienv/bin/activate"
pip install flask flask-cors > /dev/null 2>&1

echo ""
echo "======================================================================"
echo "  🚀 Starting Backend API Server"
echo "======================================================================"

# Start backend in background
python "$SCRIPT_DIR/backend_api.py" &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend running on http://localhost:5000 (PID: $BACKEND_PID)${NC}"

echo ""
echo "======================================================================"
echo "  🎨 Starting React UI"
echo "======================================================================"

# Start React
cd "$SCRIPT_DIR/react"
npm start &
REACT_PID=$!

echo ""
echo "======================================================================"
echo "  ✨ A2A-MCP Chatbot System Running!"
echo "======================================================================"
echo -e "${GREEN}  📍 Backend API: http://localhost:5000${NC}"
echo -e "${GREEN}  🎨 React UI: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop both servers${NC}"
echo "======================================================================"

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "Goodbye!"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait $BACKEND_PID $REACT_PID

