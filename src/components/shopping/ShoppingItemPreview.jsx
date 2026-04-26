// src/components/shopping/ShoppingItemPreview.jsx
import { CheckCircle2, Plus, SlidersHorizontal } from 'lucide-react';
import Spinner from '@/components/ui/Spinner';

export function ShoppingItemPreview({ preview, onCompare, onAddToList, comparing, usageUsed, usageLimit }) {
  return (
    <div className="flex gap-6 items-start">
      <div className="w-40 h-40 rounded-2xl overflow-hidden flex-shrink-0 bg-surface border border-divider">
        <img src={preview} alt="Shopping item" className="w-full h-full object-cover" />
      </div>
      <div className="flex-1">
        <p className="font-bold text-ink mb-1">Item ready to compare</p>
        <p className="text-sm text-muted mb-5">
          Comparisons used: <span className="text-ink font-semibold">{usageUsed} / {usageLimit}</span> this month
        </p>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={onCompare}
            disabled={comparing || usageUsed >= usageLimit}
            className="btn-gold"
            aria-label="Compare with my wardrobe"
          >
            {comparing ? <Spinner size="sm" /> : <SlidersHorizontal size={15} />}
            Compare with My Wardrobe
          </button>
          <button onClick={onAddToList} className="btn-secondary" aria-label="Save to shopping list">
            <Plus size={15} /> Save to List
          </button>
        </div>
        {usageUsed >= usageLimit && (
          <p className="text-xs text-danger mt-3">Monthly comparison limit reached. Upgrade for unlimited comparisons.</p>
        )}
      </div>
    </div>
  );
}
