from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Repository(Base):
    __tablename__ = "repositories"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    github_repo: str = Column(String(255), nullable=False)
    stars: int = Column(Integer, nullable=False, default=0)
    forks: int = Column(Integer, nullable=False, default=0)
    open_issues: int = Column(Integer, nullable=False, default=0)
    contributors: int = Column(Integer, nullable=False, default=0)
    commit_frequency_weekly: float = Column(Float, nullable=False, default=0.0)
    collected_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class StackOverflowStats(Base):
    __tablename__ = "stackoverflow_stats"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    tag: str = Column(String(100), nullable=False)
    question_count: int = Column(Integer, nullable=False, default=0)
    new_questions_last_30_days: int = Column(Integer, nullable=False, default=0)
    collected_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class HackerNewsMention(Base):
    __tablename__ = "hackernews_mentions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    story_id: int = Column(BigInteger, nullable=False)
    title: str = Column(String(500), nullable=False)
    url: str = Column(String(1000), nullable=True)
    upvotes: int = Column(Integer, nullable=False, default=0)
    comment_count: int = Column(Integer, nullable=False, default=0)
    collected_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class TechnologyMetrics(Base):
    __tablename__ = "technology_metrics"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    # GitHub growth metrics
    stars_growth_rate: float = Column(Float, nullable=False, default=0.0)
    contributors_growth_rate: float = Column(Float, nullable=False, default=0.0)
    commit_activity_score: float = Column(Float, nullable=False, default=0.0)
    issue_resolution_rate: float = Column(Float, nullable=False, default=0.0)
    # Community signals
    stackoverflow_growth: float = Column(Float, nullable=False, default=0.0)
    hn_mentions_growth: float = Column(Float, nullable=False, default=0.0)
    discussion_velocity: float = Column(Float, nullable=False, default=0.0)
    # Composite scores (normalized 0-1)
    momentum_score: float = Column(Float, nullable=False, default=0.0)
    community_score: float = Column(Float, nullable=False, default=0.0)
    activity_score: float = Column(Float, nullable=False, default=0.0)
    last_updated: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class TechMention(Base):
    __tablename__ = "tech_mentions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    source: str = Column(String(50), nullable=False)
    mention_count: int = Column(Integer, nullable=False, default=0)
    total_upvotes: int = Column(Integer, nullable=False, default=0)
    total_comments: int = Column(Integer, nullable=False, default=0)
    collected_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
