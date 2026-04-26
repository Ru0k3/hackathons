// src/components/wardrobe/WardrobeFilterPanel.jsx
import { CATEGORIES, COLOURS, SEASONS, FORMALITY } from '@/constants/categories';
import useWardrobeStore from '@/stores/useWardrobeStore';
import FilterChip       from '@/components/ui/FilterChip';
import { Waves }        from 'lucide-react';

function FilterSection({ title, options, storeKey }) {
  const filters     = useWardrobeStore((s) => s.filters);
  const setFilter   = useWardrobeStore((s) => s.setFilter);
  const active      = filters[storeKey] || [];

  const toggle = (val) => {
    setFilter(
      storeKey,
      active.includes(val) ? active.filter((v) => v !== val) : [...active, val]
    );
  };

  return (
    <div className="mb-6">
      <p className="label">{title}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <FilterChip
            key={opt}
            label={opt}
            active={active.includes(opt)}
            onClick={() => toggle(opt)}
          />
        ))}
      </div>
    </div>
  );
}

export default function WardrobeFilterPanel() {
  const filters     = useWardrobeStore((s) => s.filters);
  const setFilter   = useWardrobeStore((s) => s.setFilter);
  const clearFilters = useWardrobeStore((s) => s.clearFilters);

  const hasFilters = Object.values(filters).some((v) =>
    Array.isArray(v) ? v.length > 0 : v
  );

  return (
    <aside className="w-56 flex-shrink-0 pr-6">
      <div className="flex items-center justify-between mb-6">
        <p className="font-bold text-sm text-ink">Filters</p>
        {hasFilters && (
          <button onClick={clearFilters} className="text-2xs text-gold font-bold tracking-widest uppercase hover:underline">
            Clear all
          </button>
        )}
      </div>

      {/* Laundry toggle */}
      <div className="mb-6">
        <button
          onClick={() => setFilter('laundry', !filters.laundry)}
          aria-pressed={filters.laundry}
          className={`flex items-center gap-2 w-full px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors
            ${filters.laundry
              ? 'bg-blue-50 border-blue-200 text-blue-700'
              : 'bg-card border-divider text-taupe hover:bg-brand-100'}`}
        >
          <Waves size={15} />
          In Laundry only
        </button>
      </div>

      <FilterSection title="Category"  options={CATEGORIES} storeKey="category"  />
      <FilterSection title="Colour"    options={COLOURS}    storeKey="colours"   />
      <FilterSection title="Season"    options={SEASONS}    storeKey="seasons"   />
      <FilterSection title="Formality" options={FORMALITY}  storeKey="formality" />
    </aside>
  );
}
