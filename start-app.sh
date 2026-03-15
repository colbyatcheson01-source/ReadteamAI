#!/bin/bash

# RedTeam AI Launcher Script
# This script starts the backend and frontend servers and opens the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to open a URL in the default web browser
open_browser() {
    local url="$1"
    # Check if we have a display environment
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        echo "No display environment detected. Application is running but browser cannot be opened."
        echo "Please access the application at:"
        echo "  - Frontend: $url"
        echo "  - Backend API: http://localhost:8000"
        return
    fi
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v gnome-open &> /dev/null; then
        gnome-open "$url"
    elif command -v kde-open &> /dev/null; then
        kde-open "$url"
    elif command -v sensible-browser &> /dev/null; then
        sensible-browser "$url"
    elif command -v x-www-browser &> /dev/null; then
        x-www-browser "$url"
    elif command -v gnome-www-browser &> /dev/null; then
        gnome-www-browser "$url"
    else
        echo "Could not find a web browser command. Please open $url manually."
    fi
}

# Start the backend server in the background
echo "Starting backend server..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "ERROR: Backend server failed to start!"
    exit 1
fi

# Start the frontend dev server in the background
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "ERROR: Frontend server failed to start!"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=============================================="
echo "  RedTeam AI - Starting Services"
echo "=============================================="
echo ""
echo "Services started successfully:"
echo "  - Backend API:  http://localhost:8000"
echo "  - Frontend UI:  http://localhost:5173"
echo ""

# Open the browser
echo "Attempting to open browser..."
open_browser http://localhost:5173

echo ""
echo "Application is running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop the servers"

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    
    # Kill the parent processes and all their children
    # Use process group to ensure all child processes are killed
    if [ -n "$BACKEND_PID" ]; then
        # Kill the entire process group
        pkill -P $BACKEND_PID 2>/dev/null
        kill -TERM $BACKEND_PID 2>/dev/null
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        # Kill the entire process group
        pkill -P $FRONTEND_PID 2>/dev/null
        kill -TERM $FRONTEND_PID 2>/dev/null
    fi
    
    # Also kill any remaining node and python processes related to the app
    pkill -f "vite" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    
    # Wait a moment for processes to terminate
    sleep 1
    
    # Force kill if still running
    pkill -9 -f "vite" 2>/dev/null
    pkill -9 -f "uvicorn" 2>/dev/null
    
    echo "All servers stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Wait indefinitely
wait
