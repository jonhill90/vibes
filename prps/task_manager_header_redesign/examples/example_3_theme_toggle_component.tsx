// Source: infra/task-manager/frontend/src/components/ThemeToggle.tsx
// Lines: 1-33
// Pattern: Theme toggle button component with accessibility
// Extracted: 2025-10-10
// Relevance: 9/10 - Current implementation (correct, relies on ThemeContext)

/**
 * ThemeToggle - Button to toggle between light and dark mode
 *
 * PURPOSE: Provides accessible theme switching with visual feedback
 *
 * FEATURES:
 * - Sun icon for light mode, Moon icon for dark mode
 * - Smooth transitions
 * - Accessible with ARIA labels
 */

import { Moon, Sun } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
      aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
      title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
    >
      {theme === "light" ? (
        <Moon className="w-5 h-5 text-gray-700" aria-hidden="true" />
      ) : (
        <Sun className="w-5 h-5 text-gray-300" aria-hidden="true" />
      )}
    </button>
  );
}
