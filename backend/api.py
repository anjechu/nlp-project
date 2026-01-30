"""
FastAPI Backend for NLP Comment Processor
Provides REST API endpoints for model requests and data queries
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db, init_db, engine
from backend.models import Review, SentimentResult, TopicResult, ProcessingJob, Base

# Import NLP processor
try:
    from nlp import NLPProcessor
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    print("⚠️ NLP Processor not available")

# Initialize FastAPI app
app = FastAPI(
    title="NLP Comment Processor API",
    description="Backend API for NLP processing and cross-cultural analysis",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


# Pydantic models for API requests/responses
class ReviewCreate(BaseModel):
    content: str
    source: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    fingerprint: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    content: str
    source: Optional[str]
    language: Optional[str]
    author: Optional[str]
    timestamp: datetime
    fingerprint: Optional[str]
    
    class Config:
        from_attributes = True


class SentimentResultResponse(BaseModel):
    id: int
    review_id: int
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    positive_score: Optional[float]
    negative_score: Optional[float]
    neutral_score: Optional[float]
    processed_at: datetime
    
    class Config:
        from_attributes = True


class TopicResultResponse(BaseModel):
    id: int
    review_id: int
    topic_id: Optional[int]
    topic_name: Optional[str]
    topic_name_cn: Optional[str]
    density: Optional[int]
    topic_sentiment_avg: Optional[float]
    llm_summary: Optional[str]
    
    class Config:
        from_attributes = True


class ProcessingJobResponse(BaseModel):
    id: int
    job_id: str
    status: str
    total_comments: Optional[int]
    processed_comments: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProcessingRequest(BaseModel):
    comments: List[str]
    source: Optional[str] = "api"
    language: Optional[str] = "unknown"


# API Endpoints

@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "message": "NLP Comment Processor API",
        "version": "1.0.0",
        "status": "running",
        "nlp_available": NLP_AVAILABLE
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Reviews endpoints
@app.post("/api/reviews/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review"""
    db_review = Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.get("/api/reviews/", response_model=List[ReviewResponse])
def read_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all reviews with pagination"""
    reviews = db.query(Review).offset(skip).limit(limit).all()
    return reviews


@app.get("/api/reviews/{review_id}", response_model=ReviewResponse)
def read_review(review_id: int, db: Session = Depends(get_db)):
    """Get a specific review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@app.delete("/api/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}


# Sentiment results endpoints
@app.get("/api/sentiment/", response_model=List[SentimentResultResponse])
def read_sentiment_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sentiment results with pagination"""
    results = db.query(SentimentResult).offset(skip).limit(limit).all()
    return results


@app.get("/api/sentiment/{review_id}", response_model=SentimentResultResponse)
def read_sentiment_for_review(review_id: int, db: Session = Depends(get_db)):
    """Get sentiment result for a specific review"""
    result = db.query(SentimentResult).filter(SentimentResult.review_id == review_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Sentiment result not found")
    return result


# Topic results endpoints
@app.get("/api/topics/", response_model=List[TopicResultResponse])
def read_topic_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all topic results with pagination"""
    results = db.query(TopicResult).offset(skip).limit(limit).all()
    return results


@app.get("/api/topics/{review_id}", response_model=List[TopicResultResponse])
def read_topics_for_review(review_id: int, db: Session = Depends(get_db)):
    """Get topic results for a specific review"""
    results = db.query(TopicResult).filter(TopicResult.review_id == review_id).all()
    return results


# Statistics endpoints
@app.get("/api/stats/overview")
def get_overview_stats(db: Session = Depends(get_db)):
    """Get overview statistics"""
    total_reviews = db.query(Review).count()
    total_sentiments = db.query(SentimentResult).count()
    total_topics = db.query(TopicResult).count()
    
    # Sentiment distribution
    positive = db.query(SentimentResult).filter(SentimentResult.sentiment_label == "positive").count()
    negative = db.query(SentimentResult).filter(SentimentResult.sentiment_label == "negative").count()
    neutral = db.query(SentimentResult).filter(SentimentResult.sentiment_label == "neutral").count()
    
    return {
        "total_reviews": total_reviews,
        "total_sentiments": total_sentiments,
        "total_topics": total_topics,
        "sentiment_distribution": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        }
    }


# Processing job endpoints
@app.get("/api/jobs/", response_model=List[ProcessingJobResponse])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all processing jobs"""
    jobs = db.query(ProcessingJob).offset(skip).limit(limit).all()
    return jobs


@app.get("/api/jobs/{job_id}", response_model=ProcessingJobResponse)
def read_job(job_id: str, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(ProcessingJob).filter(ProcessingJob.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/process/")
async def process_comments(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process comments with NLP pipeline
    Creates a background job to handle the processing
    """
    if not NLP_AVAILABLE:
        raise HTTPException(status_code=503, detail="NLP processor not available")
    
    # Create processing job
    job_id = str(uuid.uuid4())
    job = ProcessingJob(
        job_id=job_id,
        status="pending",
        total_comments=len(request.comments),
        processed_comments=0,
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    
    # Add background task
    background_tasks.add_task(
        process_comments_task,
        job_id=job_id,
        comments=request.comments,
        source=request.source,
        language=request.language
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Processing started in background"
    }


def process_comments_task(job_id: str, comments: List[str], source: str, language: str):
    """
    Background task to process comments
    Updates database with results
    """
    # This would integrate with the existing NLP processor
    # For now, it's a placeholder
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
