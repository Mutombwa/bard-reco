-- ============================================
-- UPDATE USER PASSWORD IN SUPABASE
-- ============================================
-- Run this script in Supabase SQL Editor to fix the password hash
--
-- User: Rosebud Mpofu
-- Password: Talith@17
-- Hashed: fbcf39ecb7006f9b3ec992731468453d3710e8fc6870e70b1c1af91af58178e0
--
-- Instructions:
-- 1. Go to https://supabase.com/dashboard
-- 2. Open your project: cmlbornqaojclzrtqffh
-- 3. Click 'SQL Editor' in left sidebar
-- 4. Click 'New Query'
-- 5. Copy & paste this entire file
-- 6. Click 'Run' (or press Ctrl+Enter)
-- 7. You should see: "UPDATE 1" if successful
-- ============================================

-- Update the password hash for the user
UPDATE users 
SET password_hash = 'fbcf39ecb7006f9b3ec992731468453d3710e8fc6870e70b1c1af91af58178e0'
WHERE username = 'Rosebud Mpofu';

-- Verify the update
SELECT 
    username, 
    email, 
    role,
    created_at,
    CONCAT(LEFT(password_hash, 20), '...') as password_hash_preview
FROM users 
WHERE username = 'Rosebud Mpofu';

-- ============================================
-- Expected Output:
-- 
-- username      | email                             | role | created_at           | password_hash_preview
-- --------------+-----------------------------------+------+----------------------+----------------------
-- Rosebud Mpofu | rosebud.mpofu@bardsantner.com    | user | 2025-10-23 09:21:02  | fbcf39ecb7006f9b3ec9...
--
-- ✅ If you see this, the password is now correct!
-- ✅ You can login to the app with: Rosebud Mpofu / Talith@17
-- ============================================
