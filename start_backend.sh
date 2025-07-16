#!/bin/bash

echo "🚀 Starting Advanced Travel Platform Backend..."
echo "📍 Backend will be available at: http://localhost:8001"
echo "📚 API Documentation: http://localhost:8001/docs"
echo "🔍 Health Check: http://localhost:8001/api/health"
echo "=" * 60

cd backend

# Check if Python 3.11+ is available
if command -v python3.11 &> /dev/null; then
    echo "✅ Using Python 3.11"
    python3.11 start_server.py
elif command -v python3.10 &> /dev/null; then
    echo "✅ Using Python 3.10"
    python3.10 start_server.py
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Using Python $PYTHON_VERSION"
    python3 start_server.py
else
    echo "❌ Python 3.10+ is required but not found"
    echo "Please install Python 3.10 or 3.11 from https://www.python.org/downloads/"
    exit 1
fi