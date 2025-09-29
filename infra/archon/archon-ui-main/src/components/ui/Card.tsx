import React from 'react';
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange' | 'none';
  variant?: 'default' | 'bordered';
}
export const Card: React.FC<CardProps> = ({
  children,
  accentColor = 'none',
  variant = 'default',
  className = '',
  ...props
}) => {
  const accentColorMap = {
    purple: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]',
      line: 'before:bg-purple-500',
      border: 'border-purple-300 dark:border-purple-500/30',
      gradientFrom: 'from-purple-100 dark:from-purple-500/20',
      gradientTo: 'to-white dark:to-purple-500/5'
    },
    green: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(16,185,129,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(16,185,129,0.7)]',
      line: 'before:bg-emerald-500',
      border: 'border-emerald-300 dark:border-emerald-500/30',
      gradientFrom: 'from-emerald-100 dark:from-emerald-500/20',
      gradientTo: 'to-white dark:to-emerald-500/5'
    },
    pink: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(236,72,153,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(236,72,153,0.7)]',
      line: 'before:bg-pink-500',
      border: 'border-pink-300 dark:border-pink-500/30',
      gradientFrom: 'from-pink-100 dark:from-pink-500/20',
      gradientTo: 'to-white dark:to-pink-500/5'
    },
    blue: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(59,130,246,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(59,130,246,0.7)]',
      line: 'before:bg-blue-500',
      border: 'border-blue-300 dark:border-blue-500/30',
      gradientFrom: 'from-blue-100 dark:from-blue-500/20',
      gradientTo: 'to-white dark:to-blue-500/5'
    },
    cyan: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]',
      line: 'before:bg-cyan-500',
      border: 'border-cyan-300 dark:border-cyan-500/30',
      gradientFrom: 'from-cyan-100 dark:from-cyan-500/20',
      gradientTo: 'to-white dark:to-cyan-500/5'
    },
    orange: {
      glow: 'before:shadow-[0_0_10px_2px_rgba(249,115,22,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(249,115,22,0.7)]',
      line: 'before:bg-orange-500',
      border: 'border-orange-300 dark:border-orange-500/30',
      gradientFrom: 'from-orange-100 dark:from-orange-500/20',
      gradientTo: 'to-white dark:to-orange-500/5'
    },
    none: {
      glow: '',
      line: '',
      border: 'border-gray-200 dark:border-zinc-800/50',
      gradientFrom: 'from-gray-50 dark:from-white/5',
      gradientTo: 'to-white dark:to-transparent'
    }
  };
  const variantClasses = {
    default: 'border',
    bordered: 'border'
  };
  return <div className={`
        relative p-4 rounded-md backdrop-blur-md
        bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30
        ${variantClasses[variant]} ${accentColorMap[accentColor].border}
        shadow-[0_10px_30px_-15px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_-15px_rgba(0,0,0,0.7)]
        hover:shadow-[0_15px_40px_-15px_rgba(0,0,0,0.2)] dark:hover:shadow-[0_15px_40px_-15px_rgba(0,0,0,0.9)]
        transition-all duration-300
        ${accentColor !== 'none' ? `
          before:content-[""] before:absolute before:top-[0px] before:left-[1px] before:right-[1px] before:h-[2px] 
          before:rounded-t-[4px]
          ${accentColorMap[accentColor].line} ${accentColorMap[accentColor].glow}
          after:content-[""] after:absolute after:top-0 after:left-0 after:right-0 after:h-16
          after:bg-gradient-to-b ${accentColorMap[accentColor].gradientFrom} ${accentColorMap[accentColor].gradientTo}
          after:rounded-t-md after:pointer-events-none
        ` : ''}
        ${className}
      `} {...props}>
      <div className="relative z-10">{children}</div>
    </div>;
};