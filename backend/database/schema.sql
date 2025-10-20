-- DocQA-MS Database Schema
-- PostgreSQL 15+ compatible

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- CORE TABLES
-- ==========================================

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    document_type VARCHAR(50), -- 'medical_report', 'lab_results', 'prescription', etc.
    patient_id VARCHAR(100), -- Anonymized patient identifier
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(50) DEFAULT 'uploaded', -- 'uploaded', 'processing', 'processed', 'failed'
    processing_error TEXT,
    metadata JSONB, -- Additional document metadata
    checksum VARCHAR(128), -- File integrity check
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks for semantic search
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_vector VECTOR(384), -- Adjust dimension based on embedding model
    metadata JSONB, -- Chunk-specific metadata (page, section, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Create vector extension for embeddings (if using pgvector)
-- Note: Requires pgvector extension to be installed
-- CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- ANONYMIZATION & PRIVACY
-- ==========================================

-- PII Detection results
CREATE TABLE pii_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- 'PERSON', 'LOCATION', 'DATE', 'PHONE', etc.
    entity_value TEXT NOT NULL,
    start_position INTEGER NOT NULL,
    end_position INTEGER NOT NULL,
    confidence_score DECIMAL(3,2),
    replacement_value TEXT, -- Anonymized replacement
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Anonymization mappings (for reversible anonymization if needed)
CREATE TABLE anonymization_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    original_value TEXT NOT NULL,
    anonymized_value TEXT NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, original_value)
);

-- ==========================================
-- SEARCH & INDEXING
-- ==========================================

-- Search queries log
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100), -- Anonymized user identifier
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) DEFAULT 'semantic', -- 'semantic', 'keyword', 'hybrid'
    filters JSONB, -- Applied filters (date range, document type, etc.)
    result_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search results
CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES search_queries(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
    relevance_score DECIMAL(5,4),
    matched_text TEXT,
    result_rank INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- LLM INTERACTIONS
-- ==========================================

-- QA Sessions
CREATE TABLE qa_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100), -- Anonymized user identifier
    session_title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- QA Interactions
CREATE TABLE qa_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES qa_sessions(id) ON DELETE CASCADE,
    user_query TEXT NOT NULL,
    llm_response TEXT NOT NULL,
    response_sources JSONB, -- Array of document/chunk references
    confidence_score DECIMAL(3,2),
    execution_time_ms INTEGER,
    llm_model VARCHAR(100), -- Model used (gpt-4, llama2, etc.)
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- SYNTHESIS & COMPARISONS
-- ==========================================

-- Synthesis requests
CREATE TABLE synthesis_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    request_type VARCHAR(50) NOT NULL, -- 'patient_timeline', 'comparison', 'summary'
    parameters JSONB, -- Request-specific parameters
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    result_content TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ==========================================
-- AUDIT & COMPLIANCE
-- ==========================================

-- Complete audit log for all system activities
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100), -- Anonymized user identifier
    session_id VARCHAR(255), -- User session identifier
    action VARCHAR(100) NOT NULL, -- 'upload', 'search', 'qa', 'download', etc.
    resource_type VARCHAR(50) NOT NULL, -- 'document', 'query', 'synthesis', etc.
    resource_id UUID, -- ID of the affected resource
    action_details JSONB, -- Detailed action information
    ip_address INET,
    user_agent TEXT,
    location_info JSONB, -- Geographic/location data if available
    compliance_flags JSONB, -- HIPAA/GDPR compliance flags
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    severity VARCHAR(20) DEFAULT 'info' -- 'debug', 'info', 'warning', 'error', 'critical'
);

-- ==========================================
-- SYSTEM HEALTH & METRICS
-- ==========================================

-- Service health checks
CREATE TABLE service_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    service_version VARCHAR(50),
    status VARCHAR(20) NOT NULL, -- 'healthy', 'unhealthy', 'degraded'
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB, -- Additional metadata/tags
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Documents indexes
CREATE INDEX idx_documents_patient_id ON documents(patient_id);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_upload_date ON documents(upload_date);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Document chunks indexes
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_content_gin ON document_chunks USING gin(to_tsvector('french', content));

-- PII entities indexes
CREATE INDEX idx_pii_entities_document_id ON pii_entities(document_id);
CREATE INDEX idx_pii_entities_type ON pii_entities(entity_type);

-- Search indexes
CREATE INDEX idx_search_queries_user_id ON search_queries(user_id);
CREATE INDEX idx_search_queries_created_at ON search_queries(created_at);
CREATE INDEX idx_search_results_query_id ON search_results(query_id);
CREATE INDEX idx_search_results_document_id ON search_results(document_id);

-- QA indexes
CREATE INDEX idx_qa_sessions_user_id ON qa_sessions(user_id);
CREATE INDEX idx_qa_interactions_session_id ON qa_interactions(session_id);
CREATE INDEX idx_qa_interactions_created_at ON qa_interactions(created_at);

-- Audit indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);

-- ==========================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_qa_sessions_updated_at BEFORE UPDATE ON qa_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- VIEWS FOR COMMON QUERIES
-- ==========================================

-- View for document processing status summary
CREATE VIEW document_processing_summary AS
SELECT
    processing_status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (updated_at - upload_date))) as avg_processing_time_seconds
FROM documents
GROUP BY processing_status;

-- View for user activity summary
CREATE VIEW user_activity_summary AS
SELECT
    user_id,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    COUNT(*) as total_queries,
    AVG(execution_time_ms) as avg_response_time
FROM search_queries
WHERE user_id IS NOT NULL
GROUP BY user_id;

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on sensitive tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_interactions ENABLE ROW LEVEL SECURITY;

-- Note: RLS policies would be defined based on your authentication and authorization requirements
-- This is a placeholder for future implementation

-- ==========================================
-- INITIAL DATA SEEDING
-- ==========================================

-- Insert some initial service health records
INSERT INTO service_health (service_name, status) VALUES
('api-gateway', 'healthy'),
('doc-ingestor', 'healthy'),
('deid', 'healthy'),
('indexer-semantique', 'healthy'),
('llm-qa', 'healthy'),
('synthese-comparative', 'healthy'),
('audit-logger', 'healthy');