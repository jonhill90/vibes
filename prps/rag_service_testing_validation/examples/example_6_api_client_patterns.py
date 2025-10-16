# Source: infra/rag-service/frontend/src/api/client.ts
# Lines: 1-284 (key patterns extracted)
# Pattern: TypeScript API client with typed requests/responses
# Extracted: 2025-10-16
# Relevance: 8/10

"""API Client Pattern: Typed HTTP requests with error handling.

This example demonstrates:
1. Axios client configuration with baseURL and timeout
2. Response interceptor for global error handling
3. Typed request/response interfaces
4. FormData handling for file uploads
5. Query parameter handling
6. Error extraction and user-friendly messages

Key patterns to understand for testing:
- How API calls are structured
- What error responses look like
- How FormData is used for file uploads
- Request/response type definitions

This helps write integration tests that match real API usage.
"""

# TypeScript API Client Patterns (documented for Python developers)

# Client Configuration
"""
import axios, { AxiosInstance } from 'axios';

const apiClient: AxiosInstance = axios.create({
    baseURL: 'http://localhost:8003',  // Backend URL
    timeout: 30000,  // 30 second timeout
    headers: {
        'Content-Type': 'application/json',
    },
});
"""

# Global Error Interceptor
"""
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
"""

# File Upload Pattern (multipart/form-data)
"""
export async function uploadDocument(data: DocumentUploadRequest): Promise<DocumentResponse> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    formData.append('source_id', data.source_id);

    const response = await apiClient.post<DocumentResponse>('/api/documents', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}
"""

# List with Query Parameters
"""
export async function listDocuments(params?: {
    page?: number;
    per_page?: number;
    source_id?: string;
}): Promise<{ documents: DocumentResponse[]; total: number }> {
    const response = await apiClient.get<{
        documents: DocumentResponse[];
        total: number;
    }>('/api/documents', { params });

    return response.data;
}
"""

# POST with JSON Body
"""
export async function searchDocuments(request: SearchRequest): Promise<SearchResponse> {
    const response = await apiClient.post<SearchResponse>('/api/search', request);
    return response.data;
}
"""

# DELETE with Path Parameter
"""
export async function deleteDocument(documentId: string): Promise<MessageResponse> {
    const response = await apiClient.delete<MessageResponse>(`/api/documents/${documentId}`);
    return response.data;
}
"""

# Type Definitions (Python equivalent shown)
"""
# TypeScript:
interface DocumentUploadRequest {
    title: string;
    source_id: string;
    file: File;
}

interface DocumentResponse {
    id: string;
    title: string;
    source_id?: string;
    created_at: string;
    chunk_count?: number;
}

interface ErrorResponse {
    error: string;
    suggestion?: string;
    details?: Record<string, unknown>;
}

# Python equivalent (for backend tests):
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentUploadRequest(BaseModel):
    title: str
    source_id: str
    # file is handled via UploadFile in FastAPI

class DocumentResponse(BaseModel):
    id: str
    title: str
    source_id: Optional[str] = None
    created_at: datetime
    chunk_count: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    suggestion: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
"""

# Testing API Calls (Python pytest example)
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_document(async_client: AsyncClient):
    # Prepare test file
    files = {
        'file': ('test.pdf', b'PDF content', 'application/pdf')
    }
    data = {
        'title': 'Test Document',
        'source_id': '123e4567-e89b-12d3-a456-426614174000'
    }

    # Make request
    response = await async_client.post(
        '/api/documents',
        files=files,
        data=data
    )

    # Assert response
    assert response.status_code == 201
    json_data = response.json()
    assert json_data['title'] == 'Test Document'
    assert 'id' in json_data
    assert 'chunk_count' in json_data


@pytest.mark.asyncio
async def test_list_documents_with_filter(async_client: AsyncClient):
    source_id = '123e4567-e89b-12d3-a456-426614174000'

    response = await async_client.get(
        '/api/documents',
        params={'source_id': source_id, 'page': 1, 'per_page': 10}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert 'documents' in json_data
    assert 'total' in json_data
    assert isinstance(json_data['documents'], list)


@pytest.mark.asyncio
async def test_search_documents(async_client: AsyncClient):
    search_request = {
        'query': 'machine learning',
        'limit': 10,
        'source_id': '123e4567-e89b-12d3-a456-426614174000',
        'search_type': 'vector'
    }

    response = await async_client.post(
        '/api/search',
        json=search_request
    )

    assert response.status_code == 200
    json_data = response.json()
    assert 'results' in json_data
    assert 'count' in json_data
    assert isinstance(json_data['results'], list)


@pytest.mark.asyncio
async def test_delete_document(async_client: AsyncClient):
    document_id = '123e4567-e89b-12d3-a456-426614174000'

    response = await async_client.delete(f'/api/documents/{document_id}')

    assert response.status_code == 200
    json_data = response.json()
    assert json_data['success'] is True
    assert 'message' in json_data


@pytest.mark.asyncio
async def test_upload_document_invalid_file_type(async_client: AsyncClient):
    files = {
        'file': ('test.exe', b'executable content', 'application/x-msdownload')
    }
    data = {
        'title': 'Test Document',
        'source_id': '123e4567-e89b-12d3-a456-426614174000'
    }

    response = await async_client.post(
        '/api/documents',
        files=files,
        data=data
    )

    assert response.status_code == 400
    json_data = response.json()
    assert 'error' in json_data['detail']
    assert 'invalid file type' in json_data['detail']['error'].lower()
"""

# Key Takeaways:
# 1. Match API client patterns in integration tests
# 2. Use FormData for file uploads (multipart/form-data)
# 3. Test error responses (400, 404, 413, 422, 500)
# 4. Validate response structure matches type definitions
# 5. Test query parameters and filters
# 6. Test cascading deletes (document -> chunks)
# 7. Verify error messages are user-friendly
