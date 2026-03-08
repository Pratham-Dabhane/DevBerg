import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import Card from "../components/Card";
import CategoryFilter from "../components/CategoryFilter";
import { Spinner, ErrorBox } from "../components/StatusIndicators";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { filterByCategory } from "../utils/categories";
import type { TechCategory } from "../types";

function ScoreBar({ value, max = 25 }: { value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="h-1.5 w-full rounded-full bg-gray-800">
      <div
        className={`h-1.5 rounded-full transition-all ${
          pct >= 70 ? "bg-emerald-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500"
        }`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default function RepoHealthPage() {
  const [category, setCategory] = useState<TechCategory>("all");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [sortCol, setSortCol] = useState<"health_score" | "maintainer_activity" | "risk_level">("health_score");
  const [sortAsc, setSortAsc] = useState(false);

  const health = useFetch(() => api.health(), []);
  const risks = useFetch(() => api.risks(), []);

  if (health.loading) return <Spinner />;
  if (health.error) return <ErrorBox message={health.error} />;

  const filtered = filterByCategory(health.data ?? [], category);
  const riskMap = (risks.data ?? []).reduce<Record<string, string[]>>((acc, r) => {
    (acc[r.technology] ??= []).push(r.message);
    return acc;
  }, {});

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    let diff = 0;
    if (sortCol === "health_score") diff = a.health_score - b.health_score;
    else if (sortCol === "maintainer_activity") diff = a.maintainer_activity - b.maintainer_activity;
    else {
      const order = { Low: 0, Medium: 1, High: 2, Critical: 3 };
      diff = (order[a.risk_level] ?? 4) - (order[b.risk_level] ?? 4);
    }
    return sortAsc ? diff : -diff;
  });

  function toggleSort(col: typeof sortCol) {
    if (sortCol === col) setSortAsc(!sortAsc);
    else {
      setSortCol(col);
      setSortAsc(false);
    }
  }

  const SortIcon = ({ col }: { col: typeof sortCol }) =>
    sortCol === col ? (
      sortAsc ? <ChevronUp className="inline h-3 w-3" /> : <ChevronDown className="inline h-3 w-3" />
    ) : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Repository Health</h1>
          <p className="text-sm text-gray-500">Per-technology health breakdown</p>
        </div>
        <CategoryFilter value={category} onChange={setCategory} />
      </div>

      <Card title="Health Scores" subtitle="Click a row to expand details">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                <th className="pb-2">Technology</th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("health_score")}>
                  Score <SortIcon col="health_score" />
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("risk_level")}>
                  Risk <SortIcon col="risk_level" />
                </th>
                <th className="pb-2 text-center cursor-pointer select-none" onClick={() => toggleSort("maintainer_activity")}>
                  Maintainer <SortIcon col="maintainer_activity" />
                </th>
                <th className="pb-2 text-center hidden sm:table-cell">Release</th>
                <th className="pb-2 text-center hidden sm:table-cell">Issues</th>
                <th className="pb-2 text-center hidden sm:table-cell">Contributors</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((h) => {
                const isExpanded = expanded === h.technology;
                return (
                  <>
                    <tr
                      key={h.technology}
                      onClick={() => setExpanded(isExpanded ? null : h.technology)}
                      className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer"
                    >
                      <td className="py-3 font-medium">{h.technology}</td>
                      <td className="py-3 text-center">
                        <span
                          className={`text-lg font-bold ${
                            h.health_score >= 75
                              ? "text-emerald-400"
                              : h.health_score >= 50
                                ? "text-amber-400"
                                : "text-red-400"
                          }`}
                        >
                          {h.health_score}
                        </span>
                        <span className="text-gray-500 text-xs">/100</span>
                      </td>
                      <td className="py-3 text-center">
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
                      <td className="py-3 text-center text-gray-300">{h.maintainer_activity.toFixed(1)}</td>
                      <td className="py-3 text-center text-gray-300 hidden sm:table-cell">{h.release_frequency.toFixed(1)}</td>
                      <td className="py-3 text-center text-gray-300 hidden sm:table-cell">{h.issue_resolution_speed.toFixed(1)}</td>
                      <td className="py-3 text-center text-gray-300 hidden sm:table-cell">{h.contributor_diversity.toFixed(1)}</td>
                    </tr>
                    {isExpanded && (
                      <tr key={`${h.technology}-details`} className="border-b border-gray-800/50">
                        <td colSpan={7} className="px-4 py-4">
                          <div className="grid gap-4 md:grid-cols-2">
                            {/* Score breakdown bars */}
                            <div className="space-y-3">
                              <h4 className="text-xs uppercase tracking-wider text-gray-500">Score Breakdown</h4>
                              {[
                                { label: "Maintainer Activity", value: h.maintainer_activity },
                                { label: "Release Frequency", value: h.release_frequency },
                                { label: "Issue Resolution", value: h.issue_resolution_speed },
                                { label: "Contributor Diversity", value: h.contributor_diversity },
                              ].map((item) => (
                                <div key={item.label}>
                                  <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-400">{item.label}</span>
                                    <span className="text-gray-300">{item.value.toFixed(1)}/25</span>
                                  </div>
                                  <ScoreBar value={item.value} />
                                </div>
                              ))}
                            </div>
                            {/* Insights */}
                            <div className="space-y-2">
                              <h4 className="text-xs uppercase tracking-wider text-gray-500">Insights</h4>
                              {h.insights.map((insight, i) => (
                                <p key={i} className="text-xs text-gray-400">• {insight}</p>
                              ))}
                              {(riskMap[h.technology] ?? []).map((msg, i) => (
                                <p key={`risk-${i}`} className="text-xs text-amber-400">⚠ {msg}</p>
                              ))}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
