import { apiClient } from '@/lib/apiClient'

/**
 * outfitCheck.js
 * Upload a photo of an outfit and receive AI feedback.
 */

/**
 * Submit an outfit photo for AI critique.
 * @param {File}   imageFile
 * @param {object} context   - { occasion?, weather?, style_goal? }
 * @returns {Promise<OutfitCheckResult>}
 */
export async function checkOutfit(imageFile, context = {}) {
  const form = new FormData()
  form.append('image', imageFile)
  form.append('context', JSON.stringify(context))

  const { data } = await apiClient.post('/api/outfit-check', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
  /*
    Returns: {
      score: number,          // 0–100
      verdict: string,        // e.g. "Great fit for a casual Friday"
      pros: string[],
      cons: string[],
      suggestions: string[],
      detected_items: string[],
    }
  */
}

/** Get outfit check history for the current user. */
export async function listOutfitChecks(params = {}) {
  const { data } = await apiClient.get('/api/outfit-check/history', { params })
  return data
}
