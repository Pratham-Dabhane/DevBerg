from pydantic import BaseModel
from datetime import datetime


class RepositorySchema(BaseModel):
    id: int
    technology: str
    github_repo: str
    stars: int
    forks: int
    open_issues: int
    contributors: int
    commit_frequency_weekly: float
    collected_at: datetime

    model_config = {"from_attributes": True}


class StackOverflowStatsSchema(BaseModel):
    id: int
    technology: str
    tag: str
    question_count: int
    new_questions_last_30_days: int
    collected_at: datetime

    model_config = {"from_attributes": True}


class HackerNewsMentionSchema(BaseModel):
    id: int
    technology: str
    story_id: int
    title: str
    url: str | None
    upvotes: int
    comment_count: int
    collected_at: datetime

    model_config = {"from_attributes": True}


class TechMentionSchema(BaseModel):
    id: int
    technology: str
    source: str
    mention_count: int
    total_upvotes: int
    total_comments: int
    collected_at: datetime

    model_config = {"from_attributes": True}


class TechnologyPredictionSchema(BaseModel):
    id: int
    technology: str
    predicted_growth: float
    confidence_score: float
    trend_direction: str
    momentum_score: float
    is_emerging: bool
    forecast_horizon_months: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TechnologyMetricsSchema(BaseModel):
    id: int
    technology: str
    stars_growth_rate: float
    contributors_growth_rate: float
    commit_activity_score: float
    issue_resolution_rate: float
    stackoverflow_growth: float
    hn_mentions_growth: float
    discussion_velocity: float
    momentum_score: float
    community_score: float
    activity_score: float
    last_updated: datetime

    model_config = {"from_attributes": True}


class CollectionStatusSchema(BaseModel):
    status: str
    message: str


# ── Insights schemas ──────────────────────────────────────────────

class HealthReportSchema(BaseModel):
    technology: str
    health_score: int
    risk_level: str
    maintainer_activity: float
    release_frequency: float
    issue_resolution_speed: float
    contributor_diversity: float
    insights: list[str]


class EmergingTechSchema(BaseModel):
    rank: int
    technology: str
    momentum_score: float
    predicted_growth: float
    trend_direction: str
    signals: list[str]


class TrendInsightSchema(BaseModel):
    technology: str
    category: str
    message: str
    severity: str
    data: dict = {}
