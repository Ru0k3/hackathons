// src/components/mixmatch/CanvasSlot.jsx
import { useDroppable } from '@dnd-kit/core';
import { Plus }         from 'lucide-react';

const SLOT_LABELS = {
  top:        'Top',
  bottom:     'Bottom',
  shoes:      'Shoes',
  outerwear:  'Outerwear',
  bag:        'Bag',
  hat:        'Hat',
  accessory1: 'Accessory 1',
  accessory2: 'Accessory 2',
};

export function CanvasSlot({ slotId, item, onRemove }) {
  const { isOver, setNodeRef } = useDroppable({ id: slotId });

  return (
    <div
      ref={setNodeRef}
      className={`relative rounded-2xl border-2 border-dashed aspect-square flex items-center justify-center transition-colors
        ${isOver
          ? 'border-gold bg-gold/10'
          : item
          ? 'border-divider bg-surface'
          : 'border-divider bg-surface hover:border-gold/50'}`}
      aria-label={`${SLOT_LABELS[slotId]} slot`}
    >
      {item ? (
        <>
          <img
            src={item.image}
            alt={item.category}
            className="w-full h-full object-cover rounded-[14px]"
          />
          <button
            onClick={() => onRemove?.(slotId)}
            aria-label={`Remove ${SLOT_LABELS[slotId]}`}
            className="absolute top-1.5 right-1.5 w-6 h-6 rounded-full bg-white/90 text-danger flex items-center justify-center text-xs font-bold hover:bg-white transition-colors"
          >
            ×
          </button>
          <div className="absolute bottom-1.5 left-1.5 bg-black/50 text-white text-2xs rounded-md px-1.5 py-0.5 font-bold">
            {SLOT_LABELS[slotId]}
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center gap-1 text-muted pointer-events-none">
          <Plus size={20} />
          <span className="text-2xs font-bold tracking-wide">{SLOT_LABELS[slotId]}</span>
        </div>
      )}
    </div>
  );
}
