/**
 * API Client - Axios instance with interceptors
 *
 * PATTERN: Centralized axios configuration with error handling
 * - Uses VITE_API_URL environment variable
 * - Request interceptor for headers
 * - Response interceptor for error normalization
 */

import axios, { type AxiosError, type AxiosInstance } from "axios";

/**
 * API Error - Normalized error structure
 */
export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
  validation?: Record<string, string[]>;
}

/**
 * Create axios instance with base configuration
 *
 * NOTE: baseURL is empty to use relative paths (/api/...)
 * Vite dev server proxy handles forwarding /api requests to backend
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: "", // Use relative URLs, Vite proxy handles backend routing
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Request interceptor - Add headers and logging
 */
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here in the future
    // Example: config.headers.Authorization = `Bearer ${token}`;

    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }

    return config;
  },
  (error) => {
    console.error("[API] Request error:", error);
    return Promise.reject(error);
  },
);

/**
 * Response interceptor - Handle errors consistently
 *
 * GOTCHA FIX: Handle 422 validation errors from FastAPI
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API] Response ${response.status}:`, response.data);
    }

    return response;
  },
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: "An unexpected error occurred",
      status: error.response?.status,
    };

    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      // Handle 422 Validation Errors (FastAPI format)
      if (status === 422 && data && typeof data === "object") {
        const validationData = data as { detail?: Array<{ loc: string[]; msg: string }> };
        if (validationData.detail && Array.isArray(validationData.detail)) {
          // Convert FastAPI validation errors to our format
          const validation: Record<string, string[]> = {};
          validationData.detail.forEach((err) => {
            const field = err.loc[err.loc.length - 1];
            if (!validation[field]) {
              validation[field] = [];
            }
            validation[field].push(err.msg);
          });

          apiError.message = "Validation error";
          apiError.validation = validation;
          apiError.detail = validationData.detail.map((e) => e.msg).join(", ");
        }
      }
      // Handle generic errors with detail field
      else if (data && typeof data === "object") {
        const errorData = data as { detail?: string; message?: string };
        apiError.message = errorData.detail || errorData.message || `Error ${status}`;
        apiError.detail = errorData.detail;
      }
      // Handle string responses
      else if (typeof data === "string") {
        apiError.message = data;
      }
      // Status-specific messages
      else {
        apiError.message = getDefaultErrorMessage(status);
      }
    } else if (error.request) {
      // Request made but no response received
      apiError.message = "No response from server. Please check your connection.";
      apiError.status = 0;
    } else {
      // Error in request setup
      apiError.message = error.message || "Request failed";
    }

    // Log errors in development
    if (import.meta.env.DEV) {
      console.error("[API] Error:", apiError, error);
    }

    // Reject with normalized error
    return Promise.reject(apiError);
  },
);

/**
 * Get default error message for status code
 */
function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return "Bad request";
    case 401:
      return "Unauthorized";
    case 403:
      return "Forbidden";
    case 404:
      return "Not found";
    case 500:
      return "Internal server error";
    case 502:
      return "Bad gateway";
    case 503:
      return "Service unavailable";
    default:
      return `Error ${status}`;
  }
}

export default apiClient;
