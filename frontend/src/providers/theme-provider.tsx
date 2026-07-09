"use client";

import { useEffect, useState } from "react";
import { useThemeStore } from "@/store/theme-store";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setResolvedTheme } = useThemeStore();

  useEffect(() => {
    const root = document.documentElement;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    
    const applyTheme = (resolved: "light" | "dark") => {
      root.setAttribute("data-theme", resolved);
      setResolvedTheme(resolved);
    };

    const onChange = (e: MediaQueryListEvent) => {
      applyTheme(e.matches ? "dark" : "light");
    };

    if (theme === "system") {
      const prefersDark = media.matches;
      applyTheme(prefersDark ? "dark" : "light");
      media.addEventListener("change", onChange);
    } else {
      applyTheme(theme);
    }

    return () => {
      media.removeEventListener("change", onChange);
    };
  }, [theme, setResolvedTheme]);

  return <>{children}</>;
}
