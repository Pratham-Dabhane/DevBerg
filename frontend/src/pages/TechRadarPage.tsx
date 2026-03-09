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
  Adopt: { bg: "bg-dp-accent/8", border: "border-dp-accent/20", text: "text-dp-accent" },
  Trial: { bg: "bg-dp-secondary/8", border: "border-dp-secondary/20", text: "text-dp-secondary" },
  Assess: { bg: "bg-dp-warning/8", border: "border-dp-warning/20", text: "text-dp-warning" },
  Hold: { bg: "bg-dp-danger/8", border: "border-dp-danger/20", text: "text-dp-danger" },
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
        <p className="text-sm text-dp-text-3">Lifecycle-based technology positioning inspired by ThoughtWorks</p>
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
                    stroke="#1E1F27"
                    strokeWidth="1"
                    strokeDasharray="4 4"
                    opacity={0.7}
                  />
                  <text
                    x="280"
                    y={280 - r + 14}
                    textAnchor="middle"
                    className="text-[10px] fill-dp-text-4 font-medium uppercase tracking-wider"
                  >
                    {RINGS[i]}
                  </text>
                </g>
              ))}
              {/* Quadrant lines */}
              <line x1="280" y1="20" x2="280" y2="540" stroke="#1E1F27" strokeWidth="0.5" opacity={0.4} />
              <line x1="20" y1="280" x2="540" y2="280" stroke="#1E1F27" strokeWidth="0.5" opacity={0.4} />

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
                      className={`transition-all duration-200 ${isSelected ? "fill-dp-accent/25 stroke-dp-accent" : "fill-dp-surface stroke-dp-border"}`}
                      strokeWidth={isSelected ? 2 : 1}
                    />
                    <text
                      x={cx}
                      y={cy + 1}
                      textAnchor="middle"
                      dominantBaseline="central"
                      className={`text-[8px] font-semibold pointer-events-none ${isSelected ? "fill-dp-accent" : "fill-dp-text"}`}
                    >
                      {tech.technology_name.slice(0, 4)}
                    </text>
                    <text
                      x={cx}
                      y={cy + 26}
                      textAnchor="middle"
                      className="text-[9px] fill-dp-text-3 pointer-events-none"
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
                    <div className="rounded-lg bg-dp-surface-2 px-3 py-2">
                      <p className="text-[10px] uppercase text-dp-text-3">Confidence</p>
                      <p className="text-lg font-bold">{(selectedTech.confidence_score * 100).toFixed(0)}%</p>
                    </div>
                    <div className="rounded-lg bg-dp-surface-2 px-3 py-2">
                      <p className="text-[10px] uppercase text-dp-text-3">Momentum</p>
                      <p className="text-lg font-bold">{selectedTech.momentum_score.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              </SectionCard>
            </motion.div>
          ) : (
            <SectionCard title="Select a Technology" subtitle="Click a node on the radar to view details">
              <p className="text-sm text-dp-text-3 py-4">Technologies are positioned based on their lifecycle stage and confidence score.</p>
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
