import type {
  TechnologyMetrics,
  TechnologyPrediction,
  HealthReport,
  EmergingTech,
  TrendInsight,
  MomentumData,
  LifecycleData,
  EmergingData,
  RepoHealthData,
  GraphNetwork,
  InfluenceRank,
  ClusterData,
  RecommendationData,
  ForecastData,
  NLInsight,
} from "../types";

const BASE = "";

async function get<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) throw new Error(`API ${url}: ${res.status}`);
  return res.json();
}

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${url}: ${res.status}`);
  return res.json();
}

export const api = {
  // ── Master technology list ──
  technologies: () => get<{ name: string; category: string }[]>("/api/v1/technologies"),

  // Phase 1-5 endpoints
  metricsLatest: () => get<TechnologyMetrics[]>("/api/v1/metrics/latest"),
  predictions: () => get<TechnologyPrediction[]>("/api/v1/predictions/latest"),
  predictionsEmerging: () => get<TechnologyPrediction[]>("/api/v1/predictions/emerging"),
  health: () => get<HealthReport[]>("/insights/health"),
  emerging: (top = 10) => get<EmergingTech[]>(`/insights/emerging?top=${top}`),
  trends: (tech?: string, category?: string) => {
    const params = new URLSearchParams();
    if (tech) params.set("technology", tech);
    if (category) params.set("category", category);
    const qs = params.toString();
    return get<TrendInsight[]>(`/insights/trends${qs ? `?${qs}` : ""}`);
  },
  risks: () => get<TrendInsight[]>("/insights/risks"),

  // Phase 6 — Analytics
  momentum: () => get<MomentumData[]>("/analytics/momentum"),
  lifecycle: () => get<LifecycleData[]>("/analytics/lifecycle"),
  emergingAnalytics: () => get<EmergingData[]>("/analytics/emerging"),

  // Phase 7 — Repo Health
  repoHealth: () => get<RepoHealthData[]>("/repos/health"),
  repoHealthByName: (name: string) => get<RepoHealthData>(`/repos/health/${encodeURIComponent(name)}`),

  // Phase 8 — Graph
  graphNetwork: () => get<GraphNetwork>("/graph/network"),
  graphInfluence: () => get<InfluenceRank[]>("/graph/influence"),
  graphClusters: () => get<ClusterData[]>("/graph/clusters"),

  // Phase 9 — AI
  recommend: (skills: string[]) => post<RecommendationData[]>("/ai/recommend", { skills }),
  forecast: (technology?: string) => {
    const qs = technology ? `?technology=${encodeURIComponent(technology)}` : "";
    return get<ForecastData[]>(`/ai/forecast${qs}`);
  },
  insights: (category?: string) => {
    const qs = category ? `?category=${encodeURIComponent(category)}` : "";
    return get<NLInsight[]>(`/ai/insights${qs}`);
  },
};
