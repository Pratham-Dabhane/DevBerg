// ── API response types matching the FastAPI backend ──

export interface TechnologyMetrics {
  id: number;
  technology: string;
  stars_growth_rate: number;
  contributors_growth_rate: number;
  commit_activity_score: number;
  issue_resolution_rate: number;
  stackoverflow_growth: number;
  hn_mentions_growth: number;
  discussion_velocity: number;
  momentum_score: number;
  community_score: number;
  activity_score: number;
  last_updated: string;
}

export interface TechnologyPrediction {
  id: number;
  technology: string;
  predicted_growth: number;
  confidence_score: number;
  trend_direction: "up" | "down" | "stable";
  momentum_score: number;
  is_emerging: boolean;
  forecast_horizon_months: number;
  created_at: string;
}

export interface HealthReport {
  technology: string;
  health_score: number;
  risk_level: "Low" | "Medium" | "High" | "Critical";
  maintainer_activity: number;
  release_frequency: number;
  issue_resolution_speed: number;
  contributor_diversity: number;
  insights: string[];
}

export interface EmergingTech {
  rank: number;
  technology: string;
  momentum_score: number;
  predicted_growth: number;
  trend_direction: "up" | "down" | "stable";
  signals: string[];
}

export interface TrendInsight {
  technology: string;
  category: "growth" | "decline" | "anomaly" | "milestone";
  message: string;
  severity: "info" | "warning" | "critical";
  data: Record<string, number | boolean | string>;
}

export type TechCategory = "all" | "ai" | "languages" | "databases" | "devops";

// ── Phase 6-9 types ──

export interface MomentumData {
  id: number;
  technology_name: string;
  momentum_score: number;
  stars_growth: number;
  contributors_growth: number;
  stackoverflow_growth: number;
  hn_mentions: number;
  commit_activity: number;
  timestamp: string;
}

export interface LifecycleData {
  id: number;
  technology_name: string;
  lifecycle_stage: string;
  confidence_score: number;
  momentum_score: number;
  timestamp: string;
}

export interface EmergingData {
  id: number;
  technology_name: string;
  growth_spike_score: number;
  detected_at: string;
}

export interface RepoHealthData {
  id: number;
  repository_name: string;
  health_score: number;
  risk_level: string;
  maintainer_activity: number;
  issue_resolution_speed: number;
  contributors: number;
  release_frequency: number;
  commit_frequency: number;
  last_updated: string;
}

export interface GraphNode {
  id: string;
  label: string;
  cluster_id: number;
  cluster_label: string;
  ecosystem_influence: number;
  pagerank: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface GraphNetwork {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface InfluenceRank {
  technology_name: string;
  ecosystem_influence: number;
  degree_centrality: number;
  betweenness_centrality: number;
  pagerank: number;
  closeness_centrality: number;
}

export interface ClusterData {
  cluster_id: number;
  cluster_label: string;
  technologies: string[];
}

export interface RecommendationData {
  technology_name: string;
  recommendation_score: number;
  momentum_score: number;
  skill_similarity: number;
  ecosystem_proximity: number;
  reason: string;
}

export interface ForecastData {
  id: number;
  technology: string;
  horizon_months: number;
  predicted_growth_pct: number;
  confidence_score: number;
  trend_direction: string;
  model_used: string;
  created_at: string;
}

export interface NLInsight {
  technology: string;
  category: string;
  severity: string;
  insight: string;
}
