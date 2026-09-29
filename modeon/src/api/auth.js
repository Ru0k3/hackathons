/**
 * auth.js
 * All auth operations go through the Supabase client directly via
 * useAuthStore. This file exposes the profile endpoint (backend-persisted
 * data beyond what Supabase stores).
 */
import { apiClient } from '@/lib/apiClient'

/** Fetch the current user's profile from the backend. */
export async function getProfile() {
  const { data } = await apiClient.get('/api/profile')
  return data
}

/** Create or update the profile (called after onboarding). */
export async function upsertProfile(payload) {
  const { data } = await apiClient.put('/api/profile', payload)
  return data
}

/** Delete the account and all associated data (GDPR). */
export async function deleteAccount() {
  await apiClient.delete('/api/account')
}

/** Export all user data as JSON (GDPR portability). */
export async function exportAccountData() {
  const { data } = await apiClient.get('/api/account/export')
  return data
}
