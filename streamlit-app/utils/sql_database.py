"""
SQL Server Database Module for Reconciliation App
=================================================
Handles database operations for storing reconciliation transactions and results
"""

import pyodbc
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import streamlit as st


class ReconciliationDatabase:
    """SQL Server database handler for reconciliation transactions"""
    
    def __init__(self, connection_string: str = None):
        """
        Initialize database connection
        
        Args:
            connection_string: SQL Server connection string
        """
        self.connection_string = connection_string or self._get_default_connection()
        self.conn = None
        
    def _get_default_connection(self) -> str:
        """Get default connection string from environment or config"""
        # Check if connection details are in session state or environment
        server = st.secrets.get("sql_server", {}).get("server", "localhost")
        database = st.secrets.get("sql_server", {}).get("database", "ReconciliationDB")
        username = st.secrets.get("sql_server", {}).get("username", "")
        password = st.secrets.get("sql_server", {}).get("password", "")
        
        if username and password:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        else:
            # Windows Authentication
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            return True
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.conn:
            if not self.connect():
                return False
        
        cursor = self.conn.cursor()
        
        try:
            # Reconciliation Sessions table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ReconciliationSessions' AND xtype='U')
                CREATE TABLE ReconciliationSessions (
                    SessionID INT IDENTITY(1,1) PRIMARY KEY,
                    WorkflowType VARCHAR(50) NOT NULL,
                    Username VARCHAR(100) NOT NULL,
                    StartTime DATETIME NOT NULL,
                    EndTime DATETIME,
                    Status VARCHAR(20) NOT NULL DEFAULT 'In Progress',
                    TotalMatched INT DEFAULT 0,
                    TotalUnmatched INT DEFAULT 0,
                    MatchRate DECIMAL(5,2) DEFAULT 0,
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    CONSTRAINT CHK_Status CHECK (Status IN ('In Progress', 'Completed', 'Failed'))
                )
            """)
            
            # Matched Transactions table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='MatchedTransactions' AND xtype='U')
                CREATE TABLE MatchedTransactions (
                    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
                    SessionID INT NOT NULL,
                    MatchType VARCHAR(50) NOT NULL,
                    LedgerDate DATE,
                    LedgerReference VARCHAR(255),
                    LedgerDebit DECIMAL(18,2),
                    LedgerCredit DECIMAL(18,2),
                    LedgerDescription VARCHAR(500),
                    StatementDate DATE,
                    StatementReference VARCHAR(255),
                    StatementAmount DECIMAL(18,2),
                    StatementDescription VARCHAR(500),
                    MatchScore DECIMAL(5,2),
                    Currency VARCHAR(10),
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (SessionID) REFERENCES ReconciliationSessions(SessionID)
                )
            """)
            
            # Split Transactions table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SplitTransactions' AND xtype='U')
                CREATE TABLE SplitTransactions (
                    SplitID INT IDENTITY(1,1) PRIMARY KEY,
                    SessionID INT NOT NULL,
                    SplitType VARCHAR(50) NOT NULL,
                    TotalAmount DECIMAL(18,2),
                    ComponentCount INT,
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (SessionID) REFERENCES ReconciliationSessions(SessionID)
                )
            """)
            
            # Split Transaction Components table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SplitComponents' AND xtype='U')
                CREATE TABLE SplitComponents (
                    ComponentID INT IDENTITY(1,1) PRIMARY KEY,
                    SplitID INT NOT NULL,
                    TransactionSource VARCHAR(20) NOT NULL,
                    TransactionDate DATE,
                    Reference VARCHAR(255),
                    Amount DECIMAL(18,2),
                    Description VARCHAR(500),
                    FOREIGN KEY (SplitID) REFERENCES SplitTransactions(SplitID),
                    CONSTRAINT CHK_Source CHECK (TransactionSource IN ('Ledger', 'Statement'))
                )
            """)
            
            # Unmatched Transactions table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='UnmatchedTransactions' AND xtype='U')
                CREATE TABLE UnmatchedTransactions (
                    UnmatchedID INT IDENTITY(1,1) PRIMARY KEY,
                    SessionID INT NOT NULL,
                    Source VARCHAR(20) NOT NULL,
                    TransactionDate DATE,
                    Reference VARCHAR(255),
                    Amount DECIMAL(18,2),
                    Description VARCHAR(500),
                    Currency VARCHAR(10),
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (SessionID) REFERENCES ReconciliationSessions(SessionID),
                    CONSTRAINT CHK_UnmatchedSource CHECK (Source IN ('Ledger', 'Statement'))
                )
            """)
            
            # Foreign Credits table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ForeignCredits' AND xtype='U')
                CREATE TABLE ForeignCredits (
                    ForeignCreditID INT IDENTITY(1,1) PRIMARY KEY,
                    SessionID INT NOT NULL,
                    LedgerDate DATE,
                    LedgerReference VARCHAR(255),
                    LedgerAmount DECIMAL(18,2),
                    StatementDate DATE,
                    StatementReference VARCHAR(255),
                    StatementAmount DECIMAL(18,2),
                    Currency VARCHAR(10),
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (SessionID) REFERENCES ReconciliationSessions(SessionID)
                )
            """)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error creating tables: {str(e)}")
            return False
        finally:
            cursor.close()
    
    def create_session(self, workflow_type: str, username: str) -> Optional[int]:
        """Create a new reconciliation session"""
        if not self.conn:
            if not self.connect():
                return None
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ReconciliationSessions (WorkflowType, Username, StartTime, Status)
                VALUES (?, ?, GETDATE(), 'In Progress')
            """, workflow_type, username)
            
            self.conn.commit()
            
            # Get the inserted session ID
            cursor.execute("SELECT @@IDENTITY")
            session_id = cursor.fetchone()[0]
            return int(session_id)
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error creating session: {str(e)}")
            return None
        finally:
            cursor.close()
    
    def save_matched_transactions(self, session_id: int, matched_df: pd.DataFrame) -> bool:
        """Save matched transactions to database"""
        if not self.conn:
            if not self.connect():
                return False
        
        cursor = self.conn.cursor()
        try:
            for _, row in matched_df.iterrows():
                cursor.execute("""
                    INSERT INTO MatchedTransactions (
                        SessionID, MatchType, 
                        LedgerDate, LedgerReference, LedgerDebit, LedgerCredit, LedgerDescription,
                        StatementDate, StatementReference, StatementAmount, StatementDescription,
                        MatchScore, Currency
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, 
                    session_id,
                    row.get('Match_Type', 'Unknown'),
                    row.get('Ledger_Date'),
                    row.get('Ledger_Reference', '')[:255],
                    row.get('Ledger_Debit', 0),
                    row.get('Ledger_Credit', 0),
                    row.get('Ledger_Description', '')[:500],
                    row.get('Statement_Date'),
                    row.get('Statement_Reference', '')[:255],
                    row.get('Statement_Amount', 0),
                    row.get('Statement_Description', '')[:500],
                    row.get('Match_Score', 0),
                    row.get('Currency', 'ZAR')
                )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error saving matched transactions: {str(e)}")
            return False
        finally:
            cursor.close()
    
    def save_split_transactions(self, session_id: int, split_matches: List[Dict]) -> bool:
        """Save split transactions to database"""
        if not self.conn:
            if not self.connect():
                return False
        
        cursor = self.conn.cursor()
        try:
            for split in split_matches:
                # Insert split transaction
                cursor.execute("""
                    INSERT INTO SplitTransactions (SessionID, SplitType, TotalAmount, ComponentCount)
                    VALUES (?, ?, ?, ?)
                """,
                    session_id,
                    split.get('split_type', 'Unknown'),
                    split.get('total_amount', 0),
                    len(split.get('ledger_indices', [])) + len(split.get('statement_indices', []))
                )
                
                # Get split ID
                cursor.execute("SELECT @@IDENTITY")
                split_id = int(cursor.fetchone()[0])
                
                # Insert components (this would need actual transaction data from dataframes)
                # You'll need to pass ledger and statement dataframes to get the actual data
                
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error saving split transactions: {str(e)}")
            return False
        finally:
            cursor.close()
    
    def save_unmatched_transactions(self, session_id: int, unmatched_ledger: pd.DataFrame, 
                                   unmatched_statement: pd.DataFrame) -> bool:
        """Save unmatched transactions to database"""
        if not self.conn:
            if not self.connect():
                return False
        
        cursor = self.conn.cursor()
        try:
            # Save unmatched ledger
            if not unmatched_ledger.empty:
                for _, row in unmatched_ledger.iterrows():
                    cursor.execute("""
                        INSERT INTO UnmatchedTransactions (
                            SessionID, Source, TransactionDate, Reference, Amount, Description, Currency
                        )
                        VALUES (?, 'Ledger', ?, ?, ?, ?, ?)
                    """,
                        session_id,
                        row.get('Date'),
                        row.get('Reference', '')[:255],
                        row.get('Debit', 0) or row.get('Credit', 0),
                        row.get('Description', '')[:500],
                        row.get('Currency', 'ZAR')
                    )
            
            # Save unmatched statement
            if not unmatched_statement.empty:
                for _, row in unmatched_statement.iterrows():
                    cursor.execute("""
                        INSERT INTO UnmatchedTransactions (
                            SessionID, Source, TransactionDate, Reference, Amount, Description, Currency
                        )
                        VALUES (?, 'Statement', ?, ?, ?, ?, ?)
                    """,
                        session_id,
                        row.get('Date'),
                        row.get('Reference', '')[:255],
                        row.get('Amount', 0),
                        row.get('Description', '')[:500],
                        row.get('Currency', 'ZAR')
                    )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error saving unmatched transactions: {str(e)}")
            return False
        finally:
            cursor.close()
    
    def complete_session(self, session_id: int, total_matched: int, total_unmatched: int, 
                        match_rate: float) -> bool:
        """Mark session as completed with statistics"""
        if not self.conn:
            if not self.connect():
                return False
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE ReconciliationSessions
                SET EndTime = GETDATE(),
                    Status = 'Completed',
                    TotalMatched = ?,
                    TotalUnmatched = ?,
                    MatchRate = ?
                WHERE SessionID = ?
            """, total_matched, total_unmatched, match_rate, session_id)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error completing session: {str(e)}")
            return False
        finally:
            cursor.close()
    
    def get_session_history(self, username: str = None, limit: int = 50) -> pd.DataFrame:
        """Get reconciliation session history"""
        if not self.conn:
            if not self.connect():
                return pd.DataFrame()
        
        try:
            query = """
                SELECT 
                    SessionID,
                    WorkflowType,
                    Username,
                    StartTime,
                    EndTime,
                    Status,
                    TotalMatched,
                    TotalUnmatched,
                    MatchRate
                FROM ReconciliationSessions
            """
            
            if username:
                query += " WHERE Username = ?"
                query += f" ORDER BY StartTime DESC"
                if limit:
                    query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
                return pd.read_sql(query, self.conn, params=[username])
            else:
                query += " ORDER BY StartTime DESC"
                if limit:
                    query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
                return pd.read_sql(query, self.conn)
                
        except Exception as e:
            st.error(f"Error fetching session history: {str(e)}")
            return pd.DataFrame()
    
    def get_session_details(self, session_id: int) -> Dict:
        """Get detailed information about a specific session"""
        if not self.conn:
            if not self.connect():
                return {}
        
        try:
            details = {}
            
            # Get session info
            session_df = pd.read_sql("""
                SELECT * FROM ReconciliationSessions WHERE SessionID = ?
            """, self.conn, params=[session_id])
            
            if not session_df.empty:
                details['session'] = session_df.iloc[0].to_dict()
            
            # Get matched transactions
            details['matched'] = pd.read_sql("""
                SELECT * FROM MatchedTransactions WHERE SessionID = ?
            """, self.conn, params=[session_id])
            
            # Get unmatched transactions
            details['unmatched'] = pd.read_sql("""
                SELECT * FROM UnmatchedTransactions WHERE SessionID = ?
            """, self.conn, params=[session_id])
            
            # Get split transactions
            details['splits'] = pd.read_sql("""
                SELECT * FROM SplitTransactions WHERE SessionID = ?
            """, self.conn, params=[session_id])
            
            return details
            
        except Exception as e:
            st.error(f"Error fetching session details: {str(e)}")
            return {}
