import { useState, useEffect } from 'react';
import { Check, Minus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CheckboxProps {
  checked: boolean;
  onChange?: (checked: boolean) => void;
  indeterminate?: boolean;
  disabled?: boolean;
  className?: string;
}

export const Checkbox = ({
  checked,
  onChange,
  indeterminate = false,
  disabled = false,
  className = ''
}: CheckboxProps) => {
  const [isChecked, setIsChecked] = useState(checked);

  useEffect(() => {
    setIsChecked(checked);
  }, [checked]);

  const handleClick = () => {
    if (!disabled && onChange) {
      const newChecked = !isChecked;
      setIsChecked(newChecked);
      onChange(newChecked);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`
        relative w-5 h-5 rounded-md
        bg-white/10 dark:bg-black/20
        backdrop-blur-sm
        border border-gray-300 dark:border-zinc-700
        ${isChecked || indeterminate ? 'border-blue-500 dark:border-blue-400' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        hover:border-blue-400 dark:hover:border-blue-500
        transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-blue-500/50
        ${className}
      `}
    >
      <AnimatePresence mode="wait">
        {indeterminate ? (
          <motion.div
            key="indeterminate"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <Minus className="w-3 h-3 text-blue-500 dark:text-blue-400" strokeWidth={3} />
          </motion.div>
        ) : isChecked ? (
          <motion.div
            key="checked"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <Check className="w-3 h-3 text-blue-500 dark:text-blue-400" strokeWidth={3} />
          </motion.div>
        ) : null}
      </AnimatePresence>
      
      {/* Glow effect when checked */}
      {(isChecked || indeterminate) && !disabled && (
        <div className="absolute inset-0 rounded-md bg-blue-500/20 blur-sm -z-10" />
      )}
    </button>
  );
};