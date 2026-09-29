// src/components/wardrobe/WardrobeItemCard.jsx
import { useState }        from 'react';
import { motion }          from 'framer-motion';
import { Waves, Trash2, Tag, MoreVertical } from 'lucide-react';
import LaundryBadge        from './LaundryBadge';

export default function WardrobeItemCard({ item, onToggleLaundry, onDelete, onClick }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="wardrobe-card relative rounded-2xl overflow-hidden bg-surface border border-divider cursor-pointer group aspect-square"
      onClick={() => onClick?.(item)}
      role="button"
      tabIndex={0}
      aria-label={`${item.category} — ${item.color}`}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.(item)}
    >
      <img
        src={item.image}
        alt={`${item.color} ${item.category}`}
        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />

      {/* Category badge */}
      <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg px-2 py-0.5 text-2xs font-bold tracking-wide uppercase text-ink">
        {item.category}
      </div>

      {/* Laundry badge */}
      {item.inLaundry && <LaundryBadge />}

      {/* Hover actions */}
      <div
        className="wardrobe-actions absolute top-2 right-2 flex flex-col gap-1.5 opacity-0 transition-opacity duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          aria-label="More options"
          onClick={() => setMenuOpen((o) => !o)}
          className="w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-taupe hover:text-ink transition-colors"
        >
          <MoreVertical size={14} />
        </button>
      </div>

      {/* Dropdown menu */}
      {menuOpen && (
        <div
          className="absolute top-12 right-2 bg-card border border-divider rounded-xl shadow-float z-10 min-w-[160px] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => { onToggleLaundry?.(item.id, !item.inLaundry); setMenuOpen(false); }}
            className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-ink hover:bg-brand-100 transition-colors text-left"
            aria-label={item.inLaundry ? 'Remove from laundry' : 'Mark as in laundry'}
          >
            <Waves size={14} className="text-taupe" />
            {item.inLaundry ? 'Remove from laundry' : 'Mark as in laundry'}
          </button>
          <button
            onClick={() => { onClick?.(item); setMenuOpen(false); }}
            className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-ink hover:bg-brand-100 transition-colors text-left"
            aria-label="Edit tags"
          >
            <Tag size={14} className="text-taupe" />
            Edit tags
          </button>
          <button
            onClick={() => { onDelete?.(item.id); setMenuOpen(false); }}
            className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-danger hover:bg-danger/10 transition-colors text-left"
            aria-label="Delete item"
          >
            <Trash2 size={14} />
            Delete
          </button>
        </div>
      )}
    </motion.div>
  );
}
