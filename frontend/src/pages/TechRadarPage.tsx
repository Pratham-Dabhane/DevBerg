import { useState } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import Card from "../components/Card";
import CategoryFilter from "../components/CategoryFilter";
import { Spinner, ErrorBox } from "../components/StatusIndicators";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { filterByCategory } from "../utils/categories";
import type { TechCategory, TechnologyMetrics } from "../types";

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e", "#f59e0b"];

function buildRadarData(m: TechnologyMetrics) {
  return [
    { axis: "Stars Growth", value: Math.min(m.stars_growth_rate * 100, 100) },
    { axis: "Contributor Growth", value: Math.min(m.contributors_growth_rate * 100, 100) },
    { axis: "Commit Activity", value: Math.min(m.commit_activity_score * 20, 100) },
    { axis: "Issue Resolution", value: m.issue_resolution_rate * 100 },
    { axis: "SO Growth", value: Math.min(m.stackoverflow_growth * 100, 100) },
    { axis: "HN Mentions", value: Math.min(m.hn_mentions_growth * 100, 100) },
    { axis: "Discussion", value: Math.min(m.discussion_velocity * 50, 100) },
  ];
}

export default function TechRadarPage() {
  const [category, setCategory] = useState<TechCategory>("all");
  const [selected, setSelected] = useState<string | null>(null);

  const metrics = useFetch(() => api.metricsLatest(), []);
  const health = useFetch(() => api.health(), []);

  if (metrics.loading || health.loading) return <Spinner />;
  if (metrics.error) return <ErrorBox message={metrics.error} />;

  const filtered = filterByCategory(metrics.data ?? [], category);
  const healthMap = Object.fromEntries((health.data ?? []).map((h) => [h.technology, h]));

  // If one is selected, show it; else show all overlapping
  const selectedMetrics = selected ? filtered.filter((m) => m.technology === selected) : filtered;

  // Build combined radar data with all techs as separate series
  const axes = ["Stars Growth", "Contributor Growth", "Commit Activity", "Issue Resolution", "SO Growth", "HN Mentions", "Discussion"];
  const radarData = axes.map((axis) => {
    const point: Record<string, any> = { axis };
    selectedMetrics.forEach((m) => {
      const data = buildRadarData(m);
      const match = data.find((d) => d.axis === axis);
      point[m.technology] = match?.value ?? 0;
    });
    return point;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tech Radar</h1>
          <p className="text-sm text-gray-500">Multi-dimensional technology comparison</p>
        </div>
        <CategoryFilter value={category} onChange={setCategory} />
      </div>

      {/* Tech selector */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelected(null)}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            !selected ? "bg-brand-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
          }`}
        >
          All
        </button>
        {filtered.map((m, i) => (
          <button
            key={m.technology}
            onClick={() => setSelected(m.technology === selected ? null : m.technology)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              selected === m.technology ? "bg-brand-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
            {m.technology}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Radar chart */}
        <Card title="Radar Visualization" className="lg:col-span-2">
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fill: "#6b7280", fontSize: 10 }}
                  axisLine={false}
                />
                {selectedMetrics.map((m, i) => (
                  <Radar
                    key={m.technology}
                    name={m.technology}
                    dataKey={m.technology}
                    stroke={COLORS[filtered.findIndex((f) => f.technology === m.technology) % COLORS.length]}
                    fill={COLORS[filtered.findIndex((f) => f.technology === m.technology) % COLORS.length]}
                    fillOpacity={0.15}
                    strokeWidth={2}
                  />
                ))}
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Legend / details */}
        <Card title="Technology Details">
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filtered.map((m, i) => {
              const h = healthMap[m.technology];
              return (
                <button
                  key={m.technology}
                  onClick={() => setSelected(m.technology === selected ? null : m.technology)}
                  className={`w-full text-left rounded-lg border px-4 py-3 transition-colors ${
                    selected === m.technology
                      ? "border-brand-500/50 bg-brand-600/10"
                      : "border-gray-800 bg-gray-800/30 hover:bg-gray-800/60"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                    <span className="font-medium text-sm">{m.technology}</span>
                    {h && (
                      <span
                        className={`ml-auto rounded px-2 py-0.5 text-[10px] font-semibold ${
                          h.risk_level === "Low"
                            ? "bg-emerald-900/40 text-emerald-400"
                            : h.risk_level === "Medium"
                              ? "bg-amber-900/40 text-amber-400"
                              : "bg-orange-900/40 text-orange-400"
                        }`}
                      >
                        {h.health_score}/100
                      </span>
                    )}
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-[11px] text-gray-400">
                    <span>Momentum: {m.momentum_score.toFixed(3)}</span>
                    <span>Community: {m.community_score.toFixed(3)}</span>
                    <span>Activity: {m.activity_score.toFixed(3)}</span>
                    {h && <span>Risk: {h.risk_level}</span>}
                  </div>
                </button>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}
