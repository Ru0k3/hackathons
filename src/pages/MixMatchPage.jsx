// src/pages/MixMatchPage.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Trash2, Sparkles, CheckCircle2 } from 'lucide-react';
import { useWardrobe } from '@/hooks/useWardrobe';
import { getMixMatch } from '@/api/outfits';
import { apiClient } from '@/lib/apiClient';
import PageWrapper from '@/components/layout/PageWrapper';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';

const SLOT_LABELS = ['Top', 'Bottom', 'Outerwear', 'Shoes', 'Accessory'];

export default function MixMatchPage() {
  const addToast = useUIStore((s) => s.addToast);
  const [canvas, setCanvas] = useState({}); // slotKey -> item
  const [scoring, setScoring] = useState(false);
  const [score, setScore] = useState(null);
  const { data, isLoading } = useWardrobe();
  const wardrobeItems = data?.items ?? [];
  void getMixMatch;

  const handleDrop = (slot, item) => {
    setCanvas((prev) => ({ ...prev, [slot]: item }));
    setScore(null);
  };

  const handleRemove = (slot) => {
    setCanvas((prev) => {
      const next = { ...prev };
      delete next[slot];
      return next;
    });
    setScore(null);
  };

  const handleScore = async () => {
    const count = Object.keys(canvas).length;
    if (count < 2) {
      addToast({ type: 'info', message: 'Add at least 2 items to score the combination.' });
      return;
    }

    setScoring(true);
    try {
      const item_ids = Object.values(canvas).map((i) => i.id);
      const { data: result } = await apiClient.post('/api/outfits/score', { item_ids });
      setScore(result.score);
      trackEvent('outfit_rated', { score: result.score });
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Scoring failed.' });
      setScore(null);
    } finally {
      setScoring(false);
    }
  };

  const scoreColor = score ? (score >= 80 ? 'text-ok' : score >= 60 ? 'text-gold' : 'text-danger') : 'text-ink';

  return (
    <PageWrapper>
      <header className="mb-8">
        <h1 className="font-display text-4xl md:text-5xl mb-1">Mix & Match</h1>
        <p className="text-sm text-muted italic">Drag pieces onto the canvas, then score the combination.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-8">
        {/* Canvas */}
        <div>
          <h2 className="font-display text-2xl mb-4">Canvas</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
            {SLOT_LABELS.map((slot) => {
              const item = canvas[slot];
              return (
                <div
                  key={slot}
                  className={`relative aspect-square rounded-2xl border-2 border-dashed flex flex-col items-center justify-center transition-all ${item ? 'border-gold/40 bg-gold/5' : 'border-divider bg-surface'}`}
                >
                  <div className="absolute top-2 left-2 bg-white/80 backdrop-blur-sm rounded-lg px-2 py-0.5 text-2xs font-bold tracking-wide uppercase text-taupe">{slot}</div>
                  {item ? (
                    <>
                      <img src={item.image_url} alt={item.category} className="w-full h-full object-cover rounded-2xl" />
                      <button
                        onClick={() => handleRemove(slot)}
                        className="absolute top-2 right-2 w-7 h-7 rounded-full bg-danger flex items-center justify-center text-white hover:opacity-80 transition-opacity"
                        aria-label="Remove item"
                      >
                        <Trash2 size={12} />
                      </button>
                    </>
                  ) : (
                    <div className="text-center px-4">
                      <Layers size={24} className="text-muted/40 mx-auto mb-2" />
                      <p className="text-2xs text-muted">Click a wardrobe item -&gt;</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Score section */}
          <div className="card flex flex-col md:flex-row items-center gap-5">
            <button onClick={handleScore} disabled={scoring} className="btn-gold flex-shrink-0">
              {scoring ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Scoring...</>
              ) : (
                <><Sparkles size={15} /> Score This Combination</>
              )}
            </button>
            {score && (
              <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-4">
                <div className={`font-display text-5xl ${scoreColor}`}>{score}</div>
                <div>
                  <p className="text-2xs font-bold tracking-widest uppercase text-muted mb-1">Compatibility Score</p>
                  <p className="text-sm text-taupe italic">
                    {score >= 80 ? 'Outstanding pairing. These pieces are made for each other.' :
                     score >= 60 ? 'Good combination with room for refinement.' :
                     'The pieces conflict in colour or formality.'}
                  </p>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Wardrobe picker */}
        <div>
          <h2 className="font-display text-2xl mb-4">Your Wardrobe</h2>
          <p className="text-sm text-muted mb-4">Click an item to add it to an open canvas slot.</p>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 max-h-[600px] overflow-y-auto pr-1">
              {wardrobeItems.map((item) => {
                const isOnCanvas = Object.values(canvas).some((c) => c.id === item.id);
                const firstEmpty = SLOT_LABELS.find((s) => !canvas[s]);
                return (
                  <button
                    key={item.id}
                    onClick={() => { if (!isOnCanvas && firstEmpty) handleDrop(firstEmpty, item); }}
                    disabled={isOnCanvas || !SLOT_LABELS.find((s) => !canvas[s])}
                    className={`relative aspect-square rounded-xl overflow-hidden border transition-all cursor-pointer group ${isOnCanvas ? 'opacity-40 border-gold cursor-default' : 'border-divider hover:border-gold/60 hover:scale-[1.02]'}`}
                    aria-label={`Add ${item.colour} ${item.category} to canvas`}
                  >
                    <img src={item.image_url} alt={item.category} className="w-full h-full object-cover" />
                    <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-2xs font-bold tracking-wide uppercase py-1.5 px-2">
                      {item.colour}
                    </div>
                    {isOnCanvas && (
                      <div className="absolute inset-0 bg-gold/20 flex items-center justify-center">
                        <CheckCircle2 size={24} className="text-gold" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
