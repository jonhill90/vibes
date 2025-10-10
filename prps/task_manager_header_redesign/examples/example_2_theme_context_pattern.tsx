// Source: infra/task-manager/frontend/src/contexts/ThemeContext.tsx
// Lines: 1-63
// Pattern: React Context for theme management with localStorage persistence
// Extracted: 2025-10-10
// Relevance: 9/10 - Current implementation (mostly correct, just needs Tailwind config fix)

/**
 * ThemeContext - Manages light/dark mode state
 *
 * PURPOSE: Provides theme state and toggle across the app
 *
 * FEATURES:
 * - Defaults to light mode
 * - Persists theme preference to localStorage
 * - Applies theme class to document.documentElement
 */

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light"); // Default to light mode

  // Initialize theme from localStorage or default to light
  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
    }
  }, []);

  // Apply theme to document element
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
