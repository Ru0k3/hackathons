// src/components/ui/Badge.jsx
const VARIANTS = {
  default:  'bg-gold/10 text-gold',
  laundry:  'bg-blue-100 text-blue-700',
  premium:  'bg-gold text-white',
  status:   'bg-ok/20 text-ok',
  danger:   'bg-danger/15 text-danger',
  muted:    'bg-surface text-muted',
};

export default function Badge({ variant = 'default', className = '', children }) {
  return (
    <span className={`inline-block text-2xs font-bold tracking-widest uppercase px-3 py-1 rounded-chip ${VARIANTS[variant] ?? VARIANTS.default} ${className}`}>
      {children}
    </span>
  );
}
