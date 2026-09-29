import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getShoppingList,
  addShoppingItem,
  deleteShoppingItem,
  updateShoppingItem,
} from '@/api/shopping';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';

export const SHOPPING_LIST_KEY = ['shoppingList'];

export function useShoppingList() {
  return useQuery({
    queryKey: SHOPPING_LIST_KEY,
    queryFn: getShoppingList,
  });
}

export function useAddToShoppingList() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (uploadId) => addShoppingItem({ name: 'Saved item', id: uploadId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SHOPPING_LIST_KEY });
      addToast({ type: 'success', message: 'Item added to Shopping List.' });
      trackEvent('shopping_item_saved');
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to add item.' });
    },
  });
}

export function useDeleteFromShoppingList() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (itemId) => deleteShoppingItem(itemId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SHOPPING_LIST_KEY });
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to delete item.' });
    },
  });
}

export function useMoveToWardrobe() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  return useMutation({
    mutationFn: (itemId) => {
      // TODO: full move-to-wardrobe via /api/shopping-list/:id/move-to-wardrobe
      return updateShoppingItem(itemId, { purchased: true });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SHOPPING_LIST_KEY });
      addToast({ type: 'success', message: 'Item moved to Wardrobe!' });
      trackEvent('shopping_list_item_moved_to_wardrobe');
    },
    onError: (err) => {
      addToast({ type: 'error', message: err?.message || 'Failed to move item.' });
    },
  });
}
