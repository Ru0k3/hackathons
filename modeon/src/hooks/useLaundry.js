import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateLaundryStatus } from '@/api/laundry';
import useWardrobeStore from '@/stores/useWardrobeStore';
import useUIStore from '@/stores/useUIStore';
import { WARDROBE_KEY } from '@/hooks/useWardrobe';
import { trackEvent } from '@/lib/posthog';

export function useToggleLaundry() {
  const qc = useQueryClient();
  const upsertItem = useWardrobeStore((s) => s.upsertItem);
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: ({ itemId, inLaundry }) =>
      updateLaundryStatus([
        { item_id: itemId, status: inLaundry ? 'dirty' : 'clean' },
      ]),
    onMutate: ({ itemId, inLaundry }) => {
      upsertItem({ id: itemId, inLaundry });
    },
    onSuccess: (_, { inLaundry }) => {
      qc.invalidateQueries({ queryKey: WARDROBE_KEY });
      trackEvent(inLaundry ? 'laundry_item_marked' : 'laundry_item_unmarked');
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to update laundry status.' });
    },
  });
}

export function useBulkLaundry() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (updates) => updateLaundryStatus(updates),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: WARDROBE_KEY });
      addToast({ type: 'success', message: 'Laundry status updated.' });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to update laundry status.' });
    },
  });
}
