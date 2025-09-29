import { useEffect, useState } from 'react';
/**
 * Custom hook for creating staggered entrance animations
 * @param items Array of items to animate
 * @param staggerDelay Delay between each item animation (in seconds)
 * @param forceReanimateCounter Optional counter to force reanimation when it changes
 * @returns Animation variants and props for Framer Motion
 */
export const useStaggeredEntrance = <T,>(items: T[], staggerDelay: number = 0.15, forceReanimateCounter?: number) => {
  const [isVisible, setIsVisible] = useState(false);
  useEffect(() => {
    // Set visible after component mounts for the animation to trigger
    setIsVisible(true);
    // Reset visibility briefly to trigger reanimation when counter changes
    if (forceReanimateCounter !== undefined && forceReanimateCounter > 0) {
      setIsVisible(false);
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [forceReanimateCounter]);
  // Parent container variants
  const containerVariants = {
    hidden: {
      opacity: 0
    },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: 0.1
      }
    }
  };
  // Child item variants
  const itemVariants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.98
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: 'easeOut'
      }
    }
  };
  // Title animation variants
  const titleVariants = {
    hidden: {
      opacity: 0,
      scale: 0.98
    },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: 'easeOut'
      }
    }
  };
  return {
    isVisible,
    containerVariants,
    itemVariants,
    titleVariants
  };
};