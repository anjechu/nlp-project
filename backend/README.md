# Backend API

FastAPI backend for NLP Comment Processor.

## Quick Start

1. Initialize database:
```bash
python -c "from backend.database import init_db; init_db()"
```

2. Start API server:
```bash
uvicorn backend.api:app --reload
```

3. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

See BACKEND_ARCHITECTURE.md for full API documentation.
