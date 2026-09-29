import { apiClient } from '@/lib/apiClient'

/**
 * export.js
 * Wardrobe export and outfit sharing.
 */

/**
 * Export the full wardrobe as a ZIP (images + metadata CSV).
 * Returns a Blob so the caller can trigger a browser download.
 */
export async function exportWardrobeZip() {
  const response = await apiClient.get('/api/account/export/wardrobe', {
    responseType: 'blob',
  })
  return response.data // Blob
}

/**
 * Export account data as JSON (GDPR portability).
 * Returns a Blob.
 */
export async function exportAccountJson() {
  const response = await apiClient.get('/api/account/export', {
    responseType: 'blob',
  })
  return response.data
}

/**
 * Create a shareable public link for a saved outfit.
 * @param {string} outfitId
 * @returns {{ share_url: string, expires_at: string }}
 */
export async function shareOutfit(outfitId) {
  const { data } = await apiClient.post(`/api/outfits/${outfitId}/share`)
  return data
}

/**
 * Revoke a previously generated share link.
 * @param {string} outfitId
 */
export async function revokeShareLink(outfitId) {
  await apiClient.delete(`/api/outfits/${outfitId}/share`)
}

// ── Helper: trigger a browser download from a Blob ────────────────────────────
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href     = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
