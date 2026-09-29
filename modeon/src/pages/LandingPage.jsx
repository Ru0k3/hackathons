// src/pages/LandingPage.jsx
import { useNavigate } from 'react-router-dom';
import { motion }      from 'framer-motion';
import { Sparkles, Shirt, ShoppingBag, ArrowRight, Layers, CheckCircle2, Zap, Star } from 'lucide-react';
import { ROUTES } from '@/constants/routes';

const FEATURES = [
  { icon: Shirt,       title: 'Wardrobe Intelligence', description: 'Upload your clothes once. AI tags, categorises, and tracks laundry status automatically.', accent: '#C8A97E' },
  { icon: Sparkles,    title: 'Swipe Learning',         description: 'Like or skip outfit suggestions. Every swipe trains your personal style model.', accent: '#7BAE8E' },
  { icon: ShoppingBag, title: 'Smarter Shopping',       description: 'Before you buy, see if it works with what you already own. Stop wasting money.', accent: '#C47B72' },
  { icon: Layers,      title: 'Mix & Match Canvas',     description: 'Drag and drop pieces onto a canvas and get an instant AI compatibility score.', accent: '#8C7B6B' },
];

const STATS = [
  { value: '500K', label: 'MAU target' }, { value: '20M+', label: 'Wardrobe items' },
  { value: '50M',  label: 'Outfit swipes' }, { value: '100%', label: 'Free forever' },
];

const STEPS = [
  { num: '01', title: 'Upload your wardrobe',  body: 'Photo by photo or batch upload up to 20 at once. AI removes backgrounds and tags everything.' },
  { num: '02', title: 'Swipe outfit combos',    body: 'Your personal style model learns from every swipe. The more you use it, the smarter it gets.' },
  { num: '03', title: 'Dress with confidence', body: 'Get a daily outfit card, occasion-based picks, and shopping validation from what you already own.' },
];

const containerV = { hidden: {}, show: { transition: { staggerChildren: 0.09 } } };
const itemV = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } } };

const FREE_FEATURES = ['Unlimited wardrobe items','Unlimited swipe sessions','Daily AI outfit generation','Shopping compatibility checker','Mix & Match canvas builder','Occasion-based styling','Outfit check & AI feedback','Social export (no watermark)'];

