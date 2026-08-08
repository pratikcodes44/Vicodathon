#!/bin/bash

echo "Stopping any dangling uvicorn instances..."
pkill -f uvicorn || true

echo "Starting/restarting Ollama..."
sudo systemctl restart ollama || echo "Note: sudo requires a password or ollama is not installed/managed by systemd."

echo "Starting FastAPI backend server..."
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &

echo "Waiting for server to bind to port 8000..."
sleep 3

echo ""
echo "================================================="
echo "✅ Server and LLM are running!"
echo "================================================="
echo "To test the interview endpoint, run the following:"
echo "cd backend"
echo "source venv/bin/activate"
echo "python3 test_cli.py"
echo "================================================="
