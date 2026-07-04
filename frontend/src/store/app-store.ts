import { create } from "zustand";

interface AppState {
  sidebarOpen: boolean;
  commandPaletteOpen: boolean;
  settingsSidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setSettingsSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  commandPaletteOpen: false,
  settingsSidebarOpen: false,
  setSidebarOpen: (sidebarOpen: boolean) => set({ sidebarOpen }),
  setCommandPaletteOpen: (commandPaletteOpen: boolean) =>
    set({ commandPaletteOpen }),
  setSettingsSidebarOpen: (settingsSidebarOpen: boolean) =>
    set({ settingsSidebarOpen }),
}));
