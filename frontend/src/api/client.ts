import type {
  TechnologyMetrics,
  TechnologyPrediction,
  HealthReport,
  EmergingTech,
  TrendInsight,
} from "../types";

const BASE = "";

async function get<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) throw new Error(`API ${url}: ${res.status}`);
  return res.json();
}

export const api = {
  // Metrics
  metricsLatest: () => get<TechnologyMetrics[]>("/api/v1/metrics/latest"),

  // Predictions
  predictions: () => get<TechnologyPrediction[]>("/api/v1/predictions/latest"),
  predictionsEmerging: () => get<TechnologyPrediction[]>("/api/v1/predictions/emerging"),

  // Insights
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
};
