/**
 * TanStack Query Configuration Patterns
 *
 * PURPOSE: Centralized stale time constants and query patterns
 * GOTCHA #10: Use named constants instead of magic numbers
 *
 * STALE_TIMES guide:
 * - instant (0): Always refetch (auth status, real-time data)
 * - frequent (5s): High-change data (task lists with polling)
 * - normal (30s): Medium-change data (project lists)
 * - rare (5min): Low-change data (user profiles, settings)
 * - static (Infinity): Never changes (feature flags, constants)
 */

export const STALE_TIMES = {
  instant: 0,
  frequent: 5_000, // 5 seconds
  normal: 30_000, // 30 seconds
  rare: 300_000, // 5 minutes
  static: Infinity,
} as const;

/**
 * DISABLED_QUERY_KEY: Use for conditional queries
 *
 * Example:
 * ```ts
 * useQuery({
 *   queryKey: projectId ? ['project', projectId] : DISABLED_QUERY_KEY,
 *   queryFn: () => fetchProject(projectId!),
 *   enabled: !!projectId,
 * })
 * ```
 */
export const DISABLED_QUERY_KEY = ["disabled"] as const;
