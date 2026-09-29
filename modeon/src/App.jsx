import { lazy, Suspense, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from '@/stores/useAuthStore'
import {
  ProtectedRoute,
  GuestRoute,
  AuthCallback,
} from '@/components/auth/ProtectedRoute'

const AccountPage = lazy(() => import('@/pages/AccountPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const ForgotPasswordPage = lazy(() => import('@/pages/ForgotPasswordPage'))
const LandingPage = lazy(() => import('@/pages/LandingPage'))
const MixMatchPage = lazy(() => import('@/pages/MixMatchPage'))
const MyOutfitsPage = lazy(() => import('@/pages/MyOutfitsPage'))
const OccasionStylingPage = lazy(() => import('@/pages/OccasionStylingPage'))
const PublicOutfitPage = lazy(() => import('@/pages/PublicOutfitPage'))
const SwipeSessionPage = lazy(() => import('@/pages/SwipeSessionPage'))

const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const OnboardingPage = lazy(() => import('@/pages/OnboardingPage'))
const WardrobePage = lazy(() => import('@/pages/WardrobePage'))
const OutfitsPage = lazy(() => import('@/pages/OutfitsPage'))
const OutfitCheckPage = lazy(() => import('@/pages/OutfitCheckPage'))
const ShoppingPage = lazy(() => import('@/pages/ShoppingPage'))
const LaundryPage = lazy(() => import('@/pages/LaundryPage'))
const ProfilePage = lazy(() => import('@/pages/ProfilePage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

function PageLoader() {
  return (
    <div className="page-loader">
      <span className="spinner" />
    </div>
  )
}

export default function App() {
  const initAuth = useAuthStore((s) => s.init)

  useEffect(() => {
    const cleanup = initAuth()
    return cleanup
  }, [initAuth])

  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route element={<GuestRoute />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          </Route>

          <Route path="/shared/:token" element={<PublicOutfitPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="/wardrobe" element={<WardrobePage />} />
            <Route path="/outfits" element={<OutfitsPage />} />
            <Route path="/outfits/saved" element={<MyOutfitsPage />} />
            <Route path="/outfits/swipe" element={<SwipeSessionPage />} />
            <Route path="/outfit-check" element={<OutfitCheckPage />} />
            <Route path="/shopping" element={<ShoppingPage />} />
            <Route path="/laundry" element={<LaundryPage />} />
            <Route path="/mix-match" element={<MixMatchPage />} />
            <Route path="/occasion" element={<OccasionStylingPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/account" element={<AccountPage />} />
            <Route path="/pricing" element={<Navigate to="/dashboard" replace />} />
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
