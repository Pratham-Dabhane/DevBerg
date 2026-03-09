import { useState } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { motion } from "framer-motion";
import { Swords, Trophy } from "lucide-react";

import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { useMomentum, useRepoHealth, useForecast } from "../hooks/useApi";

export default function BattlesPage() {
  const momentum = useMomentum();
  const health = useRepoHealth();
  const forecast = useForecast();

  const [techA, setTechA] = useState<string>("");
  const [techB, setTechB] = useState<string>("");

  const isLoading = momentum.isLoading || health.isLoading || forecast.isLoading;
  const error = momentum.error || health.error || forecast.error;

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const momentumData = momentum.data ?? [];
  const healthData = health.data ?? [];
  const forecastData = forecast.data ?? [];

  const availableTechs = momentumData.map((m) => m.technology_name);

  if (!techA && availableTechs.length > 0) setTechA(availableTechs[0]);
  if (!techB && availableTechs.length > 1) setTechB(availableTechs[1]);

  const getStats = (tech: string) => {
    const mom = momentumData.find((m) => m.technology_name === tech);
    const hp = healthData.find((h) => h.repository_name.toLowerCase().includes(tech.toLowerCase()));
    const fc = forecastData.filter((f) => f.technology === tech).sort((a, b) => b.horizon_months - a.horizon_months)[0];

    return {
      momentum: mom?.momentum_score ?? 0,
      stars: mom?.stars_growth ?? 0,
      contributors: mom?.contributors_growth ?? 0,
      healthScore: hp?.health_score ?? 0,
      forecastGrowth: fc?.predicted_growth_pct ?? 0,
      commits: mom?.commit_activity ?? 0,
    };
  };

  const statsA = getStats(techA);
  const statsB = getStats(techB);

  // Determine winner
  let winsA = 0, winsB = 0;
  if (statsA.momentum > statsB.momentum) winsA++; else if (statsB.momentum > statsA.momentum) winsB++;
  if (statsA.healthScore > statsB.healthScore) winsA++; else if (statsB.healthScore > statsA.healthScore) winsB++;
  if (statsA.forecastGrowth > statsB.forecastGrowth) winsA++; else if (statsB.forecastGrowth > statsA.forecastGrowth) winsB++;
  if (statsA.contributors > statsB.contributors) winsA++; else if (statsB.contributors > statsA.contributors) winsB++;
  const winner = winsA > winsB ? techA : winsB > winsA ? techB : null;

  const radarData = [
    { axis: "Momentum", a: statsA.momentum * 100, b: statsB.momentum * 100 },
    { axis: "Health", a: statsA.healthScore, b: statsB.healthScore },
    { axis: "Growth", a: Math.max(statsA.forecastGrowth, 0), b: Math.max(statsB.forecastGrowth, 0) },
    { axis: "Stars", a: statsA.stars * 100, b: statsB.stars * 100 },
    { axis: "Contributors", a: statsA.contributors * 100, b: statsB.contributors * 100 },
    { axis: "Commits", a: statsA.commits * 100, b: statsB.commits * 100 },
  ];

  const comparisonData = [
    { metric: "Momentum", [techA]: statsA.momentum, [techB]: statsB.momentum },
    { metric: "Health", [techA]: statsA.healthScore, [techB]: statsB.healthScore },
    { metric: "Forecast", [techA]: statsA.forecastGrowth, [techB]: statsB.forecastGrowth },
    { metric: "Stars Vel.", [techA]: statsA.stars, [techB]: statsB.stars },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Tech Battles</h1>
        <p className="text-sm text-gray-500">Head-to-head technology comparison</p>
      </div>

      {/* Selectors */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <select
          value={techA}
          onChange={(e) => setTechA(e.target.value)}
          className="w-full sm:w-48 rounded-lg border border-gray-800/60 bg-gray-900/50 px-3 py-2 text-sm text-gray-300 outline-none focus:border-blue-500/50"
        >
          {availableTechs.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <div className="flex items-center gap-2">
          <Swords className="h-5 w-5 text-amber-400" />
          <span className="text-sm font-semibold text-gray-400">VS</span>
        </div>

        <select
          value={techB}
          onChange={(e) => setTechB(e.target.value)}
          className="w-full sm:w-48 rounded-lg border border-gray-800/60 bg-gray-900/50 px-3 py-2 text-sm text-gray-300 outline-none focus:border-blue-500/50"
        >
          {availableTechs.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* Winner banner */}
      {winner && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center justify-center gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 py-4"
        >
          <Trophy className="h-5 w-5 text-amber-400" />
          <span className="text-sm font-semibold">
            <span className="text-amber-400">{winner}</span>
            <span className="text-gray-400"> wins {Math.max(winsA, winsB)}-{Math.min(winsA, winsB)}</span>
          </span>
        </motion.div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Radar comparison */}
        <SectionCard title="Multi-Dimensional Comparison">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                <PolarRadiusAxis tick={false} axisLine={false} />
                <Radar name={techA} dataKey="a" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} />
                <Radar name={techB} dataKey="b" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} strokeWidth={2} />
                <Tooltip content={<ChartTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2">
            <div className="flex items-center gap-2 text-xs">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              <span className="text-gray-400">{techA}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              <span className="text-gray-400">{techB}</span>
            </div>
          </div>
        </SectionCard>

        {/* Bar comparison */}
        <SectionCard title="Side-by-Side Metrics">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="metric" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey={techA} name={techA} fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey={techB} name={techB} fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>
      </div>

      {/* Detailed stats */}
      <SectionCard title="Detailed Comparison">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800/40 text-xs uppercase tracking-wider text-gray-500">
              <th className="pb-2 text-left">Metric</th>
              <th className="pb-2 text-center">{techA}</th>
              <th className="pb-2 text-center">{techB}</th>
              <th className="pb-2 text-center">Winner</th>
            </tr>
          </thead>
          <tbody>
            {[
              { label: "Momentum Score", a: statsA.momentum, b: statsB.momentum },
              { label: "Health Score", a: statsA.healthScore, b: statsB.healthScore },
              { label: "Forecast Growth", a: statsA.forecastGrowth, b: statsB.forecastGrowth },
              { label: "Stars Velocity", a: statsA.stars, b: statsB.stars },
              { label: "Contributor Velocity", a: statsA.contributors, b: statsB.contributors },
              { label: "Commit Velocity", a: statsA.commits, b: statsB.commits },
            ].map((row) => {
              const w = row.a > row.b ? techA : row.b > row.a ? techB : "Tie";
              return (
                <tr key={row.label} className="border-b border-gray-800/30">
                  <td className="py-3 text-gray-400">{row.label}</td>
                  <td className={`py-3 text-center font-medium ${w === techA ? "text-blue-400" : "text-gray-300"}`}>
                    {row.a.toFixed(3)}
                  </td>
                  <td className={`py-3 text-center font-medium ${w === techB ? "text-amber-400" : "text-gray-300"}`}>
                    {row.b.toFixed(3)}
                  </td>
                  <td className="py-3 text-center">
                    {w === "Tie" ? (
                      <span className="text-xs text-gray-500">Tie</span>
                    ) : (
                      <TechnologyBadge name={w} />
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </SectionCard>
    </div>
  );
}
