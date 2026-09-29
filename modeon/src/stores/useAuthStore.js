import { create } from 'zustand'
import { supabase } from '@/lib/supabase'
import { identifyUser, resetUser } from '@/lib/posthog'

const useAuthStore = create((set, get) => ({
  user: null,
  session: null,
  loading: true,   // true until first onAuthStateChange fires

  // ── Bootstrap: call once in App.jsx ────────────────────────────────────────
  init: () => {
    supabase.auth.getSession().then(({ data }) => {
      const session = data?.session ?? null
      const user    = session?.user ?? null
      set({ session, user, loading: false })
      if (user) identifyUser(user.id, { email: user.email })
    })

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        const user = session?.user ?? null
        set({ session, user, loading: false })
        if (user) {
          identifyUser(user.id, { email: user.email })
        } else {
          resetUser()
        }
      }
    )

    // Return cleanup so callers can unsubscribe if needed
    return () => listener.subscription.unsubscribe()
  },

  // ── Actions ────────────────────────────────────────────────────────────────
  signUp: async ({ email, password, fullName }) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } },
    })
    if (error) throw error
    return data
  },

  signIn: async ({ email, password }) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  },

  signInWithGoogle: async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) throw error
  },

  signOut: async () => {
    await supabase.auth.signOut()
    set({ user: null, session: null })
  },

  resetPassword: async (email) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset`,
    })
    if (error) throw error
  },

  updatePassword: async (newPassword) => {
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    if (error) throw error
  },

  // ── Selectors ──────────────────────────────────────────────────────────────
  isAuthenticated: () => !!get().user,
}))

export default useAuthStore
