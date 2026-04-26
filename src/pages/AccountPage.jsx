// src/pages/AccountPage.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Bell, Trash2, ChevronRight, Crown, Shield } from 'lucide-react';
import PageWrapper from '@/components/layout/PageWrapper';
import Modal from '@/components/ui/Modal';
import { getProfile, deleteAccount, exportAccountData } from '@/api/auth';
import { downloadBlob } from '@/api/export';
import useAuthStore from '@/stores/useAuthStore';
import useUIStore from '@/stores/useUIStore';
import { STYLE_ARCHETYPES } from '@/constants/styleArchetypes';
import { OCCASIONS } from '@/constants/occasions';
import { ROUTES } from '@/constants/routes';

export default function AccountPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const signOut = useAuthStore((s) => s.signOut);
  const addToast = useUIStore((s) => s.addToast);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [notifs, setNotifs] = useState({ daily: true, tips: false, newFeatures: true });
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    getProfile().then(setProfile).catch(() => {});
  }, []);

  const name = user?.user_metadata?.full_name || 'Sara Collins';
  const email = user?.email || 'sara@modeon.app';
  const initials = name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();

  const archetypes = profile?.style_archetypes ?? [];
  const occasions = profile?.occasions ?? profile?.occasion_prefs ?? [];

  const handleDeleteAccount = async () => {
    try {
      await deleteAccount();
      await useAuthStore.getState().signOut();
      navigate(ROUTES.LOGIN);
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Failed to delete account.' });
    }
    setDeleteOpen(false);
  };

  const handleLogout = async () => {
    await signOut();
    navigate(ROUTES.LOGIN);
  };

  const ToggleSwitch = ({ value, onChange, label }) => (
    <button
      onClick={onChange}
      aria-pressed={value}
      aria-label={`Toggle ${label}`}
      className={`relative w-11 h-6 rounded-full flex-shrink-0 transition-colors ${value ? 'bg-gold' : 'bg-divider'}`}
    >
      <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${value ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
  );

  return (
    <PageWrapper>
      <h1 className="font-display text-5xl mb-10">Account</h1>

      <div className="max-w-2xl flex flex-col gap-6">

        {/* Profile */}
        <section className="card">
          <h2 className="font-display text-2xl mb-6 flex items-center gap-2">
            <User size={20} /> Profile
          </h2>
          <div className="flex items-center gap-5 mb-6">
            <div className="w-16 h-16 rounded-full bg-gold/20 flex items-center justify-center text-xl font-bold text-gold border border-gold/30">
              {initials}
            </div>
            <div>
              <p className="font-bold text-lg text-ink">{name}</p>
              <p className="text-sm text-muted">{email}</p>
              <span className="badge mt-1">Free Plan ?</span>
            </div>
          </div>
          <div className="border-t border-divider pt-5">
            <p className="text-sm text-muted italic">
              Name and email are managed via your auth provider. Contact support to update them.
            </p>
          </div>
        </section>

        {/* Style Profile */}
        <section className="card">
          <div className="flex justify-between items-center mb-5">
            <h2 className="font-display text-2xl">Style Profile</h2>
            <button
              onClick={() => navigate(ROUTES.ONBOARDING)}
              className="text-2xs text-gold font-bold tracking-widest uppercase hover:underline flex items-center gap-1"
              aria-label="Edit style profile"
            >
              Edit <ChevronRight size={12} />
            </button>
          </div>
          <div className="mb-4">
            <p className="label mb-2">Archetypes</p>
            <div className="flex flex-wrap gap-2">
              {archetypes.map((a) => {
                const arch = STYLE_ARCHETYPES.find((x) => x.value === a);
                return arch ? <span key={a} className="badge">{arch.emoji} {arch.label}</span> : null;
              })}
            </div>
          </div>
          <div>
            <p className="label mb-2">Occasions</p>
            <div className="flex flex-wrap gap-2">
              {occasions.map((o) => {
                const occ = OCCASIONS.find((x) => x.value === o);
                return occ ? <span key={o} className="badge">{occ.icon} {occ.label}</span> : null;
              })}
            </div>
          </div>
        </section>

        {/* Plan */}
        <section className="card">
          <h2 className="font-display text-2xl mb-5 flex items-center gap-2">
            <Crown size={20} className="text-gold" /> Plan
          </h2>
          <div className="flex items-center justify-between mb-5 bg-gold/8 rounded-2xl p-5">
            <div>
              <p className="font-bold text-ink">Free Plan</p>
              <p className="text-sm text-muted">All core features included. No card required.</p>
            </div>
            <span className="badge bg-gold/20 text-gold">Free ?</span>
          </div>
          <p className="text-sm text-muted italic">
            Modeon is 100% free and open source. All features are available at no cost.
          </p>
        </section>

        {/* Data & Privacy */}
        <section className="card">
          <h2 className="font-display text-2xl mb-5 flex items-center gap-2">
            <Shield size={20} /> Data & Privacy
          </h2>
          <div className="flex flex-col gap-3">
            <button
              onClick={async () => {
                try {
                  const data = await exportAccountData();
                  const blob = data instanceof Blob
                    ? data
                    : new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                  downloadBlob(blob, 'modeon-data-export.json');
                  addToast({ type: 'success', message: 'Download started.' });
                } catch (err) {
                  addToast({ type: 'error', message: err?.message || 'Export failed.' });
                }
              }}
              className="btn-secondary w-full justify-start"
            >
              Export my data (GDPR)
            </button>
          </div>
        </section>

        {/* Notifications */}
        <section className="card">
          <h2 className="font-display text-2xl mb-5 flex items-center gap-2">
            <Bell size={20} /> Notifications
          </h2>
          <div className="flex flex-col gap-5">
            {[
              { key: 'daily', label: 'Daily outfit reminder', desc: 'Get a nudge each morning to check your outfit.' },
              { key: 'tips', label: 'Style tips', desc: 'Occasional curated styling advice.' },
              { key: 'newFeatures', label: 'New features', desc: 'Be the first to know about updates.' },
            ].map(({ key, label, desc }) => (
              <div key={key} className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-sm text-ink">{label}</p>
                  <p className="text-xs text-muted">{desc}</p>
                </div>
                <ToggleSwitch
                  value={notifs[key]}
                  label={label}
                  onChange={() => {
                    setNotifs((p) => ({ ...p, [key]: !p[key] }));
                  }}
                />
              </div>
            ))}
          </div>
        </section>

        {/* Danger zone */}
        <section className="card" style={{ borderColor: 'rgba(196,123,114,0.3)' }}>
          <h2 className="font-display text-xl text-danger mb-4">Danger Zone</h2>
          <div className="flex gap-3 flex-wrap">
            <button onClick={handleLogout} className="btn-secondary" aria-label="Sign out">
              Sign Out
            </button>
            <button onClick={() => setDeleteOpen(true)} className="btn-danger" aria-label="Delete account">
              <Trash2 size={15} /> Delete Account
            </button>
          </div>
        </section>
      </div>

      {/* Delete confirmation modal */}
      <Modal open={deleteOpen} onClose={() => setDeleteOpen(false)} title="Delete Account">
        <p className="text-sm text-taupe mb-6 leading-relaxed">
          This will permanently delete your account, wardrobe, and all saved outfits.
          This action <strong className="text-danger">cannot be undone</strong>.
        </p>
        <div className="flex gap-3 justify-end">
          <button onClick={() => setDeleteOpen(false)} className="btn-secondary">Cancel</button>
          <button onClick={handleDeleteAccount} className="btn-danger">Yes, Delete My Account</button>
        </div>
      </Modal>
    </PageWrapper>
  );
}
