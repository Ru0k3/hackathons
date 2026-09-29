import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import useAuthStore from '@/stores/useAuthStore'
import { trackEvent } from '@/lib/posthog'

export default function RegisterPage() {
  const navigate         = useNavigate()
  const signUp           = useAuthStore((s) => s.signUp)
  const signInWithGoogle = useAuthStore((s) => s.signInWithGoogle)

  const [fullName,  setFullName]  = useState('')
  const [email,     setEmail]     = useState('')
  const [password,  setPassword]  = useState('')
  const [confirm,   setConfirm]   = useState('')
  const [error,     setError]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const [verifyMsg, setVerifyMsg] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      await signUp({ email, password, fullName })
      trackEvent('sign_up', { method: 'email' })
      // Supabase sends a confirmation email; user lands on /onboarding after verifying
      setVerifyMsg(true)
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
      trackEvent('sign_up', { method: 'google' })
    } catch (err) {
      setError(err.message)
    }
  }

  if (verifyMsg) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-logo">ModeOn</div>
          <h1 className="auth-title">Check your inbox</h1>
          <p className="auth-success">
            We sent a confirmation link to <strong>{email}</strong>. Click it to
            activate your account and get started.
          </p>
          <p className="auth-footer">
            <Link to="/login" className="auth-link">Back to sign in</Link>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">ModeOn</div>
        <h1 className="auth-title">Create your account</h1>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <p className="auth-error">{error}</p>}

          <label className="auth-label">
            Full name
            <input
              type="text"
              className="auth-input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
              required
            />
          </label>

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
              autoComplete="new-password"
              minLength={8}
              required
            />
          </label>

          <label className="auth-label">
            Confirm password
            <input
              type="password"
              className="auth-input"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
              required
            />
          </label>

          <button
            type="submit"
            className="btn-primary auth-submit"
            disabled={loading}
          >
            {loading ? 'Creating account…' : 'Create account'}
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

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
