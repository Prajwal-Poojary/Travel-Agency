#!/bin/bash

echo "🚀 Starting Advanced Travel Platform Frontend..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔗 Make sure backend is running at: http://localhost:8001"
echo "=" * 60

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --legacy-peer-deps
fi

echo "🎯 Starting React development server..."
npm start