// src/components/layout/TopBar.jsx
import { Bell } from 'lucide-react';
import ThemeToggle from '@/components/ui/ThemeToggle';
import useAuthStore from '@/stores/useAuthStore';

export default function TopBar({ title }) {
  const user = useAuthStore((s) => s.user);
  return (
    <header className="h-14 flex items-center justify-between px-8 border-b border-divider bg-canvas/80 backdrop-blur-sm sticky top-0 z-30">
      {title && <h2 className="font-display text-lg text-ink">{title}</h2>}
      <div className="flex items-center gap-3 ml-auto">
        <button
          aria-label="Notifications"
          className="w-9 h-9 rounded-full bg-surface border border-divider flex items-center justify-center text-taupe hover:text-ink transition-colors cursor-pointer"
        >
          <Bell size={16} />
        </button>
        <ThemeToggle />
        <div className="w-9 h-9 rounded-full bg-gold/20 flex items-center justify-center text-gold font-bold text-sm">
          {user?.email?.[0]?.toUpperCase() ?? 'U'}
        </div>
      </div>
    </header>
  );
}
