// src/components/outfitcheck/OutfitCheckResult.jsx
import { motion }  from 'framer-motion';
import { Star }    from 'lucide-react';

function ScoreCard({ title, score, feedback, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="card p-5"
    >
      <div className="flex justify-between items-start mb-3">
        <p className="font-bold text-sm text-ink">{title}</p>
        <span className="badge">{score}/10</span>
      </div>
      <p className="text-sm text-taupe leading-relaxed">{feedback}</p>
    </motion.div>
  );
}

export function OutfitCheckResult({ result }) {
  if (!result) return null;
  const stars = Math.round(result.overall_score);

  return (
    <div className="flex flex-col gap-4">
      {/* Overall score */}
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card text-center py-8"
      >
        <p className="label mb-3">Overall Score</p>
        <div className="flex justify-center gap-1 mb-3">
          {Array.from({ length: 10 }).map((_, i) => (
            <Star
              key={i}
              size={22}
              className={i < stars ? 'text-gold' : 'text-divider'}
              fill={i < stars ? 'currentColor' : 'none'}
            />
          ))}
        </div>
        <p className="font-display text-4xl text-ink">{result.overall_score}<span className="text-xl text-muted"> / 10</span></p>
        {result.summary && <p className="text-sm text-taupe italic mt-3 max-w-md mx-auto">{result.summary}</p>}
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard title="Colour Harmony"     score={result.colour_harmony?.score}    feedback={result.colour_harmony?.feedback}    delay={0.05} />
        <ScoreCard title="Fit & Proportion"   score={result.fit_proportion?.score}    feedback={result.fit_proportion?.feedback}    delay={0.10} />
        <ScoreCard title="Occasion Match"     score={result.occasion_match?.score}    feedback={result.occasion_match?.feedback}    delay={0.15} />
      </div>
    </div>
  );
}
