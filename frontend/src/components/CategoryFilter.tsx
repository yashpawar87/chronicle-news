import { CATEGORIES, CATEGORY_LABELS, type Category } from "@/lib/news.types";

interface CategoryFilterProps {
  selected: Category[];
  onChange: (categories: Category[]) => void;
}

export function CategoryFilter({ selected, onChange }: CategoryFilterProps) {
  const allSelected = selected.length === CATEGORIES.length;

  const toggle = (cat: Category) => {
    if (selected.includes(cat)) {
      if (selected.length === 1) return; // at least one stays active
      onChange(selected.filter((c) => c !== cat));
    } else {
      onChange([...selected, cat]);
    }
  };

  const chipBase =
    "rounded-full border px-5 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

  return (
    <div className="flex flex-wrap items-center justify-center gap-2.5">
      <button
        type="button"
        onClick={() => onChange([...CATEGORIES])}
        aria-pressed={allSelected}
        className={`${chipBase} ${
          allSelected
            ? "border-primary bg-primary text-primary-foreground"
            : "border-border bg-card text-foreground hover:border-foreground/40"
        }`}
      >
        For You
      </button>
      {CATEGORIES.map((cat) => {
        const active = !allSelected && selected.includes(cat);
        return (
          <button
            key={cat}
            type="button"
            onClick={() => toggle(cat)}
            aria-pressed={selected.includes(cat)}
            className={`${chipBase} ${
              active
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-card text-foreground hover:border-foreground/40"
            }`}
          >
            {CATEGORY_LABELS[cat]}
          </button>
        );
      })}
    </div>
  );
}
