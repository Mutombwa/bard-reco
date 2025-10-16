-- =====================================================
-- Create SQL Server Login and User for Reconciliation App
-- =====================================================
-- Run this script in SSMS after enabling Mixed Mode Authentication
-- and restarting SQL Server
-- =====================================================

USE master;
GO

-- Create a SQL Server login with password
-- Change the password to something secure!
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'ReconciliationApp')
BEGIN
    CREATE LOGIN ReconciliationApp 
    WITH PASSWORD = 'Recon@2025!Secure', 
         DEFAULT_DATABASE = ReconciliationDB,
         CHECK_EXPIRATION = OFF,
         CHECK_POLICY = OFF;
    
    PRINT 'Login "ReconciliationApp" created successfully';
END
ELSE
BEGIN
    PRINT 'Login "ReconciliationApp" already exists';
END
GO

-- Switch to the ReconciliationDB database
USE ReconciliationDB;
GO

-- Create a database user for the login
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'ReconciliationApp')
BEGIN
    CREATE USER ReconciliationApp FOR LOGIN ReconciliationApp;
    PRINT 'User "ReconciliationApp" created successfully';
END
ELSE
BEGIN
    PRINT 'User "ReconciliationApp" already exists';
END
GO

-- Grant necessary permissions
-- db_datareader: Can read all data
-- db_datawriter: Can insert, update, delete data
-- db_ddladmin: Can create/modify tables (if needed in future)
ALTER ROLE db_datareader ADD MEMBER ReconciliationApp;
ALTER ROLE db_datawriter ADD MEMBER ReconciliationApp;
PRINT 'Permissions granted to ReconciliationApp';
GO

-- Test the login (optional)
PRINT '===========================================';
PRINT 'SQL Server Login Created Successfully!';
PRINT 'Username: ReconciliationApp';
PRINT 'Password: Recon@2025!Secure';
PRINT 'Database: ReconciliationDB';
PRINT '';
PRINT 'IMPORTANT: Change the password in this script';
PRINT 'before using in production!';
PRINT '===========================================';
GO
