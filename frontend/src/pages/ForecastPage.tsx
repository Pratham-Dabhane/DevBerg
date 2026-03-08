import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  Cell,
} from "recharts";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

import Card from "../components/Card";
import CategoryFilter from "../components/CategoryFilter";
import { Spinner, ErrorBox } from "../components/StatusIndicators";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { filterByCategory } from "../utils/categories";
import type { TechCategory } from "../types";

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e", "#f59e0b"];

const TrendIcon = ({ dir }: { dir: string }) => {
  if (dir === "up") return <ArrowUpRight className="h-4 w-4 text-emerald-400" />;
  if (dir === "down") return <ArrowDownRight className="h-4 w-4 text-red-400" />;
  return <Minus className="h-4 w-4 text-gray-400" />;
};

export default function ForecastPage() {
  const [category, setCategory] = useState<TechCategory>("all");

  const predictions = useFetch(() => api.predictions(), []);
  const metrics = useFetch(() => api.metricsLatest(), []);

  if (predictions.loading || metrics.loading) return <Spinner />;
  if (predictions.error) return <ErrorBox message={predictions.error} />;

  const filteredPredictions = filterByCategory(predictions.data ?? [], category);
  const filteredMetrics = filterByCategory(metrics.data ?? [], category);

  // Predicted growth bar chart
  const growthData = filteredPredictions
    .map((p) => ({
      name: p.technology,
      predicted_growth: p.predicted_growth,
      confidence: p.confidence_score,
      trend: p.trend_direction,
    }))
    .sort((a, b) => b.predicted_growth - a.predicted_growth);

  // Confidence area data (simulate a timeline for visual effect)
  const confidenceData = filteredPredictions.map((p, i) => ({
    name: p.technology,
    confidence: Math.round(p.confidence_score * 100),
    momentum: Math.round(p.momentum_score * 100),
  }));

  // Forecast projection: for each tech, show current momentum vs predicted growth
  const comparisonData = filteredPredictions.map((p) => {
    const m = filteredMetrics.find((met) => met.technology === p.technology);
    return {
      name: p.technology,
      current: m ? Math.round(m.momentum_score * 100) : 0,
      predicted: Math.round(p.predicted_growth * 100),
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Forecast</h1>
          <p className="text-sm text-gray-500">Predicted technology adoption trends over the next 6 months</p>
        </div>
        <CategoryFilter value={category} onChange={setCategory} />
      </div>

      {/* Prediction cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {filteredPredictions.map((p) => (
          <div
            key={p.technology}
            className="rounded-xl border border-gray-800 bg-gray-900/60 p-4 space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-sm">{p.technology}</span>
              <TrendIcon dir={p.trend_direction} />
            </div>
            <p className="text-2xl font-bold">
              {(p.predicted_growth * 100).toFixed(1)}
              <span className="text-sm font-normal text-gray-500">%</span>
            </p>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span>Confidence: {(p.confidence_score * 100).toFixed(0)}%</span>
              <span>•</span>
              <span>{p.forecast_horizon_months}mo horizon</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-gray-800">
              <div
                className="h-1.5 rounded-full bg-brand-500 transition-all"
                style={{ width: `${Math.min(p.confidence_score * 100, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Predicted Growth Chart */}
        <Card title="Predicted Growth" subtitle="6-month forecast">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={growthData} layout="vertical" barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fill: "#6b7280", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={90}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(val: number) => `${(val * 100).toFixed(1)}%`}
                />
                <Bar dataKey="predicted_growth" name="Predicted Growth" radius={[0, 6, 6, 0]}>
                  {growthData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Current vs Predicted */}
        <Card title="Current Momentum vs Predicted Growth" subtitle="Where things are headed">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "#6b7280", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  unit="%"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(val: number) => `${val}%`}
                />
                <Bar dataKey="current" name="Current Momentum" fill="#6b7280" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predicted" name="Predicted Growth" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Confidence */}
      <Card title="Model Confidence" subtitle="Forecast reliability per technology">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={confidenceData}>
              <defs>
                <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="name"
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#6b7280", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                unit="%"
                domain={[0, 100]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #374151",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="confidence"
                name="Confidence"
                stroke="#3b82f6"
                fill="url(#confGrad)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="momentum"
                name="Momentum"
                stroke="#8b5cf6"
                fill="none"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
