// src/hooks/useTheme.js

import { useEffect } from 'react';
import useUIStore from '@/stores/useUIStore';

export function useTheme() {
  const { theme, toggleTheme } = useUIStore();

  // Persist theme preference to localStorage and sync the DOM class
  useEffect(() => {
    const saved = localStorage.getItem('modeon-theme');
    if (saved && saved !== theme) {
      toggleTheme();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    localStorage.setItem('modeon-theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  return { theme, toggleTheme };
}
