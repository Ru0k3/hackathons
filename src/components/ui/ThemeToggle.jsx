// src/components/ui/ThemeToggle.jsx
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';

export default function ThemeToggle({ className = '' }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className={`w-9 h-9 rounded-full bg-surface border border-divider flex items-center justify-center text-taupe hover:text-ink transition-colors cursor-pointer ${className}`}
    >
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}
