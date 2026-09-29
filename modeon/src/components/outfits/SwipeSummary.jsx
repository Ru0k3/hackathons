// src/components/outfits/SwipeSummary.jsx
import { motion }     from 'framer-motion';
import { Heart, Star, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES }     from '@/constants/routes';

export default function SwipeSummary({ liked = 0, saved = 0, total = 0, onRestart }) {
  const navigate = useNavigate();
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card text-center max-w-md mx-auto"
    >
      <div className="w-16 h-16 bg-gold/15 rounded-full flex items-center justify-center mx-auto mb-5">
        <Star size={30} className="text-gold" fill="currentColor" />
      </div>
      <h2 className="font-display text-3xl mb-2 text-ink">Session Complete</h2>
      <p className="text-muted text-sm mb-8">You reviewed {total} outfits.</p>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-ok/10 rounded-2xl p-4">
          <div className="font-display text-3xl text-ok mb-1">{liked}</div>
          <div className="text-2xs font-bold tracking-widest uppercase text-ok/80">Liked</div>
        </div>
        <div className="bg-gold/10 rounded-2xl p-4">
          <div className="font-display text-3xl text-gold mb-1">{saved}</div>
          <div className="text-2xs font-bold tracking-widest uppercase text-gold/80">Saved</div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <button onClick={() => navigate(ROUTES.MY_OUTFITS)} className="btn-gold w-full justify-center">
          <Heart size={16} /> View Saved Outfits
        </button>
        <button onClick={onRestart} className="btn-secondary w-full justify-center">
          <RefreshCw size={16} /> Start New Session
        </button>
      </div>
    </motion.div>
  );
}
