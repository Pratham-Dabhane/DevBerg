import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Globe, MapPin } from "lucide-react";

import MetricCard from "../components/ui/MetricCard";
import { SectionCard, PageSpinner, PageError } from "../components/ui/PageShell";
import ScoreBar from "../components/ui/ScoreBar";
import { useMomentum } from "../hooks/useApi";

// Simulated global activity by region (since backend endpoint doesn't exist yet)
const REGIONS = [
  { name: "North America", lat: 40, lng: -100, weight: 0.9 },
  { name: "Europe", lat: 50, lng: 10, weight: 0.85 },
  { name: "India", lat: 20, lng: 78, weight: 0.8 },
  { name: "China", lat: 35, lng: 105, weight: 0.75 },
  { name: "Southeast Asia", lat: 10, lng: 106, weight: 0.6 },
  { name: "South America", lat: -15, lng: -55, weight: 0.5 },
  { name: "Africa", lat: 5, lng: 25, weight: 0.35 },
  { name: "Oceania", lat: -25, lng: 135, weight: 0.45 },
  { name: "Middle East", lat: 25, lng: 45, weight: 0.4 },
  { name: "Japan & Korea", lat: 36, lng: 138, weight: 0.7 },
];

const ACTIVITY_LEVELS = ["High", "Medium", "Low"] as const;

function getActivityLevel(score: number): typeof ACTIVITY_LEVELS[number] {
  if (score > 0.7) return "High";
  if (score > 0.4) return "Medium";
  return "Low";
}

const activityColors: Record<string, string> = {
  High: "text-emerald-400",
  Medium: "text-amber-400",
  Low: "text-gray-500",
};

export default function GlobalMapPage() {
  const { data, isLoading, error } = useMomentum();
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [techFilter, setTechFilter] = useState<string | null>(null);

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const techs = (data ?? []).map((m) => m.technology_name);

  // Simulated regional activity data per technology
  const regionData = useMemo(() => {
    return REGIONS.map((region) => ({
      ...region,
      technologies: (data ?? []).map((tech) => ({
        name: tech.technology_name,
        activity: getActivityLevel(
          region.weight * tech.momentum_score * (0.7 + Math.random() * 0.6)
        ),
        score: region.weight * tech.momentum_score,
      })),
    }));
  }, [data]);

  const filteredRegions = techFilter
    ? regionData.map((r) => ({
        ...r,
        technologies: r.technologies.filter((t) => t.name === techFilter),
      }))
    : regionData;

  const selected = filteredRegions.find((r) => r.name === selectedRegion);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Global Developer Activity</h1>
        <p className="text-sm text-gray-500">Developer ecosystem activity patterns across regions</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Regions Tracked" value={REGIONS.length} icon={<Globe className="h-4 w-4" />} />
        <MetricCard label="Technologies" value={techs.length} />
        <MetricCard label="Highest Activity" value="North America" />
        <MetricCard label="Fastest Growing" value="India" />
      </div>

      {/* Tech filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setTechFilter(null)}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            !techFilter ? "bg-blue-500/15 text-blue-400" : "bg-gray-800/50 text-gray-500 hover:text-gray-300"
          }`}
        >
          All Technologies
        </button>
        {techs.map((tech) => (
          <button
            key={tech}
            onClick={() => setTechFilter(techFilter === tech ? null : tech)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              techFilter === tech ? "bg-blue-500/15 text-blue-400" : "bg-gray-800/50 text-gray-500 hover:text-gray-300"
            }`}
          >
            {tech}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Map placeholder using SVG world visualization */}
        <SectionCard title="Activity Map" subtitle="Click a region to explore" className="lg:col-span-2">
          <div className="relative h-[400px] rounded-lg bg-gray-900/50 overflow-hidden">
            {/* Simplified SVG world map dots */}
            <svg viewBox="0 0 800 400" className="w-full h-full">
              {/* Grid lines */}
              {Array.from({ length: 9 }, (_, i) => (
                <line key={`h${i}`} x1="0" y1={i * 50} x2="800" y2={i * 50} stroke="#1f2937" strokeWidth="0.5" />
              ))}
              {Array.from({ length: 17 }, (_, i) => (
                <line key={`v${i}`} x1={i * 50} y1="0" x2={i * 50} y2="400" stroke="#1f2937" strokeWidth="0.5" />
              ))}

              {/* Region dots */}
              {filteredRegions.map((region) => {
                const x = ((region.lng + 180) / 360) * 800;
                const y = ((90 - region.lat) / 180) * 400;
                const avgScore = region.technologies.reduce((s, t) => s + t.score, 0) / Math.max(region.technologies.length, 1);
                const isSelected = selectedRegion === region.name;
                const radius = 8 + avgScore * 20;

                return (
                  <g key={region.name} onClick={() => setSelectedRegion(isSelected ? null : region.name)} className="cursor-pointer">
                    {/* Pulse animation */}
                    <circle cx={x} cy={y} r={radius + 4} fill="none" stroke="#3b82f6" strokeWidth="1" opacity={isSelected ? 0.5 : 0}>
                      {isSelected && (
                        <animate attributeName="r" from={String(radius)} to={String(radius + 15)} dur="1.5s" repeatCount="indefinite" />
                      )}
                      {isSelected && (
                        <animate attributeName="opacity" from="0.5" to="0" dur="1.5s" repeatCount="indefinite" />
                      )}
                    </circle>
                    {/* Main dot */}
                    <circle
                      cx={x}
                      cy={y}
                      r={radius}
                      fill={isSelected ? "#3b82f6" : avgScore > 0.5 ? "#22c55e" : avgScore > 0.3 ? "#f59e0b" : "#6b7280"}
                      opacity={0.7}
                      className="transition-all duration-200 hover:opacity-100"
                    />
                    <text
                      x={x}
                      y={y - radius - 6}
                      textAnchor="middle"
                      className="text-[9px] fill-gray-400 pointer-events-none"
                    >
                      {region.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </SectionCard>

        {/* Region detail */}
        <div className="space-y-4">
          {selected ? (
            <motion.div
              key={selected.name}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <SectionCard title={selected.name} subtitle="Technology activity breakdown">
                <div className="space-y-3">
                  {selected.technologies.map((t) => (
                    <div key={t.name} className="flex items-center justify-between">
                      <span className="text-sm text-gray-300">{t.name}</span>
                      <span className={`text-xs font-medium ${activityColors[t.activity]}`}>
                        {t.activity}
                      </span>
                    </div>
                  ))}
                </div>
              </SectionCard>
            </motion.div>
          ) : (
            <SectionCard title="Region Details" subtitle="Click a region on the map">
              <p className="text-sm text-gray-500 py-4">Select a region to see technology adoption patterns.</p>
            </SectionCard>
          )}

          {/* Global rankings */}
          <SectionCard title="Regional Rankings" subtitle="By average activity score">
            <div className="space-y-2">
              {filteredRegions
                .map((r) => ({
                  ...r,
                  avg: r.technologies.reduce((s, t) => s + t.score, 0) / Math.max(r.technologies.length, 1),
                }))
                .sort((a, b) => b.avg - a.avg)
                .map((r, i) => (
                  <div
                    key={r.name}
                    className="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-800/30 rounded px-2 py-1.5 transition-colors"
                    onClick={() => setSelectedRegion(r.name)}
                  >
                    <span className="text-xs font-bold text-gray-500 w-5">{i + 1}</span>
                    <MapPin className="h-3 w-3 text-gray-600" />
                    <span className="text-gray-300 flex-1">{r.name}</span>
                    <ScoreBar value={r.avg * 100} className="w-16" />
                  </div>
                ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
