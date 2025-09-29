import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

export interface CornerRadius {
  topLeft?: number;
  topRight?: number;
  bottomRight?: number;
  bottomLeft?: number;
}

export type GlowIntensity = 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
export type ColorOption = 'none' | 'purple' | 'pink' | 'blue' | 'green' | 'red';

export interface NeonButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: React.ReactNode;
  
  // Layer controls
  showLayer2?: boolean;
  layer2Inset?: number; // Inset in pixels, can be negative for overlap
  
  // Colors
  layer1Color?: ColorOption;
  layer2Color?: ColorOption;
  
  // Corner radius per layer
  layer1Radius?: CornerRadius;
  layer2Radius?: CornerRadius;
  
  // Glow controls
  layer1Glow?: GlowIntensity;
  layer2Glow?: GlowIntensity;
  borderGlow?: GlowIntensity;
  
  // Border controls
  layer1Border?: boolean;
  layer2Border?: boolean;
  
  // Text controls
  coloredText?: boolean; // Whether text takes on the button color
  
  // Size
  size?: 'sm' | 'md' | 'lg' | 'xl';
  
  // Basic states
  disabled?: boolean;
  fullWidth?: boolean;
}

export const NeonButton = React.forwardRef<HTMLButtonElement, NeonButtonProps>(({
  children,
  showLayer2 = false,
  layer2Inset = 8,
  layer1Color = 'none',
  layer2Color = 'none',
  layer1Radius = { topLeft: 12, topRight: 12, bottomRight: 12, bottomLeft: 12 },
  layer2Radius = { topLeft: 24, topRight: 24, bottomRight: 24, bottomLeft: 24 },
  layer1Glow = 'md',
  layer2Glow = 'md',
  borderGlow = 'none',
  layer1Border = true,
  layer2Border = true,
  coloredText = false,
  size = 'md',
  disabled = false,
  fullWidth = false,
  className,
  ...props
}, ref) => {
  // Size mappings
  const sizeClasses = {
    sm: 'px-3 py-1.5',
    md: 'px-4 py-2',
    lg: 'px-6 py-3',
    xl: 'px-8 py-4'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl'
  };

  // Glow intensity mappings
  const glowSizes = {
    none: { blur: 0, spread: 0, opacity: 0 },
    sm: { blur: 10, spread: 5, opacity: 0.3 },
    md: { blur: 15, spread: 10, opacity: 0.4 },
    lg: { blur: 20, spread: 15, opacity: 0.5 },
    xl: { blur: 30, spread: 20, opacity: 0.6 },
    xxl: { blur: 40, spread: 30, opacity: 0.7 }
  };

  // Convert radius object to style
  const getRadiusStyle = (radius: CornerRadius) => ({
    borderTopLeftRadius: `${radius.topLeft || 0}px`,
    borderTopRightRadius: `${radius.topRight || 0}px`,
    borderBottomRightRadius: `${radius.bottomRight || 0}px`,
    borderBottomLeftRadius: `${radius.bottomLeft || 0}px`,
  });

  // Color mappings for gradients and borders
  const getColorConfig = (color: ColorOption) => {
    const configs = {
      none: {
        border: 'border-white/20',
        glow: 'rgba(255,255,255,0.4)',
        glowDark: 'rgba(255,255,255,0.3)',
        aurora: 'rgba(255,255,255,0.4)',
        auroraDark: 'rgba(255,255,255,0.2)',
        text: 'rgb(156 163 175)', // gray-400
        textRgb: '156, 163, 175'
      },
      purple: {
        border: 'border-purple-400/30',
        glow: 'rgba(168,85,247,0.6)',
        glowDark: 'rgba(168,85,247,0.5)',
        aurora: 'rgba(168,85,247,0.8)',
        auroraDark: 'rgba(147,51,234,0.6)',
        text: 'rgb(168 85 247)', // purple-500
        textRgb: '168, 85, 247'
      },
      pink: {
        border: 'border-pink-400/30',
        glow: 'rgba(236,72,153,0.6)',
        glowDark: 'rgba(236,72,153,0.5)',
        aurora: 'rgba(236,72,153,0.8)',
        auroraDark: 'rgba(219,39,119,0.6)',
        text: 'rgb(236 72 153)', // pink-500
        textRgb: '236, 72, 153'
      },
      blue: {
        border: 'border-blue-400/30',
        glow: 'rgba(59,130,246,0.6)',
        glowDark: 'rgba(59,130,246,0.5)',
        aurora: 'rgba(59,130,246,0.8)',
        auroraDark: 'rgba(37,99,235,0.6)',
        text: 'rgb(59 130 246)', // blue-500
        textRgb: '59, 130, 246'
      },
      green: {
        border: 'border-green-400/30',
        glow: 'rgba(34,197,94,0.6)',
        glowDark: 'rgba(34,197,94,0.5)',
        aurora: 'rgba(34,197,94,0.8)',
        auroraDark: 'rgba(22,163,74,0.6)',
        text: 'rgb(34 197 94)', // green-500
        textRgb: '34, 197, 94'
      },
      red: {
        border: 'border-red-400/30',
        glow: 'rgba(239,68,68,0.6)',
        glowDark: 'rgba(239,68,68,0.5)',
        aurora: 'rgba(239,68,68,0.8)',
        auroraDark: 'rgba(220,38,38,0.6)',
        text: 'rgb(239 68 68)', // red-500
        textRgb: '239, 68, 68'
      }
    };
    return configs[color];
  };

  const layer1Config = getColorConfig(layer1Color);
  const layer2Config = getColorConfig(layer2Color);
  const layer1GlowConfig = glowSizes[layer1Glow];
  const layer2GlowConfig = glowSizes[layer2Glow];
  const borderGlowConfig = glowSizes[borderGlow];

  // Build box shadow
  const buildBoxShadow = () => {
    const shadows = [];
    
    // Layer 1 external glow
    if (layer1Glow !== 'none' && !disabled) {
      shadows.push(`0 0 ${layer1GlowConfig.blur}px ${layer1Config.glow}`);
      shadows.push(`0 0 ${layer1GlowConfig.spread}px ${layer1Config.glowDark}`);
    }
    
    // Border glow
    if (borderGlow !== 'none' && layer1Border && !disabled) {
      shadows.push(`inset 0 0 ${borderGlowConfig.blur}px ${layer1Config.glow}`);
    }
    
    return shadows.length > 0 ? shadows.join(', ') : undefined;
  };

  return (
    <motion.button
      ref={ref}
      disabled={disabled}
      className={cn(
        'relative overflow-hidden transition-all duration-300 group',
        sizeClasses[size],
        fullWidth && 'w-full',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      style={{
        ...getRadiusStyle(layer1Radius),
        boxShadow: buildBoxShadow(),
      }}
      {...props}
    >
      {/* Layer 1 - Main glass layer (opaque black glass) */}
      <div className="relative w-full h-full" style={getRadiusStyle(layer1Radius)}>
        {/* Border glow behind the glass */}
        {layer1Border && layer1Glow !== 'none' && (
          <div 
            className="absolute inset-0"
            style={{
              ...getRadiusStyle(layer1Radius),
              boxShadow: `0 0 ${layer1GlowConfig.blur}px ${layer1Config.glow}, 0 0 ${layer1GlowConfig.spread}px ${layer1Config.glowDark}`,
            }}
          />
        )}
        
        {/* Glass surface */}
        <div
          className={cn(
            'absolute inset-0',
            layer1Color === 'none' 
              ? 'bg-white/90 dark:bg-black/90' 
              : 'bg-white/90 dark:bg-black/90',
            'backdrop-blur-md',
            layer1Border && `border ${layer1Config.border}`,
            'transition-all duration-300'
          )}
          style={getRadiusStyle(layer1Radius)}
        >
          {/* Aurora glow effect for Layer 1 */}
          {layer1Color !== 'none' && layer1Glow !== 'none' && (
            <div 
              className="absolute inset-0 -z-10"
              style={{
                ...getRadiusStyle(layer1Radius),
                opacity: layer1GlowConfig.opacity
              }}
            >
              <div 
                className="absolute -inset-[100px] blur-3xl animate-[pulse_4s_ease-in-out_infinite]"
                style={{
                  background: `radial-gradient(circle, ${layer1Config.aurora} 0%, ${layer1Config.auroraDark} 40%, transparent 70%)`
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Layer 2 - Inner glass pill (optional) */}
      {showLayer2 && (
        <div 
          className="absolute pointer-events-none"
          style={{
            top: `${layer2Inset}px`,
            left: `${layer2Inset}px`,
            right: `${layer2Inset}px`,
            bottom: `${layer2Inset}px`
          }}
        >
          <div
            className={cn(
              'relative w-full h-full backdrop-blur-sm',
              layer2Color === 'none' 
                ? 'bg-gradient-to-b from-white/20 to-white/10 dark:from-white/20 dark:to-black/20' 
                : layer2Color === 'purple'
                  ? 'bg-gradient-to-b from-purple-500/30 to-purple-600/30'
                  : layer2Color === 'pink'
                    ? 'bg-gradient-to-b from-pink-500/30 to-pink-600/30'
                    : layer2Color === 'blue'
                      ? 'bg-gradient-to-b from-blue-500/30 to-blue-600/30'
                      : layer2Color === 'green'
                        ? 'bg-gradient-to-b from-green-500/30 to-green-600/30'
                        : 'bg-gradient-to-b from-red-500/30 to-red-600/30',
              layer2Border && `border ${layer2Config.border}`,
              'transition-all duration-300'
            )}
            style={{
              ...getRadiusStyle(layer2Radius),
              boxShadow: layer2Glow !== 'none' 
                ? `0 0 ${layer2GlowConfig.blur}px ${layer2Config.glow}, 0 0 ${layer2GlowConfig.spread}px ${layer2Config.glowDark}` 
                : undefined,
            }}
          >
            {/* Aurora glow for Layer 2 that shines on Layer 1 */}
            {layer2Color !== 'none' && layer2Glow !== 'none' && (
              <div 
                className="absolute inset-0"
                style={{
                  ...getRadiusStyle(layer2Radius),
                  opacity: layer2GlowConfig.opacity
                }}
              >
                <div 
                  className="absolute -inset-[50px] blur-2xl animate-[pulse_6s_ease-in-out_infinite]"
                  style={{
                    background: `radial-gradient(circle, ${layer2Config.aurora} 0%, ${layer2Config.auroraDark} 30%, transparent 60%)`
                  }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Text content - translucent to let color shine through */}
      <span 
        className={cn(
          'relative z-10 font-medium',
          textSizeClasses[size],
          !coloredText && 'mix-blend-overlay dark:mix-blend-screen'
        )}
        style={{
          color: coloredText 
            ? (showLayer2 && layer2Color !== 'none' 
                ? layer2Config.text 
                : layer1Color !== 'none' 
                  ? layer1Config.text 
                  : 'rgba(255, 255, 255, 0.8)')
            : 'rgba(255, 255, 255, 0.8)',
          textShadow: coloredText && ((showLayer2 && layer2Color !== 'none') || (!showLayer2 && layer1Color !== 'none'))
            ? '0 1px 2px rgba(0,0,0,0.8)'
            : undefined
        }}
      >
        {children}
      </span>
    </motion.button>
  );
});

NeonButton.displayName = 'NeonButton'; 