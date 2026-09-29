// src/components/ui/Modal.jsx
import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

const SIZE_MAP = {
  sm:  'max-w-sm',
  md:  'max-w-lg',
  lg:  'max-w-2xl',
  xl:  'max-w-4xl',
};

export default function Modal({ open, onClose, title, children, maxWidth, size = 'md' }) {
  const widthClass = maxWidth || SIZE_MAP[size] || 'max-w-lg';

  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label={title}>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 bg-ink/40 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 12 }}
            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
            className={`relative z-10 w-full ${widthClass} bg-card border border-divider rounded-card shadow-float p-8 max-h-[90vh] overflow-y-auto`}
          >
            <div className="flex items-start justify-between mb-6">
              {title && <h2 className="font-display text-2xl text-ink">{title}</h2>}
              <button
                onClick={onClose}
                aria-label="Close modal"
                className="ml-auto w-9 h-9 rounded-full bg-surface flex items-center justify-center text-muted hover:text-ink transition-colors border-0 cursor-pointer flex-shrink-0"
              >
                <X size={16} />
              </button>
            </div>
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
