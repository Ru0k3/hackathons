// src/components/mixmatch/MixMatchCanvas.jsx
import { CanvasSlot } from './CanvasSlot';

const SLOTS = ['top', 'bottom', 'shoes', 'outerwear', 'bag', 'hat', 'accessory1', 'accessory2'];

export function MixMatchCanvas({ slotItems, onRemoveSlot }) {
  return (
    <div className="flex-1">
      <p className="label mb-4">Your Canvas</p>
      <div className="grid grid-cols-4 gap-3">
        {SLOTS.map((slotId) => (
          <CanvasSlot
            key={slotId}
            slotId={slotId}
            item={slotItems[slotId]}
            onRemove={onRemoveSlot}
          />
        ))}
      </div>
    </div>
  );
}
