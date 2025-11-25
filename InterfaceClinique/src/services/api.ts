import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import type {
  User,
  Document,
  SearchResponse,
  QAResponse,
  QARequest,
  DashboardStats,
  FilterOptions,
  AuditLog,
  SynthesisRequest,
  SynthesisResponse,
  PaginatedResponse,
  ApiError
} from '../types';

// API Base URL Configuration
// Development: Direct connection to backend http://localhost:8000/api/v1
// Production: Uses full URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

console.log('🔧 API Configuration:', {
  mode: import.meta.env.MODE,
  baseURL: API_BASE_URL,
  isDev: import.meta.env.DEV,
  fullURL: API_BASE_URL + '/documents/upload' // Show full upload URL
});

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token from secure memory storage
apiClient.interceptors.request.use(
  async (config) => {
    // Debug: Log the full request URL (only in development)
    if (import.meta.env.DEV) {
      console.log('Making request to:', (config.baseURL || '') + (config.url || ''));
    }
    
    // Import tokenStore dynamically to avoid circular dependency
    const { tokenStore } = await import('../hooks/useAuthToken');
    let token = tokenStore.getToken();
    
    // If no token in memory, try to get fresh token from Auth0
    if (!token) {
      console.warn('No token found in memory, attempting to refresh...');
      // Dispatch custom event to trigger token refresh
      window.dispatchEvent(new CustomEvent('auth0-token-refresh'));
      // Wait a bit for token to be refreshed
      await new Promise(resolve => setTimeout(resolve, 500));
      token = tokenStore.getToken();
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
      originalRequest._retry = true;

      console.warn('Auth error, attempting to refresh Auth0 token...');
      
      // Trigger Auth0 token refresh
      window.dispatchEvent(new CustomEvent('auth0-token-refresh'));
      
      // Wait for token to be refreshed
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Get token from secure memory storage
      const { tokenStore } = await import('../hooks/useAuthToken');
      const newToken = tokenStore.getToken();
      
      if (newToken) {
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } else {
        // No token available, clear memory and redirect to login
        tokenStore.clearToken();
        console.error('Failed to refresh token, redirecting to login');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Generic API methods with proper typing
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then((res) => res.data),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then((res) => res.data),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then((res) => res.data),

  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then((res) => res.data),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then((res) => res.data),
};

// Authentication API
export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post<{ access_token: string; token_type: string; expires_in: number }>('/auth/login', credentials),

  refresh: (refreshToken: string) =>
    api.post<{ access_token: string; token_type: string; expires_in: number }>('/auth/refresh', { refresh_token: refreshToken }),

  logout: () =>
    api.post('/auth/logout'),

  getProfile: () =>
    api.get<User>('/auth/profile'),
};

// Document API
export const documentsApi = {
  upload: (formData: FormData, onProgress?: (progress: number) => void) => {
    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };
    return apiClient.post<{ document_id: string; status: string; message: string }>('/documents/upload', formData, config);
  },

  list: (params?: FilterOptions & { limit?: number; offset?: number }) =>
    api.get<PaginatedResponse<Document>>('/documents', { params }),

  get: (documentId: string) =>
    api.get<Document>(`/documents/${documentId}`),

  delete: (documentId: string) =>
    api.delete(`/documents/${documentId}`),

  update: (documentId: string, data: Partial<Document>) =>
    api.put<Document>(`/documents/${documentId}`, data),
};

// Search API
export const searchApi = {
  search: (query: string, filters?: FilterOptions, limit?: number) =>
    api.post<SearchResponse>('/search', {
      query,
      filters,
      limit: limit || 20,
    }),
};

// Q&A API
export const qaApi = {
  ask: (request: QARequest) => {
    const params = new URLSearchParams();
    params.append('question', request.question);
    if (request.session_id) {
      params.append('session_id', request.session_id);
    }
    if (request.context_documents && request.context_documents.length > 0) {
      request.context_documents.forEach(docId => {
        params.append('context_documents', docId);
      });
    }
    return api.post<QAResponse>(`/qa/ask?${params.toString()}`);
  },

  getSessions: () =>
    api.get<Array<{ id: string; title: string; created_at: string; last_message_at: string }>>('/qa/sessions'),

  getSession: (sessionId: string) =>
    api.get<Array<{ role: string; content: string; timestamp: string }>>(`/qa/sessions/${sessionId}`),

  deleteSession: (sessionId: string) =>
    api.delete(`/qa/sessions/${sessionId}`),
};

// Synthesis API
export const synthesisApi = {
  generate: (request: SynthesisRequest) =>
    api.post<SynthesisResponse>('/synthesis', request),

  get: (synthesisId: string) =>
    api.get<SynthesisResponse>(`/synthesis/${synthesisId}`),

  list: (params?: { limit?: number; offset?: number }) =>
    api.get<PaginatedResponse<SynthesisResponse>>('/synthesis', { params }),
};

// Audit API
export const auditApi = {
  getLogs: (params?: {
    user_id?: string;
    action?: string;
    date_from?: string;
    date_to?: string;
    resource_type?: string;
    limit?: number;
    offset?: number;
  }) =>
    api.get<PaginatedResponse<AuditLog>>('/audit/logs', { params }),
};

// Dashboard API
export const dashboardApi = {
  getStats: () =>
    api.get<DashboardStats>('/dashboard/stats'),

  getRecentActivity: (limit?: number) =>
    api.get<Array<{ type: string; timestamp: string; details: string; user?: string }>>('/dashboard/activity', {
      params: { limit: limit || 10 },
    }),

  getWeeklyActivity: () =>
    api.get<{ documents: number[]; questions: number[] }>('/dashboard/weekly-activity'),
};

// Health check
export const healthApi = {
  check: () =>
    api.get<{ status: string; timestamp: string; services: Record<string, string> }>('/health'),
};

// Error handling utility
export const handleApiError = (error: any): ApiError => {
  if (error.response?.data?.error) {
    return {
      code: error.response.data.error.code || 'UNKNOWN_ERROR',
      message: error.response.data.error.message || 'An unknown error occurred',
      details: error.response.data.error.details,
      timestamp: new Date().toISOString(),
    };
  }

  if (error.code === 'NETWORK_ERROR') {
    return {
      code: 'NETWORK_ERROR',
      message: 'Unable to connect to the server. Please check your internet connection.',
      timestamp: new Date().toISOString(),
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: error.message || 'An unexpected error occurred',
    timestamp: new Date().toISOString(),
  };
};

export default apiClient;