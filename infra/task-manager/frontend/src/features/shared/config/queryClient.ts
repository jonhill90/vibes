/**
 * TanStack Query Client Configuration
 *
 * PURPOSE: QueryClient with smart defaults for task management
 * GOTCHAS ADDRESSED:
 *   - Gotcha #10: refetchIntervalInBackground: false to pause polling when tab hidden
 *   - Don't retry 4xx errors (client errors are not transient)
 */

import { QueryClient } from "@tanstack/react-query";
import { STALE_TIMES } from "./queryPatterns";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // STALE TIME: How long data is considered fresh (no refetch)
      // Default: 30 seconds (medium-change data)
      staleTime: STALE_TIMES.normal,

      // GC TIME (formerly cacheTime): How long unused data stays in cache
      // Default: 10 minutes (balance memory vs UX)
      gcTime: 10 * 60 * 1000,

      // REFETCH BEHAVIOR: Refetch when window regains focus
      // Rationale: User returning to tab likely wants fresh data
      // ETag headers make this cheap if data unchanged
      refetchOnWindowFocus: true,

      // RETRY LOGIC: Don't retry client errors (4xx)
      // Rationale: 4xx errors are permanent (bad request, unauthorized, not found)
      // Only retry transient errors (5xx, network failures)
      retry: (failureCount, error) => {
        // Don't retry more than 3 times
        if (failureCount >= 3) return false;

        // Check if error has status code
        if (error && typeof error === "object" && "status" in error) {
          const status = (error as { status: number }).status;
          // Don't retry 4xx client errors
          if (status >= 400 && status < 500) return false;
        }

        // Retry on 5xx server errors and network failures
        return true;
      },

      // BACKGROUND POLLING: CRITICAL - Pause polling when tab hidden
      // GOTCHA #10: Without this, polling continues when user switches tabs
      // Result: Wasted API calls, battery drain on mobile
      refetchIntervalInBackground: false,
    },
    mutations: {
      // MUTATION RETRY: Don't retry mutations by default
      // Rationale: Mutations can have side effects (duplicate creates)
      // Let user explicitly retry via UI
      retry: false,
    },
  },
});
