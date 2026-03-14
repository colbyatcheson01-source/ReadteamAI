#!/bin/bash

# RedTeam AI Launcher Script
# This script starts the backend and frontend servers and opens the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to open a URL in the default web browser
open_browser() {
    local url="$1"
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

# Start the frontend dev server in the background
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Open the browser
echo "Opening application in browser..."
open_browser http://localhost:5173

echo "Application is running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop the servers"

# Handle cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait indefinitely
wait
