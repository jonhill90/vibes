# Task 5 Implementation: Backend Service Layer (Tasks with Position Logic)

## Files Created/Modified

1. **Created**: `src/services/task_service.py` (530 lines)
   - Full TaskService implementation with atomic position reordering
   
2. **Modified**: `src/services/__init__.py`
   - Added TaskService import and export

## Implementation Highlights

### 1. Position Reordering Logic (CRITICAL)

The `update_task_position()` method implements **Gotcha #2** pattern:

```python
async def update_task_position(task_id, new_status, new_position):
    async with self.db_pool.acquire() as conn:
        async with conn.transaction():
            # Step 1: Lock rows in ORDER BY id (prevent deadlocks)
            await conn.execute("""
                SELECT id FROM tasks
                WHERE status = $1 AND position >= $2
                ORDER BY id  -- CRITICAL for deadlock prevention
                FOR UPDATE
            """, new_status, new_position)
            
            # Step 2: Atomic batch update - increment positions
            await conn.execute("""
                UPDATE tasks
                SET position = position + 1, updated_at = NOW()
                WHERE status = $1 AND position >= $2
            """, new_status, new_position)
            
            # Step 3: Update target task
            await conn.execute("""
                UPDATE tasks
                SET status = $1, position = $2, updated_at = NOW()
                WHERE id = $3
            """, new_status, new_position, task_id)
```

**Why this works**:
- Transaction ensures atomicity (all-or-nothing)
- SELECT ... FOR UPDATE locks rows to prevent concurrent modifications
- ORDER BY id ensures locks are acquired in consistent order (prevents deadlocks)
- Batch UPDATE is much faster than individual updates

### 2. Create Task with Position Reordering

`create_task()` uses the same pattern when inserting at a specific position:

```python
if data.position > 0:
    # Lock rows ORDER BY id
    await conn.execute("""
        SELECT id FROM tasks
        WHERE status = $1 AND position >= $2
        ORDER BY id
        FOR UPDATE
    """, data.status, data.position)
    
    # Increment existing positions
    await conn.execute("""
        UPDATE tasks
        SET position = position + 1, updated_at = NOW()
        WHERE status = $1 AND position >= $2
    """, data.status, data.position)
```

### 3. List Tasks with Field Exclusion

`list_tasks()` implements performance optimization for large descriptions:

```python
if exclude_large_fields:
    # Truncate description > 1000 chars at database level
    select_fields = """
        CASE
            WHEN LENGTH(description) > 1000
            THEN SUBSTRING(description FROM 1 FOR 1000) || '...'
            ELSE description
        END as description
    """
```

This prevents sending large text fields over the network for list views.

### 4. Gotchas Addressed

✅ **Gotcha #2**: Position reordering uses transaction + row locking
- SELECT ... FOR UPDATE acquires locks
- ORDER BY id prevents deadlocks
- Transaction ensures atomicity

✅ **Gotcha #12**: Always uses `async with pool.acquire()`
- Every database operation properly acquires and releases connections
- No connection leaks

✅ **Gotcha #7**: Uses $1, $2 placeholders (asyncpg style)
- NOT %s (which is psycopg2 style)
- All queries use proper parameterization

✅ **Gotcha #1**: All methods are `async def`
- Non-blocking database operations
- Proper async/await usage throughout

### 5. Error Handling Pattern

All methods return `tuple[bool, dict]`:

```python
# Success
return True, {"task": task_data, "message": "Success"}

# Failure
return False, {"error": "Error message"}
```

This pattern (from Archon codebase) makes error handling explicit and predictable.

### 6. Validation Methods

- `validate_status(status)` - checks against VALID_STATUSES
- `validate_priority(priority)` - checks against VALID_PRIORITIES

Both return `tuple[bool, str]` for consistent error reporting.

### 7. Service Methods Implemented

1. `list_tasks(filters, page, per_page, exclude_large_fields)` - Paginated list with filtering
2. `get_task(task_id)` - Get single task
3. `create_task(data)` - Create with position reordering
4. `update_task_position(task_id, new_status, new_position)` - Atomic position update
5. `update_task(task_id, data)` - Partial field updates
6. `delete_task(task_id)` - Delete task

## Testing Recommendations

### Unit Tests (Mocked DB)

```python
async def test_validate_status():
    service = TaskService(mock_pool)
    assert service.validate_status("todo") == (True, "")
    assert service.validate_status("invalid")[0] == False

async def test_create_task():
    service = TaskService(mock_pool)
    success, result = await service.create_task(task_data)
    assert success == True
    assert "task" in result
```

### Integration Tests (Real DB)

```python
async def test_concurrent_position_updates():
    """Test that concurrent updates don't create duplicate positions"""
    service = TaskService(db_pool)
    
    # Create tasks at position 1, 2, 3
    # Then concurrently move two tasks to position 2
    # Verify no duplicate positions result
    
    tasks = await asyncio.gather(
        service.update_task_position("task1", "doing", 2),
        service.update_task_position("task2", "doing", 2),
    )
    
    # Check final positions are unique
    all_tasks = await service.list_tasks({"status": "doing"})
    positions = [t["position"] for t in all_tasks[1]["tasks"]]
    assert len(positions) == len(set(positions))  # No duplicates
```

## Validation Results

✅ Python syntax check passed
✅ All methods follow asyncpg patterns
✅ Position reordering implements Gotcha #2 exactly
✅ Lock ordering (ORDER BY id) prevents deadlocks
✅ Transaction isolation ensures atomicity
✅ Error handling follows tuple[bool, dict] pattern
✅ Validation methods included
✅ Logging added for debugging

## Next Steps

1. **Task 6**: Create FastAPI routes that call these service methods
2. **Task 8**: Create MCP server that uses TaskService
3. **Integration testing**: Test concurrent position updates with real database
4. **Performance testing**: Verify field exclusion improves list performance

## Dependencies

- ✅ Task 2 (Pydantic Models) - TaskCreate, TaskUpdate imported
- ✅ Task 3 (Database Config) - db_pool from database.py used

## File Locations

- Service: `/Users/jon/source/vibes/task-management-ui/backend/src/services/task_service.py`
- Init: `/Users/jon/source/vibes/task-management-ui/backend/src/services/__init__.py`
