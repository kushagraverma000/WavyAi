#!/bin/bash

# WavyAI Quick Start Script
# This script helps you start the prototype quickly

echo "🚀 Starting WavyAI Prototype..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python and Node.js found"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend/.env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
ENVIRONMENT=development
DEBUG=true
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
fi

echo "✅ Backend setup complete"
echo ""

# Start backend in background
echo "🌐 Starting backend server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend/.env file..."
    echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
fi

echo "✅ Frontend setup complete"
echo ""

# Start frontend
echo "🌐 Starting frontend server..."
echo ""
echo "=========================================="
echo "✅ WavyAI Prototype is starting!"
echo "=========================================="
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start frontend (this blocks)
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT


