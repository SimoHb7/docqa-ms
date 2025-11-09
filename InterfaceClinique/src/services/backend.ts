// Backend integration service for InterfaceClinique

import { api } from './api';
import type {
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
  User,
} from '../types';

// Backend health check
export const checkBackendHealth = async () => {
  try {
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      status: 'online',
      services: data.services || {},
      timestamp: data.timestamp,
    };
  } catch (error) {
    console.warn('Backend health check failed:', error);
    return {
      status: 'offline',
      services: {},
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

// Document operations
export const backendDocuments = {
  // Upload document
  upload: async (file: File, metadata?: Record<string, any>) => {
    const formData = new FormData();
    formData.append('file', file);

    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Document upload failed:', error);
      throw error;
    }
  },

  // List documents
  list: async (params?: FilterOptions & { limit?: number; offset?: number }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, String(value));
          }
        });
      }

      const response = await fetch(`http://localhost:8000/api/v1/documents?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      // Return mock data for development
      return {
        documents: [
          {
            id: 'mock-doc-1',
            filename: 'rapport_medical.pdf',
            file_type: 'pdf',
            file_size: 245760,
            processing_status: 'indexed',
            is_anonymized: true,
            metadata: {
              patient_id: 'ANON_PAT_001',
              document_type: 'medical_report',
              upload_date: new Date().toISOString(),
            },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'mock-doc-2',
            filename: 'resultats_lab.pdf',
            file_type: 'pdf',
            file_size: 189432,
            processing_status: 'processing',
            is_anonymized: false,
            metadata: {
              patient_id: 'ANON_PAT_002',
              document_type: 'lab_results',
              upload_date: new Date().toISOString(),
            },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        total: 2,
        limit: 50,
        offset: 0,
      };
    }
  },

  // Get document details
  get: async (documentId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch document: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch document:', error);
      // Return mock data
      return {
        id: documentId,
        filename: 'mock_document.pdf',
        content: 'Contenu du document mock pour le développement...',
        metadata: {},
        created_at: new Date().toISOString(),
      };
    }
  },

  // Delete document
  delete: async (documentId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete document: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to delete document:', error);
      throw error;
    }
  },
};

// Search operations
export const backendSearch = {
  search: async (query: string, filters?: FilterOptions, limit?: number) => {
    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          filters,
          limit: limit || 20,
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Search failed:', error);
      // Return mock search results
      return {
        results: [
          {
            chunk_id: 'mock-chunk-1',
            document_id: 'mock-doc-1',
            content: `Résultats de recherche pour "${query}". Contenu médical anonymisé...`,
            score: 0.89,
            metadata: {
              page: 1,
              section: 'clinical_report',
            },
          },
          {
            chunk_id: 'mock-chunk-2',
            document_id: 'mock-doc-1',
            content: `Informations supplémentaires concernant "${query}" dans le document...`,
            score: 0.76,
            metadata: {
              page: 2,
              section: 'treatment_plan',
            },
          },
        ],
        total: 2,
        query,
        execution_time_ms: 150,
      };
    }
  },
};

// Q&A operations
export const backendQA = {
  ask: async (request: QARequest) => {
    try {
      const response = await fetch('http://localhost:8000/qa/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Q&A failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Q&A failed:', error);
      // Return mock Q&A response
      return {
        answer: `Réponse simulée à votre question: "${request.question}". En mode développement, le backend n'est pas disponible.`,
        sources: [
          {
            document_id: 'mock-doc-1',
            chunk_id: 'mock-chunk-1',
            content: 'Source de la réponse simulée...',
            score: 0.85,
          },
        ],
        confidence_score: 0.82,
        execution_time_ms: 250,
        model_used: 'mock-model',
        tokens_used: 150,
        session_id: request.session_id || 'mock-session',
      };
    }
  },
};

// Dashboard operations
export const backendDashboard = {
  getStats: async () => {
    try {
      const response = await fetch('http://localhost:8000/dashboard/stats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      // Return mock stats
      return {
        totalDocuments: 42,
        totalQuestions: 156,
        averageConfidence: 0.83,
        averageResponseTime: 245,
        documentsByType: {
          medical_report: 25,
          lab_results: 12,
          prescription: 5,
        },
        documentsByStatus: {
          indexed: 38,
          processing: 3,
          failed: 1,
        },
        recentActivity: [
          {
            type: 'upload',
            timestamp: new Date().toISOString(),
            details: 'Nouveau document téléchargé',
          },
          {
            type: 'question',
            timestamp: new Date(Date.now() - 300000).toISOString(),
            details: 'Question posée sur l\'hypertension',
          },
        ],
        systemHealth: {
          uptime: 345600, // 4 days in seconds
          apiResponseTime: 145,
          errorRate: 0.02,
        },
      };
    }
  },
};

// Audit operations
export const backendAudit = {
  getLogs: async (params?: {
    user_id?: string;
    action?: string;
    date_from?: string;
    date_to?: string;
    resource_type?: string;
    limit?: number;
    offset?: number;
  }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, String(value));
          }
        });
      }

      const response = await fetch(`http://localhost:8000/audit/logs?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch audit logs: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
      // Return mock audit logs
      return {
        logs: [
          {
            id: 'mock-log-1',
            timestamp: new Date().toISOString(),
            user_id: 'user-123',
            user_name: 'Dr. Martin',
            action: 'document_upload',
            resource_type: 'document',
            resource_id: 'doc-123',
            details: { filename: 'rapport.pdf' },
            ip_address: '192.168.1.100',
          },
          {
            id: 'mock-log-2',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            user_id: 'user-456',
            user_name: 'Dr. Dubois',
            action: 'search_query',
            resource_type: 'query',
            resource_id: 'query-456',
            details: { query: 'traitement hypertension' },
            ip_address: '192.168.1.101',
          },
        ],
        total: 2,
      };
    }
  },
};

// Synthesis operations
export const backendSynthesis = {
  generate: async (request: SynthesisRequest): Promise<SynthesisResponse> => {
    try {
      const response = await fetch('http://localhost:8005/api/v1/synthesis/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Synthesis failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Synthesis generation failed:', error);
      throw error;
    }
  },

  list: async (params?: { limit?: number; offset?: number }) => {
    // Mock implementation for now since we don't have a list endpoint yet
    return {
      data: [],
      total: 0,
    };
  },
};

// Export all backend services
export const backend = {
  health: checkBackendHealth,
  documents: backendDocuments,
  search: backendSearch,
  qa: backendQA,
  dashboard: backendDashboard,
  audit: backendAudit,
  synthesis: backendSynthesis,
};

export default backend;