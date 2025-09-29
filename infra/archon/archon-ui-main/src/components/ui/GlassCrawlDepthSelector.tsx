import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface GlassCrawlDepthSelectorProps {
  value: number;
  onChange: (value: number) => void;
  showTooltip?: boolean;
  onTooltipToggle?: (show: boolean) => void;
  className?: string;
}

export const GlassCrawlDepthSelector: React.FC<GlassCrawlDepthSelectorProps> = ({
  value,
  onChange,
  showTooltip = false,
  onTooltipToggle,
  className
}) => {
  const levels = [1, 2, 3, 4, 5];
  const [hoveredLevel, setHoveredLevel] = useState<number | null>(null);
  
  // Get descriptive text for each level
  const getLevelDescription = (level: number) => {
    switch (level) {
      case 1: return "Single page only";
      case 2: return "Page + immediate links";
      case 3: return "2 levels deep";
      case 4: return "3 levels deep";
      case 5: return "Maximum depth";
      default: return "";
    }
  };

  return (
    <div className={cn("relative inline-block", className)}>
      {/* Main container for circles and tubes */}
      <div className="flex items-center gap-4 relative">
        {/* Glass tubes connecting the circles - positioned behind circles */}
        <div className="absolute inset-0 flex items-center">
          {levels.slice(0, -1).map((level, index) => (
            <div
              key={`tube-${level}`}
              className={cn(
                "h-0.5 flex-1 transition-all duration-300",
                "backdrop-blur-md",
                level < value 
                  ? "bg-blue-500/50" 
                  : "bg-white/10 dark:bg-zinc-700/20"
              )}
              style={{
                marginLeft: index === 0 ? '24px' : '8px',
                marginRight: index === levels.length - 2 ? '24px' : '8px'
              }}
            />
          ))}
        </div>
        
        {/* Glass circle buttons */}
        {levels.map((level) => {
          const isSelected = level <= value;
          const isCurrentValue = level === value;
          const isHovered = level === hoveredLevel;
          
          return (
            <button
              key={level}
              onClick={() => onChange(level)}
              onMouseEnter={() => setHoveredLevel(level)}
              onMouseLeave={() => setHoveredLevel(null)}
              className={cn(
                "relative z-10 w-12 h-12 rounded-full transition-all duration-300",
                "flex items-center justify-center flex-shrink-0",
                "hover:scale-110 active:scale-95"
              )}
            >
              {/* Outer glass layer with glow */}
              <div className={cn(
                "absolute inset-0 rounded-full transition-all duration-300",
                "backdrop-blur-xl border",
                isSelected 
                  ? "bg-black/90 border-blue-500/50" 
                  : "bg-black/95 border-red-500/30"
              )}>
                {/* Glow effect - pulsing for current value */}
                <div className={cn(
                  "absolute -inset-2 rounded-full transition-all duration-300",
                  isSelected
                    ? "bg-blue-500/30 blur-lg"
                    : "bg-red-500/20 blur-md",
                  isCurrentValue && "animate-pulse-glow"
                )} />
              </div>
              
              {/* Inner glass layer */}
              <div className={cn(
                "absolute inset-[3px] rounded-full transition-all duration-300",
                "backdrop-blur-md border",
                isSelected 
                  ? "bg-gradient-to-b from-blue-500/30 to-blue-600/40 border-blue-400/60" 
                  : "bg-gradient-to-b from-white/5 to-white/10 border-white/20"
              )} />
              
              {/* Number display */}
              <span className={cn(
                "relative z-20 text-base font-bold transition-all duration-300",
                isSelected 
                  ? "text-blue-300 drop-shadow-[0_0_10px_rgba(59,130,246,0.8)]" 
                  : "text-gray-400 dark:text-gray-500"
              )}>
                {level}
              </span>
            </button>
          );
        })}
      </div>
      
      {/* Selected/Hovered level indicator text */}
      <div className="mt-4 text-sm text-gray-600 dark:text-zinc-400 text-center transition-all duration-200">
        {getLevelDescription(hoveredLevel || value)}
      </div>
      
      {/* Detailed tooltip - positioned better */}
      {showTooltip && onTooltipToggle && (
        <motion.div 
          className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-4 p-3 bg-gray-900/95 dark:bg-black/95 text-white rounded-lg shadow-xl w-80 backdrop-blur-md border border-gray-700"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <h4 className="font-semibold mb-2 text-sm">Crawl Depth Explained</h4>
          <div className="space-y-1.5 text-xs">
            <div className={cn("transition-all duration-300", value === 1 ? "text-blue-300" : "text-gray-300")}>
              <span className="font-medium text-blue-400">Level 1:</span> Only the URL you provide (1-50 pages)
              <div className="text-gray-500 text-[10px]">Best for: Single articles, specific pages</div>
            </div>
            <div className={cn("transition-all duration-300", value === 2 ? "text-blue-300" : "text-gray-300")}>
              <span className="font-medium text-green-400">Level 2:</span> URL + all linked pages (10-200 pages)
              <div className="text-gray-500 text-[10px]">Best for: Documentation sections, blogs</div>
            </div>
            <div className={cn("transition-all duration-300", value === 3 ? "text-blue-300" : "text-gray-300")}>
              <span className="font-medium text-yellow-400">Level 3:</span> URL + 2 levels of links (50-500 pages)
              <div className="text-gray-500 text-[10px]">Best for: Entire sites, comprehensive docs</div>
            </div>
            <div className={cn("transition-all duration-300", value >= 4 ? "text-blue-300" : "text-gray-300")}>
              <span className="font-medium text-orange-400">Level 4-5:</span> Very deep crawling (100-1000+ pages)
              <div className="text-gray-500 text-[10px]">Warning: May include irrelevant content</div>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-gray-700 text-[10px] text-gray-500">
            💡 More data isn't always better. Choose based on your needs.
          </div>
        </motion.div>
      )}
    </div>
  );
};