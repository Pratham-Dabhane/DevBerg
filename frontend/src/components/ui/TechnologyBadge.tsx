const COLORS: Record<string, string> = {
  // AI / ML
  LangChain: "bg-purple-400/10 text-purple-400 border-purple-400/15",
  PyTorch: "bg-orange-400/10 text-orange-400 border-orange-400/15",
  TensorFlow: "bg-amber-400/10 text-amber-400 border-amber-400/15",
  "Hugging Face": "bg-yellow-400/10 text-yellow-400 border-yellow-400/15",
  OpenAI: "bg-emerald-400/10 text-emerald-400 border-emerald-400/15",
  Ollama: "bg-stone-400/10 text-stone-400 border-stone-400/15",
  "scikit-learn": "bg-sky-400/10 text-sky-400 border-sky-400/15",
  Qdrant: "bg-dp-secondary/10 text-dp-secondary border-dp-secondary/15",
  ChromaDB: "bg-teal-400/10 text-teal-400 border-teal-400/15",
  // Backend
  FastAPI: "bg-emerald-500/10 text-emerald-400 border-emerald-500/15",
  Django: "bg-green-400/10 text-green-400 border-green-400/15",
  Flask: "bg-slate-400/10 text-slate-400 border-slate-400/15",
  "Express.js": "bg-lime-400/10 text-lime-400 border-lime-400/15",
  NestJS: "bg-rose-400/10 text-rose-400 border-rose-400/15",
  "Spring Boot": "bg-green-500/10 text-green-400 border-green-500/15",
  Laravel: "bg-red-400/10 text-red-400 border-red-400/15",
  // Frontend
  React: "bg-sky-400/10 text-sky-400 border-sky-400/15",
  Vue: "bg-emerald-400/10 text-emerald-400 border-emerald-400/15",
  Angular: "bg-red-400/10 text-red-400 border-red-400/15",
  Svelte: "bg-orange-400/10 text-orange-400 border-orange-400/15",
  "Next.js": "bg-stone-400/10 text-stone-300 border-stone-400/15",
  Astro: "bg-fuchsia-400/10 text-fuchsia-400 border-fuchsia-400/15",
  "Tailwind CSS": "bg-cyan-400/10 text-cyan-400 border-cyan-400/15",
  htmx: "bg-indigo-400/10 text-indigo-400 border-indigo-400/15",
  // Systems
  Rust: "bg-orange-400/10 text-orange-400 border-orange-400/15",
  Go: "bg-sky-400/10 text-sky-400 border-sky-400/15",
  Kotlin: "bg-violet-400/10 text-violet-400 border-violet-400/15",
  TypeScript: "bg-dp-secondary/10 text-dp-secondary border-dp-secondary/15",
  // Databases
  PostgreSQL: "bg-indigo-400/10 text-indigo-400 border-indigo-400/15",
  MongoDB: "bg-green-400/10 text-green-400 border-green-400/15",
  Redis: "bg-red-400/10 text-red-400 border-red-400/15",
  Supabase: "bg-emerald-400/10 text-emerald-400 border-emerald-400/15",
  // DevOps
  Docker: "bg-cyan-400/10 text-cyan-400 border-cyan-400/15",
  Kubernetes: "bg-blue-400/10 text-blue-400 border-blue-400/15",
  Terraform: "bg-violet-400/10 text-violet-400 border-violet-400/15",
  // Runtime / Tools
  Bun: "bg-amber-400/10 text-amber-400 border-amber-400/15",
  Deno: "bg-stone-400/10 text-stone-300 border-stone-400/15",
  "Node.js": "bg-green-400/10 text-green-400 border-green-400/15",
  Vite: "bg-violet-400/10 text-violet-400 border-violet-400/15",
  // Mobile
  Flutter: "bg-sky-400/10 text-sky-400 border-sky-400/15",
  "React Native": "bg-sky-400/10 text-sky-400 border-sky-400/15",
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
