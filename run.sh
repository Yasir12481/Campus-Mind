#!/bin/bash
set -e

echo "🎓 CampusMind — Smart Campus Management System"
echo "================================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose v2 is required. Please update Docker."
    exit 1
fi

echo "🚀 Starting all services..."
docker compose up --build -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend not responding yet. Check: docker compose logs backend"
fi

echo ""
echo "================================================"
echo "🌐 Frontend:        http://localhost:3000"
echo "🔧 Backend API:     http://localhost:8000"
echo "📖 API Docs:        http://localhost:8000/docs"
echo "================================================"
echo ""
echo "To stop: docker compose down"
echo "To view logs: docker compose logs -f"
