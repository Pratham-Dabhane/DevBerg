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
