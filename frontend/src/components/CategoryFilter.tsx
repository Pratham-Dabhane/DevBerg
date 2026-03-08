import type { TechCategory } from "../types";
import { CATEGORY_LABELS } from "../utils/categories";

interface Props {
  value: TechCategory;
  onChange: (v: TechCategory) => void;
}

const categories: TechCategory[] = ["all", "ai", "languages", "databases", "devops"];

export default function CategoryFilter({ value, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            value === cat
              ? "bg-brand-600 text-white"
              : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200"
          }`}
        >
          {CATEGORY_LABELS[cat]}
        </button>
      ))}
    </div>
  );
}
