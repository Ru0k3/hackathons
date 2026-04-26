import { apiClient } from '@/lib/apiClient'

/**
 * laundry.js
 * Track which items are dirty / in-wash / clean.
 */

/** Get the current laundry state for all wardrobe items. */
export async function getLaundryStatus() {
  const { data } = await apiClient.get('/api/laundry')
  return data // { items: LaundryItem[] }
}

/**
 * Update the laundry status of one or more items.
 * @param {Array<{ item_id: string, status: 'clean'|'dirty'|'washing' }>} updates
 */
export async function updateLaundryStatus(updates) {
  const { data } = await apiClient.patch('/api/laundry', { updates })
  return data
}

/** Mark all items in the basket as clean (post-laundry reset). */
export async function markAllClean() {
  const { data } = await apiClient.post('/api/laundry/reset')
  return data
}

/**
 * Get AI suggestions for what to wear based on what's currently clean.
 */
export async function getCleanOutfitSuggestions() {
  const { data } = await apiClient.get('/api/laundry/suggestions')
  return data // { outfits: GeneratedOutfit[] }
}
