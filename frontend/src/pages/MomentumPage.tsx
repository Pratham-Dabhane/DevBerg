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
} from "recharts";
import { motion } from "framer-motion";
import { Flame } from "lucide-react";

import { SectionCard, ChartTooltip, PageSpinner, PageError } from "../components/ui/PageShell";
import TrendIndicator from "../components/ui/TrendIndicator";
import { useMomentum } from "../hooks/useApi";

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e", "#f59e0b"];

const CATEGORY_MAP: Record<string, string> = {
  FastAPI: "Backend",
  LangChain: "AI",
  Rust: "Languages",
  Bun: "Languages",
  Qdrant: "Database",
};

export default function MomentumPage() {
  const { data, isLoading, error } = useMomentum();
  const [minScore, setMinScore] = useState(0);
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [sortCol, setSortCol] = useState<"momentum_score" | "stars_growth" | "contributors_growth">("momentum_score");
  const [sortAsc, setSortAsc] = useState(false);

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const items = (data ?? [])
    .filter((m) => m.momentum_score >= minScore)
    .filter((m) => categoryFilter === "All" || CATEGORY_MAP[m.technology_name] === categoryFilter)
    .sort((a, b) => {
      const diff = a[sortCol] - b[sortCol];
      return sortAsc ? diff : -diff;
    });

  const chartData = items.map((m) => ({
    name: m.technology_name,
    score: m.momentum_score,
  })).sort((a, b) => b.score - a.score);

  function toggleSort(col: typeof sortCol) {
    if (sortCol === col) setSortAsc(!sortAsc);
    else { setSortCol(col); setSortAsc(false); }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Momentum Intelligence</h1>
        <p className="text-sm text-gray-500">Technology momentum scoring and velocity analysis</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Category:</span>
          {["All", "AI", "Backend", "Languages", "Database"].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                categoryFilter === cat
                  ? "bg-blue-500/15 text-blue-400"
                  : "bg-gray-800/50 text-gray-500 hover:text-gray-300"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-gray-500">Min score:</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={minScore}
            onChange={(e) => setMinScore(parseFloat(e.target.value))}
            className="w-24 accent-blue-500"
          />
          <span className="text-xs text-gray-400 w-8">{minScore.toFixed(2)}</span>
        </div>
      </div>

      {/* Momentum chart */}
      <SectionCard title="Momentum Rankings" subtitle="Sorted by composite momentum score">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" barSize={18}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} tickLine={false} width={90} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="score" name="Momentum Score" radius={[0, 6, 6, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </SectionCard>

      {/* Table */}
      <SectionCard title="Momentum Details" subtitle="Click column headers to sort">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800/40 text-xs uppercase tracking-wider text-gray-500">
                <th className="pb-2 text-left">Technology</th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("momentum_score")}>
                  Momentum {sortCol === "momentum_score" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("stars_growth")}>
                  Stars Growth {sortCol === "stars_growth" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("contributors_growth")}>
                  Contributor Growth {sortCol === "contributors_growth" && (sortAsc ? "↑" : "↓")}
                </th>
                <th className="pb-2 text-center hidden md:table-cell">SO Growth</th>
                <th className="pb-2 text-center hidden md:table-cell">HN Mentions</th>
                <th className="pb-2 text-center hidden lg:table-cell">Commit Activity</th>
                <th className="pb-2 text-center">Trend</th>
              </tr>
            </thead>
            <tbody>
              {items.map((m, i) => (
                <motion.tr
                  key={m.technology_name}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors"
                >
                  <td className="py-3 font-medium flex items-center gap-2">
                    {m.technology_name}
                    {m.momentum_score > 0.5 && (
                      <span className="text-orange-400" title="Fast growing">
                        <Flame className="h-3.5 w-3.5" />
                      </span>
                    )}
                  </td>
                  <td className="py-3 text-center">
                    <span className={`font-bold ${m.momentum_score > 0.5 ? "text-emerald-400" : m.momentum_score > 0.2 ? "text-blue-400" : "text-gray-400"}`}>
                      {m.momentum_score.toFixed(3)}
                    </span>
                  </td>
                  <td className="py-3 text-center text-gray-300">{m.stars_growth.toFixed(3)}</td>
                  <td className="py-3 text-center text-gray-300">{m.contributors_growth.toFixed(3)}</td>
                  <td className="py-3 text-center text-gray-400 hidden md:table-cell">{m.stackoverflow_growth.toFixed(3)}</td>
                  <td className="py-3 text-center text-gray-400 hidden md:table-cell">{m.hn_mentions.toFixed(3)}</td>
                  <td className="py-3 text-center text-gray-400 hidden lg:table-cell">{m.commit_activity.toFixed(3)}</td>
                  <td className="py-3 text-center">
                    <TrendIndicator direction={m.momentum_score > 0.3 ? "up" : m.momentum_score > 0.1 ? "stable" : "down"} />
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}
