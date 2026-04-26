import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { OutfitCollage } from '@/components/outfits/OutfitCard'
import { ROUTES } from '@/constants/routes'
import { apiClient } from '@/lib/apiClient'

const DEFAULT_OUTFIT = {
  occasion: 'Shared Outfit',
  explanation: 'This outfit was shared from Modeon.',
  items: [],
}

function normaliseOutfit(payload) {
  if (!payload || typeof payload !== 'object') return DEFAULT_OUTFIT

  const items =
    (Array.isArray(payload.items) && payload.items) ||
    (Array.isArray(payload.image_urls) && payload.image_urls) ||
    (Array.isArray(payload.item_images) && payload.item_images) ||
    []

  return {
    occasion: payload.occasion || payload.name || DEFAULT_OUTFIT.occasion,
    explanation: payload.explanation || payload.notes || DEFAULT_OUTFIT.explanation,
    items: items.filter((item) => typeof item === 'string'),
  }
}

export default function PublicOutfitPage() {
  const { token } = useParams()
  const [outfit, setOutfit] = useState(DEFAULT_OUTFIT)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    async function loadPublicOutfit() {
      if (!token) {
        setError('Missing share token.')
        setLoading(false)
        return
      }
      setLoading(true)
      setError('')
      try {
        const { data } = await apiClient.get(`/api/outfits/public/${token}`)
        if (!active) return
        setOutfit(normaliseOutfit(data))
      } catch (err) {
        if (!active) return
        setError(err?.message || 'Unable to load shared outfit.')
      } finally {
        if (active) setLoading(false)
      }
    }
    loadPublicOutfit()
    return () => {
      active = false
    }
  }, [token])

  const heading = useMemo(
    () => `The ${outfit.occasion || 'Shared'} Ensemble`,
    [outfit.occasion],
  )

  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-divider">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-gold rounded-full flex items-center justify-center">
            <span className="font-display text-white font-bold text-base leading-none">M</span>
          </div>
          <span className="font-display font-bold text-lg text-ink">Modeon</span>
        </div>
        <Link to={ROUTES.REGISTER} className="btn-gold text-xs px-5 py-2.5" aria-label="Get Modeon free">
          <Sparkles size={13} /> Get Modeon Free
        </Link>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="card overflow-hidden p-0 relative">
            <OutfitCollage items={outfit.items} height={420} radius={0} />

            <div className="absolute bottom-4 right-4 flex items-center gap-1.5 bg-black/40 backdrop-blur-sm text-white rounded-chip px-3 py-1.5 text-2xs font-bold tracking-wide">
              <div className="w-4 h-4 bg-gold rounded-full flex items-center justify-center">
                <span className="font-display text-white font-bold text-xs leading-none">M</span>
              </div>
              Modeon
            </div>

            <div className="p-6">
              {loading ? (
                <p className="text-sm text-muted">Loading shared outfit...</p>
              ) : error ? (
                <p className="text-sm text-danger">{error}</p>
              ) : (
                <>
                  {outfit.occasion && (
                    <span className="badge mb-3 inline-block">{outfit.occasion}</span>
                  )}
                  <p className="font-display text-2xl mb-3">{heading}</p>
                  <p className="text-sm text-taupe italic leading-relaxed">{outfit.explanation}</p>
                </>
              )}
            </div>
          </div>

          <div className="text-center mt-8">
            <p className="text-sm text-muted mb-4">
              Want AI outfit suggestions from your own wardrobe?
            </p>
            <Link to={ROUTES.REGISTER} className="btn-gold" aria-label="Create your Modeon account">
              <Sparkles size={15} /> Create Your Own - Free
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
