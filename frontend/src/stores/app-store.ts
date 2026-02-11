import { create } from 'zustand';

interface AppState {
  sidebarOpen: boolean;
  darkMode: boolean;
  searchOpen: boolean;
  toggleSidebar: () => void;
  toggleDarkMode: () => void;
  toggleSearch: () => void;
  setSearchOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  darkMode: true,
  searchOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleDarkMode: () => {
    set((s) => {
      const newMode = !s.darkMode;
      document.documentElement.classList.toggle('dark', newMode);
      return { darkMode: newMode };
    });
  },
  toggleSearch: () => set((s) => ({ searchOpen: !s.searchOpen })),
  setSearchOpen: (open) => set({ searchOpen: open }),
}));
