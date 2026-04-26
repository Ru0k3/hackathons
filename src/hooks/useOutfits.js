import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listOutfits,
  createOutfit,
  updateOutfit,
  deleteOutfit,
  generateOutfits,
} from '@/api/outfits';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';

export const OUTFITS_KEY = ['outfits'];

export function useSavedOutfits(page = 1) {
  return useQuery({
    queryKey: [...OUTFITS_KEY, page],
    queryFn: () => listOutfits({ page }),
  });
}

export function useGenerateOutfit() {
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (params) => generateOutfits(params),
    onSuccess: () => {
      trackEvent('outfit_generated');
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to generate outfit.' });
    },
  });
}

export function useSaveOutfit() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: ({ outfitId, meta }) => createOutfit({ ...(meta ?? {}) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: OUTFITS_KEY });
      addToast({ type: 'success', message: 'Outfit saved!' });
      trackEvent('outfit_saved');
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to save outfit.' });
    },
  });
}

export function useRateOutfit() {
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: ({ outfitId, rating }) => updateOutfit(outfitId, { rating }),
    onSuccess: (_, { rating }) => {
      trackEvent('outfit_rated', { rating });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to rate outfit.' });
    },
  });
}

export function useDeleteOutfit() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (outfitId) => deleteOutfit(outfitId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: OUTFITS_KEY });
      addToast({ type: 'success', message: 'Outfit removed.' });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to delete outfit.' });
    },
  });
}
