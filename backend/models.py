"""
Database models for NLP Comment Processor
Defines three core tables: reviews, sentiment_results, topic_results
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Review(Base):
    """
    原始评论表 (Original Reviews Table)
    Stores raw comment data from various sources
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # 评论内容
    source = Column(String(100))  # 来源 (game name, platform, etc.)
    language = Column(String(20))  # 语言 (chinese, japanese, english, etc.)
    author = Column(String(255))  # 作者
    timestamp = Column(DateTime, default=datetime.utcnow)  # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    fingerprint = Column(String(64), unique=True, index=True)  # 指纹用于去重
    
    # Relationships
    sentiment_results = relationship("SentimentResult", back_populates="review", cascade="all, delete-orphan")
    topic_results = relationship("TopicResult", back_populates="review", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Review(id={self.id}, source={self.source}, language={self.language})>"


class SentimentResult(Base):
    """
    情感分析结果表 (Sentiment Analysis Results Table)
    Stores sentiment scores and classifications for reviews
    """
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    
    # Sentiment scores
    sentiment_score = Column(Float)  # 情感得分 (-1.0 to 1.0)
    sentiment_label = Column(String(20))  # 情感标签 (positive, negative, neutral)
    
    # Detailed scores
    positive_score = Column(Float)  # 正面得分
    negative_score = Column(Float)  # 负面得分
    neutral_score = Column(Float)  # 中性得分
    
    # Model information
    model_name = Column(String(255))  # 使用的模型名称
    confidence = Column(Float)  # 置信度
    
    # Processing metadata
    processed_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # 处理时间（秒）
    
    # Relationship
    review = relationship("Review", back_populates="sentiment_results")

    def __repr__(self):
        return f"<SentimentResult(id={self.id}, review_id={self.review_id}, label={self.sentiment_label})>"


class TopicResult(Base):
    """
    话题聚类结果表 (Topic Clustering Results Table)
    Stores topic modeling and clustering results
    """
    __tablename__ = "topic_results"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    
    # Topic information
    topic_id = Column(Integer, index=True)  # 话题ID
    topic_name = Column(String(255))  # 话题名称 (e.g., "Graphics Quality")
    topic_name_cn = Column(String(255))  # 中文话题名称
    
    # Clustering information
    cluster_label = Column(Integer)  # 聚类标签
    density = Column(Integer)  # 话题密度（提到次数）
    
    # Embeddings and features
    embedding = Column(JSON)  # 向量嵌入 (stored as JSON array)
    representative_words = Column(JSON)  # 代表性词汇列表
    
    # Topic statistics
    topic_sentiment_avg = Column(Float)  # 该话题的平均情感
    confidence = Column(Float)  # 聚类置信度
    
    # LLM enhancements
    llm_summary = Column(Text)  # LLM生成的话题总结
    llm_insight = Column(Text)  # LLM生成的洞察
    
    # Processing metadata
    processed_at = Column(DateTime, default=datetime.utcnow)
    algorithm = Column(String(50))  # 使用的算法 (e.g., "HDBSCAN")
    
    # Relationship
    review = relationship("Review", back_populates="topic_results")

    def __repr__(self):
        return f"<TopicResult(id={self.id}, review_id={self.review_id}, topic={self.topic_name})>"


# Additional helper models
class ProcessingJob(Base):
    """
    处理任务表 (Processing Jobs Table)
    Tracks NLP processing jobs and their status
    """
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(64), unique=True, index=True)  # 任务ID
    status = Column(String(20))  # 状态 (pending, processing, completed, failed)
    
    # Job details
    input_file = Column(String(500))  # 输入文件路径
    total_comments = Column(Integer)  # 总评论数
    processed_comments = Column(Integer)  # 已处理评论数
    
    # Results
    output_file = Column(String(500))  # 输出文件路径
    report_file = Column(String(500))  # 报告文件路径
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    processing_duration = Column(Float)  # 处理时长（秒）
    
    # Error handling
    error_message = Column(Text)  # 错误信息
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, job_id={self.job_id}, status={self.status})>"
