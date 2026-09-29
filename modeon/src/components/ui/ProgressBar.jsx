// src/components/ui/ProgressBar.jsx
export default function ProgressBar({ value = 0, max = 100, label, className = '' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-2xs font-bold tracking-wider uppercase text-muted">{label}</span>
          <span className="text-2xs font-bold text-gold">{Math.round(pct)}%</span>
        </div>
      )}
      <div className="h-1.5 bg-surface rounded-full overflow-hidden" role="progressbar" aria-valuenow={value} aria-valuemax={max}>
        <div
          className="h-full bg-gold rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
