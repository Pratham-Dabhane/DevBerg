import type { TechCategory } from "../types";

// Map each technology to its category for filtering
const TECH_CATEGORIES: Record<string, TechCategory> = {
  FastAPI: "ai",
  LangChain: "ai",
  Rust: "languages",
  Bun: "languages",
  Qdrant: "databases",
};

export function techCategory(name: string): TechCategory {
  return TECH_CATEGORIES[name] ?? "all";
}

export function filterByCategory<T extends { technology: string }>(
  items: T[],
  category: TechCategory,
): T[] {
  if (category === "all") return items;
  return items.filter((i) => techCategory(i.technology) === category);
}

export const CATEGORY_LABELS: Record<TechCategory, string> = {
  all: "All Technologies",
  ai: "AI Frameworks",
  languages: "Programming Languages",
  databases: "Databases",
  devops: "DevOps Tools",
};
