import React from 'react';
/**
 * Props for the Button component
 */
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
  neonLine?: boolean;
  icon?: React.ReactNode;
}
/**
 * Button - A customizable button component
 *
 * This component provides a reusable button with various styles,
 * sizes, and color options.
 */
export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  accentColor = 'purple',
  neonLine = false,
  icon,
  className = '',
  ...props
}) => {
  // Size variations
  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5 rounded',
    md: 'text-sm px-4 py-2 rounded-md',
    lg: 'text-base px-6 py-2.5 rounded-md'
  };
  // Style variations based on variant
  const variantClasses = {
    primary: `
      relative overflow-hidden backdrop-blur-md font-medium
      bg-${accentColor}-500/80 text-black dark:text-white
      border border-${accentColor}-500/50 border-t-${accentColor}-300
      shadow-lg shadow-${accentColor}-500/40 hover:shadow-xl hover:shadow-${accentColor}-500/50
      group
    `,
    secondary: `bg-black/90 border text-white border-${accentColor}-500 text-${accentColor}-400`,
    outline: `bg-white dark:bg-transparent border text-gray-800 dark:text-white border-${accentColor}-500 hover:bg-${accentColor}-500/10`,
    ghost: 'bg-transparent text-gray-700 dark:text-white hover:bg-gray-100/50 dark:hover:bg-white/5'
  };
  // Neon line color mapping
  const neonLineColor = {
    purple: 'bg-purple-500 shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]',
    green: 'bg-emerald-500 shadow-[0_0_10px_2px_rgba(16,185,129,0.4)] dark:shadow-[0_0_20px_5px_rgba(16,185,129,0.7)]',
    pink: 'bg-pink-500 shadow-[0_0_10px_2px_rgba(236,72,153,0.4)] dark:shadow-[0_0_20px_5px_rgba(236,72,153,0.7)]',
    blue: 'bg-blue-500 shadow-[0_0_10px_2px_rgba(59,130,246,0.4)] dark:shadow-[0_0_20px_5px_rgba(59,130,246,0.7)]',
    cyan: 'bg-cyan-500 shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]',
    orange: 'bg-orange-500 shadow-[0_0_10px_2px_rgba(249,115,22,0.4)] dark:shadow-[0_0_20px_5px_rgba(249,115,22,0.7)]'
  };
  return <button className={`
        inline-flex items-center justify-center transition-all duration-200
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `} {...props}>
      {/* Luminous inner light source for primary variant */}
      {variant === 'primary' && <>
          <div className="absolute left-0 right-0 w-[150%] h-[200%] -translate-x-[25%] -translate-y-[30%] opacity-80 group-hover:opacity-100 rounded-[100%] blur-2xl transition-all duration-500 group-hover:scale-110 luminous-button-glow" style={{
        background: `radial-gradient(circle, ${accentColor === 'green' ? 'rgba(16, 185, 129, 0.9)' : accentColor === 'blue' ? 'rgba(59, 130, 246, 0.9)' : accentColor === 'pink' ? 'rgba(236, 72, 153, 0.9)' : accentColor === 'cyan' ? 'rgba(34, 211, 238, 0.9)' : accentColor === 'orange' ? 'rgba(249, 115, 22, 0.9)' : 'rgba(168, 85, 247, 0.9)'} 0%, transparent 70%)`,
        filter: `drop-shadow(0 0 15px ${accentColor === 'green' ? 'rgba(16, 185, 129, 0.8)' : accentColor === 'blue' ? 'rgba(59, 130, 246, 0.8)' : accentColor === 'pink' ? 'rgba(236, 72, 153, 0.8)' : accentColor === 'cyan' ? 'rgba(34, 211, 238, 0.8)' : accentColor === 'orange' ? 'rgba(249, 115, 22, 0.8)' : 'rgba(168, 85, 247, 0.8)'})`
      }} aria-hidden="true" />
          {/* Subtle shine effect on top */}
          <div className="absolute inset-x-0 top-0 h-[1px] bg-white/70 opacity-90" aria-hidden="true" />
          {/* Enhanced outer glow effect */}
          <div className="absolute inset-0 rounded-md opacity-50 group-hover:opacity-70" style={{
        boxShadow: `0 0 20px 5px ${accentColor === 'green' ? 'rgba(16, 185, 129, 0.6)' : accentColor === 'blue' ? 'rgba(59, 130, 246, 0.6)' : accentColor === 'pink' ? 'rgba(236, 72, 153, 0.6)' : accentColor === 'cyan' ? 'rgba(34, 211, 238, 0.6)' : accentColor === 'orange' ? 'rgba(249, 115, 22, 0.6)' : 'rgba(168, 85, 247, 0.6)'}`
      }} aria-hidden="true" />
        </>}
      {/* Content with icon support */}
      <span className="relative z-10 flex items-center justify-center">
        {icon && <span className="mr-2">{icon}</span>}
        {children}
      </span>
      {/* Optional neon line below button */}
      {neonLine && <span className={`absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[2px] ${neonLineColor[accentColor]}`}></span>}
    </button>;
};