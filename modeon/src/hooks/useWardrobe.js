import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listWardrobeItems,
  deleteWardrobeItem,
  updateWardrobeItem,
  addWardrobeItem,
} from '@/api/wardrobe';
import useWardrobeStore from '@/stores/useWardrobeStore';
import useUIStore from '@/stores/useUIStore';

export const WARDROBE_KEY = ['wardrobe'];

function uploadWardrobeItems(files) {
  const file = files?.[0];
  if (!file) {
    throw new Error('No file provided.');
  }
  return addWardrobeItem(file, {});
}

export function useWardrobe(filters = {}) {
  const setItems = useWardrobeStore((s) => s.setItems);

  return useQuery({
    queryKey: [...WARDROBE_KEY, filters],
    queryFn: () => listWardrobeItems(filters),
    onSuccess: (data) => setItems(data.items ?? []),
  });
}

export function useDeleteWardrobeItem() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (itemId) => deleteWardrobeItem(itemId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: WARDROBE_KEY });
      addToast({ type: 'success', message: 'Item removed from wardrobe.' });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to remove item.' });
    },
  });
}

export function useTagWardrobeItem() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: ({ itemId, tags }) => updateWardrobeItem(itemId, tags),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: WARDROBE_KEY });
      addToast({ type: 'success', message: 'Tags updated.' });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to update tags.' });
    },
  });
}

export function useUploadWardrobeItems() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (files) => uploadWardrobeItems(files),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: WARDROBE_KEY });
      addToast({ type: 'success', message: 'Item uploaded to wardrobe.' });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to upload item.' });
    },
  });
}
