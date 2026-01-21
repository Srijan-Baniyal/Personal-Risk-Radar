#!/bin/bash
# Quick setup script for Personal Risk Radar

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         🎯 Personal Risk Radar - Setup                  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv package manager not found"
    echo "💡 Install it from: https://docs.astral.sh/uv/"
    exit 1
fi

echo "✅ uv found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
uv sync
echo "✅ Dependencies installed"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python run.py init
echo "✅ Database initialized"
echo ""

# Load sample data
echo "📥 Starting API to load sample data..."
python run.py api --port 8000 &
API_PID=$!
sleep 3

echo "📊 Loading sample data..."
python run.py load
echo "✅ Sample data loaded"
echo ""

# Stop API
kill $API_PID 2>/dev/null || true
sleep 1

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║  ✅ Setup Complete!                                     ║"
echo "║                                                          ║"
echo "║  Quick Start:                                            ║"
echo "║  $ python run.py api      # Start API server            ║"
echo "║  $ python run.py ui       # Start Streamlit UI          ║"
echo "║  $ python run.py status   # Check system status         ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
