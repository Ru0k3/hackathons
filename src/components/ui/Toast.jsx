// src/components/ui/Toast.jsx
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';
import useUIStore from '@/stores/useUIStore';

const ICONS = {
  success: <CheckCircle2 size={16} className="text-ok flex-shrink-0" />,
  error:   <AlertCircle  size={16} className="text-danger flex-shrink-0" />,
  info:    <Info         size={16} className="text-gold flex-shrink-0" />,
};

const BORDERS = {
  success: 'border-ok/30',
  error:   'border-danger/30',
  info:    'border-gold/30',
};

export default function Toast({ id, type = 'info', message }) {
  const removeToast = useUIStore((s) => s.removeToast);
  return (
    <motion.div
      initial={{ opacity: 0, x: 48 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 48 }}
      className={`flex items-start gap-3 bg-card border ${BORDERS[type] ?? BORDERS.info} rounded-xl px-4 py-3 shadow-float max-w-sm`}
    >
      {ICONS[type]}
      <p className="text-sm text-ink flex-1 leading-snug">{message}</p>
      <button
        onClick={() => removeToast(id)}
        aria-label="Dismiss notification"
        className="text-muted hover:text-ink transition-colors border-0 bg-transparent cursor-pointer"
      >
        <X size={14} />
      </button>
    </motion.div>
  );
}
