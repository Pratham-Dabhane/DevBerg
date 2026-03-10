import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
} from "recharts";
import { AlertTriangle, Zap, Shield, Activity } from "lucide-react";
import { motion } from "framer-motion";

import MetricCard from "../components/ui/MetricCard";
import InsightCard from "../components/ui/InsightCard";
import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import TrendIndicator from "../components/ui/TrendIndicator";
import { useMomentum, useEmergingAnalytics, useNLInsights, useRepoHealth } from "../hooks/useApi";
import { useStaggerReveal } from "../animations/useScrollReveal";



export default function DashboardPage() {
  const momentum = useMomentum();
  const emerging = useEmergingAnalytics();
  const insights = useNLInsights();
  const repoHealth = useRepoHealth();

  const staggerRef = useStaggerReveal<HTMLDivElement>(":scope > *");

  const isLoading = momentum.isLoading || emerging.isLoading || insights.isLoading || repoHealth.isLoading;
  const error = momentum.error || emerging.error || insights.error || repoHealth.error;

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const momentumData = momentum.data ?? [];
  const emergingData = emerging.data ?? [];
  const insightData = insights.data ?? [];
  const healthData = repoHealth.data ?? [];

  const avgMomentum = momentumData.length > 0
    ? (momentumData.reduce((s, m) => s + m.momentum_score, 0) / momentumData.length).toFixed(2)
    : "0";
  const emergingCount = emergingData.length;
  const avgHealth = healthData.length > 0
    ? Math.round(healthData.reduce((s, h) => s + h.health_score, 0) / healthData.length)
    : 0;
  const criticalInsights = insightData.filter((i) => i.severity === "critical").length;

  const chartData = momentumData.map((m) => ({
    name: m.technology_name,
    momentum: m.momentum_score,
    stars: m.stars_growth,
    contributors: m.contributors_growth,
  }));

  return (
    <div ref={staggerRef} className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-dp-text-3">Developer Ecosystem Intelligence Overview</p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          label="Avg Momentum"
          value={avgMomentum}
          icon={<Activity className="h-4 w-4" />}
        />
        <MetricCard
          label="Emerging Techs"
          value={emergingCount}
          icon={<Zap className="h-4 w-4" />}
        />
        <MetricCard
          label="Avg Repo Health"
          value={`${avgHealth}/100`}
          icon={<Shield className="h-4 w-4" />}
        />
        <MetricCard
          label="Critical Alerts"
          value={criticalInsights}
          icon={<AlertTriangle className="h-4 w-4" />}
        />
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Technology Momentum" subtitle="Score breakdown by technology">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <BarChart data={chartData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: "#5A5A6E", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="momentum" name="Momentum" fill="#6BE6C1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="stars" name="Stars Velocity" fill="#7C9BFF" radius={[4, 4, 0, 0]} />
                <Bar dataKey="contributors" name="Contributors" fill="#A78BFA" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>

        <SectionCard title="Growth Trends" subtitle="Momentum over technologies">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="momGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6BE6C1" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#6BE6C1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" />
                <XAxis dataKey="name" tick={{ fill: "#5A5A6E", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="momentum" stroke="#6BE6C1" fill="url(#momGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>
      </div>

      {/* Bottom: Top emerging + latest insights */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Top Emerging Technologies" subtitle="Highest growth spike scores">
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {emergingData
              .sort((a, b) => b.growth_spike_score - a.growth_spike_score)
              .slice(0, 5)
              .map((tech, i) => (
                <motion.div
                  key={tech.technology_name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center gap-3 rounded-lg bg-dp-surface border border-dp-border px-4 py-3"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-dp-accent-dim text-xs font-bold text-dp-accent">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{tech.technology_name}</p>
                    <p className="text-xs text-dp-text-3">
                      Growth spike: {tech.growth_spike_score.toFixed(2)}
                    </p>
                  </div>
                  <TrendIndicator direction="up" value={tech.growth_spike_score * 100} />
                </motion.div>
              ))}
            {emergingData.length === 0 && (
              <p className="text-sm text-dp-text-3 py-4 text-center">No emerging technologies detected</p>
            )}
          </div>
        </SectionCard>

        <SectionCard title="Latest Ecosystem Insights" subtitle="AI-generated intelligence">
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {insightData.slice(0, 6).map((insight, i) => (
              <InsightCard
                key={i}
                technology={insight.technology}
                severity={insight.severity}
                insight={insight.insight}
                category={insight.category}
              />
            ))}
            {insightData.length === 0 && (
              <p className="text-sm text-dp-text-3 py-4 text-center">No insights generated yet</p>
            )}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
