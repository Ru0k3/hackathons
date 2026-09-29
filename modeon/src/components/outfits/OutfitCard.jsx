// src/components/outfits/OutfitCard.jsx
import { motion }               from 'framer-motion';
import { Heart, Share2, Trash2, MapPin, Calendar } from 'lucide-react';

export function OutfitCollage({ items = [], height = 280, radius = 16 }) {
  const style = { height, borderRadius: radius, overflow: 'hidden' };
  if (items.length === 0) return <div style={style} className="bg-surface" />;
  if (items.length <= 2) {
    return (
      <div style={{ ...style, display: 'grid', gridTemplateColumns: `repeat(${items.length}, 1fr)`, gap: 4 }}>
        {items.map((src, i) => (
          <img key={i} src={src} alt="Outfit item" className="w-full h-full object-cover" />
        ))}
      </div>
    );
  }
  return (
    <div style={{ ...style, display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 4 }}>
      <img src={items[0]} alt="Outfit item" style={{ gridRow: '1 / 3' }} className="w-full h-full object-cover" />
      {items.slice(1, 3).map((src, i) => (
        <img key={i} src={src} alt="Outfit item" className="w-full h-full object-cover" />
      ))}
    </div>
  );
}

export default function OutfitCard({ outfit, onSave, onDelete, onShare }) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="saved-card card relative overflow-hidden"
    >
      <OutfitCollage items={outfit.items} />

      {/* Hover actions */}
      <div className="saved-actions absolute top-6 right-6 flex flex-col gap-2 opacity-0 transition-opacity duration-200">
        {onShare && (
          <button
            onClick={() => onShare?.(outfit)}
            aria-label="Share outfit"
            className="w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-taupe hover:text-ink transition-colors"
          >
            <Share2 size={16} />
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete?.(outfit.id)}
            aria-label="Delete outfit"
            className="w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-danger hover:opacity-80 transition-opacity"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      <div className="mt-5 flex flex-col gap-2">
        <div className="flex justify-between items-center">
          {outfit.occasion && (
            <span className="flex items-center gap-1 text-2xs font-bold tracking-widest uppercase text-gold">
              <MapPin size={11} /> {outfit.occasion}
            </span>
          )}
          {outfit.date && (
            <span className="flex items-center gap-1 text-2xs text-muted font-medium">
              <Calendar size={11} /> {outfit.date}
            </span>
          )}
        </div>
        <h3 className="font-display text-xl text-ink">
          {outfit.name || `The ${outfit.occasion || 'Saved'} Ensemble`}
        </h3>
        {outfit.explanation && (
          <p className="text-sm text-taupe italic leading-relaxed line-clamp-2">{outfit.explanation}</p>
        )}
      </div>

      {onSave && (
        <button onClick={() => onSave?.(outfit)} className="btn-secondary w-full justify-center mt-5 text-2xs">
          <Heart size={14} /> Save
        </button>
      )}
    </motion.div>
  );
}
