import { apiClient } from '@/lib/apiClient'

/**
 * wardrobe.js
 * CRUD for wardrobe items. Images are uploaded as multipart/form-data;
 * all other operations are JSON.
 */

/** List all wardrobe items for the current user. */
export async function listWardrobeItems(params = {}) {
  const { data } = await apiClient.get('/api/wardrobe', { params })
  return data // { items: WardrobeItem[], total: number }
}

/** Fetch a single wardrobe item by ID. */
export async function getWardrobeItem(itemId) {
  const { data } = await apiClient.get(`/api/wardrobe/${itemId}`)
  return data
}

/**
 * Upload a new wardrobe item with image.
 * @param {File}   imageFile - The image file to upload.
 * @param {object} metadata  - { category, colour, brand, tags, ... }
 */
export async function addWardrobeItem(imageFile, metadata = {}) {
  const form = new FormData()
  form.append('image', imageFile)
  form.append('metadata', JSON.stringify(metadata))

  const { data } = await apiClient.post('/api/wardrobe', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/** Update metadata for an existing wardrobe item (no image change). */
export async function updateWardrobeItem(itemId, metadata) {
  const { data } = await apiClient.patch(`/api/wardrobe/${itemId}`, metadata)
  return data
}

/** Delete a wardrobe item (also removes blobs from Azure). */
export async function deleteWardrobeItem(itemId) {
  await apiClient.delete(`/api/wardrobe/${itemId}`)
}

/** Get AI-generated tags/category suggestion for an image before saving. */
export async function classifyImage(imageFile) {
  const form = new FormData()
  form.append('image', imageFile)

  const { data } = await apiClient.post('/api/wardrobe/classify', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data // { category, colour, tags, description }
}
