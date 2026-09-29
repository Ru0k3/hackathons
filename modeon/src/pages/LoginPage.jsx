import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '@/stores/useAuthStore'
import { trackEvent } from '@/lib/posthog'

export default function LoginPage() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const from      = location.state?.from?.pathname ?? '/dashboard'

  const signIn           = useAuthStore((s) => s.signIn)
  const signInWithGoogle = useAuthStore((s) => s.signInWithGoogle)
  const resetPassword    = useAuthStore((s) => s.resetPassword)

  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [resetSent, setResetSent] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await signIn({ email, password })
      trackEvent('login', { method: 'email' })
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogle() {
    setError('')
    try {
      await signInWithGoogle()
      trackEvent('login', { method: 'google' })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleForgotPassword() {
    if (!email) {
      setError('Enter your email address above, then click "Forgot password".')
      return
    }
    setError('')
    setLoading(true)
    try {
      await resetPassword(email)
      setResetSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">ModeOn</div>
        <h1 className="auth-title">Welcome back</h1>

        {resetSent ? (
          <p className="auth-success">
            Check your inbox — we sent a password reset link to <strong>{email}</strong>.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form">
            {error && <p className="auth-error">{error}</p>}

            <label className="auth-label">
              Email
              <input
                type="email"
                className="auth-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </label>

            <label className="auth-label">
              Password
              <input
                type="password"
                className="auth-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            <button
              type="button"
              className="auth-link-btn"
              onClick={handleForgotPassword}
            >
              Forgot password?
            </button>

            <button
              type="submit"
              className="btn-primary auth-submit"
              disabled={loading}
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>

            <div className="auth-divider"><span>or</span></div>

            <button
              type="button"
              className="btn-secondary auth-google"
              onClick={handleGoogle}
            >
              Continue with Google
            </button>
          </form>
        )}

        <p className="auth-footer">
          Don't have an account?{' '}
          <Link to="/register" className="auth-link">Create one</Link>
        </p>
      </div>
    </div>
  )
}
