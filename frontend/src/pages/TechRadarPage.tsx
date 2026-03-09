import { useState } from "react";
import { motion } from "framer-motion";

import { SectionCard, PageSpinner, PageError } from "../components/ui/PageShell";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { useLifecycle } from "../hooks/useApi";

const RINGS = ["Adopt", "Trial", "Assess", "Hold"] as const;

const RING_MAP: Record<string, typeof RINGS[number]> = {
  Stable: "Adopt",
  Growth: "Trial",
  Emerging: "Assess",
  Declining: "Hold",
  Dead: "Hold",
};

const RING_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  Adopt: { bg: "bg-emerald-500/8", border: "border-emerald-500/20", text: "text-emerald-400" },
  Trial: { bg: "bg-blue-500/8", border: "border-blue-500/20", text: "text-blue-400" },
  Assess: { bg: "bg-amber-500/8", border: "border-amber-500/20", text: "text-amber-400" },
  Hold: { bg: "bg-red-500/8", border: "border-red-500/20", text: "text-red-400" },
};

const RING_RADII = [90, 155, 210, 260];

export default function TechRadarPage() {
  const { data, isLoading, error } = useLifecycle();
  const [selected, setSelected] = useState<string | null>(null);

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const items = data ?? [];
  const grouped = RINGS.map((ring) => ({
    ring,
    techs: items.filter((t) => RING_MAP[t.lifecycle_stage] === ring),
  }));

  const selectedTech = items.find((t) => t.technology_name === selected);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Technology Radar</h1>
        <p className="text-sm text-gray-500">Lifecycle-based technology positioning inspired by ThoughtWorks</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Radar visualization */}
        <SectionCard title="Radar View" className="lg:col-span-2">
          <div className="flex items-center justify-center">
            <svg viewBox="0 0 560 560" className="w-full max-w-[500px]">
              {/* Rings */}
              {RING_RADII.map((r, i) => (
                <g key={RINGS[i]}>
                  <circle
                    cx="280"
                    cy="280"
                    r={r}
                    fill="none"
                    stroke="#374151"
                    strokeWidth="1"
                    strokeDasharray="4 4"
                    opacity={0.5}
                  />
                  <text
                    x="280"
                    y={280 - r + 14}
                    textAnchor="middle"
                    className="text-[10px] fill-gray-600 font-medium uppercase tracking-wider"
                  >
                    {RINGS[i]}
                  </text>
                </g>
              ))}
              {/* Quadrant lines */}
              <line x1="280" y1="20" x2="280" y2="540" stroke="#374151" strokeWidth="0.5" opacity={0.3} />
              <line x1="20" y1="280" x2="540" y2="280" stroke="#374151" strokeWidth="0.5" opacity={0.3} />

              {/* Tech nodes */}
              {items.map((tech, idx) => {
                const ring = RING_MAP[tech.lifecycle_stage] ?? "Hold";
                const ringIdx = RINGS.indexOf(ring);
                const innerR = ringIdx === 0 ? 30 : RING_RADII[ringIdx - 1] + 10;
                const outerR = RING_RADII[ringIdx] - 10;
                const r = innerR + (outerR - innerR) * tech.confidence_score;
                const angle = (idx / items.length) * 2 * Math.PI - Math.PI / 2;
                const cx = 280 + r * Math.cos(angle);
                const cy = 280 + r * Math.sin(angle);
                const isSelected = selected === tech.technology_name;

                return (
                  <g
                    key={tech.technology_name}
                    onClick={() => setSelected(isSelected ? null : tech.technology_name)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={cx}
                      cy={cy}
                      r={isSelected ? 18 : 14}
                      className={`transition-all duration-200 ${isSelected ? "fill-blue-500/30 stroke-blue-400" : "fill-gray-800/80 stroke-gray-600"}`}
                      strokeWidth={isSelected ? 2 : 1}
                    />
                    <text
                      x={cx}
                      y={cy + 1}
                      textAnchor="middle"
                      dominantBaseline="central"
                      className={`text-[8px] font-semibold pointer-events-none ${isSelected ? "fill-blue-300" : "fill-gray-300"}`}
                    >
                      {tech.technology_name.slice(0, 4)}
                    </text>
                    <text
                      x={cx}
                      y={cy + 26}
                      textAnchor="middle"
                      className="text-[9px] fill-gray-500 pointer-events-none"
                    >
                      {tech.technology_name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </SectionCard>

        {/* Detail panel */}
        <div className="space-y-4">
          {selectedTech ? (
            <motion.div
              key={selectedTech.technology_name}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <SectionCard title={selectedTech.technology_name} subtitle={`${selectedTech.lifecycle_stage} Stage`}>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-gray-800/30 px-3 py-2">
                      <p className="text-[10px] uppercase text-gray-500">Confidence</p>
                      <p className="text-lg font-bold">{(selectedTech.confidence_score * 100).toFixed(0)}%</p>
                    </div>
                    <div className="rounded-lg bg-gray-800/30 px-3 py-2">
                      <p className="text-[10px] uppercase text-gray-500">Momentum</p>
                      <p className="text-lg font-bold">{selectedTech.momentum_score.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              </SectionCard>
            </motion.div>
          ) : (
            <SectionCard title="Select a Technology" subtitle="Click a node on the radar to view details">
              <p className="text-sm text-gray-500 py-4">Technologies are positioned based on their lifecycle stage and confidence score.</p>
            </SectionCard>
          )}

          {/* Ring legend */}
          <SectionCard title="Rings">
            <div className="space-y-2">
              {grouped.map(({ ring, techs }) => (
                <div key={ring} className={`rounded-lg border px-3 py-2 ${RING_COLORS[ring].bg} ${RING_COLORS[ring].border}`}>
                  <p className={`text-xs font-semibold ${RING_COLORS[ring].text}`}>
                    {ring} <span className="text-gray-500 font-normal">({techs.length})</span>
                  </p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {techs.map((t) => (
                      <TechnologyBadge key={t.technology_name} name={t.technology_name} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
