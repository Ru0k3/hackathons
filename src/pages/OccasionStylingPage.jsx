// src/pages/OccasionStylingPage.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Heart } from 'lucide-react';
import PageWrapper from '@/components/layout/PageWrapper';
import { OutfitCollage } from '@/components/outfits/OutfitCard';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';
import { getOccasionStyling } from '@/api/outfits';

const OCCASIONS = [
  { id: 'casual', label: 'Casual', emoji: '\u2615' },
  { id: 'work', label: 'Work', emoji: '\uD83D\uDCBC' },
  { id: 'date', label: 'Date Night', emoji: '\uD83C\uDF19' },
  { id: 'formal', label: 'Formal', emoji: '\u2728' },
  { id: 'brunch', label: 'Weekend Brunch', emoji: '\uD83C\uDF3F' },
  { id: 'travel', label: 'Travel', emoji: '\u2708\uFE0F' },
  { id: 'gym', label: 'Gym', emoji: '\uD83C\uDFC3' },
  { id: 'beach', label: 'Beach', emoji: '\uD83C\uDF0A' },
];

export default function OccasionStylingPage() {
  const addToast = useUIStore((s) => s.addToast);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [outfits, setOutfits] = useState([]);
  const [saved, setSaved] = useState(new Set());

  const handleSelect = async (occ) => {
    setSelected(occ.id);
    setOutfits([]);
    setLoading(true);
    trackEvent('swipe_session_started', { occasion: occ.id });

    try {
      const data = await getOccasionStyling({ occasion: occ.id });
      setOutfits(data?.outfits ?? []);
    } catch {
      addToast({ type: 'error', message: 'Failed to load outfits.' });
      setOutfits([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = (id) => {
    setSaved((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

    addToast({ type: 'success', message: saved.has(id) ? 'Outfit removed.' : 'Outfit saved!' });
    trackEvent('outfit_saved', { source: 'occasion' });
  };

  return (
    <PageWrapper>
      <header className="mb-8">
        <h1 className="font-display text-4xl md:text-5xl mb-1">Occasion Styling</h1>
        <p className="text-sm text-muted italic">Pick an occasion. Get outfits tailored for it.</p>
      </header>

      {/* Occasion grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {OCCASIONS.map((occ) => (
          <button
            key={occ.id}
            onClick={() => handleSelect(occ)}
            className={`rounded-2xl p-5 border transition-all text-left flex flex-col gap-2 ${selected === occ.id ? 'bg-gold text-white border-gold shadow-gold' : 'bg-card border-divider hover:border-gold/60 text-ink'}`}
            aria-label={`Show ${occ.label} outfits`}
            aria-pressed={selected === occ.id}
          >
            <span className="text-2xl">{occ.emoji}</span>
            <span className="text-xs font-bold tracking-widest uppercase">{occ.label}</span>
          </button>
        ))}
      </div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {loading && (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center py-20 gap-4">
            <div className="w-10 h-10 border-2 border-gold border-t-transparent rounded-full animate-spin" />
            <p className="text-muted font-medium">Generating occasion outfits...</p>
          </motion.div>
        )}

        {!loading && outfits.length > 0 && (
          <motion.div key="results" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="font-display text-2xl mb-6">
              {OCCASIONS.find((o) => o.id === selected)?.emoji} {OCCASIONS.find((o) => o.id === selected)?.label} Outfits
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {outfits.map((outfit, i) => (
                <motion.div key={outfit.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="card overflow-hidden">
                  <OutfitCollage items={outfit.items} height={280} radius={12} />
                  <div className="mt-5 flex flex-col gap-3">
                    <p className="text-sm text-taupe italic leading-relaxed">{outfit.explanation}</p>
                    <button
                      onClick={() => handleSave(outfit.id)}
                      className={saved.has(outfit.id) ? 'btn-gold w-full justify-center' : 'btn-secondary w-full justify-center'}
                      aria-label={saved.has(outfit.id) ? 'Saved' : 'Save outfit'}
                    >
                      <Heart size={14} fill={saved.has(outfit.id) ? 'currentColor' : 'none'} />
                      {saved.has(outfit.id) ? 'Saved' : 'Save Outfit'}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {!loading && !outfits.length && (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
            <Calendar size={48} className="text-muted/40 mx-auto mb-4" />
            <p className="font-display text-xl text-ink mb-2">Choose an occasion above</p>
            <p className="text-sm text-muted">AI will generate outfit suggestions from your wardrobe.</p>
          </motion.div>
        )}
      </AnimatePresence>
    </PageWrapper>
  );
}
