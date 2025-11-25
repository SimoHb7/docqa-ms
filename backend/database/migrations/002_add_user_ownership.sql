-- Migration: Add user_id to documents and qa_interactions for user-specific access
-- Created: 2025-11-24

-- Add user_id to documents table
ALTER TABLE documents
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Create index for faster user document queries
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- Add user_id to qa_interactions table
ALTER TABLE qa_interactions
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Create index for faster user QA history queries
CREATE INDEX idx_qa_interactions_user_id ON qa_interactions(user_id);

-- Add user_id to audit_logs table (if not already present)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'audit_logs' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE audit_logs
        ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;
        
        CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
    END IF;
END $$;

-- Update existing records to have NULL user_id (can be manually updated later)
-- In production, you might want to assign existing data to a "system" user

COMMENT ON COLUMN documents.user_id IS 'User who uploaded the document';
COMMENT ON COLUMN qa_interactions.user_id IS 'User who asked the question';
COMMENT ON COLUMN audit_logs.user_id IS 'User who performed the action';
