/**
 * groupBy - Utility to group array items by a key
 *
 * PURPOSE: Group tasks by status for Kanban board columns
 *
 * @param array - Array to group
 * @param key - Key to group by
 * @returns Object with keys as group names and values as arrays of items
 *
 * EXAMPLE:
 * ```ts
 * const tasks = [
 *   { id: '1', status: 'todo', title: 'Task 1' },
 *   { id: '2', status: 'doing', title: 'Task 2' },
 *   { id: '3', status: 'todo', title: 'Task 3' },
 * ];
 * const grouped = groupBy(tasks, 'status');
 * // { todo: [...], doing: [...] }
 * ```
 */
export function groupBy<T, K extends keyof T>(
  array: T[],
  key: K,
): Record<string, T[]> {
  return array.reduce(
    (result, item) => {
      const groupKey = String(item[key]);
      if (!result[groupKey]) {
        result[groupKey] = [];
      }
      result[groupKey].push(item);
      return result;
    },
    {} as Record<string, T[]>,
  );
}
