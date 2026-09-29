import { create } from 'zustand';

// State: { uploadedItem, shoppingList, compareResult, compareUsage }
// Actions: setUploadedItem, setShoppingList, addToList, removeFromList, setCompareResult, setCompareUsage

const useShoppingStore = create((set) => ({
  uploadedItem:  null,
  shoppingList:  [],
  compareResult: null,
  compareUsage:  { used: 0, limit: 5 },

  setUploadedItem:  (uploadedItem)  => set({ uploadedItem }),
  setCompareResult: (compareResult) => set({ compareResult }),
  setCompareUsage:  (compareUsage)  => set({ compareUsage }),

  setShoppingList: (shoppingList) => set({ shoppingList }),

  addToList: (item) =>
    set((s) => ({
      shoppingList: s.shoppingList.some((i) => i.id === item.id)
        ? s.shoppingList
        : [...s.shoppingList, item],
    })),

  removeFromList: (id) =>
    set((s) => ({ shoppingList: s.shoppingList.filter((i) => i.id !== id) })),
}));

export default useShoppingStore;
