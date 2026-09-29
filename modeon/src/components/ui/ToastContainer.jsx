// src/components/ui/ToastContainer.jsx
import { AnimatePresence } from 'framer-motion';
import useUIStore from '@/stores/useUIStore';
import Toast from './Toast';

export default function ToastContainer() {
  const toasts = useUIStore((s) => s.toasts);
  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
      <AnimatePresence>
        {toasts.map((t) => (
          <div key={t.id} className="pointer-events-auto">
            <Toast {...t} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}
