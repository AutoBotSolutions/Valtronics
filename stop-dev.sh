#!/bin/bash

# Stop development servers for Valtronics

echo "🛑 Stopping Valtronics development servers..."

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID
        fi
        echo "✅ Backend stopped"
    else
        echo "ℹ️  Backend process not found"
    fi
    rm .backend.pid
else
    echo "ℹ️  Backend PID file not found"
fi

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -9 $FRONTEND_PID
        fi
        echo "✅ Frontend stopped"
    else
        echo "ℹ️  Frontend process not found"
    fi
    rm .frontend.pid
else
    echo "ℹ️  Frontend PID file not found"
fi

# Kill any remaining processes on ports 8000 and 3000
echo "🧹 Cleaning up any remaining processes..."

# Kill processes on port 8000
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo "🔧 Killing process on port 8000 (PID: $BACKEND_PORT_PID)"
    kill $BACKEND_PORT_PID 2>/dev/null || true
fi

# Kill processes on port 3000
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null || true)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo "🎨 Killing process on port 3000 (PID: $FRONTEND_PORT_PID)"
    kill $FRONTEND_PORT_PID 2>/dev/null || true
fi

echo "✅ All servers stopped successfully!"
