// src/components/ui/FilterChip.jsx
import { X } from 'lucide-react';

export default function FilterChip({ label, onRemove, active = false }) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-2xs font-bold tracking-wider uppercase px-3 py-1.5 rounded-chip border transition-colors cursor-default
      ${active ? 'bg-gold text-white border-gold' : 'bg-surface text-taupe border-divider'}`}
    >
      {label}
      {onRemove && (
        <button
          onClick={onRemove}
          aria-label={`Remove ${label} filter`}
          className="border-0 bg-transparent cursor-pointer p-0 leading-none text-current opacity-70 hover:opacity-100"
        >
          <X size={11} />
        </button>
      )}
    </span>
  );
}
