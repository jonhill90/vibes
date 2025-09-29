import React from 'react';
import { motion } from 'framer-motion';

interface PowerButtonProps {
  isOn: boolean;
  onClick: () => void;
  color?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
  size?: number;
}

// Helper function to get color hex values for animations
const getColorValue = (color: string) => {
  const colorValues = {
    purple: 'rgb(168,85,247)',
    green: 'rgb(16,185,129)',
    pink: 'rgb(236,72,153)',
    blue: 'rgb(59,130,246)',
    cyan: 'rgb(34,211,238)',
    orange: 'rgb(249,115,22)'
  };
  return colorValues[color as keyof typeof colorValues] || colorValues.blue;
};

export const PowerButton: React.FC<PowerButtonProps> = ({
  isOn,
  onClick,
  color = 'blue',
  size = 40
}) => {
  const colorMap = {
    purple: {
      border: 'border-purple-400',
      glow: 'shadow-[0_0_15px_rgba(168,85,247,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(168,85,247,1)]',
      fill: 'bg-purple-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(168,85,247,0.8)]'
    },
    green: {
      border: 'border-emerald-400',
      glow: 'shadow-[0_0_15px_rgba(16,185,129,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(16,185,129,1)]',
      fill: 'bg-emerald-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(16,185,129,0.8)]'
    },
    pink: {
      border: 'border-pink-400',
      glow: 'shadow-[0_0_15px_rgba(236,72,153,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(236,72,153,1)]',
      fill: 'bg-pink-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(236,72,153,0.8)]'
    },
    blue: {
      border: 'border-blue-400',
      glow: 'shadow-[0_0_15px_rgba(59,130,246,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(59,130,246,1)]',
      fill: 'bg-blue-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(59,130,246,0.8)]'
    },
    cyan: {
      border: 'border-cyan-400',
      glow: 'shadow-[0_0_15px_rgba(34,211,238,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(34,211,238,1)]',
      fill: 'bg-cyan-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(34,211,238,0.8)]'
    },
    orange: {
      border: 'border-orange-400',
      glow: 'shadow-[0_0_15px_rgba(249,115,22,0.8)]',
      glowHover: 'hover:shadow-[0_0_25px_rgba(249,115,22,1)]',
      fill: 'bg-orange-400',
      innerGlow: 'shadow-[inset_0_0_10px_rgba(249,115,22,0.8)]'
    }
  };

  const styles = colorMap[color];

  return (
    <motion.button
      onClick={onClick}
      className={`
        relative rounded-full border-2 transition-all duration-300
        ${styles.border}
        ${isOn ? styles.glow : 'shadow-[0_0_5px_rgba(0,0,0,0.3)]'}
        ${styles.glowHover}
        bg-gradient-to-b from-gray-900 to-black
        hover:scale-110
        active:scale-95
      `}
      style={{ width: size, height: size }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Outer ring glow effect - keep this for the button border glow */}
      <motion.div
        className={`
          absolute inset-[-4px] rounded-full border-2
          ${isOn ? styles.border : 'border-transparent'}
          blur-sm
        `}
        animate={{
          opacity: isOn ? [0.3, 0.6, 0.3] : 0,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Inner glow effect - glows inside the button */}
      <motion.div
        className={`
          absolute inset-[2px] rounded-full
          ${isOn ? styles.fill : ''}
          blur-md opacity-20
        `}
        animate={{
          opacity: isOn ? [0.1, 0.3, 0.1] : 0,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Inner power symbol container */}
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Power symbol (circle with line) */}
        <motion.svg
          width={size * 0.5}
          height={size * 0.5}
          viewBox="0 0 24 24"
          fill="none"
          className="relative z-10"
          animate={{
            filter: isOn ? [
              `drop-shadow(0 0 8px ${getColorValue(color)}) drop-shadow(0 0 12px ${getColorValue(color)})`,
              `drop-shadow(0 0 12px ${getColorValue(color)}) drop-shadow(0 0 16px ${getColorValue(color)})`,
              `drop-shadow(0 0 8px ${getColorValue(color)}) drop-shadow(0 0 12px ${getColorValue(color)})`
            ] : 'none'
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          {/* Power line */}
          <path
            d="M12 2L12 12"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            className={isOn ? 'text-white' : 'text-gray-600'}
          />
          {/* Power circle */}
          <path
            d="M18.36 6.64a9 9 0 1 1-12.73 0"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            className={isOn ? 'text-white' : 'text-gray-600'}
          />
        </motion.svg>

        {/* Inner glow when on - removed since it was causing circle behind icon */}
      </div>

      {/* Removed center dot - it was causing the colored circles */}
    </motion.button>
  );
};