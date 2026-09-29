import { useEffect } from 'react'
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '@/stores/useAuthStore'

export function ProtectedRoute() {
  const user = useAuthStore((s) => s.user)
  const loading = useAuthStore((s) => s.loading)
  const location = useLocation()

  if (loading) {
    return (
      <div className="auth-loading">
        <span className="spinner" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}

export function AuthCallback() {
  const user = useAuthStore((s) => s.user)
  const loading = useAuthStore((s) => s.loading)
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && user) {
      navigate('/onboarding', { replace: true })
    } else if (!loading && !user) {
      navigate('/login', { replace: true })
    }
  }, [user, loading, navigate])

  return (
    <div className="auth-loading">
      <span className="spinner" />
      <p>Signing you in...</p>
    </div>
  )
}

export function GuestRoute() {
  const user = useAuthStore((s) => s.user)
  const loading = useAuthStore((s) => s.loading)

  if (loading) return null
  if (user) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
