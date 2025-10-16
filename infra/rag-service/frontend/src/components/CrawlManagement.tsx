import { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import {
  listCrawlJobs,
  startCrawl,
  abortCrawlJob,
  listSources,
  CrawlJobResponse,
  CrawlStartRequest,
  SourceResponse,
} from '../api/client';

/**
 * CrawlManagement Component
 *
 * Provides interface for managing web crawl jobs.
 * Features:
 * - Start new crawl jobs with URL, source, max pages, and depth configuration
 * - List all crawl jobs with status filters and pagination
 * - View job details (progress, errors, metadata)
 * - Abort running jobs
 * - Auto-refresh job list every 5 seconds when jobs are running
 * - Color-coded status badges for visual clarity
 */

interface CrawlFormData {
  source_id: string;
  url: string;
  max_pages: number;
  max_depth: number;
}

type StatusFilter = 'all' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export default function CrawlManagement() {
  const [crawlJobs, setCrawlJobs] = useState<CrawlJobResponse[]>([]);
  const [sources, setSources] = useState<SourceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<CrawlFormData>({
    defaultValues: {
      max_pages: 100,
      max_depth: 3,
    },
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

  // Load crawl jobs
  const loadCrawlJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = statusFilter === 'all' ? {} : { status: statusFilter };
      const data = await listCrawlJobs(params);
      setCrawlJobs(data.crawl_jobs);
    } catch (err) {
      console.error('Failed to load crawl jobs:', err);
      setError(err instanceof Error ? err.message : 'Failed to load crawl jobs');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadCrawlJobs();
  }, [loadCrawlJobs]);

  // Auto-refresh when jobs are running
  useEffect(() => {
    if (!autoRefresh) return;

    const hasActiveJobs = crawlJobs.some(
      (job) => job.status === 'pending' || job.status === 'running'
    );

    if (!hasActiveJobs) return;

    const interval = setInterval(() => {
      loadCrawlJobs();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [crawlJobs, autoRefresh, loadCrawlJobs]);

  // Start new crawl
  const onStartCrawl = async (data: CrawlFormData) => {
    setError(null);
    try {
      const request: CrawlStartRequest = {
        source_id: data.source_id,
        url: data.url,
        max_pages: data.max_pages,
        max_depth: data.max_depth,
      };

      await startCrawl(request);
      reset();
      await loadCrawlJobs();
    } catch (err) {
      console.error('Failed to start crawl:', err);
      setError(err instanceof Error ? err.message : 'Failed to start crawl');
    }
  };

  // Abort crawl job
  const handleAbortJob = async (jobId: string) => {
    setError(null);
    try {
      await abortCrawlJob(jobId);
      await loadCrawlJobs();
    } catch (err) {
      console.error('Failed to abort job:', err);
      setError(err instanceof Error ? err.message : 'Failed to abort job');
    }
  };

  // Toggle job details
  const toggleJobDetails = (jobId: string) => {
    setExpandedJobId(expandedJobId === jobId ? null : jobId);
  };

  // Get status badge style
  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'completed':
        return styles.statusCompleted;
      case 'running':
        return styles.statusRunning;
      case 'pending':
        return styles.statusPending;
      case 'failed':
        return styles.statusFailed;
      case 'cancelled':
        return styles.statusCancelled;
      default:
        return styles.statusDefault;
    }
  };

  // Format date
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  };

  // Calculate progress percentage
  const getProgress = (job: CrawlJobResponse) => {
    if (job.pages_total) {
      return Math.round((job.pages_crawled / job.pages_total) * 100);
    }
    return Math.round((job.pages_crawled / job.max_pages) * 100);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Crawl Management</h2>

      {/* Error Display */}
      {error && (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
        </div>
      )}

      {/* Start Crawl Form */}
      <div style={styles.createSection}>
        <h3 style={styles.subheading}>Start New Crawl</h3>
        <form onSubmit={handleSubmit(onStartCrawl)} style={styles.form}>
          <div style={styles.formRow}>
            <div style={styles.formGroup}>
              <label htmlFor="source_id" style={styles.label}>
                Source *
              </label>
              <select
                id="source_id"
                {...register('source_id', { required: 'Source is required' })}
                style={styles.select}
              >
                <option value="">Select source...</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.title || source.url || `Untitled ${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`}
                  </option>
                ))}
              </select>
              {errors.source_id && <span style={styles.error}>{errors.source_id.message}</span>}
            </div>

            <div style={styles.formGroup}>
              <label htmlFor="url" style={styles.label}>
                Starting URL *
              </label>
              <input
                id="url"
                type="url"
                {...register('url', { required: 'URL is required' })}
                style={styles.input}
                placeholder="https://example.com"
              />
              {errors.url && <span style={styles.error}>{errors.url.message}</span>}
            </div>

            <div style={styles.formGroupSmall}>
              <label htmlFor="max_pages" style={styles.label}>
                Max Pages
              </label>
              <input
                id="max_pages"
                type="number"
                {...register('max_pages', { required: true, min: 1, max: 1000 })}
                style={styles.input}
                placeholder="100"
              />
              {errors.max_pages && <span style={styles.error}>1-1000</span>}
            </div>

            <div style={styles.formGroupSmall}>
              <label htmlFor="max_depth" style={styles.label}>
                Max Depth
              </label>
              <input
                id="max_depth"
                type="number"
                {...register('max_depth', { required: true, min: 0, max: 10 })}
                style={styles.input}
                placeholder="3"
              />
              {errors.max_depth && <span style={styles.error}>0-10</span>}
            </div>

            <button type="submit" style={styles.startButton}>
              Start Crawl
            </button>
          </div>
        </form>
      </div>

      {/* Crawl Jobs List */}
      <div style={styles.listSection}>
        <div style={styles.listHeader}>
          <h3 style={styles.subheading}>Crawl Jobs</h3>
          <div style={styles.controls}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                style={styles.checkbox}
              />
              Auto-refresh
            </label>
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
              <option value="cancelled">Cancelled</option>
            </select>
            <button onClick={loadCrawlJobs} style={styles.refreshButton}>
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div style={styles.loadingContainer}>
            <p style={styles.loadingText}>Loading crawl jobs...</p>
          </div>
        ) : crawlJobs.length === 0 ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>No crawl jobs found</p>
            <p style={styles.emptyHint}>Start your first crawl using the form above</p>
          </div>
        ) : (
          <div style={styles.jobsContainer}>
            {crawlJobs.map((job) => (
              <div key={job.id} style={styles.jobCard}>
                {/* Job Header */}
                <div style={styles.jobHeader} onClick={() => toggleJobDetails(job.id)}>
                  <div style={styles.jobInfo}>
                    <div style={styles.jobTitle}>
                      <span style={styles.jobUrl}>
                        {(job.metadata.url as string) || 'Unknown URL'}
                      </span>
                      <span style={{ ...styles.statusBadge, ...getStatusStyle(job.status) }}>
                        {job.status}
                      </span>
                    </div>
                    <div style={styles.jobMeta}>
                      <span>ID: {job.id.substring(0, 8)}...</span>
                      <span>Source: {job.source_id.substring(0, 8)}...</span>
                      <span>
                        Pages: {job.pages_crawled}/{job.max_pages} ({getProgress(job)}%)
                      </span>
                      {job.error_count > 0 && (
                        <span style={styles.errorCount}>Errors: {job.error_count}</span>
                      )}
                    </div>
                  </div>
                  <div style={styles.jobActions}>
                    {(job.status === 'pending' || job.status === 'running') && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAbortJob(job.id);
                        }}
                        style={styles.abortButton}
                      >
                        Abort
                      </button>
                    )}
                    <button style={styles.expandButton}>
                      {expandedJobId === job.id ? '▲' : '▼'}
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                {(job.status === 'running' || job.status === 'pending') && (
                  <div style={styles.progressContainer}>
                    <div
                      style={{
                        ...styles.progressBar,
                        width: `${getProgress(job)}%`,
                      }}
                    />
                  </div>
                )}

                {/* Expanded Job Details */}
                {expandedJobId === job.id && (
                  <div style={styles.jobDetails}>
                    <div style={styles.detailsGrid}>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Created:</span>
                        <span>{formatDate(job.created_at)}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Started:</span>
                        <span>{formatDate(job.started_at)}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Completed:</span>
                        <span>{formatDate(job.completed_at)}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Max Depth:</span>
                        <span>{job.max_depth}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Current Depth:</span>
                        <span>{job.current_depth}</span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Total Pages:</span>
                        <span>{job.pages_total || 'Unknown'}</span>
                      </div>
                    </div>

                    {job.error_message && (
                      <div style={styles.errorDetail}>
                        <strong>Error:</strong> {job.error_message}
                      </div>
                    )}

                    {Object.keys(job.metadata).length > 0 && (
                      <div style={styles.metadataDetail}>
                        <strong>Metadata:</strong>
                        <pre style={styles.metadataJson}>
                          {JSON.stringify(job.metadata, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Inline styles
const styles = {
  container: {
    maxWidth: '1200px',
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
  formGroupSmall: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
    minWidth: '100px',
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
  startButton: {
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
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '14px',
    color: '#555',
  },
  checkbox: {
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
  jobsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  jobCard: {
    backgroundColor: '#fff',
    border: '1px solid #ddd',
    borderRadius: '8px',
    overflow: 'hidden',
    transition: 'box-shadow 0.2s ease',
  },
  jobHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  },
  jobInfo: {
    flex: 1,
  },
  jobTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px',
  },
  jobUrl: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#333',
  },
  statusBadge: {
    padding: '4px 8px',
    fontSize: '12px',
    fontWeight: '500',
    borderRadius: '4px',
    textTransform: 'uppercase' as const,
  },
  statusCompleted: {
    backgroundColor: '#d4edda',
    color: '#155724',
  },
  statusRunning: {
    backgroundColor: '#cce5ff',
    color: '#004085',
  },
  statusPending: {
    backgroundColor: '#fff3cd',
    color: '#856404',
  },
  statusFailed: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
  },
  statusCancelled: {
    backgroundColor: '#e2e3e5',
    color: '#383d41',
  },
  statusDefault: {
    backgroundColor: '#f8f9fa',
    color: '#6c757d',
  },
  jobMeta: {
    display: 'flex',
    gap: '16px',
    fontSize: '12px',
    color: '#666',
    flexWrap: 'wrap' as const,
  },
  errorCount: {
    color: '#dc3545',
    fontWeight: '500',
  },
  jobActions: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  abortButton: {
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
  progressContainer: {
    height: '4px',
    backgroundColor: '#e9ecef',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007bff',
    transition: 'width 0.3s ease',
  },
  jobDetails: {
    padding: '16px',
    backgroundColor: '#f8f9fa',
    borderTop: '1px solid #ddd',
  },
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px',
    marginBottom: '16px',
  },
  detailItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  } as React.CSSProperties,
  detailLabel: {
    fontSize: '12px',
    fontWeight: '500',
    color: '#666',
    textTransform: 'uppercase' as const,
  },
  errorDetail: {
    padding: '12px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    fontSize: '14px',
    color: '#721c24',
    marginTop: '12px',
  },
  metadataDetail: {
    marginTop: '12px',
    fontSize: '14px',
  },
  metadataJson: {
    padding: '12px',
    backgroundColor: '#fff',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '12px',
    overflow: 'auto',
    marginTop: '8px',
  },
};
