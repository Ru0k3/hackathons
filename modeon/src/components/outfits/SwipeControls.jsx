// src/components/outfits/SwipeControls.jsx
import { X, Star, Heart } from 'lucide-react';

export default function SwipeControls({ onDislike, onSave, onLike, disabled }) {
  return (
    <div className="flex items-center justify-center gap-6 mt-8" role="group" aria-label="Swipe controls">
      <button
        onClick={onDislike}
        disabled={disabled}
        aria-label="Dislike — skip this outfit (Left arrow)"
        className="w-16 h-16 rounded-full bg-card border-2 border-divider flex items-center justify-center text-danger hover:border-danger hover:bg-danger/10 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-card"
      >
        <X size={26} />
      </button>

      <button
        onClick={onSave}
        disabled={disabled}
        aria-label="Save this outfit (Up arrow)"
        className="w-20 h-20 rounded-full bg-gold flex items-center justify-center text-white hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed shadow-gold"
      >
        <Star size={30} fill="white" />
      </button>

      <button
        onClick={onLike}
        disabled={disabled}
        aria-label="Like this outfit (Right arrow)"
        className="w-16 h-16 rounded-full bg-card border-2 border-divider flex items-center justify-center text-ok hover:border-ok hover:bg-ok/10 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-card"
      >
        <Heart size={26} />
      </button>
    </div>
  );
}
