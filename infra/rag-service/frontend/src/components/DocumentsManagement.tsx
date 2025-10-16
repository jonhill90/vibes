import { useState, useEffect, useCallback } from 'react';
import {
  listDocuments,
  deleteDocument,
  listSources,
  DocumentResponse,
  SourceResponse,
} from '../api/client';

/**
 * DocumentsManagement Component
 *
 * Provides interface for managing uploaded documents with CRUD operations.
 * Features:
 * - List all documents with metadata (title, type, chunk_count, source)
 * - Filter documents by source with dropdown
 * - Delete documents with two-step confirmation modal
 * - Pagination support for large document collections
 * - Auto-refresh with manual refresh button
 * - Color-coded type badges for visual clarity
 * - Success/error toast notifications
 *
 * Pattern: Adapted from CrawlManagement.tsx (state management, modals, filters)
 */

type SourceFilter = 'all' | string; // 'all' or source UUID

export default function DocumentsManagement() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [sources, setSources] = useState<SourceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<SourceFilter>('all');
  const [expandedDocId, setExpandedDocId] = useState<string | null>(null);
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    total: 0,
    pages: 0,
  });

  // Load sources on mount
  useEffect(() => {
    const loadSources = async () => {
      try {
        const data = await listSources();
        setSources(data);
      } catch (err) {
        console.error('Failed to load sources:', err);
        setError(err instanceof Error ? err.message : 'Failed to load sources');
      }
    };
    loadSources();
  }, []);

  // Load documents
  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const params = sourceFilter === 'all' ? {} : { source_id: sourceFilter };
      const data = await listDocuments(params);
      setDocuments(data.documents);
      setPagination({
        page: data.page,
        total: data.total,
        pages: data.pages,
      });
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [sourceFilter]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // Delete document with confirmation
  const handleDeleteDocument = async (docId: string) => {
    setError(null);
    setSuccess(null);
    try {
      await deleteDocument(docId);
      setDeletingDocId(null);
      setSuccess('Document deleted successfully');
      await loadDocuments();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to delete document:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  // Toggle document details
  const toggleDocDetails = (docId: string) => {
    setExpandedDocId(expandedDocId === docId ? null : docId);
  };

  // Get document type badge style
  const getTypeStyle = (type?: string) => {
    if (!type) return styles.typeDefault;

    switch (type.toLowerCase()) {
      case 'pdf':
        return styles.typePdf;
      case 'markdown':
      case 'md':
        return styles.typeMarkdown;
      case 'html':
        return styles.typeHtml;
      case 'docx':
        return styles.typeDocx;
      case 'text':
      case 'txt':
        return styles.typeText;
      default:
        return styles.typeDefault;
    }
  };

  // Format date
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  };

  // Get source title by ID
  const getSourceTitle = (sourceId?: string) => {
    if (!sourceId) return 'Unknown Source';
    const source = sources.find((s) => s.id === sourceId);
    if (!source) return `Source ${sourceId.substring(0, 8)}...`;
    return source.title || source.url || `${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`;
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Documents Management</h2>

      {/* Error Display */}
      {error && (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
          <button onClick={() => setError(null)} style={styles.dismissButton}>
            Dismiss
          </button>
        </div>
      )}

      {/* Success Display */}
      {success && (
        <div style={styles.successContainer}>
          <p style={styles.successText}>{success}</p>
          <button onClick={() => setSuccess(null)} style={styles.dismissButton}>
            Dismiss
          </button>
        </div>
      )}

      {/* Documents List */}
      <div style={styles.listSection}>
        <div style={styles.listHeader}>
          <h3 style={styles.subheading}>
            Documents ({pagination.total} total)
          </h3>
          <div style={styles.controls}>
            <label style={styles.filterLabel}>
              Filter by Source:
              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value as SourceFilter)}
                style={styles.select}
              >
                <option value="all">All Sources</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.title || source.url || `${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`}
                  </option>
                ))}
              </select>
            </label>
            <button onClick={loadDocuments} style={styles.refreshButton}>
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div style={styles.loadingContainer}>
            <p style={styles.loadingText}>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>No documents found</p>
            <p style={styles.emptyHint}>
              {sourceFilter === 'all'
                ? 'Upload your first document to get started'
                : 'No documents found for this source. Try selecting a different source.'}
            </p>
          </div>
        ) : (
          <div style={styles.documentsContainer}>
            {/* Table Header */}
            <div style={styles.tableHeader}>
              <div style={styles.colTitle}>Title</div>
              <div style={styles.colType}>Type</div>
              <div style={styles.colChunks}>Chunks</div>
              <div style={styles.colSource}>Source</div>
              <div style={styles.colCreated}>Created</div>
              <div style={styles.colActions}>Actions</div>
            </div>

            {/* Document Rows */}
            {documents.map((doc) => (
              <div key={doc.id} style={styles.documentCard}>
                {/* Document Row */}
                <div style={styles.documentRow}>
                  <div style={styles.colTitle}>
                    <button
                      onClick={() => toggleDocDetails(doc.id)}
                      style={styles.titleButton}
                    >
                      {doc.title || 'Untitled Document'}
                    </button>
                  </div>
                  <div style={styles.colType}>
                    <span style={{ ...styles.typeBadge, ...getTypeStyle(doc.document_type) }}>
                      {doc.document_type || 'unknown'}
                    </span>
                  </div>
                  <div style={styles.colChunks}>
                    <span style={styles.chunkCount}>
                      {doc.chunk_count !== undefined ? doc.chunk_count : '-'}
                    </span>
                  </div>
                  <div style={styles.colSource}>
                    <span style={styles.sourceText}>
                      {getSourceTitle(doc.source_id)}
                    </span>
                  </div>
                  <div style={styles.colCreated}>
                    <span style={styles.dateText}>
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div style={styles.colActions}>
                    <button
                      onClick={() => setDeletingDocId(doc.id)}
                      style={styles.deleteButton}
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => toggleDocDetails(doc.id)}
                      style={styles.expandButton}
                    >
                      {expandedDocId === doc.id ? '▲' : '▼'}
                    </button>
                  </div>
                </div>

                {/* Expanded Document Details */}
                {expandedDocId === doc.id && (
                  <div style={styles.documentDetails}>
                    <div style={styles.detailsGrid}>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Document ID:</span>
                        <span style={styles.detailValue}>{doc.id}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Source ID:</span>
                        <span style={styles.detailValue}>{doc.source_id || 'N/A'}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Document Type:</span>
                        <span style={styles.detailValue}>{doc.document_type || 'N/A'}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Chunk Count:</span>
                        <span style={styles.detailValue}>
                          {doc.chunk_count !== undefined ? doc.chunk_count : 'N/A'}
                        </span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Created:</span>
                        <span style={styles.detailValue}>{formatDate(doc.created_at)}</span>
                      </div>
                      {doc.url && (
                        <div style={styles.detailItem}>
                          <span style={styles.detailLabel}>URL:</span>
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={styles.detailLink}
                          >
                            {doc.url}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination Info */}
        {!loading && documents.length > 0 && (
          <div style={styles.paginationInfo}>
            <p style={styles.paginationText}>
              Page {pagination.page} of {pagination.pages} ({pagination.total} documents total)
            </p>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deletingDocId && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h3 style={styles.modalTitle}>Confirm Delete</h3>
            <p style={styles.modalText}>
              Are you sure you want to delete this document? This will also delete all
              associated chunks and cannot be undone.
            </p>
            <div style={styles.modalActions}>
              <button
                onClick={() => handleDeleteDocument(deletingDocId)}
                style={styles.confirmDeleteButton}
              >
                Delete Document
              </button>
              <button
                onClick={() => setDeletingDocId(null)}
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
    maxWidth: '1400px',
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
    color: '#555',
  },
  errorContainer: {
    padding: '16px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    marginBottom: '16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: {
    color: '#721c24',
    margin: 0,
    flex: 1,
  },
  successContainer: {
    padding: '16px',
    backgroundColor: '#d4edda',
    border: '1px solid #c3e6cb',
    borderRadius: '4px',
    marginBottom: '16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  successText: {
    color: '#155724',
    margin: 0,
    flex: 1,
  },
  dismissButton: {
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#333',
    backgroundColor: 'transparent',
    border: '1px solid currentColor',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  listSection: {
    marginTop: '32px',
  },
  listHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    flexWrap: 'wrap' as const,
    gap: '16px',
  },
  controls: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  filterLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#555',
    fontWeight: '500',
  },
  select: {
    padding: '8px 12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
    backgroundColor: '#fff',
    cursor: 'pointer',
  },
  refreshButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
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
  documentsContainer: {
    backgroundColor: '#fff',
    border: '1px solid #ddd',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  tableHeader: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 0.8fr 1.5fr 1fr 1.2fr',
    gap: '16px',
    padding: '12px 16px',
    backgroundColor: '#f8f9fa',
    borderBottom: '2px solid #ddd',
    fontWeight: '600',
    fontSize: '14px',
    color: '#555',
  },
  documentCard: {
    borderBottom: '1px solid #e9ecef',
    transition: 'background-color 0.2s ease',
  },
  documentRow: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 0.8fr 1.5fr 1fr 1.2fr',
    gap: '16px',
    padding: '16px',
    alignItems: 'center',
  },
  colTitle: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  colType: {},
  colChunks: {
    textAlign: 'center' as const,
  },
  colSource: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  colCreated: {},
  colActions: {
    display: 'flex',
    gap: '8px',
    justifyContent: 'flex-end',
  },
  titleButton: {
    padding: 0,
    fontSize: '14px',
    fontWeight: '500',
    color: '#007bff',
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    textAlign: 'left' as const,
    textDecoration: 'underline',
  },
  typeBadge: {
    padding: '4px 8px',
    fontSize: '11px',
    fontWeight: '600',
    borderRadius: '4px',
    textTransform: 'uppercase' as const,
    display: 'inline-block',
  },
  typePdf: {
    backgroundColor: '#ffeaea',
    color: '#c92a2a',
  },
  typeMarkdown: {
    backgroundColor: '#e3f2fd',
    color: '#1565c0',
  },
  typeHtml: {
    backgroundColor: '#fff3e0',
    color: '#e65100',
  },
  typeDocx: {
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
  },
  typeText: {
    backgroundColor: '#f3e5f5',
    color: '#6a1b9a',
  },
  typeDefault: {
    backgroundColor: '#f5f5f5',
    color: '#616161',
  },
  chunkCount: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
  },
  sourceText: {
    fontSize: '13px',
    color: '#666',
  },
  dateText: {
    fontSize: '13px',
    color: '#666',
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
  expandButton: {
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#333',
    backgroundColor: '#f8f9fa',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  documentDetails: {
    padding: '16px',
    backgroundColor: '#f8f9fa',
    borderTop: '1px solid #ddd',
  },
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '12px',
  },
  detailItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  detailLabel: {
    fontSize: '12px',
    fontWeight: '500',
    color: '#666',
    textTransform: 'uppercase' as const,
  },
  detailValue: {
    fontSize: '14px',
    color: '#333',
    wordBreak: 'break-word' as const,
  },
  detailLink: {
    fontSize: '14px',
    color: '#007bff',
    textDecoration: 'underline',
  },
  paginationInfo: {
    marginTop: '16px',
    textAlign: 'center' as const,
  },
  paginationText: {
    fontSize: '14px',
    color: '#666',
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
    maxWidth: '500px',
    width: '90%',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
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
    lineHeight: '1.5',
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
};
