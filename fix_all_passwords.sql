-- ============================================
-- FIX ALL USER PASSWORDS IN SUPABASE
-- ============================================
-- Run this script in Supabase SQL Editor to fix password hashes for all users
--
-- Instructions:
-- 1. Go to https://supabase.com/dashboard
-- 2. Open your project: cmlbornqaojclzrtqffh
-- 3. Click 'SQL Editor' in left sidebar
-- 4. Click 'New Query'
-- 5. Copy & paste this entire file
-- 6. Click 'Run' (or press Ctrl+Enter)
-- 7. You should see: "UPDATE 2" if successful
-- ============================================

-- Fix tatenda.mutombwa password
-- Plain text: admin123
-- Hashed: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
UPDATE users 
SET password_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
WHERE username = 'tatenda.mutombwa';

-- Fix Rosebud Mpofu password
-- Plain text: Talith@17
-- Hashed: fbcf39ecb7006f9b3ec992731468453d3710e8fc6870e70b1c1af91af58178e0
UPDATE users 
SET password_hash = 'fbcf39ecb7006f9b3ec992731468453d3710e8fc6870e70b1c1af91af58178e0'
WHERE username = 'Rosebud Mpofu';

-- Verify all users
SELECT 
    username, 
    email, 
    role,
    created_at,
    CONCAT(LEFT(password_hash, 20), '...') as password_hash_preview
FROM users 
ORDER BY created_at;

-- ============================================
-- Expected Output:
-- 
-- username          | email                             | role  | created_at           | password_hash_preview
-- ------------------+-----------------------------------+-------+----------------------+----------------------
-- tatenda.mutombwa  | tatenda.mutombwa@bardsantner.com | admin | 2025-10-23 07:41:45  | 240be518fabd2724ddb6...
-- Rosebud Mpofu     | rosebud.mpofu@bardsantner.com    | user  | 2025-10-23 09:21:02  | fbcf39ecb7006f9b3ec9...
--
-- ✅ If you see both users with correct hashes, you're good!
--
-- Login Credentials:
-- 1. tatenda.mutombwa / admin123
-- 2. Rosebud Mpofu / Talith@17
-- ============================================
