# Task 3 Implementation Complete: Create Optimistic Mutation Hook

## Task Information
- **Task ID**: N/A (Part of multi_project_selector PRP execution)
- **Task Name**: Task 3: Create Optimistic Mutation Hook
- **Responsibility**: Create project mutation with optimistic updates, rollback, and race condition prevention
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
None (this task extends an existing file from Task 2)

### Modified Files:
1. **`/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/hooks/useProjectQueries.ts`** (231 lines total, +151 lines added)
   - **Added Imports**:
     - `useQueryClient`, `useMutation` from `@tanstack/react-query`
     - `createOptimisticEntity`, `OptimisticEntity`, `removeDuplicateEntities`, `replaceOptimisticEntity` from optimistic utils
     - `ProjectCreate` type import
   - **Added Hook**: `useCreateProject()` mutation hook (lines 102-179)
   - **Pattern**: Complete optimistic update flow with race condition prevention
   - **Documentation**: Comprehensive JSDoc comments explaining gotchas and patterns
   - **Usage Example**: Added example in documentation showing usage with isPending state

## Implementation Details

### Core Features Implemented

#### 1. useCreateProject Mutation Hook
- **MutationKey**: `['createProject']` for concurrent mutation tracking
- **Type Safety**: Full TypeScript generics with context type `{ previousProjects?: Project[]; optimisticId: string }`
- **Service Integration**: Calls `projectService.createProject(projectData)`

#### 2. onMutate - Optimistic Update Logic
- **Race Condition Prevention**: `await queryClient.cancelQueries({ queryKey: projectKeys.lists() })` (CRITICAL)
- **State Snapshot**: Captures `previousProjects` for rollback capability
- **Optimistic Entity Creation**: Uses `createOptimisticEntity<Project>()` with:
  - Temporary ID: `temp-${Date.now()}`
  - Stable `_localId` via nanoid
  - `_optimistic` flag for UI state indication
- **Cache Update**: Adds optimistic project at beginning of list
- **Context Return**: Returns `{ previousProjects, optimisticId }` for error/success handlers

#### 3. onError - Rollback on Failure
- **Error Logging**: Logs error message with project name context
- **State Restoration**: Restores `previousProjects` from context
- **User Feedback**: Placeholder for toast notification (TODO)

#### 4. onSuccess - Server Data Replacement
- **Optimistic Replacement**: Uses `replaceOptimisticEntity()` to swap temp entity with server data
- **Deduplication**: Applies `removeDuplicateEntities()` to handle race conditions
- **Clean Data**: Removes `_optimistic` and `_localId` flags from final state

#### 5. onSettled - Concurrent Mutation Handling
- **Mutation Counting**: Checks `queryClient.isMutating({ mutationKey: ['createProject'] })`
- **Conditional Invalidation**: Only invalidates if `mutationCount === 1` (last mutation)
- **Double-Click Protection**: Prevents invalidation race conditions from concurrent creates

### Critical Gotchas Addressed

#### Gotcha #1: Race Condition - Optimistic Update Overwritten
**Problem**: Background refetch could overwrite optimistic update if not cancelled
**Implementation**:
```typescript
await queryClient.cancelQueries({ queryKey: projectKeys.lists() });
```
**Result**: All in-flight queries cancelled before optimistic update applied

#### Gotcha #2: Concurrent Mutations - Double-Click Issues
**Problem**: Multiple rapid mutations cause invalidation race conditions
**Implementation**:
```typescript
const mutationCount = queryClient.isMutating({ mutationKey: ['createProject'] });
if (mutationCount === 1) {
  queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
}
```
**Result**: Only last mutation triggers invalidation, preventing overwrites

#### Gotcha #10: TanStack Query v5 Breaking Changes
**Implementation**: Used object-based mutation syntax throughout
```typescript
return useMutation<Project, Error, ProjectCreate, Context>({
  mutationKey: ["createProject"],
  mutationFn: (data) => projectService.createProject(data),
  onMutate: async (data) => { ... },
  // ... other handlers
});
```
**Result**: Compliant with TanStack Query v5 API

## Dependencies Verified

### Completed Dependencies:
- **Task 2**: Query keys and list query (`useProjects`, `projectKeys`) exist in same file
- **Shared Utilities**:
  - `createOptimisticEntity` exists at `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/shared/utils/optimistic.ts`
  - `replaceOptimisticEntity` exists (lines 68-81)
  - `removeDuplicateEntities` exists (lines 94-108)
- **Project Service**:
  - `createProject` method exists at `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/services/projectService.ts` (lines 58-61)
  - Returns `Promise<Project>` matching expected type
- **Project Types**:
  - `Project` interface exists (id, name, description, created_at, updated_at)
  - `ProjectCreate` interface exists (name, description?)

### External Dependencies:
- **@tanstack/react-query**: v5.85.8 (verified in package.json)
  - `useQueryClient` hook available
  - `useMutation` hook available
  - `isMutating` method available
- **nanoid**: v5.0.9 (verified in package.json, used by createOptimisticEntity)
- **TypeScript**: v5.5.4 (verified in package.json, ensures type safety)

## Testing Checklist

### Manual Testing (When Component Integration Added in Task 5):
- [ ] Create project via modal form
- [ ] Verify optimistic project appears immediately in dropdown
- [ ] Verify optimistic project has "pending" visual indicator (if implemented in UI)
- [ ] Verify server project replaces optimistic project on success
- [ ] Test error scenario: network disconnect, verify rollback to previous state
- [ ] Test double-click: create two projects rapidly, verify both succeed
- [ ] Verify no duplicate projects in list after mutations complete
- [ ] Check browser console: no errors, proper error logging on failure

