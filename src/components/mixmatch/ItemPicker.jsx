// src/components/mixmatch/ItemPicker.jsx
import { useDraggable }     from '@dnd-kit/core';
import { CSS }              from '@dnd-kit/utilities';
import useWardrobeStore     from '@/stores/useWardrobeStore';

function DraggableItem({ item }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id:   `picker-${item.id}`,
    data: { item },
  });

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      style={{ transform: CSS.Translate.toString(transform) }}
      className={`relative rounded-xl overflow-hidden aspect-square cursor-grab active:cursor-grabbing border border-divider transition-all
        ${isDragging ? 'opacity-50 scale-95' : 'hover:border-gold'}`}
      aria-label={`Drag ${item.color} ${item.category}`}
    >
      <img src={item.image} alt={`${item.color} ${item.category}`} className="w-full h-full object-cover" />
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-1.5">
        <p className="text-2xs text-white font-bold truncate">{item.category}</p>
      </div>
    </div>
  );
}

export function ItemPicker() {
  const items = useWardrobeStore((s) => s.items.filter((i) => !i.inLaundry));

  return (
    <aside className="w-52 flex-shrink-0 flex flex-col gap-3">
      <p className="label">Drag items onto the canvas</p>
      <div className="overflow-y-auto flex-1 grid grid-cols-2 gap-2 pr-1" style={{ maxHeight: 500 }}>
        {items.map((item) => (
          <DraggableItem key={item.id} item={item} />
        ))}
        {items.length === 0 && (
          <p className="col-span-2 text-sm text-muted italic text-center py-8">
            No items available. Upload some wardrobe items first.
          </p>
        )}
      </div>
    </aside>
  );
}
