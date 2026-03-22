# Backend Architecture Documentation

## Overview

The NLP Comment Processor has been enhanced with a modern **frontend-backend separation architecture**:

- **Frontend**: Streamlit web interface
- **Backend**: FastAPI REST API  
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support

This architecture enables scalable processing, multiple client support, persistent data storage, and RESTful API access.

## Architecture Diagram

```
┌─────────────────┐
│   Streamlit     │  ← Frontend (Port 8501)
│   Frontend      │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│    FastAPI      │  ← Backend API (Port 8000)
│    Backend      │
└────────┬────────┘
         │ SQLAlchemy ORM
         ↓
┌─────────────────┐
│   Database      │  ← Data Layer (SQLite/PostgreSQL)
│  (SQLAlchemy)   │
└─────────────────┘
     │
     ├─ reviews (原始评论)
     ├─ sentiment_results (情感得分)
     └─ topic_results (话题聚类)
```

## Database Schema (最终敲定的表结构)

### 1. reviews (原始评论表)

Stores raw comment data from various sources.

**Columns:**
- `id` (Integer, PK): 主键
- `content` (Text): 评论内容
- `source` (String): 来源 (game name, platform)
- `language` (String): 语言 (chinese, japanese, english)
- `author` (String): 作者
- `timestamp` (DateTime): 时间戳
- `fingerprint` (String, Unique): 指纹用于去重

**Relationships:** One-to-many with sentiment_results and topic_results

### 2. sentiment_results (情感得分表)

Stores sentiment analysis results.

**Columns:**
- `id` (Integer, PK): 主键
- `review_id` (Integer, FK): 关联评论ID
- `sentiment_score` (Float): 情感得分 (-1.0 to 1.0)
- `sentiment_label` (String): positive/negative/neutral
- `positive_score`, `negative_score`, `neutral_score` (Float): 详细分数
- `model_name` (String): 使用的模型
- `confidence` (Float): 置信度
- `processed_at` (DateTime): 处理时间

### 3. topic_results (话题聚类表)

Stores topic modeling and clustering results.

**Columns:**
- `id` (Integer, PK): 主键
- `review_id` (Integer, FK): 关联评论ID
- `topic_id` (Integer): 话题ID
- `topic_name` (String): 话题名称
- `topic_name_cn` (String): 中文话题名称
- `density` (Integer): 话题密度
- `embedding` (JSON): 向量嵌入
- `representative_words` (JSON): 代表性词汇
- `llm_summary` (Text): LLM生成的总结
- `algorithm` (String): 使用的算法 (HDBSCAN)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from backend.database import init_db; init_db()"
```

### 3. Start Backend (FastAPI)
```bash
uvicorn backend.api:app --reload --port 8000
```
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### 4. Start Frontend (Streamlit)
```bash
streamlit run frontend/app.py
```
Frontend: http://localhost:8501

## API Endpoints

**Health:**
- `GET /` - Root endpoint
- `GET /health` - Health check

**Reviews:**
- `POST /api/reviews/` - Create review
- `GET /api/reviews/` - List reviews
- `GET /api/reviews/{id}` - Get review
- `DELETE /api/reviews/{id}` - Delete review

**Sentiment:**
- `GET /api/sentiment/` - List sentiment results
- `GET /api/sentiment/{review_id}` - Get sentiment for review

**Topics:**
- `GET /api/topics/` - List topic results
- `GET /api/topics/{review_id}` - Get topics for review

**Statistics:**
- `GET /api/stats/overview` - Overview statistics

**Jobs:**
- `POST /api/process/` - Start processing job
- `GET /api/jobs/` - List jobs
- `GET /api/jobs/{job_id}` - Get job status

## Usage Example

```python
import requests

API_URL = "http://localhost:8000"

# Create review
review = {
    "content": "这个游戏很好玩！",
    "source": "steam",
    "language": "chinese"
}
response = requests.post(f"{API_URL}/api/reviews/", json=review)
print(response.json())

# Get statistics
stats = requests.get(f"{API_URL}/api/stats/overview").json()
print(stats)
```

## Production Deployment

Use Docker Compose for production deployment with PostgreSQL database.

---

**Version**: 1.0.0
**Status**: ✅ Architecture Finalized and Production-Ready
