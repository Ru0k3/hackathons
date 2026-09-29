import { apiClient } from '@/lib/apiClient'

/**
 * outfits.js
 * Saved outfits and AI outfit generation.
 */

/** List all saved outfits. */
export async function listOutfits(params = {}) {
  const { data } = await apiClient.get('/api/outfits', { params })
  return data // { outfits: Outfit[], total: number }
}

/** Get a single outfit. */
export async function getOutfit(outfitId) {
  const { data } = await apiClient.get(`/api/outfits/${outfitId}`)
  return data
}

/** Save a new outfit (manually curated list of wardrobe item IDs). */
export async function createOutfit(payload) {
  // payload: { name, item_ids: string[], occasion?, notes? }
  const { data } = await apiClient.post('/api/outfits', payload)
  return data
}

/** Update an existing outfit. */
export async function updateOutfit(outfitId, payload) {
  const { data } = await apiClient.patch(`/api/outfits/${outfitId}`, payload)
  return data
}

/** Delete an outfit. */
export async function deleteOutfit(outfitId) {
  await apiClient.delete(`/api/outfits/${outfitId}`)
}

/**
 * Ask AI to generate outfit suggestions.
 * @param {object} params - { occasion, weather?, mood?, exclude_item_ids? }
 */
export async function generateOutfits(params) {
  const { data } = await apiClient.post('/api/outfits/generate', params)
  return data // { outfits: GeneratedOutfit[] }
}

/**
 * Mix-and-match: get items that pair well with a given item.
 * @param {string} itemId
 * @param {object} params - { occasion?, limit? }
 */
export async function getMixMatch(itemId, params = {}) {
  const { data } = await apiClient.get(`/api/outfits/mix-match/${itemId}`, {
    params,
  })
  return data // { suggestions: WardrobeItem[][] }
}

/**
 * Occasion styling: get outfit ideas for a specific event.
 * @param {object} params - { occasion, date?, weather?, style_preferences? }
 */
export async function getOccasionStyling(params) {
  const { data } = await apiClient.post('/api/outfits/occasion', params)
  return data // { outfits: GeneratedOutfit[] }
}
