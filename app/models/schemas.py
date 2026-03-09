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


# ── Analytics schemas ─────────────────────────────────────────────

class TechnologyMomentumSchema(BaseModel):
    id: int
    technology_name: str
    momentum_score: float
    stars_growth: float
    contributors_growth: float
    stackoverflow_growth: float
    hn_mentions: float
    commit_activity: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class TechnologyLifecycleSchema(BaseModel):
    id: int
    technology_name: str
    lifecycle_stage: str
    confidence_score: float
    momentum_score: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class EmergingTechnologySchema(BaseModel):
    id: int
    technology_name: str
    growth_spike_score: float
    detected_at: datetime

    model_config = {"from_attributes": True}


# ── Repository Health schemas ─────────────────────────────────────

class RepositoryHealthSchema(BaseModel):
    id: int
    repository_name: str
    health_score: float
    risk_level: str
    maintainer_activity: float
    issue_resolution_speed: float
    contributors: int
    release_frequency: float
    commit_frequency: float
    last_updated: datetime

    model_config = {"from_attributes": True}


# ── Graph schemas ─────────────────────────────────────────────────

class TechnologyGraphMetricsSchema(BaseModel):
    id: int
    technology_name: str
    degree_centrality: float
    betweenness_centrality: float
    closeness_centrality: float
    pagerank: float
    ecosystem_influence: float
    cluster_id: int
    cluster_label: str
    last_updated: datetime

    model_config = {"from_attributes": True}


class GraphNodeSchema(BaseModel):
    id: str
    label: str
    cluster_id: int
    cluster_label: str
    ecosystem_influence: float
    pagerank: float


class GraphEdgeSchema(BaseModel):
    source: str
    target: str
    relationship: str


class GraphNetworkSchema(BaseModel):
    nodes: list[GraphNodeSchema]
    edges: list[GraphEdgeSchema]


class InfluenceRankSchema(BaseModel):
    technology_name: str
    ecosystem_influence: float
    degree_centrality: float
    betweenness_centrality: float
    closeness_centrality: float
    pagerank: float


class ClusterSchema(BaseModel):
    cluster_id: int
    cluster_label: str
    technologies: list[str]


# ── AI / Recommendation schemas ─────────────────────────────────

class SkillProfileInput(BaseModel):
    skills: list[str]


class RecommendationSchema(BaseModel):
    technology_name: str
    recommendation_score: float
    skill_similarity: float
    momentum_score: float
    ecosystem_proximity: float
    reason: str


class UserRecommendationSchema(BaseModel):
    id: int
    skill_profile: str
    technology_name: str
    recommendation_score: float
    skill_similarity: float
    momentum_score: float
    ecosystem_proximity: float
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TechnologyForecastSchema(BaseModel):
    id: int
    technology: str
    horizon_months: int
    predicted_growth_pct: float
    model_used: str
    confidence_score: float
    trend_direction: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NLInsightSchema(BaseModel):
    technology: str
    insight: str
    category: str
    severity: str
