// src/components/outfits/OutfitCardStack.jsx
import { useState, useEffect, useCallback } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import { OutfitCollage } from './OutfitCard';

const SWIPE_THRESHOLD = 100;

function SwipeCard({ outfit, onSwipe, isTop, offset }) {
  const x       = useMotionValue(0);
  const rotate  = useTransform(x, [-300, 300], [-18, 18]);
  const likeOp  = useTransform(x, [0, SWIPE_THRESHOLD],      [0, 1]);
  const skipOp  = useTransform(x, [-SWIPE_THRESHOLD, 0],     [1, 0]);

  const handleDragEnd = (_, info) => {
    if (info.offset.x > SWIPE_THRESHOLD)       onSwipe('like');
    else if (info.offset.x < -SWIPE_THRESHOLD) onSwipe('dislike');
  };

  return (
    <motion.div
      drag={isTop ? 'x' : false}
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      style={{
        x, rotate,
        position: 'absolute',
        width: '100%',
        scale: isTop ? 1 : 0.95 - offset * 0.02,
        y: offset * 14,
        zIndex: 10 - offset,
      }}
      className="cursor-grab active:cursor-grabbing select-none"
      whileTap={{ scale: 1.02 }}
    >
      <div className="bg-card border border-divider rounded-card shadow-float overflow-hidden">
        <OutfitCollage items={outfit.items} height={380} radius={0} />

        {/* Like overlay */}
        <motion.div
          style={{ opacity: likeOp }}
          className="absolute inset-0 flex items-start justify-end p-6 pointer-events-none"
        >
          <div className="bg-ok text-white font-bold text-2xl px-5 py-2 rounded-xl rotate-12 border-4 border-white/60">
            LIKE ♥
          </div>
        </motion.div>

        {/* Skip overlay */}
        <motion.div
          style={{ opacity: skipOp }}
          className="absolute inset-0 flex items-start justify-start p-6 pointer-events-none"
        >
          <div className="bg-danger text-white font-bold text-2xl px-5 py-2 rounded-xl -rotate-12 border-4 border-white/60">
            SKIP ✕
          </div>
        </motion.div>

        <div className="p-6">
          <p className="text-sm text-taupe italic leading-relaxed">{outfit.explanation}</p>
        </div>
      </div>
    </motion.div>
  );
}

export default function OutfitCardStack({ outfits, onSwipe, onSave }) {
  const [queue, setQueue]   = useState(outfits);
  const [exiting, setExiting] = useState(null);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e) => {
      if (!queue.length) return;
      if (e.key === 'ArrowRight') handleSwipe('like');
      if (e.key === 'ArrowLeft')  handleSwipe('dislike');
      if (e.key === 'ArrowUp')    handleSave();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [queue]);

  const handleSwipe = useCallback((direction) => {
    if (!queue.length) return;
    const [top, ...rest] = queue;
    onSwipe?.(top, direction);
    setQueue(rest);
  }, [queue, onSwipe]);

  const handleSave = useCallback(() => {
    if (!queue.length) return;
    const [top, ...rest] = queue;
    onSave?.(top);
    setQueue(rest);
  }, [queue, onSave]);

  return (
    <div className="relative w-full max-w-md mx-auto" style={{ height: 520 }}>
      <AnimatePresence>
        {queue.slice(0, 3).map((outfit, i) => (
          <SwipeCard
            key={outfit.id}
            outfit={outfit}
            isTop={i === 0}
            offset={i}
            onSwipe={i === 0 ? handleSwipe : undefined}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
