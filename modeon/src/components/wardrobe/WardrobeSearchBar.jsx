// src/components/wardrobe/WardrobeSearchBar.jsx
import { Search, X } from 'lucide-react';

export default function WardrobeSearchBar({ value, onChange }) {
  return (
    <div className="relative flex-1 max-w-sm">
      <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search category, colour, tag…"
        aria-label="Search wardrobe"
        className="input pl-10 pr-9"
      />
      {value && (
        <button
          onClick={() => onChange('')}
          aria-label="Clear search"
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
