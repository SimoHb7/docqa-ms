-- Add document_anonymizations table for DeID service

CREATE TABLE IF NOT EXISTS document_anonymizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL,
    anonymized_content TEXT NOT NULL,
    pii_entities JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
--tt

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_anonymizations_document_id ON document_anonymizations(document_id);
CREATE INDEX IF NOT EXISTS idx_document_anonymizations_created_at ON document_anonymizations(created_at DESC);
