import type { TechCategory } from "../types";
import { CATEGORY_LABELS } from "../utils/categories";
import { useTechnologies } from "../hooks/useApi";
import { extractCategories } from "../utils/categories";

interface Props {
  value: TechCategory;
  onChange: (v: TechCategory) => void;
}

export default function CategoryFilter({ value, onChange }: Props) {
  const { data: techList } = useTechnologies();
  const categories = techList ? extractCategories(techList) : ["all"];

  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            value === cat
              ? "bg-dp-accent-dim text-dp-accent"
              : "bg-dp-surface text-dp-text-3 hover:bg-dp-surface-2 hover:text-dp-text-2"
          }`}
        >
          {CATEGORY_LABELS[cat] || cat}
        </button>
      ))}
    </div>
  );
}
