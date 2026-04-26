// src/components/outfits/DailyOutfitCard.jsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { X, Heart, RefreshCw, Star, Sparkles } from 'lucide-react';
import useUIStore from '@/stores/useUIStore';
import { useGenerateOutfit, useSaveOutfit } from '@/hooks/useOutfits';

export default function DailyOutfitCard() {
  const addToast = useUIStore((s) => s.addToast);
  const { mutate: generate, data: generatedData, isPending: generating } = useGenerateOutfit();
  const { mutate: save, isPending: saving } = useSaveOutfit();

  const [liked, setLiked] = useState(null); // null | true | false
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    generate({ occasion: 'casual', n: 1 });
  }, []);

  const outfit = generatedData?.outfits?.[0] ?? null;

  useEffect(() => {
    setSaved(false);
  }, [outfit?.id]);

  const handleTryAnother = () => {
    generate({ occasion: 'casual', n: 1 });
  };

  const handleSave = () => {
    save({ outfitId: outfit?.id, meta: outfit ?? {} });
    setSaved(true);
  };

  const items = outfit?.items ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card flex flex-col relative overflow-hidden"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <span className="badge">Today's Selection</span>
          <h2 className="font-display text-3xl mt-2">{outfit?.name ?? 'Generating your look...'}</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setLiked(false);
              addToast({ type: 'info', message: "Noted! We'll refine your suggestions." });
            }}
            aria-label="Dislike outfit"
            className={`w-10 h-10 rounded-full border flex items-center justify-center transition-all
              ${liked === false ? 'border-danger bg-danger/10 text-danger' : 'border-divider bg-card text-danger hover:border-danger'}`}
          >
            <X size={18} />
          </button>
          <button
            onClick={() => {
              setLiked(true);
              addToast({ type: 'success', message: 'Loved! Your style profile is updating.' });
            }}
            aria-label="Like outfit"
            className={`w-10 h-10 rounded-full border flex items-center justify-center transition-all
              ${liked === true ? 'border-ok bg-ok/10 text-ok' : 'border-divider bg-card text-ok hover:border-ok'}`}
          >
            <Heart size={18} fill={liked === true ? 'currentColor' : 'none'} />
          </button>
        </div>
      </div>

      {/* Collage */}
      {generating || !outfit ? (
        <div className="min-h-[280px] flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin mx-auto my-12" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-3 mb-6 min-h-[280px]">
            <div className="rounded-2xl overflow-hidden col-span-1">
              <img src={items[0]} className="w-full h-full object-cover" alt="Blazer" />
            </div>
            <div className="flex flex-col gap-3">
              <div className="rounded-2xl overflow-hidden flex-1">
                <img src={items[1]} className="w-full h-full object-cover" alt="Shoes" />
              </div>
              <div className="rounded-2xl overflow-hidden flex-1">
                <img src={items[2]} className="w-full h-full object-cover" alt="Top" />
              </div>
            </div>
            <div className="rounded-2xl overflow-hidden col-span-1">
              <img src={items[3]} className="w-full h-full object-cover" alt="Bag" />
            </div>
          </div>

          {/* Explanation */}
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl px-6 py-5 border border-white/70 mb-5">
            <p className="italic leading-relaxed text-taupe text-sm">{outfit.explanation}</p>
          </div>
        </>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={handleTryAnother} className="btn-secondary flex-1 justify-center">
          <RefreshCw size={15} /> Try Another
        </button>
        <button
          onClick={handleSave}
          disabled={saved || saving || !outfit}
          className="btn-gold flex-1 justify-center"
          aria-label="Save outfit"
        >
          <Star size={15} fill={saved ? 'white' : 'none'} />
          {saved ? 'Saved!' : 'Save Outfit'}
        </button>
      </div>

      {/* Decorative circle */}
      <div className="absolute -bottom-16 -right-16 w-48 h-48 bg-gold/8 rounded-full pointer-events-none" />
    </motion.div>
  );
}
