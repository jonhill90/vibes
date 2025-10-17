import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import {
  listSources,
  createSource,
  updateSource,
  deleteSource,
  SourceResponse,
  SourceRequest,
} from '../api/client';

/**
 * SourceManagement Component
 *
 * Provides CRUD interface for managing document sources.
 * Features:
 * - Table listing all sources with metadata
 * - Create source form with validation
 * - Edit source functionality (inline or modal)
 * - Delete with confirmation dialog
 * - Loading states and error handling
 */

interface EditingSource {
  id: string;
  title: string;
}

export default function SourceManagement() {
  const [sources, setSources] = useState<SourceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingSource, setEditingSource] = useState<EditingSource | null>(null);
  const [deletingSourceId, setDeletingSourceId] = useState<string | null>(null);
  const [enabledCollections, setEnabledCollections] = useState<('documents' | 'code' | 'media')[]>(['documents']);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<SourceRequest>();

  // Load sources
  const loadSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listSources();
      setSources(data);
    } catch (err) {
      console.error('Failed to load sources:', err);
      setError(err instanceof Error ? err.message : 'Failed to load sources');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  // Collection options configuration
  const collectionOptions = [
    {
      value: 'documents' as const,
      label: 'Documents',
      description: 'General text, articles, documentation, blog posts',
      icon: '📄',
      disabled: false,
    },
    {
      value: 'code' as const,
      label: 'Code',
      description: 'Source code, snippets, technical examples, API docs',
      icon: '💻',
      disabled: false,
    },
    {
      value: 'media' as const,
      label: 'Media',
      description: 'Images, diagrams, visual content (coming soon)',
      icon: '🖼️',
      disabled: true,
    },
  ];

  // Handle collection toggle
  const handleCollectionToggle = (collectionType: 'documents' | 'code' | 'media') => {
    setEnabledCollections((prev) => {
      if (prev.includes(collectionType)) {
        // Remove if already selected (but ensure at least one remains)
        if (prev.length === 1) {
          return prev; // Don't allow removing last collection
        }
        return prev.filter((c) => c !== collectionType);
      } else {
        // Add if not selected
        return [...prev, collectionType];
      }
    });
  };

  // Create source
  const onCreateSource = async (data: SourceRequest) => {
    setError(null);
    try {
      await createSource({
        ...data,
        source_type: 'upload', // Always default to 'upload' type
        enabled_collections: enabledCollections,
      });
      reset();
      setEnabledCollections(['documents']); // Reset to default
      await loadSources();
    } catch (err) {
      console.error('Failed to create source:', err);
      setError(err instanceof Error ? err.message : 'Failed to create source');
    }
  };

  // Update source
  const handleUpdateSource = async () => {
    if (!editingSource) return;

    setError(null);
    try {
      await updateSource(editingSource.id, {
        title: editingSource.title,
      });
      setEditingSource(null);
      await loadSources();
    } catch (err) {
      console.error('Failed to update source:', err);
      setError(err instanceof Error ? err.message : 'Failed to update source');
    }
  };

  // Delete source
  const handleDeleteSource = async (id: string) => {
    setError(null);
    try {
      await deleteSource(id);
      setDeletingSourceId(null);
      await loadSources();
    } catch (err) {
      console.error('Failed to delete source:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete source');
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Source Management</h2>

      {/* Error Display */}
      {error && (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
        </div>
      )}

      {/* Create Source Form */}
      <div style={styles.createSection}>
        <h3 style={styles.subheading}>Create New Source</h3>
        <form onSubmit={handleSubmit(onCreateSource)} style={styles.form}>
          <div style={styles.formRow}>
            <div style={styles.formGroup}>
              <label htmlFor="title" style={styles.label}>
                Source Title
              </label>
              <input
                id="title"
                type="text"
                {...register('title')}
                style={styles.input}
                placeholder="e.g., Documentation, Research Papers"
              />
              {errors.title && <span style={styles.error}>{errors.title.message}</span>}
            </div>
          </div>

          {/* Collection Selection */}
          <div style={styles.collectionSection}>
            <label style={styles.label}>
              Enable Collections *
              <span style={styles.helpText}>
                {' '}Select which embedding types to use for this source
              </span>
            </label>

            <div style={styles.collectionCheckboxes}>
              {collectionOptions.map((option) => (
                <label
                  key={option.value}
                  style={{
                    ...styles.collectionOption,
                    ...(option.disabled ? styles.collectionOptionDisabled : {}),
                    ...(enabledCollections.includes(option.value) && !option.disabled
                      ? styles.collectionOptionSelected
                      : {}),
                  }}
                >
                  <input
                    type="checkbox"
                    checked={enabledCollections.includes(option.value)}
                    onChange={() => handleCollectionToggle(option.value)}
                    disabled={option.disabled}
                    style={styles.collectionCheckbox}
                  />
                  <div style={styles.collectionInfo}>
                    <div style={styles.collectionHeader}>
                      <span style={styles.collectionIcon}>{option.icon}</span>
                      <span style={styles.collectionLabel}>{option.label}</span>
                    </div>
                    <div style={styles.collectionDescription}>
                      {option.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>

            {enabledCollections.length === 0 && (
              <div style={styles.errorMessage}>
                At least one collection must be enabled
              </div>
            )}
          </div>

          <div style={styles.formRow}>
            <button type="submit" style={styles.createButton}>
              Create Source
            </button>
          </div>
        </form>
      </div>

      {/* Sources Table */}
      <div style={styles.tableSection}>
        <h3 style={styles.subheading}>Existing Sources</h3>

        {loading ? (
          <div style={styles.loadingContainer}>
            <p style={styles.loadingText}>Loading sources...</p>
          </div>
        ) : sources?.length === 0 ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>No sources found</p>
            <p style={styles.emptyHint}>Create your first source using the form above</p>
          </div>
        ) : (
          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeaderRow}>
                  <th style={styles.tableHeader}>Title</th>
                  <th style={styles.tableHeader}>Collections</th>
                  <th style={styles.tableHeader}>Status</th>
                  <th style={styles.tableHeader}>Created</th>
                  <th style={styles.tableHeader}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sources?.map((source) => (
                  <tr key={source.id} style={styles.tableRow}>
                    <td style={styles.tableCell}>
                      {editingSource?.id === source.id ? (
                        <input
                          type="text"
                          value={editingSource.title}
                          onChange={(e) =>
                            setEditingSource({ ...editingSource, title: e.target.value })
                          }
                          style={styles.editInput}
                        />
                      ) : (
                        source.title || source.url || `Untitled ${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`
                      )}
                    </td>
                    <td style={styles.tableCell}>
                      {source.enabled_collections?.map((collection) => {
                        const option = collectionOptions.find(opt => opt.value === collection);
                        return option ? `${option.icon} ${option.label}` : collection;
                      }).join(', ') || '📄 Documents'}
                    </td>
                    <td style={styles.tableCell}>
                      <span style={{
                        ...styles.statusBadge,
                        backgroundColor:
                          source.status === 'completed' ? '#d4edda' :
                          source.status === 'failed' ? '#f8d7da' :
                          source.status === 'processing' ? '#fff3cd' :
                          '#e2e3e5'
                      }}>
                        {source.status}
                      </span>
                    </td>
                    <td style={styles.tableCell}>
                      {new Date(source.created_at).toLocaleDateString()}
                    </td>
                    <td style={styles.tableCell}>
                      {editingSource?.id === source.id ? (
                        <div style={styles.actionButtons}>
                          <button
                            onClick={handleUpdateSource}
                            style={styles.saveButton}
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingSource(null)}
                            style={styles.cancelButton}
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div style={styles.actionButtons}>
                          <button
                            onClick={() =>
                              setEditingSource({
                                id: source.id,
                                title: source.title || '',
                              })
                            }
                            style={styles.editButton}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => setDeletingSourceId(source.id)}
                            style={styles.deleteButton}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      {deletingSourceId && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h3 style={styles.modalTitle}>Confirm Delete</h3>
            <p style={styles.modalText}>
              Are you sure you want to delete this source? This action cannot be undone.
            </p>
            <div style={styles.modalActions}>
              <button
                onClick={() => handleDeleteSource(deletingSourceId)}
                style={styles.confirmDeleteButton}
              >
                Delete
              </button>
              <button
                onClick={() => setDeletingSourceId(null)}
                style={styles.cancelModalButton}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Inline styles
const styles = {
  container: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: '20px',
  },
  heading: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333',
  },
  subheading: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#555',
  },
  errorContainer: {
    padding: '16px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    marginBottom: '16px',
  },
  errorText: {
    color: '#721c24',
    margin: 0,
  },
  createSection: {
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    marginBottom: '32px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  formRow: {
    display: 'flex',
    gap: '16px',
    alignItems: 'flex-end',
    flexWrap: 'wrap' as const,
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
    flex: '1',
    minWidth: '200px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#555',
  },
  input: {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
  },
  select: {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
    backgroundColor: '#fff',
  },
  error: {
    fontSize: '12px',
    color: '#dc3545',
  },
  createButton: {
    padding: '10px 24px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    height: 'fit-content',
  },
  tableSection: {
    marginTop: '32px',
  },
  loadingContainer: {
    textAlign: 'center' as const,
    padding: '40px',
  },
  loadingText: {
    fontSize: '16px',
    color: '#666',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '40px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
  },
  emptyText: {
    fontSize: '18px',
    color: '#333',
    margin: '0 0 8px 0',
  },
  emptyHint: {
    fontSize: '14px',
    color: '#666',
    margin: 0,
  },
  tableContainer: {
    overflowX: 'auto' as const,
    border: '1px solid #ddd',
    borderRadius: '8px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    backgroundColor: '#fff',
  },
  tableHeaderRow: {
    backgroundColor: '#f8f9fa',
  },
  tableHeader: {
    padding: '12px',
    textAlign: 'left' as const,
    fontSize: '14px',
    fontWeight: '600',
    color: '#555',
    borderBottom: '2px solid #ddd',
  },
  tableRow: {
    borderBottom: '1px solid #eee',
  },
  tableCell: {
    padding: '12px',
    fontSize: '14px',
    color: '#333',
  },
  editInput: {
    padding: '6px',
    fontSize: '14px',
    border: '1px solid #007bff',
    borderRadius: '4px',
    width: '100%',
  },
  editSelect: {
    padding: '6px',
    fontSize: '14px',
    border: '1px solid #007bff',
    borderRadius: '4px',
    backgroundColor: '#fff',
  },
  actionButtons: {
    display: 'flex',
    gap: '8px',
  },
  editButton: {
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  deleteButton: {
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#dc3545',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  saveButton: {
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  cancelButton: {
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#333',
    backgroundColor: '#f8f9fa',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  modalOverlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: '#fff',
    padding: '24px',
    borderRadius: '8px',
    maxWidth: '400px',
    width: '90%',
  },
  modalTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#333',
    marginBottom: '16px',
  },
  modalText: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '24px',
  },
  modalActions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
  },
  confirmDeleteButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#dc3545',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  cancelModalButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
    backgroundColor: '#f8f9fa',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  statusBadge: {
    display: 'inline-block',
    padding: '4px 8px',
    fontSize: '12px',
    fontWeight: '500',
    borderRadius: '4px',
    textTransform: 'capitalize' as const,
  },
  collectionSection: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
    marginTop: '16px',
  },
  helpText: {
    fontSize: '12px',
    fontWeight: '400',
    color: '#888',
  },
  collectionCheckboxes: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  collectionOption: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '16px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backgroundColor: '#fff',
  },
  collectionOptionSelected: {
    borderColor: '#28a745',
    backgroundColor: '#f0f9f4',
  },
  collectionOptionDisabled: {
    cursor: 'not-allowed',
    opacity: 0.6,
    backgroundColor: '#f8f9fa',
  },
  collectionCheckbox: {
    width: '18px',
    height: '18px',
    marginTop: '2px',
    cursor: 'pointer',
    flexShrink: 0,
  },
  collectionInfo: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
    flex: 1,
  },
  collectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#333',
  },
  collectionIcon: {
    fontSize: '20px',
  },
  collectionLabel: {
    fontSize: '16px',
    fontWeight: '600',
  },
  collectionDescription: {
    fontSize: '14px',
    color: '#666',
    lineHeight: '1.4',
  },
  errorMessage: {
    fontSize: '13px',
    color: '#dc3545',
    padding: '8px 12px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
  },
};