export default function LandingPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-canvas">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 md:px-14 py-5 border-b border-divider sticky top-0 bg-canvas/90 backdrop-blur-md z-40">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gold rounded-full flex items-center justify-center shadow-gold">
            <span className="font-display text-white font-bold text-base leading-none">M</span>
          </div>
          <span className="font-display font-bold text-xl text-ink">Modeon</span>
        </div>
        <div className="flex gap-3">
          <button onClick={() => navigate(ROUTES.LOGIN)}    className="btn-secondary text-xs px-5 py-2.5">Sign In</button>
          <button onClick={() => navigate(ROUTES.REGISTER)} className="btn-gold text-xs px-5 py-2.5">Get Started Free</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative text-center py-28 px-8 max-w-5xl mx-auto overflow-hidden">
        <div className="absolute -top-32 -right-40 w-[600px] h-[600px] bg-gold/8 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-32 w-[400px] h-[400px] bg-ok/8 rounded-full blur-3xl pointer-events-none" />
        <motion.div initial="hidden" animate="show" variants={containerV}>
          <motion.div variants={itemV}>
            <span className="badge mb-6 inline-flex items-center gap-1.5"><Zap size={10} /> Open Source · Free Forever</span>
          </motion.div>
          <motion.h1 variants={itemV} className="font-display text-6xl md:text-7xl lg:text-8xl text-ink leading-[1.05] mb-6">
            Your AI<br /><span className="text-gold">Fashion</span><br />Advisor
          </motion.h1>
          <motion.p variants={itemV} className="text-lg md:text-xl text-taupe max-w-xl mx-auto mb-10 leading-relaxed">
            Modeon turns your wardrobe into a personal style system — AI-generated outfits, smarter shopping decisions, and a closet you'll actually use.
          </motion.p>
          <motion.div variants={itemV} className="flex gap-4 justify-center flex-wrap">
            <button onClick={() => navigate(ROUTES.REGISTER)} className="btn-gold text-sm px-8 py-4 shadow-gold">Start for Free <ArrowRight size={16} /></button>
            <button onClick={() => navigate(ROUTES.LOGIN)}    className="btn-secondary text-sm px-8 py-4">Sign In</button>
          </motion.div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="border-y border-divider bg-surface">
        <div className="max-w-5xl mx-auto px-8 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {STATS.map(({ value, label }, i) => (
            <motion.div key={label} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
              <div className="font-display text-4xl text-gold mb-1">{value}</div>
              <div className="text-2xs font-bold tracking-widest uppercase text-muted">{label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-8 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display text-5xl text-ink mb-4">Everything your wardrobe needs</h2>
          <p className="text-muted text-lg">A complete styling system, right in your browser.</p>
        </div>
        <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-6" initial="hidden" whileInView="show" viewport={{ once: true }} variants={containerV}>
          {FEATURES.map(({ icon: Icon, title, description, accent }) => (
            <motion.div key={title} variants={itemV} className="card flex gap-5 items-start hover:shadow-float transition-shadow duration-300">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${accent}20` }}>
                <Icon size={22} style={{ color: accent }} />
              </div>
              <div>
                <h3 className="font-display text-xl text-ink mb-2">{title}</h3>
                <p className="text-muted text-sm leading-relaxed">{description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* How it works */}
      <section className="py-24 px-8 bg-surface border-y border-divider">
        <div className="max-w-4xl mx-auto">
          <h2 className="font-display text-5xl text-ink text-center mb-16">How it works</h2>
          <div className="flex flex-col gap-12">
            {STEPS.map(({ num, title, body }, i) => (
              <motion.div key={num} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="flex gap-8 items-start">
                <div className="font-display text-5xl text-gold/30 leading-none flex-shrink-0 w-16 text-right">{num}</div>
                <div>
                  <h3 className="font-display text-2xl text-ink mb-2">{title}</h3>
                  <p className="text-muted leading-relaxed">{body}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 px-8 max-w-3xl mx-auto text-center">
        <h2 className="font-display text-5xl text-ink mb-4">Simple pricing</h2>
        <p className="text-muted mb-12 text-lg">Everything free. Always. No paywalls, no feature gates.</p>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card max-w-md mx-auto" style={{ borderColor: 'rgba(200,169,126,0.4)' }}>
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="font-display text-3xl text-ink">Free</p>
              <p className="text-2xs font-bold tracking-widest uppercase text-muted mt-1">Open Source · Forever</p>
            </div>
            <div className="w-14 h-14 bg-gold/15 rounded-2xl flex items-center justify-center">
              <Star size={24} className="text-gold" />
            </div>
          </div>
          <ul className="flex flex-col gap-3 text-left mb-8">
            {FREE_FEATURES.map((feat) => (
              <li key={feat} className="flex items-center gap-3 text-sm text-ink">
                <CheckCircle2 size={16} className="text-ok flex-shrink-0" />{feat}
              </li>
            ))}
          </ul>
          <button onClick={() => navigate(ROUTES.REGISTER)} className="btn-gold w-full justify-center">Get Started Free <ArrowRight size={15} /></button>
        </motion.div>
      </section>

      {/* CTA */}
      <section className="py-24 px-8 bg-ink text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="font-display text-5xl text-white mb-4">Dress better. Waste less.</h2>
          <p className="text-white/60 text-lg mb-10 max-w-lg mx-auto">Join thousands who've stopped impulse buying and started dressing with intention.</p>
          <button onClick={() => navigate(ROUTES.REGISTER)} className="btn-gold text-sm px-10 py-4 shadow-gold">Start for Free <ArrowRight size={16} /></button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-divider py-10 px-8 text-center bg-canvas">
        <div className="flex items-center justify-center gap-2.5 mb-3">
          <div className="w-6 h-6 bg-gold rounded-full flex items-center justify-center shadow-gold">
            <span className="font-display text-white font-bold text-sm leading-none">M</span>
          </div>
          <span className="font-display font-bold text-lg text-ink">Modeon</span>
        </div>
        <p className="text-sm text-muted">© {new Date().getFullYear()} Modeon. Open Source. Dress better, waste less.</p>
      </footer>
    </div>
  );
}
