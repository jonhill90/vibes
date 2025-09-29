import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
interface ThemeToggleProps {
  accentColor?: 'purple' | 'green' | 'pink' | 'blue';
}
export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  accentColor = 'blue'
}) => {
  const {
    theme,
    setTheme
  } = useTheme();
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };
  const accentColorMap = {
    purple: {
      border: 'border-purple-300 dark:border-purple-500/30',
      hover: 'hover:border-purple-400 dark:hover:border-purple-500/60',
      text: 'text-purple-600 dark:text-purple-500',
      bg: 'from-purple-100/80 to-purple-50/60 dark:from-white/10 dark:to-black/30'
    },
    green: {
      border: 'border-emerald-300 dark:border-emerald-500/30',
      hover: 'hover:border-emerald-400 dark:hover:border-emerald-500/60',
      text: 'text-emerald-600 dark:text-emerald-500',
      bg: 'from-emerald-100/80 to-emerald-50/60 dark:from-white/10 dark:to-black/30'
    },
    pink: {
      border: 'border-pink-300 dark:border-pink-500/30',
      hover: 'hover:border-pink-400 dark:hover:border-pink-500/60',
      text: 'text-pink-600 dark:text-pink-500',
      bg: 'from-pink-100/80 to-pink-50/60 dark:from-white/10 dark:to-black/30'
    },
    blue: {
      border: 'border-blue-300 dark:border-blue-500/30',
      hover: 'hover:border-blue-400 dark:hover:border-blue-500/60',
      text: 'text-blue-600 dark:text-blue-500',
      bg: 'from-blue-100/80 to-blue-50/60 dark:from-white/10 dark:to-black/30'
    }
  };
  return <button onClick={toggleTheme} className={`
        relative p-2 rounded-md backdrop-blur-md 
        bg-gradient-to-b ${accentColorMap[accentColor].bg}
        border ${accentColorMap[accentColor].border} ${accentColorMap[accentColor].hover}
        ${accentColorMap[accentColor].text}
        shadow-[0_0_10px_rgba(0,0,0,0.05)] dark:shadow-[0_0_10px_rgba(0,0,0,0.3)]
        transition-all duration-300 flex items-center justify-center
      `} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
      {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>;
};