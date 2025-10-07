/**
 * Optimistic Update Utilities
 *
 * PURPOSE: Utilities for TanStack Query optimistic updates
 * PATTERN: Stable _localId for optimistic entities
 *
 * USAGE:
 * ```ts
 * const optimisticTask = createOptimisticEntity<Task>({
 *   title: "New task",
 *   status: "todo",
 * });
 * // optimisticTask has _localId and _optimistic flag
 *
 * // Replace optimistic with server data
 * const updated = replaceOptimisticEntity(
 *   tasks,
 *   optimisticTask._localId,
 *   serverTask
 * );
 * ```
 */

import { nanoid } from "nanoid";

/**
 * OptimisticEntity: Interface for entities with optimistic flags
 *
 * PATTERN: Entities during optimistic updates have:
 * - _optimistic: true (flag for UI to show pending state)
 * - _localId: stable ID for replacing with server data
 */
export interface OptimisticEntity {
  _optimistic: true;
  _localId: string;
}

/**
 * Create optimistic entity with stable local ID
 *
 * PATTERN: Use nanoid() for collision-free temporary IDs
 * - _optimistic flag allows UI to show "pending" state
 * - _localId allows replacing with server data on success
 *
 * @param data - Partial entity data
 * @returns Entity with optimistic flags
 */
export function createOptimisticEntity<T extends Record<string, any>>(data: Partial<T>): T & OptimisticEntity {
  return {
    ...data,
    _optimistic: true,
    _localId: nanoid(),
  } as T & OptimisticEntity;
}

/**
 * Replace optimistic entity with server data
 *
 * PATTERN: Find by _localId, replace with server entity
 * - Removes _optimistic and _localId flags
 * - Preserves order in array
 *
 * @param entities - Array of entities (some may be optimistic)
 * @param localId - _localId of optimistic entity to replace
 * @param serverEntity - Real entity from server
 * @returns Updated array with server entity
 */
export function replaceOptimisticEntity<T extends Record<string, any>>(
  entities: (T & Partial<OptimisticEntity>)[],
  localId: string,
  serverEntity: T,
): T[] {
  return entities.map((entity) => {
    if (entity._localId === localId) {
      // Remove optimistic flags
      const { _optimistic, _localId, ...rest } = entity;
      return serverEntity;
    }
    return entity as T;
  });
}

/**
 * Remove duplicate entities (by id field)
 *
 * PATTERN: Deduplicate after replacing optimistic entities
 * - Sometimes server returns entity before onSuccess runs
 * - Keeps latest version (last in array)
 *
 * @param entities - Array of entities
 * @param idField - Field to use for deduplication (default: "id")
 * @returns Deduplicated array
 */
export function removeDuplicateEntities<T extends Record<string, any>>(
  entities: T[],
  idField: keyof T = "id",
): T[] {
  const seen = new Map<any, T>();

  for (const entity of entities) {
    const id = entity[idField];
    if (id !== undefined) {
      seen.set(id, entity);
    }
  }

  return Array.from(seen.values());
}

/**
 * Check if entity is optimistic
 *
 * @param entity - Entity to check
 * @returns true if entity is optimistic
 */
export function isOptimisticEntity(entity: any): entity is OptimisticEntity {
  return entity?._optimistic === true && typeof entity?._localId === "string";
}
