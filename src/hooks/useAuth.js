import { useCallback } from 'react';
import useAuthStore from '@/stores/useAuthStore';
import useUIStore from '@/stores/useUIStore';
import { trackEvent } from '@/lib/posthog';

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const session = useAuthStore((s) => s.session);
  const isAuthenticatedSelector = useAuthStore((s) => s.isAuthenticated);
  const addToast = useUIStore((s) => s.addToast);

  const handleLogin = useCallback(async ({ email, password }) => {
    try {
      const result = await useAuthStore.getState().signIn({ email, password });
      if (result?.session) {
        trackEvent('user_logged_in', { method: 'email' });
      }
      return result;
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Login failed' });
      throw err;
    }
  }, [addToast]);

  const handleRegister = useCallback(async ({ email, password, displayName }) => {
    try {
      const result = await useAuthStore
        .getState()
        .signUp({ email, password, fullName: displayName });
      trackEvent('user_registered', { method: 'email' });
      return result;
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Registration failed' });
      throw err;
    }
  }, [addToast]);

  const handleLogout = useCallback(async () => {
    await useAuthStore.getState().signOut();
  }, []);

  const handleMicrosoftLogin = useCallback(async () => {
    await useAuthStore.getState().signInWithGoogle();
  }, []);

  const handleResetPassword = useCallback(async ({ email }) => {
    await useAuthStore.getState().resetPassword(email);
    addToast({ type: 'success', message: 'Password reset email sent!' });
  }, [addToast]);

  return {
    user,
    session,
    isAuthenticated: typeof isAuthenticatedSelector === 'function'
      ? isAuthenticatedSelector()
      : !!isAuthenticatedSelector,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    loginMicrosoft: handleMicrosoftLogin,
    resetPassword: handleResetPassword,
  };
}
