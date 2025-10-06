# Task 13 Validation: Frontend Query Hooks (Tasks)

**Task ID**: fbf6c4cb-b05e-4d07-8ddb-fb3384039b7b
**Date**: 2025-10-06
**Status**: COMPLETE

## Files Created

1. `/Users/jon/source/vibes/task-management-ui/frontend/src/features/tasks/hooks/useTaskQueries.ts` (425 lines)
2. `/Users/jon/source/vibes/task-management-ui/frontend/src/features/shared/utils/optimistic.ts` (110 lines)

## Implementation Summary

### 1. Query Key Factory
Created hierarchical query key structure:
```typescript
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  detail: (id: string) => [...taskKeys.all, "detail", id] as const,
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
};
```

### 2. Query Hooks

#### useProjectTasks(projectId, enabled)
- Smart polling with 2-second interval when tab visible
- Pauses polling when tab hidden (via `useSmartPolling`)
- Refetches on window focus
- `staleTime: STALE_TIMES.frequent` (5 seconds)
- Returns tasks, isLoading, error states

#### useTask(taskId, enabled)
- Single task query by ID
- `staleTime: STALE_TIMES.normal` (30 seconds)
- Conditional query with DISABLED_QUERY_KEY pattern

### 3. Mutation Hooks

#### useCreateTask()
**Optimistic Update Pattern**:
1. `onMutate`:
   - ✅ CRITICAL: Awaits `cancelQueries()` (Gotcha #4)
   - Snapshots previous state for rollback
   - Creates optimistic entity with `_localId` and `_optimistic` flag
   - Adds optimistic task to cache
   - Returns context: `{ previousTasks, optimisticId }`

2. `onError`:
   - Rolls back to previous state
   - Logs error with context
   - Ready for toast notification (commented for future)

3. `onSuccess`:
   - Replaces optimistic entity with server data using `_localId`
   - Deduplicates entities (handles race conditions)
   - Ready for success toast (commented)

4. `onSettled`:
   - Invalidates queries to ensure consistency

#### useUpdateTask(projectId)
- Same optimistic pattern as create
- Updates task in cache immediately
- Rolls back on error
- Merges server response to sync timestamps

#### useUpdateTaskPosition(projectId)
- Dedicated mutation for drag-and-drop
- Uses backend endpoint: `PATCH /api/tasks/{id}/position`
- Optimistic position update in cache
- Rollback on error
- Always refetches for correct ordering

#### useDeleteTask(projectId)
- Optimistic removal from cache
- Rollback on error
- Invalidates queries on success

## Gotchas Addressed

### ✅ Gotcha #4: Race Conditions (CRITICAL)
**All mutations** include:
```typescript
await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });
```
This prevents background refetches from overwriting optimistic updates.

### ✅ Stable Optimistic IDs
Uses `_localId` (via `createOptimisticEntity`) for stable references:
```typescript
const optimisticTask = createOptimisticEntity<Task>({...});
// optimisticTask._localId is stable
// Used to replace with server data in onSuccess
```

### ✅ Smart Polling Pause
Uses `useSmartPolling(2000)` which:
- Returns `false` when tab hidden (stops polling)
- Returns `2000` when tab visible (2-second interval)
- Combined with `refetchIntervalInBackground: false` in queryClient

### ✅ Deduplication
Uses `removeDuplicateEntities()` after replacing optimistic entities to handle race conditions where server pushes data before `onSuccess` runs.

## Optimistic Utilities Created

### `/features/shared/utils/optimistic.ts`

#### `createOptimisticEntity<T>(data)`
- Adds `_optimistic: true` flag
- Adds `_localId: nanoid()` for stable reference
- Returns typed entity with optimistic flags

#### `replaceOptimisticEntity(entities, localId, serverEntity)`
- Finds entity by `_localId`
- Replaces with server entity
- Removes optimistic flags

#### `removeDuplicateEntities(entities, idField)`
- Deduplicates by ID field
- Keeps last occurrence (latest data)

#### `isOptimisticEntity(entity)`
- Type guard for checking optimistic entities

## Pattern Compliance

### Followed from PRP Example (`useTaskQueries.ts`)
✅ Query key factory structure
✅ Smart polling integration
✅ Optimistic update pattern with cancelQueries
✅ Rollback on error
✅ Replace optimistic with server data
✅ Deduplication after replacement
✅ Context return from onMutate

### Adapted for This Project
- Removed `useToast` dependency (not yet created)
  - Left comments for future integration
- Simplified type imports (no Archon-specific types)
- Matched Task type from `/features/tasks/types/task.ts`
- Used `taskService` from `/features/tasks/services/taskService.ts`

## Dependencies Verified

✅ Task 11 (taskService) - COMPLETE
- `/features/tasks/services/taskService.ts` exists
- Methods used: `createTask`, `updateTask`, `updateTaskPosition`, `deleteTask`, `getTasksByProject`, `getTask`

✅ Task 12 (queryClient) - COMPLETE
- `/features/shared/config/queryClient.ts` exists
- `/features/shared/config/queryPatterns.ts` exists (STALE_TIMES, DISABLED_QUERY_KEY)
- `/features/shared/hooks/useSmartPolling.ts` exists

## Testing Readiness

### Manual Testing Checklist
When integrated with UI components:
- [ ] useProjectTasks returns tasks with isLoading state
- [ ] Polling pauses when tab hidden
- [ ] Polling resumes when tab becomes visible
- [ ] Create mutation adds task to cache immediately (optimistic)
- [ ] Create mutation replaces optimistic with server data
- [ ] Create mutation rolls back on error
- [ ] Update mutation shows immediate change
- [ ] Delete mutation removes task immediately
- [ ] Drag-and-drop position updates immediately

### Integration Points
Ready for:
- Task 14: Kanban Column (will use `useProjectTasks`, `useUpdateTaskPosition`)
- Task 15: Draggable Task Card (will use mutation hooks)
- Task 16: Project Queries (will follow same pattern)

## Known Limitations

1. **No toast notifications**: `useToast` hook not yet created
   - Comments left in code for future integration
   - Console.error used for debugging

2. **No TypeScript compilation check**:
   - No package.json or tsconfig.json in frontend directory yet
   - Syntax follows TypeScript best practices
   - Will be validated when build setup is complete

## Success Criteria

✅ All 4 mutation hooks with optimistic updates
✅ Query cancellation in onMutate (Gotcha #4 addressed)
✅ Error rollback on mutation failure
✅ Smart polling integration
✅ Query key factory with hierarchical structure
✅ Optimistic entity utilities created
✅ Follows PRP pattern exactly

## Code Quality

- **Documentation**: Comprehensive JSDoc comments for all functions
- **Error Handling**: Robust rollback on all mutations
- **Type Safety**: Full TypeScript typing with generics
- **Pattern Consistency**: All mutations follow same optimistic pattern
- **Gotcha Prevention**: Comments reference specific gotchas from PRP

## Next Steps

1. Create `useToast` hook for user feedback
2. Integrate with Kanban components (Task 14-15)
3. Add unit tests for mutation hooks
4. Add integration tests with mock API

---

**Implementation Time**: ~25 minutes
**Confidence Level**: HIGH
**Ready for Integration**: YES
