# Source: infra/rag-service/frontend/src/components/CrawlManagement.tsx
# Lines: 1-457 (key patterns extracted)
# Pattern: React component with CRUD operations, forms, and state management
# Extracted: 2025-10-16
# Relevance: 10/10

"""React Component Pattern: CRUD Management with Forms.

This example demonstrates:
1. Component structure for management UIs
2. Form handling with react-hook-form
3. List display with filters and pagination
4. Modal dialogs for confirmations
5. Auto-refresh for active jobs
6. Error handling and loading states

Key patterns to mimic:
- useState for state management
- useEffect for data loading and auto-refresh
- useCallback for memoized functions
- Form validation with react-hook-form
- Confirmation modals before delete
- Status-based conditional rendering
- Inline styles for component styling

This pattern can be adapted for DocumentsManagement component.
"""

# TypeScript/React patterns (documented for Python developers)

# Component State Structure
"""
const [items, setItems] = useState<ItemResponse[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
const [expandedItemId, setExpandedItemId] = useState<string | null>(null);
const [deletingItemId, setDeletingItemId] = useState<string | null>(null);
"""

# Form Handling Pattern
"""
const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
    defaultValues: {
        field1: 'default_value',
        field2: 100,
    },
});

const onSubmit = async (data: FormData) => {
    setError(null);
    try {
        await createItem(data);
        reset();
        await loadItems();
    } catch (err) {
        setError(err instanceof Error ? err.message : 'Operation failed');
    }
};
"""

# Data Loading Pattern
"""
const loadItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
        const params = statusFilter === 'all' ? {} : { status: statusFilter };
        const data = await listItems(params);
        setItems(data.items);
    } catch (err) {
        console.error('Failed to load items:', err);
        setError(err instanceof Error ? err.message : 'Failed to load items');
    } finally {
        setLoading(false);
    }
}, [statusFilter]);

useEffect(() => {
    loadItems();
}, [loadItems]);
"""

# Auto-Refresh Pattern (for active jobs/processes)
"""
useEffect(() => {
    if (!autoRefresh) return;

    const hasActiveItems = items?.some(
        (item) => item.status === 'pending' || item.status === 'running'
    );

    if (!hasActiveItems) return;

    const interval = setInterval(() => {
        loadItems();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
}, [items, autoRefresh, loadItems]);
"""

# Delete with Confirmation Modal Pattern
"""
const [deletingItemId, setDeletingItemId] = useState<string | null>(null);

const handleDeleteItem = async (itemId: string) => {
    setError(null);
    try {
        await deleteItem(itemId);
        setDeletingItemId(null);
        await loadItems();
    } catch (err) {
        console.error('Failed to delete item:', err);
        setError(err instanceof Error ? err.message : 'Failed to delete item');
    }
};

// In JSX:
<button
    onClick={(e) => {
        e.stopPropagation();
        setDeletingItemId(item.id);
    }}
    style={styles.deleteButton}
>
    Delete
</button>

{deletingItemId && (
    <div style={styles.modalOverlay}>
        <div style={styles.modal}>
            <h3>Confirm Delete</h3>
            <p>Are you sure? This action cannot be undone.</p>
            <div style={styles.modalActions}>
                <button onClick={() => handleDeleteItem(deletingItemId)}>
                    Delete
                </button>
                <button onClick={() => setDeletingItemId(null)}>
                    Cancel
                </button>
            </div>
        </div>
    </div>
)}
"""

# Status Badge Pattern
"""
const getStatusStyle = (status: string) => {
    switch (status) {
        case 'completed':
            return styles.statusCompleted;  // Green background
        case 'running':
            return styles.statusRunning;    // Blue background
        case 'pending':
            return styles.statusPending;    // Yellow background
        case 'failed':
            return styles.statusFailed;     // Red background
        default:
            return styles.statusDefault;    // Gray background
    }
};

<span style={{ ...styles.statusBadge, ...getStatusStyle(item.status) }}>
    {item.status}
</span>
"""

# Expandable Card Pattern
"""
const [expandedItemId, setExpandedItemId] = useState<string | null>(null);

const toggleItemDetails = (itemId: string) => {
    setExpandedItemId(expandedItemId === itemId ? null : itemId);
};

// In JSX:
<div
    style={styles.itemHeader}
    onClick={() => toggleItemDetails(item.id)}
>
    {/* Header content */}
</div>

{expandedItemId === item.id && (
    <div style={styles.itemDetails}>
        {/* Detailed information */}
    </div>
)}
"""

# Filter Dropdown Pattern
"""
<select
    value={statusFilter}
    onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
    style={styles.select}
>
    <option value="all">All Statuses</option>
    <option value="pending">Pending</option>
    <option value="running">Running</option>
    <option value="completed">Completed</option>
    <option value="failed">Failed</option>
</select>
"""

# Empty State Pattern
"""
{items?.length === 0 ? (
    <div style={styles.emptyState}>
        <p style={styles.emptyText}>No items found</p>
        <p style={styles.emptyHint}>Create your first item using the form above</p>
    </div>
) : (
    <div style={styles.itemsContainer}>
        {items?.map((item) => (
            <ItemCard key={item.id} item={item} />
        ))}
    </div>
)}
"""

# Loading State Pattern
"""
{loading ? (
    <div style={styles.loadingContainer}>
        <p style={styles.loadingText}>Loading items...</p>
    </div>
) : (
    // Render content
)}
"""

# Error Display Pattern
"""
{error && (
    <div style={styles.errorContainer}>
        <p style={styles.errorText}>{error}</p>
    </div>
)}
"""

# Key Takeaways for DocumentsManagement Component:
# 1. Use same state management patterns (useState, useEffect)
# 2. Implement delete confirmation modal
# 3. Show document metadata (title, type, chunk count, created date)
# 4. Add source filter dropdown (reuse from SearchInterface)
# 5. Display chunk count for each document
# 6. Add pagination if > 25 documents
# 7. Show loading/error/empty states
# 8. Use inline styles matching CrawlManagement aesthetic
# 9. Include success/error toast notifications
