"use client";

import { useEffect } from "react";

// Always enforce dark theme on all platforms.
export const themeInitScript = "document.documentElement.setAttribute('data-theme','dark');";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", "dark");
  }, []);

  return <>{children}</>;
}
