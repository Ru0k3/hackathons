// src/components/outfits/OutfitGallery.jsx
import { AnimatePresence } from 'framer-motion';
import OutfitCard          from './OutfitCard';
import EmptyState          from '@/components/ui/EmptyState';
import { Heart }           from 'lucide-react';

export default function OutfitGallery({ outfits, onDelete, onShare }) {
  if (!outfits.length) {
    return (
      <EmptyState
        icon={Heart}
        title="No saved outfits yet"
        description="Like or save outfits during your swipe session to build your collection."
      />
    );
  }
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <AnimatePresence mode="popLayout">
        {outfits.map((outfit) => (
          <OutfitCard
            key={outfit.id}
            outfit={outfit}
            onDelete={onDelete}
            onShare={onShare}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
