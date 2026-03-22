#!/bin/bash
# Start Backend (FastAPI)

echo "🚀 Starting NLP Comment Processor Backend..."
echo ""

# Initialize database if needed
echo "📊 Initializing database..."
python -c "from backend.database import init_db; init_db()"

echo ""
echo "✅ Starting FastAPI server on port 8000..."
echo "📄 API Documentation: http://localhost:8000/docs"
echo ""

uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
