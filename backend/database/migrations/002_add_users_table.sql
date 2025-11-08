-- Migration: Add Users Table for Auth0 Integration
-- Date: 2025-01-28
-- Description: Creates users table to store Auth0 authenticated users and updates foreign keys

-- Step 1: Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth0_sub VARCHAR(255) UNIQUE NOT NULL, -- Auth0 subject identifier (sub claim)
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    nickname VARCHAR(100),
    picture VARCHAR(500), -- URL to user's profile picture
    role VARCHAR(50) DEFAULT 'clinician', -- clinician, admin, researcher, etc.
    permissions JSONB DEFAULT '[]'::jsonb, -- Array of permission strings
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb, -- Additional user metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_auth0_sub ON users(auth0_sub);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Step 3: Add temporary column to qa_interactions if it doesn't exist
ALTER TABLE qa_interactions 
ADD COLUMN IF NOT EXISTS user_uuid UUID;

-- Step 4: Add temporary column to audit_logs if it doesn't exist
ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS user_uuid UUID;

-- Step 5: Create default admin user for testing
INSERT INTO users (auth0_sub, email, name, role, permissions, is_active, email_verified)
VALUES (
    'auth0|default-admin',
    'admin@interfaceclinique.com',
    'Admin User',
    'admin',
    '["read_documents", "upload_documents", "ask_questions", "manage_users", "view_audit_logs"]'::jsonb,
    TRUE,
    TRUE
)
ON CONFLICT (auth0_sub) DO NOTHING;

-- Step 6: Create default clinician user for testing
INSERT INTO users (auth0_sub, email, name, role, permissions, is_active, email_verified)
VALUES (
    'auth0|default-clinician',
    'clinician@interfaceclinique.com',
    'Clinical User',
    'clinician',
    '["read_documents", "upload_documents", "ask_questions"]'::jsonb,
    TRUE,
    TRUE
)
ON CONFLICT (auth0_sub) DO NOTHING;

-- Step 7: Migrate existing qa_interactions data
-- Link old user_id (VARCHAR) to new user_uuid (UUID) by creating a default user if needed
DO $$
DECLARE
    default_user_uuid UUID;
BEGIN
    -- Get or create a default 'legacy' user for existing records
    INSERT INTO users (auth0_sub, email, name, role, is_active)
    VALUES (
        'legacy|migrated-user',
        'legacy@interfaceclinique.com',
        'Legacy User (Pre-Auth0)',
        'clinician',
        TRUE
    )
    ON CONFLICT (auth0_sub) 
    DO UPDATE SET email = EXCLUDED.email
    RETURNING id INTO default_user_uuid;
    
    -- Update qa_interactions to reference the legacy user
    UPDATE qa_interactions
    SET user_uuid = default_user_uuid
    WHERE user_id IS NOT NULL AND user_uuid IS NULL;
END $$;

-- Step 8: Migrate existing audit_logs data
DO $$
DECLARE
    default_user_uuid UUID;
BEGIN
    SELECT id INTO default_user_uuid
    FROM users
    WHERE auth0_sub = 'legacy|migrated-user';
    
    UPDATE audit_logs
    SET user_uuid = default_user_uuid
    WHERE user_id IS NOT NULL AND user_uuid IS NULL;
END $$;

-- Step 9: Drop old user_id columns and rename new ones
ALTER TABLE qa_interactions DROP COLUMN IF EXISTS user_id;
ALTER TABLE qa_interactions RENAME COLUMN user_uuid TO user_id;

ALTER TABLE audit_logs DROP COLUMN IF EXISTS user_id;
ALTER TABLE audit_logs RENAME COLUMN user_uuid TO user_id;

-- Step 10: Add foreign key constraints
ALTER TABLE qa_interactions 
ADD CONSTRAINT fk_qa_interactions_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE audit_logs 
ADD CONSTRAINT fk_audit_logs_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Step 11: Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Migration complete
-- You can now use the users table for Auth0 authentication
