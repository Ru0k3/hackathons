// src/components/mixmatch/CompatibilityScore.jsx
import { motion } from 'framer-motion';
import Spinner    from '@/components/ui/Spinner';

export function CompatibilityScore({ score, explanation, loading }) {
  const r          = 44;
  const circ       = 2 * Math.PI * r;
  const dashOffset = circ - (circ * (score ?? 0)) / 100;
  const colour     = score >= 75 ? '#7BAE8E' : score >= 50 ? '#C8A97E' : '#C47B72';

  return (
    <div className="card flex gap-6 items-center">
      {loading ? (
        <Spinner size="lg" />
      ) : (
        <>
          {/* Circular progress */}
          <div className="flex-shrink-0 relative w-28 h-28">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r={r} fill="none" stroke="#E6E1D8" strokeWidth="10" />
              <motion.circle
                cx="50" cy="50" r={r}
                fill="none"
                stroke={colour}
                strokeWidth="10"
                strokeDasharray={circ}
                initial={{ strokeDashoffset: circ }}
                animate={{ strokeDashoffset: dashOffset }}
                transition={{ duration: 1, ease: 'easeOut' }}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="font-display text-2xl font-bold text-ink">{score ?? '–'}</span>
              <span className="text-2xs text-muted font-bold">/ 100</span>
            </div>
          </div>

          <div className="flex-1">
            <p className="font-bold text-ink mb-1">Compatibility Score</p>
            {explanation ? (
              <p className="text-sm text-taupe leading-relaxed">{explanation}</p>
            ) : (
              <p className="text-sm text-muted italic">
                Add items to the canvas, then click "Score Outfit" to get AI feedback.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
