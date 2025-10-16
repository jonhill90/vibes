import axios, { AxiosInstance, AxiosError } from 'axios';

/**
 * API Client for RAG Service Backend
 *
 * Provides typed functions for interacting with the REST API endpoints.
 * Configured with baseURL from VITE_API_URL environment variable.
 */

// Type definitions
export interface DocumentUploadRequest {
  title: string;
  source_id?: string;
  file: File;
}

export interface DocumentResponse {
  id: string;
  title: string;
  source_id?: string;
  created_at: string;
  chunk_count?: number;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  source_id?: string;
  search_type?: 'vector' | 'hybrid';
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  title: string;
  text: string;
  score: number;
  source_id?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  count: number;
  search_type: string;
  took_ms?: number;
}

export interface SourceRequest {
  title?: string;
  source_type: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface SourceResponse {
  id: string;
  title?: string;
  source_type: string;
  url?: string;
  status: string;
  metadata?: Record<string, unknown>;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ErrorResponse {
  error: string;
  suggestion?: string;
  details?: Record<string, unknown>;
}

export interface CrawlStartRequest {
  source_id: string;
  url: string;
  max_pages?: number;
  max_depth?: number;
}

export interface CrawlJobResponse {
  id: string;
  source_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  pages_crawled: number;
  pages_total?: number;
  max_pages: number;
  max_depth: number;
  current_depth: number;
  error_message?: string;
  error_count: number;
  metadata: Record<string, unknown>;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CrawlJobListResponse {
  crawl_jobs: CrawlJobResponse[];
  total_count: number;
  limit: number;
  offset: number;
}

export interface MessageResponse {
  success: boolean;
  message: string;
}

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    // Extract error message from response or use generic message
    const message = error.response?.data?.error || error.message || 'An unexpected error occurred';
    const suggestion = error.response?.data?.suggestion;

    console.error('API Error:', {
      message,
      suggestion,
      status: error.response?.status,
      url: error.config?.url,
    });

    // Re-throw with enhanced error information
    throw new Error(`${message}${suggestion ? ` (${suggestion})` : ''}`);
  }
);

/**
 * Upload a document to the RAG service
 */
export async function uploadDocument(data: DocumentUploadRequest): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('title', data.title);
  if (data.source_id) {
    formData.append('source_id', data.source_id);
  }

  const response = await apiClient.post<DocumentResponse>('/api/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

/**
 * List documents with optional pagination
 */
export async function listDocuments(params?: {
  page?: number;
  per_page?: number;
  source_id?: string;
}): Promise<{ documents: DocumentResponse[]; total: number; page: number; pages: number }> {
  const response = await apiClient.get<{
    documents: DocumentResponse[];
    total: number;
    page: number;
    pages: number;
  }>('/api/documents', { params });

  return response.data;
}

/**
 * Search documents using vector or hybrid search
 */
export async function searchDocuments(request: SearchRequest): Promise<SearchResponse> {
  const response = await apiClient.post<SearchResponse>('/api/search', request);
  return response.data;
}

/**
 * List all sources
 */
export async function listSources(): Promise<SourceResponse[]> {
  const response = await apiClient.get<{ sources: SourceResponse[] }>('/api/sources');
  return response.data.sources;
}

/**
 * Create a new source
 */
export async function createSource(data: SourceRequest): Promise<SourceResponse> {
  const response = await apiClient.post<SourceResponse>('/api/sources', data);
  return response.data;
}

/**
 * Update a source
 */
export async function updateSource(id: string, data: Partial<SourceRequest>): Promise<SourceResponse> {
  const response = await apiClient.put<SourceResponse>(`/api/sources/${id}`, data);
  return response.data;
}

/**
 * Delete a source
 */
export async function deleteSource(id: string): Promise<void> {
  await apiClient.delete(`/api/sources/${id}`);
}

/**
 * Start a new web crawl job
 */
export async function startCrawl(data: CrawlStartRequest): Promise<CrawlJobResponse> {
  const response = await apiClient.post<CrawlJobResponse>('/api/crawls', data);
  return response.data;
}

/**
 * List crawl jobs with optional filters and pagination
 */
export async function listCrawlJobs(params?: {
  source_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<CrawlJobListResponse> {
  const response = await apiClient.get<CrawlJobListResponse>('/api/crawls', { params });
  return response.data;
}

/**
 * Get a single crawl job by ID
 */
export async function getCrawlJob(jobId: string): Promise<CrawlJobResponse> {
  const response = await apiClient.get<CrawlJobResponse>(`/api/crawls/${jobId}`);
  return response.data;
}

/**
 * Abort a running crawl job
 */
export async function abortCrawlJob(jobId: string): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>(`/api/crawls/${jobId}/abort`);
  return response.data;
}

export default apiClient;
