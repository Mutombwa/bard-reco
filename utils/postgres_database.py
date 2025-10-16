"""
PostgreSQL/Supabase Database Module for Reconciliation App
===========================================================
Cloud-compatible database that works on Streamlit Cloud
"""

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None

import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import streamlit as st


class PostgreSQLDatabase:
    """PostgreSQL database handler for reconciliation transactions"""
    
    def __init__(self, connection_string: str = None):
        """
        Initialize database connection
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string or self._get_default_connection()
        self.conn = None
        
    def _get_default_connection(self) -> str:
        """Get default connection string from Streamlit secrets"""
        try:
            # For Streamlit Cloud secrets
            db_config = st.secrets.get("postgres", {})
            host = db_config.get("host", "localhost")
            port = db_config.get("port", "5432")
            database = db_config.get("database", "reconciliation_db")
            user = db_config.get("user", "postgres")
            password = db_config.get("password", "")
            
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        except:
            return "postgresql://postgres:password@localhost:5432/reconciliation_db"
    
    def connect(self) -> bool:
        """Establish database connection"""
        if not PSYCOPG2_AVAILABLE:
            st.error("❌ psycopg2 is not available. Please install: pip install psycopg2-binary")
            return False
        
        try:
            self.conn = psycopg2.connect(self.connection_string)
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
                CREATE TABLE IF NOT EXISTS reconciliation_sessions (
                    session_id SERIAL PRIMARY KEY,
                    workflow_type VARCHAR(50) NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status VARCHAR(20) NOT NULL DEFAULT 'In Progress',
                    total_matched INTEGER DEFAULT 0,
                    total_unmatched INTEGER DEFAULT 0,
                    match_rate DECIMAL(5,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT chk_status CHECK (status IN ('In Progress', 'Completed', 'Failed'))
                )
            """)
            
            # Matched Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matched_transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES reconciliation_sessions(session_id) ON DELETE CASCADE,
                    match_type VARCHAR(50) NOT NULL,
                    ledger_date DATE,
                    ledger_reference VARCHAR(255),
                    ledger_debit DECIMAL(18,2),
                    ledger_credit DECIMAL(18,2),
                    ledger_description TEXT,
                    statement_date DATE,
                    statement_reference VARCHAR(255),
                    statement_amount DECIMAL(18,2),
                    statement_description TEXT,
                    match_score DECIMAL(5,2),
                    currency VARCHAR(10) DEFAULT 'ZAR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Unmatched Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unmatched_transactions (
                    unmatched_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES reconciliation_sessions(session_id) ON DELETE CASCADE,
                    source VARCHAR(20) NOT NULL,
                    transaction_date DATE,
                    reference VARCHAR(255),
                    amount DECIMAL(18,2),
                    description TEXT,
                    currency VARCHAR(10) DEFAULT 'ZAR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT chk_source CHECK (source IN ('Ledger', 'Statement'))
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_username ON reconciliation_sessions(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_workflow ON reconciliation_sessions(workflow_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matched_session ON matched_transactions(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unmatched_session ON unmatched_transactions(session_id)")
            
            self.conn.commit()
            st.success("✅ Database tables created successfully!")
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
                INSERT INTO reconciliation_sessions (workflow_type, username, start_time, status)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 'In Progress')
                RETURNING session_id
            """, (workflow_type, username))
            
            session_id = cursor.fetchone()[0]
            self.conn.commit()
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
                    INSERT INTO matched_transactions (
                        session_id, match_type, 
                        ledger_date, ledger_reference, ledger_debit, ledger_credit, ledger_description,
                        statement_date, statement_reference, statement_amount, statement_description,
                        match_score, currency
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    row.get('Match_Type', 'Unknown'),
                    row.get('Ledger_Date'),
                    str(row.get('Ledger_Reference', ''))[:255],
                    row.get('Ledger_Debit', 0),
                    row.get('Ledger_Credit', 0),
                    str(row.get('Ledger_Description', '')),
                    row.get('Statement_Date'),
                    str(row.get('Statement_Reference', ''))[:255],
                    row.get('Statement_Amount', 0),
                    str(row.get('Statement_Description', '')),
                    row.get('Match_Score', 0),
                    row.get('Currency', 'ZAR')
                ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Error saving matched transactions: {str(e)}")
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
                        INSERT INTO unmatched_transactions (
                            session_id, source, transaction_date, reference, amount, description, currency
                        )
                        VALUES (%s, 'Ledger', %s, %s, %s, %s, %s)
                    """, (
                        session_id,
                        row.get('Date'),
                        str(row.get('Reference', ''))[:255],
                        row.get('Debit', 0) or row.get('Credit', 0),
                        str(row.get('Description', '')),
                        row.get('Currency', 'ZAR')
                    ))
            
            # Save unmatched statement
            if not unmatched_statement.empty:
                for _, row in unmatched_statement.iterrows():
                    cursor.execute("""
                        INSERT INTO unmatched_transactions (
                            session_id, source, transaction_date, reference, amount, description, currency
                        )
                        VALUES (%s, 'Statement', %s, %s, %s, %s, %s)
                    """, (
                        session_id,
                        row.get('Date'),
                        str(row.get('Reference', ''))[:255],
                        row.get('Amount', 0),
                        str(row.get('Description', '')),
                        row.get('Currency', 'ZAR')
                    ))
            
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
                UPDATE reconciliation_sessions
                SET end_time = CURRENT_TIMESTAMP,
                    status = 'Completed',
                    total_matched = %s,
                    total_unmatched = %s,
                    match_rate = %s
                WHERE session_id = %s
            """, (total_matched, total_unmatched, match_rate, session_id))
            
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
                    session_id,
                    workflow_type,
                    username,
                    start_time,
                    end_time,
                    status,
                    total_matched,
                    total_unmatched,
                    match_rate
                FROM reconciliation_sessions
            """
            
            if username:
                query += " WHERE username = %s"
                query += " ORDER BY start_time DESC LIMIT %s"
                return pd.read_sql(query, self.conn, params=(username, limit))
            else:
                query += " ORDER BY start_time DESC LIMIT %s"
                return pd.read_sql(query, self.conn, params=(limit,))
                
        except Exception as e:
            st.error(f"Error fetching session history: {str(e)}")
            return pd.DataFrame()
