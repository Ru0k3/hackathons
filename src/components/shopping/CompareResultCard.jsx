// src/components/shopping/CompareResultCard.jsx
import { CheckCircle2, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export function CompareResultCard({ result }) {
  const compatible = result?.result === 'compatible';
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl border p-6 flex gap-4 items-start
        ${compatible ? 'bg-ok/10 border-ok/30' : 'bg-danger/10 border-danger/30'}`}
    >
      <div className="flex-shrink-0 mt-0.5">
        {compatible
          ? <CheckCircle2 size={28} className="text-ok" />
          : <XCircle     size={28} className="text-danger" />}
      </div>
      <div>
        <p className={`font-bold text-lg mb-1 ${compatible ? 'text-ok' : 'text-danger'}`}>
          {compatible ? 'Great match for your wardrobe!' : 'May not fit your current wardrobe'}
        </p>
        <p className="text-sm text-taupe leading-relaxed">{result?.explanation}</p>
        {result?.matching_items?.length > 0 && (
          <p className="text-xs text-muted mt-3">
            Works with: <span className="font-semibold text-ink">{result.matching_items.join(', ')}</span>
          </p>
        )}
      </div>
    </motion.div>
  );
}
