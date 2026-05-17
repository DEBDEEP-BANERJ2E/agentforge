#!/bin/bash
set -e

echo "=== AgentForge starting on HF Spaces ==="

# Activate watsonx Orchestrate environment from env vars
if command -v orchestrate &>/dev/null; then
    if [ -n "$ORCHESTRATE_API_KEY" ] && [ -n "$ORCHESTRATE_SERVICE_URL" ]; then
        echo "Activating Orchestrate environment..."
        orchestrate env activate "${ORCHESTRATE_ENV_NAME:-wx0-AWS}" 2>/dev/null || \
            echo "Warning: orchestrate env activation failed — deploy steps may not work"
    else
        echo "Warning: ORCHESTRATE_API_KEY / ORCHESTRATE_SERVICE_URL not set"
    fi
fi

# Start FastAPI backend on port 8000 (internal)
echo "Starting FastAPI backend on :8000..."
cd /app
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start Next.js frontend on port 7860 (public HF Spaces port)
echo "Starting Next.js frontend on :7860..."
cd /app/frontend
PORT=7860 npm start
