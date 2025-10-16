-- =====================================================
-- BARD-RECO SQL Server Database Setup Script
-- =====================================================
-- Run this script in SQL Server Management Studio (SSMS)
-- or Azure Data Studio to create the database and tables
-- =====================================================

-- Create database (if not exists)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ReconciliationDB')
BEGIN
    CREATE DATABASE ReconciliationDB;
    PRINT 'Database ReconciliationDB created successfully';
END
ELSE
BEGIN
    PRINT 'Database ReconciliationDB already exists';
END
GO

-- Use the database
USE ReconciliationDB;
GO

-- =====================================================
-- Table 1: Reconciliation Sessions
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ReconciliationSessions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ReconciliationSessions] (
        [SessionID] INT IDENTITY(1,1) PRIMARY KEY,
        [WorkflowType] VARCHAR(50) NOT NULL,
        [Username] VARCHAR(100) NOT NULL,
        [StartTime] DATETIME NOT NULL DEFAULT GETDATE(),
        [EndTime] DATETIME NULL,
        [Status] VARCHAR(20) NOT NULL DEFAULT 'In Progress',
        [TotalMatched] INT DEFAULT 0,
        [TotalUnmatched] INT DEFAULT 0,
        [MatchRate] DECIMAL(5,2) DEFAULT 0,
        [CreatedAt] DATETIME DEFAULT GETDATE(),
        CONSTRAINT [CHK_Status] CHECK ([Status] IN ('In Progress', 'Completed', 'Failed'))
    );
    
    -- Create indexes for better query performance
    CREATE INDEX [IX_Sessions_Username] ON [dbo].[ReconciliationSessions] ([Username]);
    CREATE INDEX [IX_Sessions_WorkflowType] ON [dbo].[ReconciliationSessions] ([WorkflowType]);
    CREATE INDEX [IX_Sessions_StartTime] ON [dbo].[ReconciliationSessions] ([StartTime] DESC);
    
    PRINT 'Table ReconciliationSessions created successfully';
END
ELSE
BEGIN
    PRINT 'Table ReconciliationSessions already exists';
END
GO

-- =====================================================
-- Table 2: Matched Transactions
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MatchedTransactions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MatchedTransactions] (
        [TransactionID] INT IDENTITY(1,1) PRIMARY KEY,
        [SessionID] INT NOT NULL,
        [MatchType] VARCHAR(50) NOT NULL,
        [LedgerDate] DATE NULL,
        [LedgerReference] VARCHAR(255) NULL,
        [LedgerDebit] DECIMAL(18,2) NULL,
        [LedgerCredit] DECIMAL(18,2) NULL,
        [LedgerDescription] VARCHAR(500) NULL,
        [StatementDate] DATE NULL,
        [StatementReference] VARCHAR(255) NULL,
        [StatementAmount] DECIMAL(18,2) NULL,
        [StatementDescription] VARCHAR(500) NULL,
        [MatchScore] DECIMAL(5,2) NULL,
        [Currency] VARCHAR(10) DEFAULT 'ZAR',
        [CreatedAt] DATETIME DEFAULT GETDATE(),
        CONSTRAINT [FK_MatchedTransactions_Session] FOREIGN KEY ([SessionID]) 
            REFERENCES [dbo].[ReconciliationSessions]([SessionID]) ON DELETE CASCADE
    );
    
    -- Create indexes
    CREATE INDEX [IX_Matched_SessionID] ON [dbo].[MatchedTransactions] ([SessionID]);
    CREATE INDEX [IX_Matched_MatchType] ON [dbo].[MatchedTransactions] ([MatchType]);
    CREATE INDEX [IX_Matched_LedgerDate] ON [dbo].[MatchedTransactions] ([LedgerDate]);
    
    PRINT 'Table MatchedTransactions created successfully';
END
ELSE
BEGIN
    PRINT 'Table MatchedTransactions already exists';
