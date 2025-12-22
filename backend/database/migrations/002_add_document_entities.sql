-- Migration: Add document_entities table for NER
-- Created: 2024-12-22
-- Purpose: Store Named Entity Recognition results

-- Create document_entities table
CREATE TABLE IF NOT EXISTS document_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    entity_text TEXT NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- DISEASE, MEDICATION, SYMPTOM, DOSAGE, DATE, PROCEDURE, ANATOMY, TEST
    start_pos INTEGER,
    end_pos INTEGER,
    confidence DECIMAL(5,4),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_document_entities_document_id ON document_entities(document_id);
CREATE INDEX IF NOT EXISTS idx_document_entities_type ON document_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_document_entities_confidence ON document_entities(confidence);

-- Add classification and NER status columns to documents table if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='documents' AND column_name='classification') THEN
        ALTER TABLE documents ADD COLUMN classification VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='documents' AND column_name='classification_confidence') THEN
        ALTER TABLE documents ADD COLUMN classification_confidence DECIMAL(5,4);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='documents' AND column_name='ner_processed') THEN
        ALTER TABLE documents ADD COLUMN ner_processed BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='documents' AND column_name='ner_entities_count') THEN
        ALTER TABLE documents ADD COLUMN ner_entities_count INTEGER DEFAULT 0;
    END IF;
END $$;

COMMENT ON TABLE document_entities IS 'Stores Named Entity Recognition results from medical documents';
COMMENT ON COLUMN document_entities.entity_type IS 'Type of entity: DISEASE, MEDICATION, SYMPTOM, DOSAGE, DATE, PROCEDURE, ANATOMY, TEST';
COMMENT ON COLUMN document_entities.confidence IS 'Confidence score from NER model (0.0 to 1.0)';
