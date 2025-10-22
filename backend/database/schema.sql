-- DocQA-MS Database Schema - SIMPLIFIED VERSION FOR STUDENT PROJECT
-- Optimized for 45-day development timeline

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- CORE TABLES (PHASE 1 - ESSENTIAL)
-- ==========================================

-- Documents table (simplified)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    content TEXT,
    file_size BIGINT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(50) DEFAULT 'uploaded',
    is_anonymized BOOLEAN DEFAULT FALSE,
    indexed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks for semantic search
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- QA Interactions (simplified - no sessions for now)
CREATE TABLE qa_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    context_documents UUID[], -- Array of document_ids used
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    llm_model VARCHAR(100) DEFAULT 'llama3.1:8b',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs (simplified)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- PHASE 2 TABLES (ADD LATER IF TIME ALLOWS)
-- ==========================================
-- These can be added in Phase 2 (days 31-45) if time permits

-- PII Detection results (Phase 2)
-- CREATE TABLE pii_entities (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
--     entity_type VARCHAR(50) NOT NULL,
--     entity_value TEXT NOT NULL,
--     confidence_score DECIMAL(3,2),
--     replacement_value TEXT,
--     detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Search queries log (Phase 2)
-- CREATE TABLE search_queries (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id VARCHAR(100),
--     query_text TEXT NOT NULL,
--     result_count INTEGER DEFAULT 0,
--     execution_time_ms INTEGER,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Synthesis requests (Phase 2 - if time allows)
-- CREATE TABLE synthesis_requests (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id VARCHAR(100),
--     request_type VARCHAR(50) NOT NULL,
--     parameters JSONB,
--     status VARCHAR(50) DEFAULT 'pending',
--     result_content TEXT,
--     execution_time_ms INTEGER,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Essential indexes for Phase 1
CREATE INDEX idx_documents_upload_date ON documents(upload_date DESC);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_documents_anonymized ON documents(is_anonymized);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_content ON document_chunks USING gin(to_tsvector('french', content));
CREATE INDEX idx_qa_interactions_created_at ON qa_interactions(created_at DESC);
CREATE INDEX idx_qa_interactions_user ON qa_interactions(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ==========================================
-- INITIAL TEST DATA
-- ==========================================

-- Sample medical document for testing
INSERT INTO documents (filename, file_type, content, file_size, processing_status, metadata)
VALUES (
    'rapport_medical_patient_001.pdf',
    'pdf',
    'RAPPORT MEDICAL\n\nPatient: Jean Dupont\nDate: 15 janvier 2024\n\nANTÉCÉDENTS:\nLe patient présente une hypertension artérielle connue depuis 5 ans, traitée par irbesartan 150mg/j.\n\nEXAMEN CLINIQUE:\nTA: 140/85 mmHg\nPouls: 72/min régulier\nAuscultation cardiaque: rythmes réguliers, pas de souffle\n\nCONCLUSION:\nBonne observance thérapeutique. Contrôle tensionnel satisfaisant.\n\nDr. Smith\nCardiologue',
    245760,
    'processed',
    '{"author": "Dr. Smith", "specialty": "cardiology", "language": "fr", "patient_id": "PAT_001"}'
);

-- Sample document chunks (fixed JSONB casting)
INSERT INTO document_chunks (document_id, chunk_index, content, metadata)
SELECT
    d.id,
    1,
    'RAPPORT MEDICAL Patient: Jean Dupont Date: 15 janvier 2024 ANTÉCÉDENTS: Le patient présente une hypertension artérielle connue depuis 5 ans',
    '{"page": 1, "section": "header"}'::jsonb
FROM documents d WHERE d.filename = 'rapport_medical_patient_001.pdf'

UNION ALL

SELECT
    d.id,
    2,
    'EXAMEN CLINIQUE: TA: 140/85 mmHg Pouls: 72/min régulier Auscultation cardiaque: rythmes réguliers, pas de souffle',
    '{"page": 1, "section": "clinical_exam"}'::jsonb
FROM documents d WHERE d.filename = 'rapport_medical_patient_001.pdf'

UNION ALL

SELECT
    d.id,
    3,
    'CONCLUSION: Bonne observance thérapeutique. Contrôle tensionnel satisfaisant. Dr. Smith Cardiologue',
    '{"page": 1, "section": "conclusion"}'::jsonb
FROM documents d WHERE d.filename = 'rapport_medical_patient_001.pdf';

-- Sample QA interaction
INSERT INTO qa_interactions (user_id, question, answer, context_documents, confidence_score, response_time_ms)
VALUES (
    'user_123',
    'Quel est le traitement actuel de l''hypertension du patient?',
    'Le patient suit un traitement par irbesartan 150mg une fois par jour. La tension artérielle est bien contrôlée à 140/85 mmHg.',
    ARRAY[(SELECT id FROM documents WHERE filename = 'rapport_medical_patient_001.pdf')],
    0.91,
    1250
);

-- Sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details)
VALUES
(
    'user_123',
    'document_upload',
    'document',
    (SELECT id FROM documents WHERE filename = 'rapport_medical_patient_001.pdf'),
    '{"filename": "rapport_medical_patient_001.pdf", "size": 245760}'
),
(
    'user_123',
    'qa_interaction',
    'qa_session',
    (SELECT id FROM qa_interactions WHERE question LIKE '%hypertension%'),
    '{"question_length": 50, "response_length": 120}'
);