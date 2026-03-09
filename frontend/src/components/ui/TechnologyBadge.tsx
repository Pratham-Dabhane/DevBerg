const COLORS: Record<string, string> = {
  FastAPI: "bg-emerald-500/10 text-emerald-400 border-emerald-500/15",
  LangChain: "bg-purple-400/10 text-purple-400 border-purple-400/15",
  Rust: "bg-orange-400/10 text-orange-400 border-orange-400/15",
  Bun: "bg-amber-400/10 text-amber-400 border-amber-400/15",
  Qdrant: "bg-dp-secondary/10 text-dp-secondary border-dp-secondary/15",
  Python: "bg-yellow-400/10 text-yellow-400 border-yellow-400/15",
  Docker: "bg-cyan-400/10 text-cyan-400 border-cyan-400/15",
  React: "bg-sky-400/10 text-sky-400 border-sky-400/15",
  TypeScript: "bg-dp-secondary/10 text-dp-secondary border-dp-secondary/15",
  PostgreSQL: "bg-indigo-400/10 text-indigo-400 border-indigo-400/15",
};

const DEFAULT = "bg-dp-text-3/10 text-dp-text-2 border-dp-text-3/15";

export default function TechnologyBadge({ name, className = "" }: { name: string; className?: string }) {
  const colors = COLORS[name] ?? DEFAULT;
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${colors} ${className}`}>
      {name}
    </span>
  );
}
