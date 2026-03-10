import type { TechCategory } from "../types";

// Maps backend category names to TechCategory keys.
// The mapping is case-insensitive; unknown categories pass through as lowercase.
const BACKEND_TO_CATEGORY: Record<string, TechCategory> = {
  AI: "ai",
  Backend: "backend",
  Frontend: "frontend",
  Systems: "systems",
  Database: "database",
  DevOps: "devops",
  Mobile: "mobile",
  Runtime: "runtime",
};

/** Convert a backend category string to a TechCategory key. */
export function toTechCategory(backendCategory: string): TechCategory {
  return BACKEND_TO_CATEGORY[backendCategory] ?? backendCategory.toLowerCase();
}

/** Build a { techName → TechCategory } map from the /technologies response. */
export function buildCategoryMap(
  techs: { name: string; category: string }[],
): Record<string, TechCategory> {
  const map: Record<string, TechCategory> = {};
  for (const t of techs) {
    map[t.name] = toTechCategory(t.category);
  }
  return map;
}

/** Extract unique category list (with "all" prepended) from the /technologies response. */
export function extractCategories(
  techs: { name: string; category: string }[],
): TechCategory[] {
  const unique = [...new Set(techs.map((t) => toTechCategory(t.category)))].sort();
  return ["all", ...unique];
}

export function techCategory(
  name: string,
  categoryMap?: Record<string, TechCategory>,
): TechCategory {
  if (categoryMap) return categoryMap[name] ?? "all";
  return "all";
}

export function filterByCategory<T extends { technology: string }>(
  items: T[],
  category: TechCategory,
  categoryMap?: Record<string, TechCategory>,
): T[] {
  if (category === "all") return items;
  return items.filter((i) => techCategory(i.technology, categoryMap) === category);
}

export const CATEGORY_LABELS: Record<string, string> = {
  all: "All Technologies",
  ai: "AI & ML",
  backend: "Backend",
  frontend: "Frontend",
  systems: "Systems & Languages",
  database: "Databases",
  devops: "DevOps & Infra",
  mobile: "Mobile",
  runtime: "Runtime & Tooling",
};