END
GO

-- =====================================================
-- Table 3: Split Transactions
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SplitTransactions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[SplitTransactions] (
        [SplitID] INT IDENTITY(1,1) PRIMARY KEY,
        [SessionID] INT NOT NULL,
        [SplitType] VARCHAR(50) NOT NULL,
        [TotalAmount] DECIMAL(18,2) NULL,
        [ComponentCount] INT NULL,
        [CreatedAt] DATETIME DEFAULT GETDATE(),
        CONSTRAINT [FK_SplitTransactions_Session] FOREIGN KEY ([SessionID]) 
            REFERENCES [dbo].[ReconciliationSessions]([SessionID]) ON DELETE CASCADE
    );
    
    CREATE INDEX [IX_Split_SessionID] ON [dbo].[SplitTransactions] ([SessionID]);
    
    PRINT 'Table SplitTransactions created successfully';
END
ELSE
BEGIN
    PRINT 'Table SplitTransactions already exists';
END
GO

-- =====================================================
-- Table 4: Split Transaction Components
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SplitComponents]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[SplitComponents] (
        [ComponentID] INT IDENTITY(1,1) PRIMARY KEY,
        [SplitID] INT NOT NULL,
        [TransactionSource] VARCHAR(20) NOT NULL,
        [TransactionDate] DATE NULL,
        [Reference] VARCHAR(255) NULL,
        [Amount] DECIMAL(18,2) NULL,
        [Description] VARCHAR(500) NULL,
        CONSTRAINT [FK_SplitComponents_Split] FOREIGN KEY ([SplitID]) 
            REFERENCES [dbo].[SplitTransactions]([SplitID]) ON DELETE CASCADE,
        CONSTRAINT [CHK_SplitSource] CHECK ([TransactionSource] IN ('Ledger', 'Statement'))
    );
    
    CREATE INDEX [IX_Components_SplitID] ON [dbo].[SplitComponents] ([SplitID]);
    
    PRINT 'Table SplitComponents created successfully';
END
ELSE
BEGIN
    PRINT 'Table SplitComponents already exists';
END
GO

-- =====================================================
-- Table 5: Unmatched Transactions
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UnmatchedTransactions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[UnmatchedTransactions] (
        [UnmatchedID] INT IDENTITY(1,1) PRIMARY KEY,
        [SessionID] INT NOT NULL,
        [Source] VARCHAR(20) NOT NULL,
        [TransactionDate] DATE NULL,
        [Reference] VARCHAR(255) NULL,
        [Amount] DECIMAL(18,2) NULL,
        [Description] VARCHAR(500) NULL,
        [Currency] VARCHAR(10) DEFAULT 'ZAR',
        [CreatedAt] DATETIME DEFAULT GETDATE(),
        CONSTRAINT [FK_UnmatchedTransactions_Session] FOREIGN KEY ([SessionID]) 
            REFERENCES [dbo].[ReconciliationSessions]([SessionID]) ON DELETE CASCADE,
        CONSTRAINT [CHK_UnmatchedSource] CHECK ([Source] IN ('Ledger', 'Statement'))
    );
    
    CREATE INDEX [IX_Unmatched_SessionID] ON [dbo].[UnmatchedTransactions] ([SessionID]);
    CREATE INDEX [IX_Unmatched_Source] ON [dbo].[UnmatchedTransactions] ([Source]);
    
    PRINT 'Table UnmatchedTransactions created successfully';
END
ELSE
BEGIN
    PRINT 'Table UnmatchedTransactions already exists';
END
GO

