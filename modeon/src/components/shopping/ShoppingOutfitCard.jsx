// src/components/shopping/ShoppingOutfitCard.jsx
// Static outfit card used in the Shopping List Outfit Generator (no swipe mechanic)
import { motion }          from 'framer-motion';
import { OutfitCollage }   from '@/components/outfits/OutfitCard';

export function ShoppingOutfitCard({ outfit, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="card overflow-hidden"
    >
      <OutfitCollage items={outfit.items} height={240} />
      <div className="mt-4">
        <span className="badge mb-2">Combination {index + 1}</span>
        <p className="text-sm text-taupe italic leading-relaxed mt-1">{outfit.explanation}</p>
      </div>
    </motion.div>
  );
}
