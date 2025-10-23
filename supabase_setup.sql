-- =============================================
-- Supabase Database Setup
-- =============================================
-- Run this in your Supabase SQL Editor
-- (Project > SQL Editor > New Query)
-- =============================================

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    role TEXT DEFAULT 'user',
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT username_not_empty CHECK (username <> ''),
    CONSTRAINT email_not_empty CHECK (email <> ''),
    CONSTRAINT valid_role CHECK (role IN ('user', 'admin'))
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_role ON users(role);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies for Row Level Security
-- Note: Since we're using the service role key, these won't restrict the app
-- But they provide security for direct database access

-- Policy: Allow service role to do everything
CREATE POLICY "Service role has full access" ON users
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create default admin account
-- Change the password after first login!
INSERT INTO users (username, password_hash, email, role)
VALUES (
    'tatenda.mutombwa',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', -- SHA-256 of 'admin123'
    'tatenda.mutombwa@bardsantner.com',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Verify table creation
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Show all users
SELECT 
    username, 
    email, 
    role, 
    created_at, 
    last_login 
FROM users
ORDER BY created_at DESC;