-- =====================================================
-- Table 6: Foreign Credits
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ForeignCredits]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ForeignCredits] (
        [ForeignCreditID] INT IDENTITY(1,1) PRIMARY KEY,
        [SessionID] INT NOT NULL,
        [LedgerDate] DATE NULL,
        [LedgerReference] VARCHAR(255) NULL,
        [LedgerAmount] DECIMAL(18,2) NULL,
        [StatementDate] DATE NULL,
        [StatementReference] VARCHAR(255) NULL,
        [StatementAmount] DECIMAL(18,2) NULL,
        [Currency] VARCHAR(10) DEFAULT 'ZAR',
        [CreatedAt] DATETIME DEFAULT GETDATE(),
        CONSTRAINT [FK_ForeignCredits_Session] FOREIGN KEY ([SessionID]) 
            REFERENCES [dbo].[ReconciliationSessions]([SessionID]) ON DELETE CASCADE
    );
    
    CREATE INDEX [IX_ForeignCredits_SessionID] ON [dbo].[ForeignCredits] ([SessionID]);
    
    PRINT 'Table ForeignCredits created successfully';
END
ELSE
BEGIN
    PRINT 'Table ForeignCredits already exists';
END
GO

-- =====================================================
-- Create Views for Reporting
-- =====================================================

-- View: Session Summary
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_SessionSummary')
    DROP VIEW [dbo].[vw_SessionSummary];
GO

CREATE VIEW [dbo].[vw_SessionSummary]
AS
SELECT 
    rs.SessionID,
    rs.WorkflowType,
    rs.Username,
    rs.StartTime,
    rs.EndTime,
    rs.Status,
    rs.TotalMatched,
    rs.TotalUnmatched,
    rs.MatchRate,
    DATEDIFF(MINUTE, rs.StartTime, ISNULL(rs.EndTime, GETDATE())) AS DurationMinutes,
    (SELECT COUNT(*) FROM MatchedTransactions WHERE SessionID = rs.SessionID) AS MatchedCount,
    (SELECT COUNT(*) FROM UnmatchedTransactions WHERE SessionID = rs.SessionID) AS UnmatchedCount,
    (SELECT COUNT(*) FROM SplitTransactions WHERE SessionID = rs.SessionID) AS SplitCount
FROM ReconciliationSessions rs;
GO

PRINT 'View vw_SessionSummary created successfully';
GO

-- View: Match Type Distribution
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_MatchTypeDistribution')
    DROP VIEW [dbo].[vw_MatchTypeDistribution];
GO

CREATE VIEW [dbo].[vw_MatchTypeDistribution]
AS
SELECT 
    SessionID,
    MatchType,
    COUNT(*) AS TransactionCount,
    SUM(StatementAmount) AS TotalAmount,
    AVG(MatchScore) AS AvgMatchScore
FROM MatchedTransactions
GROUP BY SessionID, MatchType;
GO

PRINT 'View vw_MatchTypeDistribution created successfully';
GO

-- =====================================================
-- Insert Sample Data (Optional - for testing)
-- =====================================================
/*
INSERT INTO ReconciliationSessions (WorkflowType, Username, StartTime, Status)
VALUES ('FNB', 'admin', GETDATE(), 'In Progress');

DECLARE @SessionID INT = SCOPE_IDENTITY();

INSERT INTO MatchedTransactions (SessionID, MatchType, LedgerDate, LedgerAmount, StatementDate, StatementAmount, MatchScore)
VALUES (@SessionID, 'Perfect Match', '2025-01-15', 1000.00, '2025-01-15', 1000.00, 100.00);
*/

-- =====================================================
-- Grant Permissions (Optional - adjust as needed)
-- =====================================================
/*
-- Create a database user for the application
CREATE LOGIN ReconciliationAppUser WITH PASSWORD = 'YourSecurePassword123!';
CREATE USER ReconciliationAppUser FOR LOGIN ReconciliationAppUser;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON DATABASE::ReconciliationDB TO ReconciliationAppUser;
*/

PRINT '===========================================';
PRINT 'Database setup completed successfully!';
PRINT 'Database: ReconciliationDB';
PRINT 'Tables created: 6';
PRINT 'Views created: 2';
PRINT '===========================================';
GO
