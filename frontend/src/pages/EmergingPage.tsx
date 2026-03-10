import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";
import { motion } from "framer-motion";
import { Flame, Zap, TrendingUp } from "lucide-react";

import MetricCard from "../components/ui/MetricCard";
import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import TrendIndicator from "../components/ui/TrendIndicator";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { useEmergingAnalytics, useMomentum } from "../hooks/useApi";
import { useStaggerReveal } from "../animations/useScrollReveal";

const COLORS = ["#F0B866", "#F59E0B", "#F87171", "#A78BFA", "#7C9BFF"];

export default function EmergingPage() {
  const { data, isLoading, error } = useEmergingAnalytics();
  const momentum = useMomentum();
  const staggerRef = useStaggerReveal<HTMLDivElement>(":scope > *");

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const items = (data ?? []).sort((a, b) => b.growth_spike_score - a.growth_spike_score);
  const momentumMap = Object.fromEntries((momentum.data ?? []).map((m) => [m.technology_name, m]));

  const chartData = items.map((e) => ({
    name: e.technology_name,
    spike: e.growth_spike_score,
  }));

  const maxSpike = items.length > 0 ? items[0].growth_spike_score : 0;
  const avgSpike = items.length > 0
    ? items.reduce((s, e) => s + e.growth_spike_score, 0) / items.length
    : 0;

  return (
    <div ref={staggerRef} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Emerging Technologies</h1>
        <p className="text-sm text-dp-text-3">Technologies with sudden growth spikes and anomalous patterns</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <MetricCard label="Emerging Detected" value={items.length} icon={<Flame className="h-4 w-4" />} />
        <MetricCard
          label="Max Growth Spike"
          value={maxSpike.toFixed(2)}
          icon={<Zap className="h-4 w-4" />}
        />
        <MetricCard
          label="Avg Growth Spike"
          value={avgSpike.toFixed(2)}
          icon={<TrendingUp className="h-4 w-4" />}
        />
      </div>

      {/* Growth spike chart */}
      <SectionCard title="Growth Spike Analysis" subtitle="Spike scores across technologies">
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <BarChart data={chartData} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "#5A5A6E", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="spike" name="Growth Spike" radius={[4, 4, 0, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </SectionCard>

      {/* Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((tech, i) => {
          const mom = momentumMap[tech.technology_name];
          return (
            <motion.div
              key={tech.technology_name}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl border border-dp-warning/15 bg-dp-warning/5 p-5 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <TechnologyBadge name={tech.technology_name} />
                <span className="rounded-full bg-dp-warning/15 px-2 py-0.5 text-[10px] font-medium text-dp-warning">
                  EMERGING
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-[10px] uppercase text-dp-text-3">Growth Spike</p>
                  <p className="font-bold text-lg">{tech.growth_spike_score.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase text-dp-text-3">Momentum</p>
                  <p className="font-bold text-lg">
                    {mom ? mom.momentum_score.toFixed(2) : "N/A"}
                  </p>
                </div>
              </div>
              {mom && (
                <div className="mt-3 flex items-center gap-2 text-xs text-dp-text-3">
                  <span>Contributor growth:</span>
                  <TrendIndicator direction={tech.growth_spike_score > 0 ? "up" : "stable"} value={mom.contributors_growth * 100} />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
