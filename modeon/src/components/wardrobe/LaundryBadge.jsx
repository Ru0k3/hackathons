// src/components/wardrobe/LaundryBadge.jsx
import { Waves } from 'lucide-react';

export default function LaundryBadge({ size = 'sm' }) {
  return (
    <div
      className={`absolute bottom-2 left-2 flex items-center gap-1 bg-blue-100 text-blue-600 rounded-chip font-bold tracking-wide
        ${size === 'sm' ? 'px-2 py-0.5 text-2xs' : 'px-3 py-1 text-xs'}`}
      aria-label="In laundry"
    >
      <Waves size={10} />
      Laundry
    </div>
  );
}
