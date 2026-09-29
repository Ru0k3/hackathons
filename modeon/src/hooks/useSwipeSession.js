import { useState, useCallback } from 'react';
import { generateOutfits, updateOutfit } from '@/api/outfits';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';

const MOCK_OUTFITS = [
  {
    id: '1',
    items: [
      'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400',
      'https://images.unsplash.com/photo-1624372333454-da58f936a1bc?w=400',
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400',
    ],
    explanation:
      'A clean, sophisticated ensemble blending warm textures with structure. Ideal for crisp spring mornings.',
  },
  {
    id: '2',
    items: [
      'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400',
      'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400',
    ],
    explanation:
      'Elegant minimalist evening wear. The slip dress paired with block heels creates a timeless silhouette.',
  },
  {
    id: '3',
    items: [
      'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400',
      'https://images.unsplash.com/photo-1512412086892-cf0449fb024b?w=400',
    ],
    explanation:
      'Modern streetwear with a luxury twist. Oversized layers for an effortless architectural vibe.',
  },
  {
    id: '4',
    items: [
      'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400',
      'https://images.unsplash.com/photo-1535633302704-c0299ba4d9cb?w=400',
      'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400',
    ],
    explanation:
      'Tonal neutrals with golden accessory punctuation. This capsule works from coffee to cocktails.',
  },
  {
    id: '5',
    items: [
      'https://images.unsplash.com/photo-1596755094514-f87034a2612d?w=400',
      'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400',
    ],
    explanation:
      'Breezy summer combination - lightweight fabrics and warm cream tones for outdoor occasions.',
  },
];

async function getSwipeSession(params) {
  return generateOutfits({ occasion: params?.occasion ?? 'casual', n: 10 });
}

async function submitSwipe(outfitId, direction) {
  return updateOutfit(outfitId, {
    rating: direction === 'right' ? 'like' : 'dislike',
  });
}

export function useSwipeSession() {
  const [outfits, setOutfits] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [liked, setLiked] = useState([]);
  const [saved, setSaved] = useState([]);
  const addToast = useUIStore((s) => s.addToast);

  const startSession = useCallback(async (params) => {
    setLoading(true);
    setDone(false);
    setIndex(0);
    setLiked([]);
    setSaved([]);
    try {
      const result = await getSwipeSession(params);
      const generated = result?.outfits ?? [];
      setOutfits(generated.length ? generated : MOCK_OUTFITS);
      trackEvent('swipe_session_started');
    } catch (err) {
      setOutfits(MOCK_OUTFITS);
      addToast({ type: 'error', message: err?.message || 'Failed to start swipe session.' });
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  const swipe = useCallback(async (direction) => {
    const current = outfits[index];
    if (!current) return;

    const normalizedDirection =
      direction === 'right' || direction === 'like' || direction === 'save' ? 'right' : 'left';

    await submitSwipe(current.id, normalizedDirection).catch(() => {});
    trackEvent('outfit_swiped', { direction });

    if (direction === 'like' || direction === 'right') setLiked((p) => [...p, current]);
    if (direction === 'save') setSaved((p) => [...p, current]);

    const next = index + 1;
    if (next >= outfits.length) {
      setDone(true);
    } else {
      setIndex(next);
    }
  }, [outfits, index]);

  return {
    outfits,
    currentOutfit: outfits[index] ?? null,
    index,
    total: outfits.length,
    loading,
    done,
    liked,
    saved,
    startSession,
    swipe,
  };
}
