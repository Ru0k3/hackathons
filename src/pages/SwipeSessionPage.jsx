// src/pages/SwipeSessionPage.jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { ROUTES } from '@/constants/routes';
import OutfitCardStack from '@/components/outfits/OutfitCardStack';
import SwipeControls from '@/components/outfits/SwipeControls';
import SwipeProgress from '@/components/outfits/SwipeProgress';
import SwipeSummary from '@/components/outfits/SwipeSummary';
import { useSwipeSession } from '@/hooks/useSwipeSession';

export default function SwipeSessionPage() {
  const navigate = useNavigate();
  const {
    currentOutfit,
    index,
    total,
    loading,
    done,
    liked,
    saved,
    startSession,
    swipe,
  } = useSwipeSession();

  useEffect(() => {
    startSession();
  }, [startSession]);

  const remaining = done ? 0 : Math.max(total - index, currentOutfit ? 1 : 0);

  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      {/* Top bar */}
      <div className="flex items-center px-8 py-5 border-b border-divider">
        <button onClick={() => navigate(ROUTES.DASHBOARD)} className="btn-ghost" aria-label="Back to dashboard">
          <ArrowLeft size={16} /> Back
        </button>
        <h1 className="font-display text-2xl mx-auto">Style Discovery</h1>
        <div className="w-24" />
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-6 py-10">
        {loading ? (
          <div className="w-10 h-10 border-2 border-gold border-t-transparent rounded-full animate-spin" />
        ) : done ? (
          <SwipeSummary
            liked={liked.length}
            saved={saved.length}
            total={total}
            onRestart={startSession}
          />
        ) : (
          <>
            <SwipeProgress current={remaining} total={total} />
            <OutfitCardStack
              key={currentOutfit?.id ?? 'empty'}
              outfits={currentOutfit ? [currentOutfit] : []}
              onSwipe={(_, direction) => swipe(direction)}
              onSave={() => swipe('save')}
            />
            <SwipeControls
              onDislike={() => swipe('dislike')}
              onSave={() => swipe('save')}
              onLike={() => swipe('like')}
              disabled={!currentOutfit}
            />
            <p className="text-2xs text-muted mt-6 font-medium">
              Dislike | Save | Like | or use arrow keys
            </p>
          </>
        )}
      </div>
    </div>
  );
}
