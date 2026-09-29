// src/pages/DashboardPage.jsx
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Shirt, ShoppingBag, Layers, Heart, TrendingUp, Waves, Calendar } from 'lucide-react';
import { ROUTES } from '@/constants/routes';
import DailyOutfitCard from '@/components/outfits/DailyOutfitCard';
import { OutfitCollage } from '@/components/outfits/OutfitCard';
import PageWrapper from '@/components/layout/PageWrapper';
import useAuthStore from '@/stores/useAuthStore';
import { useSavedOutfits } from '@/hooks/useOutfits';
import { useWardrobe } from '@/hooks/useWardrobe';
import { useToggleLaundry } from '@/hooks/useLaundry';

const QUICK_ACTIONS = [
  { icon: Sparkles, label: 'Start Swipe Session', to: ROUTES.SWIPE, style: 'btn-gold' },
  { icon: Shirt, label: 'My Wardrobe', to: ROUTES.WARDROBE, style: 'btn-secondary' },
  { icon: ShoppingBag, label: 'Shopping', to: ROUTES.SHOPPING, style: 'btn-secondary' },
  { icon: Layers, label: 'Mix & Match', to: ROUTES.MIX_MATCH, style: 'btn-secondary' },
  { icon: Calendar, label: 'Occasion Styling', to: ROUTES.OCCASION, style: 'btn-secondary' },
];

const containerV = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };
const itemV = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  const name = user?.user_metadata?.full_name?.split(' ')[0] || 'there';

  const { data: outfitsData } = useSavedOutfits(1);
  const recentOutfits = (outfitsData?.outfits ?? []).slice(0, 3);

  const { data: wardrobeData } = useWardrobe();
  const wardrobeItems = wardrobeData?.items ?? [];
  const laundryCount = wardrobeItems.filter((i) => i.inLaundry).length;
  useToggleLaundry();

  const stats = [
    { label: 'Items', value: String(wardrobeItems.length), icon: Shirt, color: 'text-gold' },
    { label: 'Outfits', value: String(outfitsData?.outfits?.length ?? 0), icon: Heart, color: 'text-ok' },
    { label: 'Laundry', value: String(laundryCount), icon: Waves, color: 'text-danger' },
    { label: 'Swipes', value: String(outfitsData?.total_swipes ?? 0), icon: TrendingUp, color: 'text-taupe' },
  ];

  return (
    <PageWrapper>
      {/* Header */}
      <motion.header initial="hidden" animate="show" variants={containerV} className="flex justify-between items-end mb-10 flex-wrap gap-6">
        <motion.div variants={itemV}>
          <h1 className="font-display text-4xl md:text-5xl mb-1">Good morning, {name} ?</h1>
          <p className="text-2xs font-bold tracking-widest uppercase text-muted">{today}</p>
        </motion.div>
        <motion.div variants={itemV} className="flex gap-3 flex-wrap">
          <button onClick={() => navigate(ROUTES.WARDROBE)} className="btn-secondary">
            <Shirt size={15} /> Upload Item
          </button>
          <button onClick={() => navigate(ROUTES.SWIPE)} className="btn-gold">
            <Sparkles size={15} /> Style Me
          </button>
        </motion.div>
      </motion.header>

      {/* Stats row */}
      <motion.div initial="hidden" animate="show" variants={containerV} className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <motion.div key={label} variants={itemV} className="bg-card border border-divider rounded-2xl p-5">
            <div className="flex items-center justify-between mb-2">
              <div className="text-2xs font-bold tracking-widest uppercase text-muted">{label}</div>
              <Icon size={16} className={color} />
            </div>
            <div className="font-display text-3xl text-ink">{value}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-8">
        {/* Daily outfit */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <DailyOutfitCard />
        </motion.div>

        {/* Right column */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="flex flex-col gap-6">
          {/* Quick actions */}
          <div className="card p-5 flex flex-col gap-3">
            <p className="label">Quick Actions</p>
            {QUICK_ACTIONS.map(({ icon: Icon, label, to, style }) => (
              <button key={to} onClick={() => navigate(to)} className={`${style} w-full justify-center`}>
                <Icon size={15} /> {label}
              </button>
            ))}
          </div>

          {/* Recent saved outfits */}
          <div className="card p-5 flex-1">
            <div className="flex justify-between items-center mb-4">
              <p className="font-display text-lg">Recent Outfits</p>
              <button onClick={() => navigate(ROUTES.MY_OUTFITS)} className="text-2xs text-gold font-bold tracking-widest uppercase hover:underline">
                View All
              </button>
            </div>
            <div className="flex flex-col gap-3">
              {recentOutfits.length === 0 ? (
                <p className="text-sm text-muted text-center py-4">No outfits saved yet.</p>
              ) : (
                recentOutfits.map((outfit) => (
                  <div key={outfit.id} className="flex items-center gap-3 rounded-xl overflow-hidden border border-divider hover:border-gold/40 transition-colors cursor-pointer" onClick={() => navigate(ROUTES.MY_OUTFITS)}>
                    <div className="w-16 h-16 flex-shrink-0">
                      <OutfitCollage items={outfit.items ?? []} height={64} radius={0} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-ink">{outfit.occasion}</p>
                      <p className="text-2xs text-muted">{(outfit.items ?? []).length} items</p>
                    </div>
                  </div>
                ))
              )}
            </div>
            <button onClick={() => navigate(ROUTES.SWIPE)} className="btn-gold w-full justify-center mt-4">
              <Sparkles size={15} /> New Swipe Session
            </button>
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  );
}
