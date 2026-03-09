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


class TechnologyPrediction(Base):
    __tablename__ = "technology_predictions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology: str = Column(String(100), nullable=False, index=True)
    predicted_growth: float = Column(Float, nullable=False, default=0.0)
    confidence_score: float = Column(Float, nullable=False, default=0.0)
    trend_direction: str = Column(String(10), nullable=False, default="stable")  # up/down/stable
    momentum_score: float = Column(Float, nullable=False, default=0.0)
    is_emerging: bool = Column(Integer, nullable=False, default=0)  # anomaly flag
    forecast_horizon_months: int = Column(Integer, nullable=False, default=6)
    created_at: datetime = Column(
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


# ── Analytics tables ──────────────────────────────────────────────

class TechnologyMomentum(Base):
    __tablename__ = "technology_momentum"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology_name: str = Column(String(100), nullable=False, index=True)
    momentum_score: float = Column(Float, nullable=False, default=0.0)
    stars_growth: float = Column(Float, nullable=False, default=0.0)
    contributors_growth: float = Column(Float, nullable=False, default=0.0)
    stackoverflow_growth: float = Column(Float, nullable=False, default=0.0)
    hn_mentions: float = Column(Float, nullable=False, default=0.0)
    commit_activity: float = Column(Float, nullable=False, default=0.0)
    timestamp: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class TechnologyLifecycle(Base):
    __tablename__ = "technology_lifecycle"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology_name: str = Column(String(100), nullable=False, index=True)
    lifecycle_stage: str = Column(String(20), nullable=False, default="Stable")
    confidence_score: float = Column(Float, nullable=False, default=0.0)
    momentum_score: float = Column(Float, nullable=False, default=0.0)
    timestamp: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class EmergingTechnology(Base):
    __tablename__ = "emerging_technologies"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology_name: str = Column(String(100), nullable=False, index=True)
    growth_spike_score: float = Column(Float, nullable=False, default=0.0)
    detected_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class RepositoryHealth(Base):
    __tablename__ = "repository_health"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    repository_name: str = Column(String(255), nullable=False, index=True)
    health_score: float = Column(Float, nullable=False, default=0.0)
    risk_level: str = Column(String(20), nullable=False, default="Critical")
    maintainer_activity: float = Column(Float, nullable=False, default=0.0)
    issue_resolution_speed: float = Column(Float, nullable=False, default=0.0)
    contributors: int = Column(Integer, nullable=False, default=0)
    release_frequency: float = Column(Float, nullable=False, default=0.0)
    commit_frequency: float = Column(Float, nullable=False, default=0.0)
    last_updated: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


# ── Graph tables ──────────────────────────────────────────────────

class TechnologyGraphMetrics(Base):
    __tablename__ = "technology_graph_metrics"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    technology_name: str = Column(String(100), nullable=False, index=True)
    degree_centrality: float = Column(Float, nullable=False, default=0.0)
    betweenness_centrality: float = Column(Float, nullable=False, default=0.0)
    closeness_centrality: float = Column(Float, nullable=False, default=0.0)
    pagerank: float = Column(Float, nullable=False, default=0.0)
    ecosystem_influence: float = Column(Float, nullable=False, default=0.0)
    cluster_id: int = Column(Integer, nullable=False, default=0)
    cluster_label: str = Column(String(50), nullable=False, default="Unknown")
    last_updated: datetime = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
