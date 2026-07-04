import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Theme } from "@/types";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  resolvedTheme: "light" | "dark";
  setResolvedTheme: (theme: "light" | "dark") => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "system",
      resolvedTheme: "light",
      setTheme: (theme: Theme) => set({ theme }),
      toggleTheme: () => {
        const { resolvedTheme } = get();
        set({ theme: resolvedTheme === "dark" ? "light" : "dark" });
      },
      setResolvedTheme: (resolvedTheme: "light" | "dark") =>
        set({ resolvedTheme }),
    }),
    {
      name: "theme-storage",
      partialize: (state) => ({ theme: state.theme }),
    }
  )
);
