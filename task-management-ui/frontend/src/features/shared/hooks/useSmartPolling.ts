/**
 * Smart Polling Hook - Visibility-Aware Refetch Intervals
 *
 * PURPOSE: Pause polling when tab/window is hidden to save resources
 * GOTCHA #10: Combines with refetchIntervalInBackground: false for full effect
 *
 * USAGE:
 * ```ts
 * const { refetchInterval } = useSmartPolling(2000); // 2s when visible
 *
 * useQuery({
 *   queryKey: ['tasks', projectId],
 *   queryFn: fetchTasks,
 *   refetchInterval, // Pauses when tab hidden
 * });
 * ```
 *
 * HOW IT WORKS:
 * 1. Listens to visibilitychange events
 * 2. Returns baseInterval when tab visible
 * 3. Returns false when tab hidden (stops polling)
 * 4. Automatically refetches when tab becomes visible (refetchOnWindowFocus)
 */

import { useEffect, useState } from "react";

export function useSmartPolling(baseInterval: number) {
  const [isVisible, setIsVisible] = useState<boolean>(!document.hidden);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    // Listen for tab visibility changes
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Cleanup listener on unmount
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  // Return false to disable polling when hidden
  // Return baseInterval when visible
  return {
    refetchInterval: isVisible ? baseInterval : false,
  };
}
