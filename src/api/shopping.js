import { apiClient } from '@/lib/apiClient'

/**
 * shopping.js
 * Shopping list management and AI gap-analysis recommendations.
 */

/** Get the user's shopping wishlist. */
export async function getShoppingList() {
  const { data } = await apiClient.get('/api/shopping')
  return data // { items: ShoppingItem[] }
}

/** Add an item to the shopping list. */
export async function addShoppingItem(payload) {
  // payload: { name, category, colour?, url?, notes?, image_url? }
  const { data } = await apiClient.post('/api/shopping', payload)
  return data
}

/** Update a shopping item (e.g. mark as purchased). */
export async function updateShoppingItem(itemId, payload) {
  const { data } = await apiClient.patch(`/api/shopping/${itemId}`, payload)
  return data
}

/** Delete a shopping item. */
export async function deleteShoppingItem(itemId) {
  await apiClient.delete(`/api/shopping/${itemId}`)
}

/**
 * Upload a screenshot / inspo image for shopping.
 * Backend stores it in Azure and returns a public URL.
 */
export async function uploadShoppingImage(imageFile) {
  const form = new FormData()
  form.append('image', imageFile)

  const { data } = await apiClient.post('/api/shopping/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data // { url: string, item_id: string }
}

/**
 * AI gap analysis: suggest what to buy to complete the wardrobe.
 * @param {object} params - { occasion?, budget?, style_goal? }
 */
export async function getShoppingRecommendations(params = {}) {
  const { data } = await apiClient.post('/api/shopping/recommend', params)
  return data // { recommendations: Recommendation[] }
}
