"use client";

import { useEffect, useState } from "react";
import { useThemeStore } from "@/store/theme-store";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setResolvedTheme } = useThemeStore();

  useEffect(() => {
    const root = document.documentElement;

    const applyTheme = (resolved: "light" | "dark") => {
      root.setAttribute("data-theme", resolved);
      setResolvedTheme(resolved);
    };

    if (theme === "system") {
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      applyTheme(prefersDark ? "dark" : "light");

      const media = window.matchMedia("(prefers-color-scheme: dark)");
      media.addEventListener("change", (e) => {
        applyTheme(e.matches ? "dark" : "light");
      });
    } else {
      applyTheme(theme);
    }
  }, [theme, setResolvedTheme]);

  return <>{children}</>;
}
