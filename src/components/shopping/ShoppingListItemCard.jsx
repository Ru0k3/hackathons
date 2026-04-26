// src/components/shopping/ShoppingListItemCard.jsx
import { motion } from 'framer-motion';
import { Trash2, ArrowUpRight, Calendar } from 'lucide-react';
import { useMoveToWardrobe } from '@/hooks/useShoppingList';

export function ShoppingListItemCard({ item, onRemove, onMoveToWardrobe }) {
  const { mutate: moveToWardrobe } = useMoveToWardrobe();

  const handleMove = () => {
    moveToWardrobe(item.id, {
      onSuccess: () => onMoveToWardrobe?.(item.id),
    });
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="card p-4 flex gap-4 items-start"
    >
      <div className="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 bg-surface">
        <img src={item.thumbnail} alt="Shopping item" className="w-full h-full object-cover" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-bold text-ink text-sm mb-1">{item.category || 'Item'}</p>
        {item.tags && (
          <div className="flex flex-wrap gap-1 mb-2">
            {Object.entries(item.tags).slice(0, 3).map(([k, v]) => (
              <span key={k} className="text-2xs bg-surface text-muted rounded-chip px-2 py-0.5 capitalize">{v}</span>
            ))}
          </div>
        )}
        {item.addedAt && (
          <span className="flex items-center gap-1 text-2xs text-muted">
            <Calendar size={10} /> Added {item.addedAt}
          </span>
        )}
      </div>
      <div className="flex flex-col gap-2 flex-shrink-0">
        <button
          onClick={handleMove}
          aria-label="Move to wardrobe"
          className="flex items-center gap-1 text-2xs font-bold tracking-wide uppercase text-gold hover:text-gold/80 transition-colors"
        >
          <ArrowUpRight size={13} /> Wardrobe
        </button>
        <button
          onClick={() => onRemove?.(item.id)}
          aria-label="Remove from list"
          className="flex items-center gap-1 text-2xs font-bold tracking-wide uppercase text-danger hover:text-danger/80 transition-colors"
        >
          <Trash2 size={13} /> Remove
        </button>
      </div>
    </motion.div>
  );
}
