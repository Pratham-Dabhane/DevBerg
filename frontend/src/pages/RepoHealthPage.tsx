import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

import MetricCard from "../components/ui/MetricCard";
import ScoreBar from "../components/ui/ScoreBar";
import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import { useRepoHealth } from "../hooks/useApi";



const riskColors: Record<string, string> = {
  Low: "bg-dp-accent/10 text-dp-accent",
  Moderate: "bg-dp-secondary/10 text-dp-secondary",
  High: "bg-dp-warning/10 text-dp-warning",
  Critical: "bg-dp-danger/10 text-dp-danger",
};

export default function RepoHealthPage() {
  const { data, isLoading, error } = useRepoHealth();
  const [selected, setSelected] = useState<string | null>(null);
  const [sortCol, setSortCol] = useState<"health_score" | "maintainer_activity" | "risk_level">("health_score");
  const [sortAsc, setSortAsc] = useState(false);

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const items = data ?? [];
  const sorted = [...items].sort((a, b) => {
    if (sortCol === "risk_level") {
      const order: Record<string, number> = { Low: 0, Moderate: 1, High: 2, Critical: 3 };
      return sortAsc ? (order[a.risk_level] ?? 4) - (order[b.risk_level] ?? 4) : (order[b.risk_level] ?? 4) - (order[a.risk_level] ?? 4);
    }
    const diff = (a[sortCol] as number) - (b[sortCol] as number);
    return sortAsc ? diff : -diff;
  });

  const avgHealth = items.length > 0 ? Math.round(items.reduce((s, h) => s + h.health_score, 0) / items.length) : 0;
  const criticalCount = items.filter((h) => h.risk_level === "Critical").length;
  const selectedItem = items.find((h) => h.repository_name === selected);

  function toggleSort(col: typeof sortCol) {
    if (sortCol === col) setSortAsc(!sortAsc);
    else { setSortCol(col); setSortAsc(false); }
  }

  const chartData = sorted.map((h) => ({
    name: h.repository_name.split("/").pop() ?? h.repository_name,
    score: h.health_score,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Repository Health</h1>
        <p className="text-sm text-dp-text-3">Comprehensive health diagnostics for tracked repositories</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Avg Health" value={`${avgHealth}/100`} />
        <MetricCard label="Repositories" value={items.length} />
        <MetricCard label="Critical Risk" value={criticalCount} />
        <MetricCard
          label="Healthiest"
          value={items.length > 0 ? (items.reduce((a, b) => a.health_score > b.health_score ? a : b).repository_name.split("/").pop() ?? "") : "N/A"}
        />
      </div>

      {/* Health chart */}
      <SectionCard title="Health Score Comparison">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} barSize={24}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E1F27" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "#5A5A6E", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: "#3A3A4A", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="score" name="Health Score" radius={[4, 4, 0, 0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.score >= 70 ? "#6BE6C1" : d.score >= 40 ? "#FFB86C" : "#FF6B6B"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </SectionCard>

      {/* Table */}
      <SectionCard title="Repository Details" subtitle="Click a row for detailed diagnostics">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dp-border text-xs uppercase tracking-wider text-dp-text-3">
                <th className="pb-2 text-left">Repository</th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("health_score")}>
                  Score {sortCol === "health_score" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("risk_level")}>
                  Risk {sortCol === "risk_level" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("maintainer_activity")}>
                  Maintainer {sortCol === "maintainer_activity" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center hidden md:table-cell">Issue Speed</th>
                <th className="pb-2 text-center hidden md:table-cell">Contributors</th>
                <th className="pb-2 text-center hidden lg:table-cell">Releases</th>
                <th className="pb-2 text-center hidden lg:table-cell">Commits</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((h, i) => (
                <motion.tr
                  key={h.repository_name}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.03 }}
                  onClick={() => setSelected(selected === h.repository_name ? null : h.repository_name)}
                  className="border-b border-dp-border/50 hover:bg-dp-surface-2 cursor-pointer transition-colors"
                >
                  <td className="py-3 font-medium text-dp-text">{h.repository_name}</td>
                  <td className="py-3 text-center">
                    <span className={`text-lg font-bold ${h.health_score >= 70 ? "text-dp-accent" : h.health_score >= 40 ? "text-dp-warning" : "text-dp-danger"}`}>
                      {h.health_score.toFixed(1)}
                    </span>
                  </td>
                  <td className="py-3 text-center">
                    <span className={`rounded px-2 py-0.5 text-xs font-medium ${riskColors[h.risk_level] ?? riskColors.High}`}>
                      {h.risk_level}
                    </span>
                  </td>
                  <td className="py-3 text-center text-dp-text">{h.maintainer_activity.toFixed(1)}</td>
                  <td className="py-3 text-center text-dp-text-2 hidden md:table-cell">{h.issue_resolution_speed.toFixed(1)}</td>
                  <td className="py-3 text-center text-dp-text-2 hidden md:table-cell">{h.contributors}</td>
                  <td className="py-3 text-center text-dp-text-2 hidden lg:table-cell">{h.release_frequency.toFixed(1)}</td>
                  <td className="py-3 text-center text-dp-text-2 hidden lg:table-cell">{h.commit_frequency.toFixed(1)}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Detail modal */}
      <AnimatePresence>
        {selectedItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
            onClick={() => setSelected(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl rounded-xl border border-dp-border bg-dp-bg p-6 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-bold">{selectedItem.repository_name}</h2>
                  <span className={`rounded px-2 py-0.5 text-xs font-medium ${riskColors[selectedItem.risk_level] ?? riskColors.High}`}>
                    {selectedItem.risk_level} Risk
                  </span>
                </div>
                <button onClick={() => setSelected(null)} className="text-dp-text-3 hover:text-dp-text">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Health gauge */}
              <div className="text-center mb-6">
                <p className={`text-5xl font-bold ${selectedItem.health_score >= 70 ? "text-dp-accent" : selectedItem.health_score >= 40 ? "text-dp-warning" : "text-dp-danger"}`}>
                  {selectedItem.health_score.toFixed(1)}
                </p>
                <p className="text-xs text-dp-text-3 mt-1">Health Score / 100</p>
              </div>

              {/* Radar */}
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={[
                    { axis: "Maintainer", value: selectedItem.maintainer_activity },
                    { axis: "Issue Speed", value: selectedItem.issue_resolution_speed },
                    { axis: "Contributors", value: Math.min(selectedItem.contributors, 30) },
                    { axis: "Releases", value: selectedItem.release_frequency },
                    { axis: "Commits", value: selectedItem.commit_frequency },
                  ]}>
                    <PolarGrid stroke="#1E1F27" />
                    <PolarAngleAxis dataKey="axis" tick={{ fill: "#5A5A6E", fontSize: 11 }} />
                    <PolarRadiusAxis tick={false} axisLine={false} />
                    <Radar dataKey="value" stroke="#6BE6C1" fill="#6BE6C1" fillOpacity={0.15} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* Breakdowns */}
              <div className="grid grid-cols-2 gap-4 mt-4">
                {[
                  { label: "Maintainer Activity", value: selectedItem.maintainer_activity, max: 30 },
                  { label: "Issue Resolution", value: selectedItem.issue_resolution_speed, max: 25 },
                  { label: "Release Frequency", value: selectedItem.release_frequency, max: 15 },
                  { label: "Commit Frequency", value: selectedItem.commit_frequency, max: 10 },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-dp-text-2">{item.label}</span>
                      <span className="text-dp-text">{item.value.toFixed(1)}</span>
                    </div>
                    <ScoreBar value={item.value} max={item.max} />
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
