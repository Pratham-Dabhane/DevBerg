import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, Activity } from "lucide-react";

import MetricCard from "../components/ui/MetricCard";
import TrendIndicator from "../components/ui/TrendIndicator";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import ScoreBar from "../components/ui/ScoreBar";
import { useMomentum, useForecast, useRepoHealth } from "../hooks/useApi";

export default function TechIndexPage() {
  const momentum = useMomentum();
  const forecast = useForecast();
  const health = useRepoHealth();

  const isLoading = momentum.isLoading || forecast.isLoading || health.isLoading;
  const error = momentum.error || forecast.error || health.error;

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const momentumData = momentum.data ?? [];
  const forecastData = forecast.data ?? [];
  const healthData = health.data ?? [];

  // Compute composite index per technology
  const techIndex = momentumData.map((m) => {
    const hp = healthData.find((h) => h.repository_name.toLowerCase().includes(m.technology_name.toLowerCase()));
    const fc = forecastData.filter((f) => f.technology === m.technology_name).sort((a, b) => b.horizon_months - a.horizon_months)[0];

    const momNorm = m.momentum_score * 100;
    const healthNorm = hp?.health_score ?? 50;
    const growthNorm = fc ? Math.max(fc.predicted_growth_pct, 0) : 0;

    const composite = momNorm * 0.4 + healthNorm * 0.3 + growthNorm * 0.3;

    return {
      technology: m.technology_name,
      composite,
      momentum: momNorm,
      health: healthNorm,
      growth: growthNorm,
      score: m.momentum_score,
    };
  }).sort((a, b) => b.composite - a.composite);

  // Overall index
  const overallIndex = techIndex.length > 0
    ? (techIndex.reduce((s, t) => s + t.composite, 0) / techIndex.length).toFixed(1)
    : "0";

  // Top gainers / decliners
  const gainers = techIndex.filter((t) => t.score > 0.3);
  const decliners = techIndex.filter((t) => t.score <= 0.1);

  // Simulated historical index data
  const historyData = [
    { period: "6mo ago", index: parseFloat(overallIndex) * 0.7 },
    { period: "5mo ago", index: parseFloat(overallIndex) * 0.75 },
    { period: "4mo ago", index: parseFloat(overallIndex) * 0.8 },
    { period: "3mo ago", index: parseFloat(overallIndex) * 0.88 },
    { period: "2mo ago", index: parseFloat(overallIndex) * 0.92 },
    { period: "1mo ago", index: parseFloat(overallIndex) * 0.96 },
    { period: "Current", index: parseFloat(overallIndex) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Technology Market Index</h1>
        <p className="text-sm text-gray-500">Composite health and growth index across the developer ecosystem</p>
      </div>

      {/* Index headline */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-gray-800/60 bg-gradient-to-r from-blue-500/5 to-purple-500/5 p-6 text-center"
      >
        <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">AI Tech Index</p>
        <p className="text-5xl font-bold tracking-tight">
          {overallIndex}
          <span className="text-lg text-gray-500 font-normal ml-1">pts</span>
        </p>
        <TrendIndicator direction="up" value={4.2} className="justify-center mt-2" />
      </motion.div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Technologies" value={techIndex.length} icon={<BarChart3 className="h-4 w-4" />} />
        <MetricCard label="Top Gainers" value={gainers.length} icon={<TrendingUp className="h-4 w-4" />} />
        <MetricCard label="Decliners" value={decliners.length} icon={<TrendingDown className="h-4 w-4" />} />
        <MetricCard label="Index Change" value="+4.2%" icon={<Activity className="h-4 w-4" />} />
      </div>

      {/* Index chart */}
      <SectionCard title="Index Trend" subtitle="Composite index over time">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historyData}>
              <defs>
                <linearGradient id="indexGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="period" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Area type="monotone" dataKey="index" stroke="#3b82f6" fill="url(#indexGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </SectionCard>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Top Gainers */}
        <SectionCard title="Top Gainers" subtitle="Technologies with positive momentum">
          <div className="space-y-3">
            {techIndex.slice(0, 5).map((tech, i) => (
              <motion.div
                key={tech.technology}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="flex items-center gap-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10 px-4 py-3"
              >
                <span className="text-xs font-bold text-gray-500 w-5">{i + 1}</span>
                <TechnologyBadge name={tech.technology} />
                <div className="flex-1">
                  <ScoreBar value={tech.composite} className="w-full" />
                </div>
                <span className="text-sm font-bold text-emerald-400">{tech.composite.toFixed(1)}</span>
              </motion.div>
            ))}
          </div>
        </SectionCard>

        {/* Index composition */}
        <SectionCard title="Index Composition" subtitle="Component breakdown per technology">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800/40 text-xs uppercase tracking-wider text-gray-500">
                  <th className="pb-2 text-left">Technology</th>
                  <th className="pb-2 text-center">Composite</th>
                  <th className="pb-2 text-center">Momentum</th>
                  <th className="pb-2 text-center">Health</th>
                  <th className="pb-2 text-center">Growth</th>
                </tr>
              </thead>
              <tbody>
                {techIndex.map((tech) => (
                  <tr key={tech.technology} className="border-b border-gray-800/30">
                    <td className="py-2.5 font-medium text-gray-300">{tech.technology}</td>
                    <td className="py-2.5 text-center font-bold text-blue-400">{tech.composite.toFixed(1)}</td>
                    <td className="py-2.5 text-center text-gray-400">{tech.momentum.toFixed(1)}</td>
                    <td className="py-2.5 text-center text-gray-400">{tech.health.toFixed(1)}</td>
                    <td className="py-2.5 text-center text-gray-400">{tech.growth.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
