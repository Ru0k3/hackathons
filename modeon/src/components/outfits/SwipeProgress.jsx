// src/components/outfits/SwipeProgress.jsx
export default function SwipeProgress({ current, total }) {
  const pct = total > 0 ? Math.round(((total - current) / total) * 100) : 0;
  return (
    <div className="w-full max-w-md mx-auto mb-6" aria-label={`${total - current} of ${total} outfits reviewed`}>
      <div className="flex justify-between mb-2">
        <span className="text-2xs font-bold tracking-widest uppercase text-muted">
          {total - current} of {total} reviewed
        </span>
        <span className="text-2xs font-bold text-gold">{pct}%</span>
      </div>
      <div className="h-1.5 bg-surface rounded-full overflow-hidden">
        <div
          className="h-full bg-gold rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
