#!/bin/bash

# Simple development startup script for Valtronics
# This version works without PostgreSQL, Redis, or MQTT

set -e

echo "🚀 Starting Valtronics Development Server..."

# Check if we're in the right directory
if [ ! -f "backend/app/main_sqlite.py" ]; then
    echo "❌ Error: Please run this script from the valtronics directory"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing backend dependencies..."
pip install -q fastapi uvicorn sqlalchemy pydantic python-multipart websockets psycopg2-binary alembic python-jose[cryptography] passlib[bcrypt] python-dotenv httpx redis celery paho-mqtt pandas numpy scikit-learn openai pytest pytest-asyncio

# Install additional dependencies for local development
pip install -q aiosqlite

echo "✅ Backend dependencies installed"

# Start backend in background
echo "🔧 Starting backend server..."
uvicorn app.main_sqlite:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo $BACKEND_PID > ../.backend.pid

cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend health
if curl -s http://localhost:8000/api/v1/health/ping > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed"
fi

# Start frontend
echo "🎨 Starting frontend development server..."
npm start &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend.pid

cd ..

echo ""
echo "🎉 Valtronics is now running!"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/api/v1/health/ping"
echo ""
echo "🛑 To stop the servers, run: ./stop-dev.sh"
echo ""
echo "📊 You can now:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Add devices using the web interface"
echo "   3. View the API documentation at http://localhost:8000/docs"
echo ""

# Save PIDs for cleanup
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Wait for user input to stop
echo "Press Ctrl+C to stop all servers..."
trap 'echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .backend.pid .frontend.pid; echo "✅ All servers stopped"; exit 0' INT

# Keep script running
wait
