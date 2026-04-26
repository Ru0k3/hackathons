// src/components/shopping/ShoppingListGrid.jsx
import { AnimatePresence }      from 'framer-motion';
import { ShoppingListItemCard } from './ShoppingListItemCard';
import EmptyState               from '@/components/ui/EmptyState';
import { ShoppingBag }          from 'lucide-react';

export function ShoppingListGrid({ items, onRemove, onMoveToWardrobe }) {
  if (!items.length) {
    return (
      <EmptyState
        icon={ShoppingBag}
        title="No items in your list yet"
        description="Upload something you're thinking about buying, then save it here."
      />
    );
  }
  return (
    <div className="flex flex-col gap-4">
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <ShoppingListItemCard
            key={item.id}
            item={item}
            onRemove={onRemove}
            onMoveToWardrobe={onMoveToWardrobe}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
