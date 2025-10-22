-- DocQA-MS Seed Data - SIMPLIFIED FOR STUDENT PROJECT
-- Only essential sample data for Phase 1

-- ==========================================
-- ADDITIONAL SAMPLE DATA (if needed beyond schema.sql)
-- ==========================================

-- Note: The main sample data is already in schema.sql
-- This file is kept minimal for Phase 1 development

-- You can add more sample data here as needed for testing

-- ==========================================
-- SAMPLE DOCUMENT CHUNKS
-- ==========================================

INSERT INTO document_chunks (
    document_id, chunk_index, content, metadata
) VALUES
(
    (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf'),
    1,
    'RAPPORT MEDICAL\n\nPatient: ANON_PAT_001\nDate: 15 janvier 2024\n\nANTÉCÉDENTS:\nLe patient présente une hypertension artérielle connue depuis 5 ans, traitée par irbesartan 150mg/j.\n\nEXAMEN CLINIQUE:\nTA: 140/85 mmHg\nPouls: 72/min régulier\nAuscultation cardiaque: rythmes réguliers, pas de souffle\n\nCONCLUSION:\nBonne observance thérapeutique. Contrôle tensionnel satisfaisant.',
    '{"page": 1, "section": "clinical_report", "language": "fr"}'
),
(
    (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf'),
    2,
    'TRAITEMENT:\n- Irbesartan 150mg: 1 comprimé par jour\n- Aspirine 75mg: 1 comprimé par jour (prévention cardiovasculaire)\n\nRECOMMANDATIONS:\n- Régime hyposodé\n- Activité physique régulière\n- Prochain contrôle dans 3 mois\n\nDr. Smith\nCardiologue',
    '{"page": 1, "section": "treatment_plan", "language": "fr"}'
),
(
    (SELECT id FROM documents WHERE filename = 'sample_lab_results_1.pdf'),
    1,
    'RÉSULTATS D''ANALYSES BIOLOGIQUES\n\nPatient: ANON_PAT_002\nDate de prélèvement: 20 janvier 2024\n\nHÉMATOLOGIE:\n- Globules rouges: 4.5 T/L (N: 4.2-5.4)\n- Hémoglobine: 13.2 g/dL (N: 12-16)\n- Leucocytes: 7.8 G/L (N: 4-10)\n- Plaquettes: 285 G/L (N: 150-400)\n\nBIOCHIMIE:\n- Glycémie: 5.2 mmol/L (N: 3.9-5.8)\n- Créatininémie: 85 µmol/L (N: 60-110)\n- Cholestérol total: 5.1 mmol/L (N: <5.2)',
    '{"page": 1, "section": "lab_results", "language": "fr"}'
);

-- ==========================================
-- SAMPLE PII ENTITIES (for testing anonymization)
-- ==========================================

INSERT INTO pii_entities (
    document_id, entity_type, entity_value, start_position, end_position,
    confidence_score, replacement_value
) VALUES
(
    (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf'),
    'PERSON',
    'Mohamed HB',
    25,
    36,
    0.95,
    'ANON_PAT_001'
),
(
    (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf'),
    'DATE',
    '15 janvier 2024',
    45,
    60,
    0.98,
    '[DATE]'
),
(
    (SELECT id FROM documents WHERE filename = 'sample_lab_results_1.pdf'),
    'PERSON',
    'Mariam mari',
    18,
    30,
    0.92,
    'ANON_PAT_002'
);

-- ==========================================
-- SAMPLE SEARCH QUERIES
-- ==========================================

INSERT INTO search_queries (
    user_id, query_text, query_type, filters, result_count, execution_time_ms
) VALUES
(
    'user_123',
    'hypertension traitement',
    'semantic',
    '{"document_type": "medical_report", "date_range": {"start": "2024-01-01", "end": "2024-12-31"}}',
    2,
    245
),
(
    'user_456',
    'résultats analyses glycémie',
    'semantic',
    '{"document_type": "lab_results"}',
    1,
    189
);

-- ==========================================
-- SAMPLE QA INTERACTIONS
-- ==========================================

INSERT INTO qa_sessions (user_id, session_title) VALUES
('user_123', 'Consultation hypertension'),
('user_456', 'Suivi diabète');

INSERT INTO qa_interactions (
    session_id, user_query, llm_response, response_sources,
    confidence_score, execution_time_ms, llm_model, tokens_used
) VALUES
(
    (SELECT id FROM qa_sessions WHERE session_title = 'Consultation hypertension'),
    'Quel est le traitement actuel de l''hypertension du patient?',
    'Le patient suit un traitement par irbesartan 150mg une fois par jour, associé à de l''aspirine 75mg pour la prévention cardiovasculaire. La tension artérielle est bien contrôlée à 140/85 mmHg.',
    '[{"document_id": "' || (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf') || '", "chunk_id": "' || (SELECT id FROM document_chunks WHERE chunk_index = 1 LIMIT 1) || '", "relevance_score": 0.92}]',
    0.88,
    1250,
    'llama2:7b-chat',
    156
),
(
    (SELECT id FROM qa_sessions WHERE session_title = 'Suivi diabète'),
    'Quels sont les derniers résultats de glycémie?',
    'La dernière glycémie mesurée est de 5.2 mmol/L, ce qui est dans les valeurs normales (3.9-5.8 mmol/L).',
    '[{"document_id": "' || (SELECT id FROM documents WHERE filename = 'sample_lab_results_1.pdf') || '", "chunk_id": "' || (SELECT id FROM document_chunks WHERE chunk_index = 1 LIMIT 1) || '", "relevance_score": 0.95}]',
    0.91,
    980,
    'llama2:7b-chat',
    98
);

-- ==========================================
-- SAMPLE AUDIT LOGS
-- ==========================================

INSERT INTO audit_logs (
    user_id, session_id, action, resource_type, resource_id,
    action_details, ip_address, severity
) VALUES
(
    'user_123',
    'session_abc123',
    'document_upload',
    'document',
    (SELECT id FROM documents WHERE filename = 'sample_medical_report_1.pdf'),
    '{"filename": "Rapport_Medical_Patient_X_2024.pdf", "size": 245760}',
    '192.168.1.100',
    'info'
),
(
    'user_123',
    'session_abc123',
    'search_query',
    'query',
    (SELECT id FROM search_queries WHERE query_text LIKE '%hypertension%' LIMIT 1),
    '{"query": "hypertension traitement", "results_count": 2}',
    '192.168.1.100',
    'info'
),
(
    'user_456',
    'session_def456',
    'qa_interaction',
    'qa_session',
    (SELECT id FROM qa_sessions WHERE session_title = 'Suivi diabète'),
    '{"question": "Quels sont les derniers résultats de glycémie?", "response_length": 98}',
    '192.168.1.101',
    'info'
);

-- ==========================================
-- SAMPLE SYNTHESIS REQUESTS
-- ==========================================

INSERT INTO synthesis_requests (
    user_id, request_type, parameters, status, result_content, execution_time_ms, completed_at
) VALUES
(
    'user_123',
    'patient_timeline',
    '{"patient_id": "ANON_PAT_001", "date_range": {"start": "2024-01-01", "end": "2024-12-31"}}',
    'completed',
    '## Chronologie du patient ANON_PAT_001\n\n**15 janvier 2024**: Consultation cardiologique - Hypertension bien contrôlée sous irbesartan 150mg/j\n**20 janvier 2024**: Analyses biologiques - Glycémie normale\n\n**Évolution**: Stabilité clinique avec bonne observance thérapeutique.',
    2340,
    NOW()
);

-- ==========================================
-- SAMPLE PERFORMANCE METRICS
-- ==========================================

INSERT INTO performance_metrics (metric_name, metric_value, metric_unit, tags) VALUES
('api_response_time', 245.50, 'ms', '{"endpoint": "/api/search", "method": "POST"}'),
('document_processing_time', 12.34, 'seconds', '{"service": "doc_ingestor", "document_type": "pdf"}'),
('llm_inference_time', 1.25, 'seconds', '{"model": "llama2:7b-chat", "tokens": 156}'),
('vector_search_time', 0.089, 'seconds', '{"index_size": 1000, "dimensions": 384}'),
('database_query_time', 15.67, 'ms', '{"table": "documents", "operation": "SELECT"}');

-- ==========================================
-- UPDATE SERVICE HEALTH
-- ==========================================

UPDATE service_health SET
    service_version = '1.0.0',
    response_time_ms = 150,
    checked_at = NOW()
WHERE service_name IN ('api-gateway', 'doc-ingestor', 'deid', 'indexer-semantique', 'llm-qa', 'synthese-comparative', 'audit-logger');