### Validation Results:

#### Code Structure Validation:
- ✅ **cancelQueries called before optimistic update** (line 113)
- ✅ **Rollback on error restores previous state** (lines 146-148)
- ✅ **Optimistic ID replaced with server ID on success** (line 159)
- ✅ **Concurrent mutations handled** (lines 172-176)
- ✅ **TypeScript context types correct** (line 105)

#### Pattern Adherence:
- ✅ **Mirrors useTaskQueries.ts structure**:
  - Same import organization
  - Same optimistic update flow
  - Same error handling pattern
  - Same documentation style
- ✅ **Follows example_2_query_hooks_pattern.ts**:
  - Query key factory usage
  - Smart polling integration (from Task 2)
  - Optimistic entity creation
  - Mutation key for tracking

#### Gotcha Coverage:
- ✅ **Gotcha #1 (race conditions)**: cancelQueries implemented
- ✅ **Gotcha #2 (concurrent mutations)**: isMutating check implemented
- ✅ **Gotcha #10 (TanStack Query v5)**: Object-based syntax used

## Success Metrics

**All PRP Requirements Met**:
- [x] **useCreateProject hook added to useProjectQueries.ts**
- [x] **cancelQueries called before optimistic update** (prevents race conditions)
- [x] **Rollback on error restores previous state** (error handler implemented)
- [x] **Optimistic ID replaced with server ID on success** (replaceOptimisticEntity used)
- [x] **Concurrent mutations handled** (isMutating check with mutationKey)
- [x] **TypeScript context types correct** (generics properly typed)
- [x] **Follows pattern from useTaskQueries.ts** (mirrors structure exactly)
- [x] **Uses shared optimistic utilities** (createOptimisticEntity, replaceOptimisticEntity, removeDuplicateEntities)
- [x] **mutationKey specified** (['createProject'] for tracking)
- [x] **Comprehensive error logging** (includes context for debugging)

**Code Quality**:
- ✅ **Comprehensive JSDoc documentation**: 17-line header explaining flow and gotchas
- ✅ **Inline comments**: Every critical section has explanation with gotcha references
- ✅ **Full TypeScript typing**: Generic types for mutation result, error, variables, context
- ✅ **Follows existing patterns**: Mirrors useTaskQueries.ts structure exactly
- ✅ **Error handling**: Comprehensive error logging with context
- ✅ **Code organization**: Logical flow from imports → hook → handlers → documentation
- ✅ **Usage example**: Added to documentation block showing practical usage
- ✅ **No magic values**: Uses projectKeys factory, shared utilities
- ✅ **Defensive coding**: Checks for context existence before using
- ✅ **TODO markers**: Placed for toast integration (planned in later tasks)

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~25 minutes
**Confidence Level**: HIGH

**Reasoning**:
1. ✅ All specific steps from PRP completed
2. ✅ Pattern from useTaskQueries.ts followed exactly
3. ✅ Critical gotchas (#1, #2, #10) addressed with implementations
4. ✅ TypeScript types properly defined with generics
5. ✅ Code structure matches existing codebase patterns
6. ✅ Comprehensive documentation added
7. ✅ Error handling and rollback implemented
8. ✅ Race condition prevention via cancelQueries
9. ✅ Concurrent mutation handling via isMutating
10. ✅ Optimistic update utilities used correctly

**Blockers**: None

### Files Created: 0
### Files Modified: 1
### Total Lines of Code: ~151 lines added (231 lines total in file)

**Ready for integration with Task 4 (EmptyProjectState) and Task 5 (CreateProjectModal).**

---

## Next Steps
1. **Task 4**: Create EmptyProjectState component (will use this hook indirectly via CreateProjectModal)
2. **Task 5**: Create CreateProjectModal component (will call `useCreateProject()` directly)
3. **Integration Testing**: Verify optimistic updates work end-to-end once modal is integrated
4. **Toast Integration**: Replace TODO comments with actual toast calls when useToast is available

## Key Implementation Decisions

### Decision 1: Optimistic Project at Beginning of List
**Choice**: `return [optimisticProject, ...old]` (prepend instead of append)
**Reasoning**:
- New projects are most relevant to user (just created)
- Matches typical UI pattern (newest first)
- Consistent with example_2_query_hooks_pattern.ts (line 89)

### Decision 2: isMutating Count Check
**Choice**: Only invalidate when `mutationCount === 1`
**Reasoning**:
- Prevents invalidation race conditions from double-clicks
- Last mutation to complete triggers single refetch
- Follows pattern from PRP gotchas.md (lines 386-395)

### Decision 3: Temporary ID Format
**Choice**: `temp-${Date.now()}`
**Reasoning**:
- Human-readable for debugging
- Timestamp ensures uniqueness within millisecond
- Matches pattern from useTaskQueries.ts (line 133)
- _localId via nanoid provides stable reference for replacement

### Decision 4: TODO Markers for Toast
**Choice**: Added TODO comments instead of implementing toast
**Reasoning**:
- Toast utility may not be available yet (depends on Task 5)
- Consistent with useTaskQueries.ts pattern (lines 162, 179, 234, 249)
- Placeholder keeps code structure clean
- Easy to find and replace later (grep for "TODO: Show toast")
