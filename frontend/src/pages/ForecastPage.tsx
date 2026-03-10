import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { motion } from "framer-motion";
import { TrendingUp } from "lucide-react";

import MetricCard from "../components/ui/MetricCard";
import TrendIndicator from "../components/ui/TrendIndicator";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import { useStaggerReveal } from "../animations/useScrollReveal";
import ScoreBar from "../components/ui/ScoreBar";
import { useForecast } from "../hooks/useApi";

const COLORS = ["#6BE6C1", "#7C9BFF", "#A78BFA", "#F0B866", "#F87171"];

export default function ForecastPage() {
  const { data, isLoading, error } = useForecast();
  const [selectedTech, setSelectedTech] = useState<string | null>(null);
  const staggerRef = useStaggerReveal<HTMLDivElement>(":scope > *");

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const items = data ?? [];
  const techs = [...new Set(items.map((f) => f.technology))];

  // Group by tech with horizons
  const grouped = techs.map((tech) => {
    const forecasts = items.filter((f) => f.technology === tech).sort((a, b) => a.horizon_months - b.horizon_months);
    return { technology: tech, forecasts };
  });

  const filteredGroup = selectedTech
    ? grouped.filter((g) => g.technology === selectedTech)
    : grouped;

  // Summary: avg predicted growth, avg confidence
  const avgGrowth = items.length > 0
    ? (items.reduce((s, f) => s + f.predicted_growth_pct, 0) / items.length).toFixed(1)
    : "0";
  const avgConfidence = items.length > 0
    ? (items.reduce((s, f) => s + f.confidence_score, 0) / items.length * 100).toFixed(0)
    : "0";

  // Chart: predicted growth by tech (latest horizon)
  const latestForecasts = techs.map((tech) => {
    const latest = items.filter((f) => f.technology === tech).sort((a, b) => b.horizon_months - a.horizon_months)[0];
    return latest;
  }).filter(Boolean).sort((a, b) => b!.predicted_growth_pct - a!.predicted_growth_pct);

  const barData = latestForecasts.map((f) => ({
    name: f!.technology,
    growth: f!.predicted_growth_pct,
    confidence: f!.confidence_score * 100,
  }));

  // Multi-horizon area chart data
  const horizonData = [3, 6, 12].map((h) => {
    const row: Record<string, any> = { horizon: `${h}mo` };
    techs.forEach((tech) => {
      const f = items.find((i) => i.technology === tech && i.horizon_months === h);
      row[tech] = f ? f.predicted_growth_pct : null;
    });
    return row;
  });

  return (
    <div ref={staggerRef} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Technology Forecast</h1>
        <p className="text-sm text-dp-text-3">Multi-horizon growth predictions with ensemble modeling</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Technologies" value={techs.length} />
        <MetricCard label="Avg Growth" value={`${avgGrowth}%`} icon={<TrendingUp className="h-4 w-4" />} />
        <MetricCard label="Avg Confidence" value={`${avgConfidence}%`} />
        <MetricCard label="Forecasts" value={items.length} />
      </div>

      {/* Tech filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedTech(null)}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            !selectedTech ? "bg-dp-accent-dim text-dp-accent" : "bg-dp-surface text-dp-text-3 hover:text-dp-text-2"
          }`}
        >
          All
        </button>
        {techs.map((tech) => (
          <button
            key={tech}
            onClick={() => setSelectedTech(selectedTech === tech ? null : tech)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              selectedTech === tech ? "bg-dp-accent-dim text-dp-accent" : "bg-dp-surface text-dp-text-3 hover:text-dp-text-2"
            }`}
          >
            {tech}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Growth comparison */}
        <SectionCard title="Predicted Growth" subtitle="Longest horizon forecast">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <BarChart data={barData} layout="vertical" barSize={18}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" horizontal={false} />
                <XAxis type="number" tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
                <YAxis type="category" dataKey="name" tick={{ fill: "#5A5A6E", fontSize: 12 }} axisLine={false} tickLine={false} width={90} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="growth" name="Growth %" radius={[0, 6, 6, 0]}>
                  {barData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>

        {/* Multi-horizon area */}
        <SectionCard title="Growth Trajectories" subtitle="3, 6, and 12-month horizons">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <AreaChart data={horizonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" />
                <XAxis dataKey="horizon" tick={{ fill: "#5A5A6E", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip content={<ChartTooltip />} />
                {(selectedTech ? [selectedTech] : techs).map((tech, i) => (
                  <Area
                    key={tech}
                    type="monotone"
                    dataKey={tech}
                    stroke={COLORS[i % COLORS.length]}
                    fill={COLORS[i % COLORS.length]}
                    fillOpacity={0.1}
                    strokeWidth={2}
                    connectNulls
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>
      </div>

      {/* Forecast cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredGroup.map((g, gi) => (
          <motion.div
            key={g.technology}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: gi * 0.05 }}
            className="dp-card p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <TechnologyBadge name={g.technology} />
              <TrendIndicator direction={g.forecasts[0]?.trend_direction ?? "stable"} />
            </div>
            <div className="space-y-3">
              {g.forecasts.map((f) => (
                <div key={f.horizon_months} className="flex items-center gap-3">
                  <span className="text-xs text-dp-text-3 w-8">{f.horizon_months}mo</span>
                  <div className="flex-1">
                    <ScoreBar value={Math.min(Math.abs(f.predicted_growth_pct), 100)} />
                  </div>
                  <span className={`text-sm font-bold ${f.predicted_growth_pct >= 0 ? "text-dp-accent" : "text-dp-danger"}`}>
                    {f.predicted_growth_pct >= 0 ? "+" : ""}{f.predicted_growth_pct.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-3 flex items-center gap-2 text-[10px] text-dp-text-3">
              <span>Confidence: {(g.forecasts[0]?.confidence_score * 100).toFixed(0)}%</span>
              <span>·</span>
              <span>Models: {g.forecasts[0]?.model_used}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
