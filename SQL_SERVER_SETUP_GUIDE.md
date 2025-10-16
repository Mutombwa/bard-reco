# 🗄️ SQL Server Integration Guide

Complete guide to setting up SQL Server for BARD-RECO reconciliation system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Database Schema](#database-schema)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The SQL Server integration allows you to:
- ✅ Save reconciliation results permanently
- ✅ Track reconciliation history
- ✅ Generate reports from historical data
- ✅ Monitor match rates over time
- ✅ Audit transaction processing

---

## 📦 Prerequisites

### Option 1: SQL Server (Local/On-Premises)

1. **SQL Server 2019 or later** (Express, Standard, or Enterprise)
   - Download: https://www.microsoft.com/sql-server/sql-server-downloads
   
2. **SQL Server Management Studio (SSMS)**
   - Download: https://aka.ms/ssmsfullsetup

3. **ODBC Driver 17 for SQL Server**
   - Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Option 2: Azure SQL Database (Cloud)

1. **Azure Account** with active subscription
2. **Azure SQL Database** instance created
3. **Firewall rules** configured to allow your IP

---

## 🚀 Installation Steps

### Step 1: Install SQL Server (Local)

```powershell
# Download SQL Server Express (Free)
# Visit: https://www.microsoft.com/sql-server/sql-server-downloads

# Choose: Express Edition (Free)
# Install with default settings
# Note down the server name: Usually (local)\SQLEXPRESS or localhost\SQLEXPRESS
```

### Step 2: Install ODBC Driver

```powershell
# Download and install ODBC Driver 17
# Visit: https://go.microsoft.com/fwlink/?linkid=2249006

# Run the installer
# Accept license terms and install
```

### Step 3: Install Python Package

```powershell
# Already included in requirements.txt
pip install pyodbc>=5.0.0
```

### Step 4: Create Database

**Option A: Using SQL Server Management Studio (SSMS)**

1. Open SSMS
2. Connect to your SQL Server instance
3. Open the file: `database_setup.sql`
4. Click Execute (F5)
5. Verify success messages

**Option B: Using Azure Data Studio**

1. Open Azure Data Studio
2. Connect to SQL Server
3. Open `database_setup.sql`
4. Run the script

**Option C: Command Line**

```powershell
# Using sqlcmd (comes with SQL Server)
sqlcmd -S localhost\SQLEXPRESS -i database_setup.sql
```

---

## ⚙️ Configuration

### Step 1: Configure in Streamlit App

1. Run the Streamlit app:
   ```powershell
   streamlit run app.py
   ```

2. Login to the application

3. Navigate to: **🗄️ Database Config**

4. Enter connection details:
   - **Server**: `localhost\SQLEXPRESS` (or your server name)
   - **Database**: `ReconciliationDB`
   - **Authentication**: Choose Windows or SQL Server
   
5. Click **🔌 Test Connection**

6. If successful, click **📋 Create Tables**

### Step 2: Using Streamlit Secrets (Production)

For Streamlit Cloud deployment:

1. Go to Streamlit Cloud dashboard
2. Select your app
3. Go to Settings → Secrets
4. Add:

```toml
[sql_server]
server = "your-server.database.windows.net"
database = "ReconciliationDB"
username = "your-username"
password = "your-password"
```

---

## 💻 Usage

### Saving Reconciliation Results

After completing a reconciliation in FNB workflow:

1. Review your matched/unmatched transactions
2. Scroll to bottom of results
3. Click **💾 Save Results** button
4. Results are saved to database
5. Note the Session ID for reference

### Viewing Historical Data

1. Navigate to **🗄️ Database Config**
2. Scroll to **📈 Session History**
3. Click **🔄 Refresh History**
4. View all past reconciliation sessions
5. Enter Session ID to view details

### Querying Data (SQL)

```sql
-- View all sessions
SELECT * FROM vw_SessionSummary
ORDER BY StartTime DESC;

-- View matched transactions for a session
SELECT * FROM MatchedTransactions
WHERE SessionID = 1;

-- Get match rate by workflow type
SELECT 
    WorkflowType,
    COUNT(*) AS SessionCount,
    AVG(MatchRate) AS AvgMatchRate,
    SUM(TotalMatched) AS TotalMatched,
    SUM(TotalUnmatched) AS TotalUnmatched
FROM ReconciliationSessions
WHERE Status = 'Completed'
GROUP BY WorkflowType;

-- View unmatched trends
SELECT 
    CAST(StartTime AS DATE) AS ReconciliationDate,
    SUM(TotalUnmatched) AS TotalUnmatched
FROM ReconciliationSessions
GROUP BY CAST(StartTime AS DATE)
ORDER BY ReconciliationDate DESC;
```

---

## 📊 Database Schema

### Tables

#### 1. ReconciliationSessions
Main session tracking table.

| Column | Type | Description |
|--------|------|-------------|
| SessionID | INT (PK) | Unique session identifier |
| WorkflowType | VARCHAR(50) | FNB, Bidvest, Corporate |
| Username | VARCHAR(100) | User who performed reconciliation |
| StartTime | DATETIME | When reconciliation started |
| EndTime | DATETIME | When reconciliation completed |
| Status | VARCHAR(20) | In Progress/Completed/Failed |
| TotalMatched | INT | Number of matched transactions |
| TotalUnmatched | INT | Number of unmatched transactions |
| MatchRate | DECIMAL(5,2) | Match percentage |

#### 2. MatchedTransactions
Stores all matched transaction pairs.

| Column | Type | Description |
|--------|------|-------------|
| TransactionID | INT (PK) | Unique transaction ID |
| SessionID | INT (FK) | Links to session |
| MatchType | VARCHAR(50) | Perfect/Fuzzy/Amount/Split |
| LedgerDate | DATE | Date from ledger |
| LedgerReference | VARCHAR(255) | Ledger reference number |
| LedgerDebit/Credit | DECIMAL(18,2) | Ledger amounts |
| LedgerDescription | VARCHAR(500) | Ledger description |
| StatementDate | DATE | Date from statement |
| StatementReference | VARCHAR(255) | Statement reference |
| StatementAmount | DECIMAL(18,2) | Statement amount |
| StatementDescription | VARCHAR(500) | Statement description |
| MatchScore | DECIMAL(5,2) | Match confidence score |
| Currency | VARCHAR(10) | Currency code (ZAR, USD, etc.) |

#### 3. SplitTransactions
Tracks split transaction groups.

#### 4. SplitComponents
Individual components of split transactions.

#### 5. UnmatchedTransactions
All unmatched items from ledger and statement.

#### 6. ForeignCredits
Special tracking for foreign currency credits.

### Views

#### vw_SessionSummary
Complete session overview with counts and duration.

#### vw_MatchTypeDistribution
Breakdown of matches by type per session.

---

## 🔧 Troubleshooting

### Connection Issues

**Error: "Login failed for user"**
```powershell
# Solution 1: Enable SQL Server Authentication
# 1. Open SSMS
# 2. Right-click server → Properties
# 3. Security → Enable "SQL Server and Windows Authentication"
# 4. Restart SQL Server service

# Solution 2: Use Windows Authentication instead
# In app: Select "Windows Authentication"
```

**Error: "Cannot open database ReconciliationDB"**
```sql
-- Database doesn't exist - run setup script
-- Open SSMS and execute: database_setup.sql
```

**Error: "Driver not found"**
```powershell
# Install ODBC Driver 17
# Download from: https://go.microsoft.com/fwlink/?linkid=2249006

# Verify installation:
Get-OdbcDriver -Name "*SQL Server*"
```

### Permission Issues

**Error: "CREATE TABLE permission denied"**
```sql
-- Grant permissions to user
USE ReconciliationDB;
GRANT CREATE TABLE TO [YourUsername];
GO
```

### Streamlit Cloud Issues

**Error: "pyodbc.Error: ('01000', ...)"**
```
Note: Streamlit Cloud doesn't support SQL Server connections directly
Use Azure SQL Database instead with connection string in secrets
```

### Performance Issues

**Slow queries on large datasets**
```sql
-- Ensure indexes are created
-- Run in SSMS:
EXEC sp_helpindex 'MatchedTransactions';
EXEC sp_helpindex 'ReconciliationSessions';

-- If missing, recreate from setup script
```

---

## 🎓 Best Practices

1. **Regular Backups**
   ```sql
   -- Backup database weekly
   BACKUP DATABASE ReconciliationDB
   TO DISK = 'C:\Backup\ReconciliationDB.bak';
   ```

2. **Archive Old Data**
   ```sql
   -- Archive sessions older than 1 year
   DELETE FROM ReconciliationSessions
   WHERE StartTime < DATEADD(YEAR, -1, GETDATE());
   ```

3. **Monitor Database Size**
   ```sql
   -- Check database size
   EXEC sp_spaceused;
   ```

4. **Use Connection Pooling**
   - Close connections after use
   - Implement retry logic
   - Handle timeouts gracefully

---

## 📞 Support

For issues:
1. Check the error logs in Streamlit app
2. Verify SQL Server is running: `services.msc` → SQL Server
3. Test connection with SSMS first
4. Check firewall rules for port 1433

---

## 🎉 Next Steps

After setup:
1. ✅ Run a test reconciliation
2. ✅ Save results to database
3. ✅ View session history
4. ✅ Create custom reports
5. ✅ Integrate with other workflows

---

**Happy Reconciling! 🚀**
