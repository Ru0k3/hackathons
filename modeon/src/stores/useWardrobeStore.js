import { create } from 'zustand';

// State: { items, filters, searchQuery }
// Actions: setItems, upsertItem, removeItem, setFilter, clearFilters, setSearchQuery
// Derived: filteredItems — applies all active filters client-side

const defaultFilters = {
  category:  [],   // string[]
  colours:   [],   // string[]
  seasons:   [],   // string[]
  formality: [],   // string[]
  laundry:   false,
};

const useWardrobeStore = create((set, get) => ({
  items:       [],
  filters:     { ...defaultFilters },
  searchQuery: '',

  setItems: (items) => set({ items }),

  upsertItem: (item) =>
    set((s) => {
      const exists = s.items.find((i) => i.id === item.id);
      return {
        items: exists
          ? s.items.map((i) => (i.id === item.id ? { ...i, ...item } : i))
          : [item, ...s.items],
      };
    }),

  removeItem: (id) =>
    set((s) => ({ items: s.items.filter((i) => i.id !== id) })),

  setFilter: (key, value) =>
    set((s) => ({ filters: { ...s.filters, [key]: value } })),

  clearFilters: () => set({ filters: { ...defaultFilters } }),

  setSearchQuery: (searchQuery) => set({ searchQuery }),

  /** Returns items after applying all active filters and search query */
  get filteredItems() {
    const { items, filters, searchQuery } = get();
    return items.filter((item) => {
      if (filters.category.length  && !filters.category.includes(item.category))   return false;
      if (filters.colours.length   && !filters.colours.includes(item.color))        return false;
      if (filters.seasons.length   && !item.seasons?.some((s) => filters.seasons.includes(s))) return false;
      if (filters.formality.length && !filters.formality.includes(item.formality))  return false;
      if (filters.laundry          && !item.inLaundry)                              return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          item.category?.toLowerCase().includes(q) ||
          item.color?.toLowerCase().includes(q) ||
          item.tags?.some((t) => t.toLowerCase().includes(q))
        );
      }
      return true;
    });
  },
}));

export default useWardrobeStore;
