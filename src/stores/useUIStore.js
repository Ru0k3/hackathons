import { create } from 'zustand';

// State: { theme, sidebarOpen, toasts, onboarded }
// Actions: toggleTheme, setSidebarOpen, addToast, removeToast, setOnboarded

let _toastId = 0;

const useUIStore = create((set) => ({
  theme:       'light',  // 'light' | 'dark'
  sidebarOpen: true,
  toasts:      [],       // { id, type, message }[]
  onboarded:   false,

  toggleTheme: () =>
    set((s) => {
      const next = s.theme === 'light' ? 'dark' : 'light';
      document.documentElement.classList.toggle('dark', next === 'dark');
      return { theme: next };
    }),

  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setOnboarded: (onboarded) => set({ onboarded }),

  addToast: ({ type = 'info', message }) => {
    const id = ++_toastId;
    set((s) => ({ toasts: [...s.toasts, { id, type, message }] }));
    // auto-dismiss after 4 seconds
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, 4000);
    return id;
  },

  removeToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

export default useUIStore;
