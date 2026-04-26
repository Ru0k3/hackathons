// src/components/wardrobe/BulkActionBar.jsx
import { AnimatePresence, motion } from 'framer-motion';
import { Waves, Trash2, X }       from 'lucide-react';

export default function BulkActionBar({ selectedIds, onClearSelection, onBulkLaundry, onBulkDelete }) {
  return (
    <AnimatePresence>
      {selectedIds.length > 0 && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0,  opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-ink text-white rounded-2xl shadow-float px-6 py-4 flex items-center gap-6 z-30"
          role="toolbar"
          aria-label="Bulk actions"
        >
          <span className="text-sm font-medium">
            {selectedIds.length} item{selectedIds.length > 1 ? 's' : ''} selected
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onBulkLaundry?.(selectedIds, true)}
              className="flex items-center gap-1.5 text-sm font-medium text-blue-300 hover:text-blue-100 transition-colors"
              aria-label="Mark selected as in laundry"
            >
              <Waves size={16} /> Laundry
            </button>
            <button
              onClick={() => onBulkDelete?.(selectedIds)}
              className="flex items-center gap-1.5 text-sm font-medium text-red-300 hover:text-red-100 transition-colors"
              aria-label="Delete selected"
            >
              <Trash2 size={16} /> Delete
            </button>
            <button
              onClick={onClearSelection}
              className="text-muted hover:text-white transition-colors"
              aria-label="Clear selection"
            >
              <X size={18} />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
