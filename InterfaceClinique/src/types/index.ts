// TypeScript type definitions for InterfaceClinique

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  role: 'admin' | 'doctor' | 'researcher' | 'quality_manager';
  organization?: string;
  permissions: string[];
  createdAt: string;
  lastLogin?: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  processing_status: 'uploaded' | 'processing' | 'anonymized' | 'indexed' | 'failed' | 'processed';
  is_anonymized: boolean;
  content?: string;
  metadata?: DocumentMetadata;
  created_at: string;
  updated_at?: string;
  upload_date?: string;
  uploaded_by?: string;
  patient_id?: string;
  document_type?: string;
}

export interface DocumentMetadata {
  patient_id?: string;
  document_type?: string;
  upload_date?: string;
  original_filename?: string;
  mime_type?: string;
  page_count?: number;
  language?: string;
  [key: string]: any;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  embedding?: number[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface QAInteraction {
  id: string;
  question: string;
  answer: string;
  confidence_score: number;
  llm_model: string;
  response_time_ms: number;
  context_documents: string[];
  metadata?: Record<string, any>;
  created_at: string;
  user_id?: string;
  session_id: string;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
  filename?: string;
  patient_id?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  execution_time_ms: number;
  filters_applied?: Record<string, any>;
}

export interface QARequest {
  question: string;
  context_documents?: string[];
  session_id?: string;
  temperature?: number;
  max_tokens?: number;
  model?: string;
}

export interface QAResponse {
  answer: string;
  sources: Array<{
    document_id: string;
    chunk_id: string;
    content: string;
    score: number;
    filename?: string;
  }>;
  confidence_score: number;
  execution_time_ms: number;
  model_used: string;
  tokens_used: number;
  session_id: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  document_id?: string;
  error?: string;
  estimated_time?: number;
}

export interface DashboardStats {
  totalDocuments: number;
  totalQuestions: number;
  averageConfidence: number;
  averageResponseTime: number;
  documentsByType: Record<string, number>;
  documentsByStatus: Record<string, number>;
  recentActivity: Array<{
    type: 'upload' | 'question' | 'search';
    timestamp: string;
    details: string;
    user?: string;
  }>;
  systemHealth: {
    uptime: number;
    apiResponseTime: number;
    errorRate: number;
  };
}

export interface FilterOptions {
  patient_id?: string;
  document_type?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  uploaded_by?: string;
  is_anonymized?: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: Array<{
    document_id: string;
    filename: string;
    excerpt: string;
    score?: number;
  }>;
  confidence?: number;
  metadata?: Record<string, any>;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
  actionLabel?: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_name?: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
}

export interface SynthesisRequest {
  synthesis_id: string;
  type: 'patient_timeline' | 'comparison' | 'summary';
  parameters: {
    patient_id?: string;
    document_ids?: string[];
    document_id?: string;
    date_range?: {
      start: string;
      end: string;
    };
    filters?: Record<string, any>;
  };
  format?: 'markdown' | 'json' | 'html';
}

export interface SynthesisResponse {
  synthesis_id?: string;
  status: 'completed' | 'processing' | 'failed';
  result: {
    title: string;
    content: string;
    sections?: Array<{
      title: string;
      content: string;
      date?: string;
    }>;
    key_findings?: string[];
    comparisons?: Array<{
      category: string;
      filename?: string;
      size?: number;
      is_anonymized?: boolean;
      pii_count?: number;
      [key: string]: any;
    }>;
    summary_points?: string[];
    recommendations?: string[];
    conclusions?: string[];
    _metadata?: {
      used_anonymized_data: boolean;
      documents_analyzed: number;
      total_pii_detected?: number;
      word_count?: number;
      is_anonymized?: boolean;
      pii_count?: number;
      error?: string;
    };
  };
  generated_at: string;
  execution_time_ms: number;
  type?: string;
  parameters?: Record<string, any>;
  sources?: Array<{
    document_id: string;
    filename: string;
    relevance_score: number;
  }>;
  metadata?: Record<string, any>;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface SearchForm {
  query: string;
  filters: FilterOptions;
  limit?: number;
}

export interface UploadForm {
  files: FileList;
  metadata?: Partial<DocumentMetadata>;
}

// WebSocket types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface DocumentProcessingUpdate extends WebSocketMessage {
  type: 'document_processing';
  data: {
    document_id: string;
    status: Document['processing_status'];
    progress?: number;
    message?: string;
  };
}

export interface SynthesisProgressUpdate extends WebSocketMessage {
  type: 'synthesis_progress';
  data: {
    synthesis_id: string;
    progress: number;
    status: 'processing' | 'completed' | 'failed';
    message?: string;
  };
}

// ML Service types
export interface MLClassificationRequest {
  text: string;
}

export interface MLClassificationResponse {
  predicted_class: string;
  confidence: number;
  all_probabilities: Record<string, number>;
  model_used: 'pretrained' | 'finetuned';
}

export interface MLEntity {
  text: string;
  label: string;
  confidence: number;
  start?: number;
  end?: number;
}

export interface MLEntityExtractionRequest {
  text: string;
}

export interface MLEntityExtractionResponse {
  value: MLEntity[];
  Count: number;
}

export interface MLAnalyzeRequest {
  text: string;
  extract_entities?: boolean;
  classify?: boolean;
}

export interface MLAnalyzeResponse {
  classification?: MLClassificationResponse;
  entities?: MLEntityExtractionResponse;
  processing_time_ms: number;
}

export interface MLHealthResponse {
  status: string;
  service: string;
  version: string;
  models_loaded: boolean;
}

export interface MLModelInfo {
  name: string;
  type: 'classification' | 'ner';
  status: 'loaded' | 'loading' | 'error';
  model_path: string;
  is_pretrained: boolean;
}