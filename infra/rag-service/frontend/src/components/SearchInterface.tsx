import { useState, useEffect, useCallback } from 'react';
import { searchDocuments, listSources, SearchResult, SourceResponse } from '../api/client';

/**
 * SearchInterface Component
 *
 * Provides semantic and hybrid search functionality.
 * Features:
 * - Search input with 500ms debounce to reduce API calls
 * - Result cards displaying title, snippet, and relevance score
 * - Filters: source selection, search type (vector/hybrid)
 * - Pagination controls for navigating results
 * - Loading states and empty states
 * - Error handling with user-friendly messages
 */

interface SearchFilters {
  query: string;
  source_id?: string;
  search_type: 'vector' | 'hybrid';
  limit: number;
}

interface SearchState {
  results: SearchResult[];
  count: number;
  took_ms?: number;
  loading: boolean;
  error?: string;
}

export default function SearchInterface() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    search_type: 'vector',
    limit: 10,
  });
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [searchState, setSearchState] = useState<SearchState>({
    results: [],
    count: 0,
    loading: false,
  });
  const [sources, setSources] = useState<SourceResponse[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  // Load sources on mount
  useEffect(() => {
    const loadSources = async () => {
      try {
        const data = await listSources();
        setSources(data);
      } catch (error) {
        console.error('Failed to load sources:', error);
      }
    };
    loadSources();
  }, []);

  // Debounce search query (500ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(filters.query);
    }, 500);

    return () => clearTimeout(timer);
  }, [filters.query]);

  // Execute search when debounced query changes
  const executeSearch = useCallback(async () => {
    if (!debouncedQuery.trim()) {
      setSearchState({ results: [], count: 0, loading: false });
      return;
    }

    setSearchState((prev) => ({ ...prev, loading: true, error: undefined }));

    try {
      const response = await searchDocuments({
        query: debouncedQuery,
        limit: filters.limit,
        source_id: filters.source_id,
        search_type: filters.search_type,
      });

      setSearchState({
        results: response.results,
        count: response.count,
        took_ms: response.took_ms,
        loading: false,
      });
      setCurrentPage(1);
    } catch (error) {
      console.error('Search error:', error);
      setSearchState({
        results: [],
        count: 0,
        loading: false,
        error: error instanceof Error ? error.message : 'Search failed',
      });
    }
  }, [debouncedQuery, filters.limit, filters.source_id, filters.search_type]);

  useEffect(() => {
    executeSearch();
  }, [executeSearch]);

  // Pagination
  const resultsPerPage = filters.limit;
  const totalPages = Math.ceil(searchState.count / resultsPerPage);
  const startIdx = (currentPage - 1) * resultsPerPage;
  const endIdx = startIdx + resultsPerPage;
  const currentResults = searchState.results.slice(startIdx, endIdx);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Search Documents</h2>

      {/* Search Controls */}
      <div style={styles.searchControls}>
        {/* Search Input */}
        <input
          type="text"
          value={filters.query}
          onChange={(e) => setFilters({ ...filters, query: e.target.value })}
          placeholder="Enter search query..."
          style={styles.searchInput}
          disabled={searchState.loading}
        />

        {/* Filters Row */}
        <div style={styles.filtersRow}>
          {/* Source Filter */}
          <div style={styles.filterGroup}>
            <label htmlFor="source-filter" style={styles.filterLabel}>
              Source:
            </label>
            <select
              id="source-filter"
              value={filters.source_id || ''}
              onChange={(e) =>
                setFilters({ ...filters, source_id: e.target.value || undefined })
              }
              style={styles.select}
              disabled={searchState.loading}
            >
              <option value="">All Sources</option>
              {sources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.title || source.url || `Untitled ${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`}
                </option>
              ))}
            </select>
          </div>

          {/* Search Type Filter */}
          <div style={styles.filterGroup}>
            <label htmlFor="search-type" style={styles.filterLabel}>
              Search Type:
            </label>
            <select
              id="search-type"
              value={filters.search_type}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  search_type: e.target.value as 'vector' | 'hybrid',
                })
              }
              style={styles.select}
              disabled={searchState.loading}
            >
              <option value="vector">Vector Only</option>
              <option value="hybrid">Hybrid (Vector + Text)</option>
            </select>
          </div>

          {/* Results Limit */}
          <div style={styles.filterGroup}>
            <label htmlFor="limit" style={styles.filterLabel}>
              Results:
            </label>
            <select
              id="limit"
              value={filters.limit}
              onChange={(e) =>
                setFilters({ ...filters, limit: parseInt(e.target.value) })
              }
              style={styles.select}
              disabled={searchState.loading}
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {searchState.loading && (
        <div style={styles.loadingContainer}>
          <p style={styles.loadingText}>Searching...</p>
        </div>
      )}

      {/* Error State */}
      {searchState.error && (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{searchState.error}</p>
        </div>
      )}

      {/* Results Info */}
      {!searchState.loading && debouncedQuery && !searchState.error && (
        <div style={styles.resultsInfo}>
          Found {searchState.count} results in {searchState.took_ms || 0}ms
        </div>
      )}

      {/* Empty State */}
      {!searchState.loading && debouncedQuery && searchState.results.length === 0 && !searchState.error && (
        <div style={styles.emptyState}>
          <p style={styles.emptyText}>No results found for "{debouncedQuery}"</p>
          <p style={styles.emptyHint}>Try different keywords or check your filters</p>
        </div>
      )}

      {/* Results */}
      {!searchState.loading && currentResults.length > 0 && (
        <div style={styles.resultsContainer}>
          {currentResults.map((result) => (
            <div key={result.chunk_id} style={styles.resultCard}>
              <div style={styles.resultHeader}>
                <h3 style={styles.resultTitle}>{result.title}</h3>
                <span style={styles.resultScore}>
                  Score: {(result.score * 100).toFixed(1)}%
                </span>
              </div>
              <p style={styles.resultSnippet}>
                {result.text.substring(0, 300)}
                {result.text.length > 300 ? '...' : ''}
              </p>
              <div style={styles.resultMeta}>
                <span style={styles.metaItem}>Doc ID: {result.document_id}</span>
                {result.source_id && (
                  <span style={styles.metaItem}>Source: {result.source_id}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!searchState.loading && searchState.results.length > 0 && totalPages > 1 && (
        <div style={styles.pagination}>
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            style={{
              ...styles.paginationButton,
              ...(currentPage === 1 ? styles.paginationButtonDisabled : {}),
            }}
          >
            Previous
          </button>
          <span style={styles.paginationInfo}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            style={{
              ...styles.paginationButton,
              ...(currentPage === totalPages ? styles.paginationButtonDisabled : {}),
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

// Inline styles
const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '20px',
  },
  heading: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333',
  },
  searchControls: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
    marginBottom: '24px',
  },
  searchInput: {
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
  },
  filtersRow: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap' as const,
  },
  filterGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  filterLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#555',
  },
  select: {
    padding: '8px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
    backgroundColor: '#fff',
  },
  loadingContainer: {
    textAlign: 'center' as const,
    padding: '40px',
  },
  loadingText: {
    fontSize: '16px',
    color: '#666',
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
  resultsInfo: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '16px',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '40px',
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
  resultsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  resultCard: {
    padding: '16px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#fff',
    transition: 'box-shadow 0.2s ease',
    cursor: 'pointer',
  },
  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  resultTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#333',
    margin: 0,
  },
  resultScore: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#007bff',
    padding: '4px 8px',
    backgroundColor: '#e7f3ff',
    borderRadius: '4px',
  },
  resultSnippet: {
    fontSize: '14px',
    color: '#555',
    lineHeight: '1.6',
    marginBottom: '8px',
  },
  resultMeta: {
    display: 'flex',
    gap: '16px',
    fontSize: '12px',
    color: '#999',
  },
  metaItem: {
    display: 'inline-block',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '16px',
    marginTop: '24px',
  },
  paginationButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  },
  paginationButtonDisabled: {
    backgroundColor: '#6c757d',
    cursor: 'not-allowed',
  },
  paginationInfo: {
    fontSize: '14px',
    color: '#666',
  },
};
