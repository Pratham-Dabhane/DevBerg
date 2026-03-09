const COLORS: Record<string, string> = {
  FastAPI: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  LangChain: "bg-purple-500/15 text-purple-400 border-purple-500/20",
  Rust: "bg-orange-500/15 text-orange-400 border-orange-500/20",
  Bun: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  Qdrant: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  Python: "bg-yellow-500/15 text-yellow-400 border-yellow-500/20",
  Docker: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
  React: "bg-sky-500/15 text-sky-400 border-sky-500/20",
  TypeScript: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  PostgreSQL: "bg-indigo-500/15 text-indigo-400 border-indigo-500/20",
};

const DEFAULT = "bg-gray-500/15 text-gray-400 border-gray-500/20";

export default function TechnologyBadge({ name, className = "" }: { name: string; className?: string }) {
  const colors = COLORS[name] ?? DEFAULT;
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${colors} ${className}`}>
      {name}
    </span>
  );
}
