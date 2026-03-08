import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RRadar,
  Treemap,
} from "recharts";
import { TrendingUp, AlertTriangle, Zap, Shield } from "lucide-react";

import Card from "../components/Card";
import CategoryFilter from "../components/CategoryFilter";
import { Spinner, ErrorBox } from "../components/StatusIndicators";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { filterByCategory } from "../utils/categories";
import type { TechCategory } from "../types";

/* ---------- tiny stat card ---------- */
function Stat({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-gray-800 bg-gray-900/60 px-4 py-3">
      <div className={`rounded-lg p-2 ${color}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-lg font-semibold">{value}</p>
      </div>
    </div>
  );
}

/* ---------- custom tooltip ---------- */
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs shadow-xl">
      <p className="font-medium text-gray-200 mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {typeof p.value === "number" ? p.value.toFixed(3) : p.value}
        </p>
      ))}
    </div>
  );
}

/* ============ Page ============ */
export default function DashboardPage() {
  const [category, setCategory] = useState<TechCategory>("all");

  const metrics = useFetch(() => api.metricsLatest(), []);
  const health = useFetch(() => api.health(), []);
  const emerging = useFetch(() => api.emerging(), []);
  const trends = useFetch(() => api.trends(), []);

  const loading = metrics.loading || health.loading || emerging.loading || trends.loading;
  const error = metrics.error || health.error || emerging.error || trends.error;

  if (loading) return <Spinner />;
  if (error) return <ErrorBox message={error} />;

  const filteredMetrics = filterByCategory(metrics.data ?? [], category);
  const filteredHealth = filterByCategory(health.data ?? [], category);
  const filteredEmerging = filterByCategory(emerging.data ?? [], category);
  const filteredTrends = filterByCategory(trends.data ?? [], category);

  // Stat summaries
  const avgHealth =
    filteredHealth.length > 0
      ? Math.round(filteredHealth.reduce((a, h) => a + h.health_score, 0) / filteredHealth.length)
      : 0;
  const emergingCount = filteredEmerging.length;
  const warningCount = filteredTrends.filter((t) => t.severity === "warning").length;
  const growthCount = filteredTrends.filter((t) => t.category === "growth").length;

  // Momentum bar chart data
  const momentumData = filteredMetrics.map((m) => ({
    name: m.technology,
    momentum: m.momentum_score,
    community: m.community_score,
    activity: m.activity_score,
  }));

  // Community heatmap as treemap
  const heatmapData = filteredMetrics.map((m) => ({
    name: m.technology,
    size: Math.max(m.stackoverflow_growth + m.hn_mentions_growth + m.discussion_velocity, 0.01),
    fill:
      m.momentum_score > 0.5
        ? "#22c55e"
        : m.momentum_score > 0.3
          ? "#3b82f6"
          : m.momentum_score > 0.15
            ? "#f59e0b"
            : "#6b7280",
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-gray-500">Developer ecosystem overview</p>
        </div>
        <CategoryFilter value={category} onChange={setCategory} />
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Avg Health Score" value={`${avgHealth}/100`} icon={Shield} color="bg-emerald-900/40 text-emerald-400" />
        <Stat label="Emerging Techs" value={emergingCount} icon={Zap} color="bg-blue-900/40 text-blue-400" />
        <Stat label="Growth Signals" value={growthCount} icon={TrendingUp} color="bg-purple-900/40 text-purple-400" />
        <Stat label="Risk Warnings" value={warningCount} icon={AlertTriangle} color="bg-amber-900/40 text-amber-400" />
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Momentum Chart */}
        <Card title="Technology Momentum" subtitle="Composite score breakdown">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={momentumData} barGap={4}>
                <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="momentum" name="Momentum" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="community" name="Community" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="activity" name="Activity" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Community Activity Heatmap */}
        <Card title="Community Activity Heatmap" subtitle="Sized by discussion volume, colored by momentum">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={heatmapData}
                dataKey="size"
                aspectRatio={4 / 3}
                stroke="#1f2937"
                content={({ x, y, width, height, name, fill }: any) => (
                  <g>
                    <rect x={x} y={y} width={width} height={height} fill={fill} rx={6} opacity={0.85} />
                    {width > 50 && height > 25 && (
                      <text x={x + width / 2} y={y + height / 2} textAnchor="middle" dominantBaseline="central" fill="#fff" fontSize={12} fontWeight={600}>
                        {name}
                      </text>
                    )}
                  </g>
                )}
              />
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Bottom row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Emerging Tech List */}
        <Card title="Emerging Tech Radar" subtitle={`Top ${filteredEmerging.length} technologies`}>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {filteredEmerging.map((tech) => (
              <div key={tech.technology} className="flex items-start gap-3 rounded-lg bg-gray-800/40 px-4 py-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-600/20 text-xs font-bold text-brand-400">
                  {tech.rank}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{tech.technology}</span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                        tech.trend_direction === "up"
                          ? "bg-emerald-900/40 text-emerald-400"
                          : tech.trend_direction === "down"
                            ? "bg-red-900/40 text-red-400"
                            : "bg-gray-700 text-gray-400"
                      }`}
                    >
                      {tech.trend_direction}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Momentum: {tech.momentum_score.toFixed(3)} &middot; Growth: {tech.predicted_growth.toFixed(3)}
                  </p>
                  {tech.signals.length > 0 && (
                    <ul className="mt-1.5 space-y-0.5">
                      {tech.signals.map((s, i) => (
                        <li key={i} className="text-[11px] text-gray-400">
                          • {s}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            ))}
            {filteredEmerging.length === 0 && <p className="text-sm text-gray-500">No emerging techs in this category.</p>}
          </div>
        </Card>

        {/* Health Table */}
        <Card title="Repo Health Overview" subtitle="Score out of 100">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                  <th className="pb-2">Technology</th>
                  <th className="pb-2 text-center">Score</th>
                  <th className="pb-2 text-center">Risk</th>
                  <th className="pb-2 text-right">Maintainer</th>
                </tr>
              </thead>
              <tbody>
                {filteredHealth.map((h) => (
                  <tr key={h.technology} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2.5 font-medium">{h.technology}</td>
                    <td className="py-2.5 text-center">
                      <span className="font-semibold">{h.health_score}</span>
                      <span className="text-gray-500">/100</span>
                    </td>
                    <td className="py-2.5 text-center">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium ${
                          h.risk_level === "Low"
                            ? "bg-emerald-900/40 text-emerald-400"
                            : h.risk_level === "Medium"
                              ? "bg-amber-900/40 text-amber-400"
                              : h.risk_level === "High"
                                ? "bg-orange-900/40 text-orange-400"
                                : "bg-red-900/40 text-red-400"
                        }`}
                      >
                        {h.risk_level}
                      </span>
                    </td>
                    <td className="py-2.5 text-right text-gray-400">{h.maintainer_activity.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
