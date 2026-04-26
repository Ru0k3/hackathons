import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home,
  Shirt,
  Sparkles,
  Heart,
  Layers,
  Calendar,
  Wand2,
  CheckCircle2,
  ShoppingBag,
  Waves,
  User,
  Crown,
} from 'lucide-react'
import { ROUTES } from '@/constants/routes'
import useAuthStore from '@/stores/useAuthStore'

const NAV = [
  { icon: Home, label: 'Dashboard', to: ROUTES.DASHBOARD },
  { icon: Shirt, label: 'Wardrobe', to: ROUTES.WARDROBE },
  { icon: Wand2, label: 'Outfits', to: ROUTES.OUTFITS },
  { icon: Heart, label: 'My Outfits', to: ROUTES.MY_OUTFITS },
  { icon: Sparkles, label: 'Swipe', to: ROUTES.SWIPE },
  { icon: Layers, label: 'Mix & Match', to: ROUTES.MIX_MATCH },
  { icon: Calendar, label: 'Occasion Styling', to: ROUTES.OCCASION },
  { icon: CheckCircle2, label: 'Outfit Check', to: ROUTES.OUTFIT_CHECK },
  { icon: ShoppingBag, label: 'Shopping', to: ROUTES.SHOPPING },
  { icon: Waves, label: 'Laundry', to: ROUTES.LAUNDRY },
  { icon: User, label: 'Profile', to: ROUTES.ACCOUNT },
]

export default function Sidebar() {
  const [expanded, setExpanded] = useState(false)
  const user = useAuthStore((s) => s.user)

  const initials = user?.email?.[0]?.toUpperCase() ?? 'U'

  return (
    <motion.aside
      initial={false}
      animate={{ width: expanded ? 220 : 76 }}
      transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      onHoverStart={() => setExpanded(true)}
      onHoverEnd={() => setExpanded(false)}
      className="fixed left-0 top-0 h-screen bg-surface border-r border-divider flex flex-col z-50 overflow-hidden"
    >
      <div className="h-[76px] flex items-center pl-6 gap-3.5 flex-shrink-0 mt-2">
        <div className="w-7 h-7 bg-gold rounded-full flex items-center justify-center flex-shrink-0">
          <span className="font-display text-white font-bold text-sm leading-none">M</span>
        </div>
        <AnimatePresence>
          {expanded && (
            <motion.span
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              className="font-display font-bold text-lg whitespace-nowrap text-ink"
            >
              Modeon
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <nav className="flex-1 pt-2" aria-label="Main navigation">
        {NAV.map(({ icon: Icon, label, to }) => (
          <NavLink
            key={to}
            to={to}
            aria-label={label}
            className={({ isActive }) =>
              `flex items-center h-[50px] w-full border-0 cursor-pointer transition-all ${
                isActive
                  ? 'text-gold border-l-[3px] border-gold bg-gold/10'
                  : 'text-muted border-l-[3px] border-transparent hover:bg-gold/5 hover:text-taupe'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className="w-[76px] flex items-center justify-center flex-shrink-0">
                  <Icon size={21} strokeWidth={isActive ? 2 : 1.5} />
                </div>
                <AnimatePresence>
                  {expanded && (
                    <motion.span
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      className={`text-sm whitespace-nowrap ${isActive ? 'font-bold' : 'font-medium'}`}
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-divider py-3.5">
        <div className="flex items-center pl-5 gap-3">
          <div className="relative w-9 h-9 rounded-full bg-taupe/20 flex items-center justify-center flex-shrink-0">
            <span className="text-sm text-taupe font-bold">{initials}</span>
            <div className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-gold rounded-full border-2 border-surface flex items-center justify-center">
              <Crown size={7} color="white" />
            </div>
          </div>
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
              >
                <div className="text-[13px] font-bold text-ink leading-tight">
                  {user?.user_metadata?.full_name ?? user?.email ?? 'Modeon User'}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  )
}
