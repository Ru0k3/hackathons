// src/components/wardrobe/WardrobeItemDetail.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Waves, Trash2, Tag, Plus } from 'lucide-react';
import { updateWardrobeItem } from '@/api/wardrobe';
import LaundryBadge from './LaundryBadge';
import useUIStore from '@/stores/useUIStore';

export default function WardrobeItemDetail({ item, onClose, onToggleLaundry, onDelete }) {
  const addToast = useUIStore((s) => s.addToast);
  const [tagInput, setTagInput] = useState('');
  const [customTags, setCustomTags] = useState(item?.tags || []);

  if (!item) return null;

  const addTag = async () => {
    const t = tagInput.trim().toLowerCase();
    if (!t || customTags.includes(t)) return;
    const next = [...customTags, t];
    setCustomTags(next);
    setTagInput('');
    try {
      await updateWardrobeItem(item.id, { tags: next });
      addToast({ type: 'success', message: 'Tag saved.' });
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Failed to save tag.' });
    }
  };

  const removeTag = (tag) => setCustomTags((prev) => prev.filter((t) => t !== tag));

  return (
    <AnimatePresence>
      {item && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-ink/20 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.aside
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 h-full w-[400px] bg-card border-l border-divider z-50 overflow-y-auto flex flex-col"
            aria-label="Item detail panel"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-divider">
              <h2 className="font-display text-xl text-ink">{item.color} {item.category}</h2>
              <button onClick={onClose} aria-label="Close panel" className="w-9 h-9 rounded-full bg-surface flex items-center justify-center text-muted hover:text-ink">
                <X size={18} />
              </button>
            </div>

            {/* Image */}
            <div className="relative mx-6 mt-6 rounded-2xl overflow-hidden aspect-square bg-surface">
              <img src={item.image} alt={`${item.color} ${item.category}`} className="w-full h-full object-cover" />
              {item.inLaundry && <LaundryBadge size="md" />}
            </div>

            {/* Tags */}
            <div className="p-6 flex-1">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="label">Category</p>
                  <p className="text-sm font-medium text-ink">{item.category}</p>
                </div>
                <div>
                  <p className="label">Colour</p>
                  <p className="text-sm font-medium text-ink">{item.color}</p>
                </div>
              </div>

              {/* Custom tags */}
              <div className="mb-6">
                <p className="label flex items-center gap-1.5"><Tag size={12} /> Custom Tags</p>
                <div className="flex flex-wrap gap-2 mb-3 min-h-[32px]">
                  {customTags.map((tag) => (
                    <span key={tag} className="flex items-center gap-1 badge text-xs">
                      {tag}
                      <button onClick={() => removeTag(tag)} aria-label={`Remove tag ${tag}`} className="ml-0.5 hover:text-danger">
                        <X size={10} />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addTag()}
                    placeholder="Add tag..."
                    aria-label="New tag"
                    className="input flex-1 text-sm py-2"
                  />
                  <button onClick={addTag} aria-label="Add tag" className="btn-secondary px-3 py-2">
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-6 border-t border-divider flex flex-col gap-3">
              <button
                onClick={() => onToggleLaundry?.(item.id, !item.inLaundry)}
                className="btn-secondary w-full justify-center gap-2"
                aria-label={item.inLaundry ? 'Remove from laundry' : 'Mark as in laundry'}
              >
                <Waves size={16} />
                {item.inLaundry ? 'Remove from Laundry' : 'Mark as In Laundry'}
              </button>
              <button
                onClick={() => { onDelete?.(item.id); onClose(); }}
                className="btn-danger w-full justify-center gap-2"
                aria-label="Delete item"
              >
                <Trash2 size={16} />
                Delete Item
              </button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
