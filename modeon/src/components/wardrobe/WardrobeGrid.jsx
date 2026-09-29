// src/components/wardrobe/WardrobeGrid.jsx
import { AnimatePresence } from 'framer-motion';
import WardrobeItemCard    from './WardrobeItemCard';
import EmptyState          from '@/components/ui/EmptyState';
import { Shirt }           from 'lucide-react';

export default function WardrobeGrid({ items, onToggleLaundry, onDelete, onItemClick }) {
  if (!items.length) {
    return (
      <EmptyState
        icon={Shirt}
        title="Your wardrobe is empty"
        description="Upload your first item to get started with AI-powered outfit suggestions."
      />
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <WardrobeItemCard
            key={item.id}
            item={item}
            onToggleLaundry={onToggleLaundry}
            onDelete={onDelete}
            onClick={onItemClick}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
