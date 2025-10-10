"""
Collaborative Dashboard Database Schema
=====================================

This module provides the database schema and operations for the collaborative
reconciliation dashboard system. It extends the existing results_db.py to add
collaborative features while maintaining compatibility.

Key Features:
- User management and authentication
- Role-based access control
- Transaction collaboration workflow
- Real-time status tracking
- Audit trails and notifications
- Session management
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import uuid
from typing import Optional, Dict, List, Any


class CollaborativeDashboardDB:
    """Professional collaborative dashboard database with advanced features"""
    
    def __init__(self, db_path: str = 'collaborative_dashboard.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._create_default_admin()
    
    def _create_tables(self):
        """Create all necessary tables for the collaborative dashboard"""
        
        # Users table for authentication and profile management
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'viewer' CHECK(role IN ('admin', 'reconciler', 'approver', 'viewer')),
                department TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table for managing collaborative sessions
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_sessions (
                id TEXT PRIMARY KEY,
                session_name TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                created_by INTEGER REFERENCES users(id),
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'under_review', 'approved', 'rejected', 'archived')),
                priority TEXT DEFAULT 'normal' CHECK(priority IN ('low', 'normal', 'high', 'urgent')),
                description TEXT,
                metadata TEXT,
                total_transactions INTEGER DEFAULT 0,
                matched_transactions INTEGER DEFAULT 0,
                unmatched_transactions INTEGER DEFAULT 0,
                foreign_credits INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table for individual transaction tracking
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS collaborative_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT REFERENCES reconciliation_sessions(id),
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('matched', 'unmatched_ledger', 'unmatched_statement', 'foreign_credit', 'split_match')),
                original_data TEXT,
                processed_data TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                reference TEXT,
                ledger_reference TEXT,
                statement_reference TEXT,
                match_confidence REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'approved', 'rejected', 'needs_attention')),
                assigned_to INTEGER REFERENCES users(id),
                reviewed_by INTEGER REFERENCES users(id),
                approved_by INTEGER REFERENCES users(id),
                comments TEXT,
                flags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Comments and collaboration notes
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transaction_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER REFERENCES collaborative_transactions(id),
                session_id TEXT REFERENCES reconciliation_sessions(id),
                user_id INTEGER REFERENCES users(id),
                comment_text TEXT NOT NULL,
                comment_type TEXT DEFAULT 'note' CHECK(comment_type IN ('note', 'question', 'approval', 'rejection', 'flag')),
                is_internal BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit trail for all operations
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                session_id TEXT REFERENCES reconciliation_sessions(id),
                action_type TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notifications system
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                session_id TEXT REFERENCES reconciliation_sessions(id),
                transaction_id INTEGER REFERENCES collaborative_transactions(id),
                notification_type TEXT NOT NULL CHECK(notification_type IN ('assignment', 'approval_request', 'status_change', 'comment', 'deadline', 'system')),
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'normal' CHECK(priority IN ('low', 'normal', 'high', 'urgent')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP
            )
        ''')
        
        # User sessions for authentication
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File attachments for transactions
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transaction_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER REFERENCES collaborative_transactions(id),
                session_id TEXT REFERENCES reconciliation_sessions(id),
                user_id INTEGER REFERENCES users(id),
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Workflow templates for different reconciliation types
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS workflow_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                workflow_type TEXT NOT NULL,
                configuration TEXT,
                match_columns TEXT,
                validation_rules TEXT,
                approval_workflow TEXT,
                created_by INTEGER REFERENCES users(id),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reports and analytics
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS saved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                filters TEXT,
                configuration TEXT,
                created_by INTEGER REFERENCES users(id),
                is_shared BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System settings
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_by INTEGER REFERENCES users(id),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Dashboard configuration and preferences
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                config_key TEXT NOT NULL,
                config_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, config_key)
            )
        ''')
        
        # Create indexes for better performance
        self._create_indexes()
        self.conn.commit()
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)", 
            "CREATE INDEX IF NOT EXISTS idx_sessions_status ON reconciliation_sessions(status)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_created_by ON reconciliation_sessions(created_by)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_session ON collaborative_transactions(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_status ON collaborative_transactions(status)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type ON collaborative_transactions(transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_comments_transaction ON transaction_comments(transaction_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read)",
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
    
    def _create_default_admin(self):
        """Create default admin user if no users exist"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            admin_password = self._hash_password("admin123")
            self.conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role, department)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", "admin@company.com", admin_password, "System Administrator", "admin", "IT"))
            self.conn.commit()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "collaborative_dashboard_salt_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info if successful"""
        password_hash = self._hash_password(password)
        cursor = self.conn.execute('''
            SELECT id, username, email, full_name, role, department, is_active, last_login
            FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        user_data = cursor.fetchone()
        if user_data:
            # Update last login
            self.conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_data[0],))
            self.conn.commit()
            
            return {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'full_name': user_data[3],
                'role': user_data[4],
                'department': user_data[5],
                'is_active': user_data[6],
                'last_login': user_data[7]
            }
        return None
    
    def create_user(self, username: str, email: str, password: str, full_name: str, 
                    role: str = 'viewer', department: str = '') -> int:
        """Create a new user"""
        password_hash = self._hash_password(password)
        cursor = self.conn.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, role, department))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def get_admin_user_id(self) -> int:
        """Get the admin user ID"""
        cursor = self.conn.execute('SELECT id FROM users WHERE username = ? LIMIT 1', ('admin',))
        result = cursor.fetchone()
        return result[0] if result else 1
    
    def create_session(self, session_name: str, workflow_type: str = '', created_by = None,
                      description: str = '', priority: str = 'normal') -> str:
        """Create a new reconciliation session"""
        session_id = str(uuid.uuid4())
        
        # Get admin user ID if not provided
        if created_by is None or isinstance(created_by, str):
            created_by = self.get_admin_user_id()
        
        self.conn.execute('''
            INSERT INTO reconciliation_sessions 
            (id, session_name, workflow_type, created_by, description, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, session_name, workflow_type, created_by, description, priority))
        
        self.conn.commit()
        return session_id
    
    def add_transaction(self, session_id: str, transaction_data: Dict) -> int:
        """Add a transaction to a session (simplified interface) - handles both old and new formats"""
        # Handle both 'type' (new) and 'transaction_type' (old) keys
        transaction_type = transaction_data.get('type') or transaction_data.get('transaction_type', 'matched')
        
        # Ensure transaction type is valid (default to 'matched' if not provided)
        if not transaction_type or transaction_type not in ['matched', 'unmatched_ledger', 'unmatched_statement', 'foreign_credit', 'split_match']:
            transaction_type = 'matched'
        
        # Get amount from various possible keys
        amount = float(transaction_data.get('amount', 0))
        
        # Get reference from various possible keys
        reference = transaction_data.get('reference', '') or transaction_data.get('ledger_reference', '') or transaction_data.get('statement_reference', '')
        
        # Build metadata from various sources
        metadata = transaction_data.get('metadata', {})
        if not metadata:
            # If no metadata provided, build it from transaction_data
            metadata = {
                'date': transaction_data.get('date', ''),
                'description': transaction_data.get('description', ''),
                'workflow_type': transaction_data.get('workflow_type', ''),
                'confidence': transaction_data.get('confidence', 0),
                'status': transaction_data.get('status', 'pending')
            }
        
        # Get confidence score
        confidence = float(metadata.get('confidence_score', 0) or metadata.get('confidence', 0) or transaction_data.get('confidence', 0))
        
        cursor = self.conn.execute('''
            INSERT INTO collaborative_transactions 
            (session_id, transaction_type, original_data, amount, reference, 
             ledger_reference, statement_reference, match_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, 
            transaction_type, 
            json.dumps(metadata), 
            amount, 
            reference,
            reference,
            reference,
            confidence
        ))
        
        transaction_id = cursor.lastrowid or 0

        # Update session transaction counts
        self._update_session_counts(session_id)

        self.conn.commit()
        return transaction_id
    
    def _update_session_counts(self, session_id: str):
        """Update transaction counts for a session"""
        # Count transactions by type
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN transaction_type = 'matched' THEN 1 ELSE 0 END) as matched,
                SUM(CASE WHEN transaction_type IN ('unmatched_ledger', 'unmatched_statement') THEN 1 ELSE 0 END) as unmatched
            FROM collaborative_transactions
            WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if row:
            self.conn.execute('''
                UPDATE reconciliation_sessions
                SET total_transactions = ?,
                    matched_transactions = ?,
                    unmatched_transactions = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row[0], row[1], row[2], session_id))
    
    def add_transaction_old(self, session_id: str, transaction_type: str, original_data: Dict,
                       amount: float = 0.0, reference: str = '', **kwargs) -> int:
        """Add a transaction to a session"""
        cursor = self.conn.execute('''
            INSERT INTO collaborative_transactions 
            (session_id, transaction_type, original_data, amount, reference, 
             ledger_reference, statement_reference, match_confidence, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, transaction_type, json.dumps(original_data), amount, reference,
            kwargs.get('ledger_reference', ''), kwargs.get('statement_reference', ''),
            kwargs.get('match_confidence', 0.0), kwargs.get('assigned_to')
        ))

        self.conn.commit()
        return cursor.lastrowid or 0

    def get_sessions(self, user_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        """Get reconciliation sessions with optional filtering"""
        sql = '''
            SELECT s.id, s.session_name, s.workflow_type, s.status, s.priority, 
                   s.total_transactions, s.matched_transactions, s.unmatched_transactions,
                   s.created_at, s.updated_at, u.full_name as created_by_name
            FROM reconciliation_sessions s
            LEFT JOIN users u ON s.created_by = u.id
        '''
        params = []
        
        conditions = []
        if user_id:
            conditions.append("s.created_by = ?")
            params.append(user_id)
        if status:
            conditions.append("s.status = ?")
            params.append(status)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY s.updated_at DESC"
        
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_session_transactions(self, session_id: str, transaction_type: Optional[str] = None) -> List[Dict]:
        """Get transactions for a specific session"""
        sql = '''
            SELECT t.*, u1.full_name as assigned_to_name, u2.full_name as reviewed_by_name,
                   u3.full_name as approved_by_name
            FROM collaborative_transactions t
            LEFT JOIN users u1 ON t.assigned_to = u1.id
            LEFT JOIN users u2 ON t.reviewed_by = u2.id  
            LEFT JOIN users u3 ON t.approved_by = u3.id
            WHERE t.session_id = ?
        '''
        params = [session_id]
        
        if transaction_type:
            sql += " AND t.transaction_type = ?"
            params.append(transaction_type)
            
        sql += " ORDER BY t.created_at DESC"
        
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_transaction_status(self, transaction_id: int, status: str, user_id: int, 
                                 comments: str = '') -> bool:
        """Update transaction status with audit trail"""
        # Get old values for audit
        cursor = self.conn.execute("SELECT status, comments FROM collaborative_transactions WHERE id = ?", 
                                 (transaction_id,))
        old_data = cursor.fetchone()
        
        if old_data:
            # Update transaction
            self.conn.execute('''
                UPDATE collaborative_transactions 
                SET status = ?, comments = ?, updated_at = CURRENT_TIMESTAMP,
                    reviewed_by = CASE WHEN ? IN ('reviewed', 'approved', 'rejected') THEN ? ELSE reviewed_by END
                WHERE id = ?
            ''', (status, comments, status, user_id, transaction_id))
            
            # Log audit trail
            self._log_audit(user_id, None, 'transaction_status_update', 'collaborative_transactions',
                           str(transaction_id), 
                           {'status': old_data[0], 'comments': old_data[1]},
                           {'status': status, 'comments': comments})
            
            self.conn.commit()
            return True
        return False
    
    def get_recent_transactions(self, limit: int = 15) -> List[Dict]:
        """Get recent transactions across all sessions"""
        sql = '''
            SELECT t.*, u1.full_name as assigned_to_name, u2.full_name as reviewed_by_name,
                   u3.full_name as approved_by_name, s.workflow_type
            FROM collaborative_transactions t
            LEFT JOIN users u1 ON t.assigned_to = u1.id
            LEFT JOIN users u2 ON t.reviewed_by = u2.id
            LEFT JOIN users u3 ON t.approved_by = u3.id
            LEFT JOIN reconciliation_sessions s ON t.session_id = s.id
            ORDER BY t.created_at DESC
            LIMIT ?
        '''
        cursor = self.conn.execute(sql, (limit,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its related transactions"""
        try:
            # Delete all transactions in this session first (due to foreign key)
            self.conn.execute('DELETE FROM collaborative_transactions WHERE session_id = ?', (session_id,))
            
            # Delete the session
            self.conn.execute('DELETE FROM reconciliation_sessions WHERE id = ?', (session_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR] Failed to delete session {session_id}: {e}")
            return False
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a single transaction"""
        try:
            self.conn.execute('DELETE FROM collaborative_transactions WHERE id = ?', (transaction_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR] Failed to delete transaction {transaction_id}: {e}")
            return False
    
    def add_comment(self, transaction_id: int, session_id: str, user_id: int, 
                   comment_text: str, comment_type: str = 'note') -> int:
        """Add a comment to a transaction"""
        cursor = self.conn.execute('''
            INSERT INTO transaction_comments 
            (transaction_id, session_id, user_id, comment_text, comment_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (transaction_id, session_id, user_id, comment_text, comment_type))

        self.conn.commit()
        return cursor.lastrowid or 0
    
    def create_notification(self, user_id: int, notification_type: str, title: str, 
                          message: str, **kwargs) -> int:
        """Create a notification for a user"""
        cursor = self.conn.execute('''
            INSERT INTO notifications 
            (user_id, session_id, transaction_id, notification_type, title, message, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, kwargs.get('session_id'), kwargs.get('transaction_id'),
              notification_type, title, message, kwargs.get('priority', 'normal')))

        self.conn.commit()
        return cursor.lastrowid or 0
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Get notifications for a user"""
        sql = '''
            SELECT id, session_id, transaction_id, notification_type, title, message, 
                   is_read, priority, created_at
            FROM notifications
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if unread_only:
            sql += " AND is_read = 0"
            
        sql += " ORDER BY created_at DESC"
        
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _log_audit(self, user_id: int, session_id: Optional[str], action_type: str,
                   table_name: str, record_id: str, old_values: Dict, new_values: Dict):
        """Log an audit trail entry"""
        self.conn.execute('''
            INSERT INTO audit_log 
            (user_id, session_id, action_type, table_name, record_id, old_values, new_values)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, action_type, table_name, record_id,
              json.dumps(old_values), json.dumps(new_values)))
    
    def get_dashboard_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get dashboard statistics"""
        stats = {}
        
        # Session statistics
        cursor = self.conn.execute('''
            SELECT status, COUNT(*) as count 
            FROM reconciliation_sessions 
            {} GROUP BY status
        '''.format("WHERE created_by = ?" if user_id else ""), 
        ([user_id] if user_id else []))
        
        stats['sessions_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Transaction statistics
        cursor = self.conn.execute('''
            SELECT transaction_type, COUNT(*) as count
            FROM collaborative_transactions t
            JOIN reconciliation_sessions s ON t.session_id = s.id
            {} GROUP BY transaction_type
        '''.format("WHERE s.created_by = ?" if user_id else ""),
        ([user_id] if user_id else []))
        
        stats['transactions_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats
    
    def get_transaction_comments(self, transaction_id: int) -> List[Dict]:
        """Get all comments for a transaction"""
        cursor = self.conn.execute('''
            SELECT c.*, u.full_name, u.role
            FROM transaction_comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.transaction_id = ?
            ORDER BY c.created_at ASC
        ''', (transaction_id,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        cursor = self.conn.execute('''
            UPDATE notifications 
            SET is_read = 1, read_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (notification_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_users(self, active_only: bool = True) -> List[Dict]:
        """Get all users"""
        sql = "SELECT id, username, email, full_name, role, department, is_active, last_login FROM users"
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY full_name"
        
        cursor = self.conn.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_user_role(self, user_id: int, new_role: str, updated_by: int) -> bool:
        """Update user role with audit trail"""
        cursor = self.conn.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        old_role = cursor.fetchone()
        
        if old_role:
            self.conn.execute("UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                            (new_role, user_id))
            
            self._log_audit(updated_by, None, 'user_role_update', 'users', str(user_id),
                           {'role': old_role[0]}, {'role': new_role})
            
            self.conn.commit()
            return True
        return False
    
    def post_reconciliation_results(self, session_id: str, results: Dict, metadata: Dict) -> bool:
        """Post reconciliation results from the main app to collaborative dashboard"""
        try:
            # Update session totals
            total_transactions = sum(len(transactions) for transactions in results.values())
            matched_transactions = len(results.get('100% MATCH', [])) + len(results.get('85% FUZZY', [])) + len(results.get('60% FUZZY', []))
            unmatched_transactions = len(results.get('UNMATCHED', []))
            foreign_credits = len(results.get('FOREIGN CREDITS', []))
            
            self.conn.execute('''
                UPDATE reconciliation_sessions 
                SET total_transactions = ?, matched_transactions = ?, 
                    unmatched_transactions = ?, foreign_credits = ?, 
                    updated_at = CURRENT_TIMESTAMP, status = 'active'
                WHERE id = ?
            ''', (total_transactions, matched_transactions, unmatched_transactions, foreign_credits, session_id))
            
            # Clear existing transactions for this session
            self.conn.execute("DELETE FROM collaborative_transactions WHERE session_id = ?", (session_id,))
            
            # Add all transactions
            for result_type, transactions in results.items():
                for transaction_data in transactions:
                    if isinstance(transaction_data, tuple) and len(transaction_data) >= 2:
                        # Matched transaction (statement, cashbook)
                        statement_data, cashbook_data = transaction_data[0], transaction_data[1]
                        
                        # Extract amount and references
                        amount = 0.0
                        reference = ""
                        ledger_ref = ""
                        statement_ref = ""
                        
                        if statement_data is not None:
                            try:
                                # Try multiple column names for amount
                                amount_cols = ['Amount', 'AMOUNT', 'amount', 'Credit Amount', 'Debit Amount']
                                for col in amount_cols:
                                    if hasattr(statement_data, col) and pd.notna(getattr(statement_data, col, None)):
                                        amount_str = str(getattr(statement_data, col)).replace(',', '').replace('(', '-').replace(')', '')
                                        amount = float(amount_str)
                                        break
                                
                                # Try multiple column names for reference
                                ref_cols = ['Reference', 'REFERENCE', 'reference', 'Description', 'DESCRIPTION']
                                for col in ref_cols:
                                    if hasattr(statement_data, col) and pd.notna(getattr(statement_data, col, None)):
                                        statement_ref = str(getattr(statement_data, col))
                                        reference = statement_ref
                                        break
                            except:
                                pass
                        
                        if cashbook_data is not None:
                            try:
                                ref_cols = ['Reference', 'REFERENCE', 'reference', 'Description', 'DESCRIPTION']
                                for col in ref_cols:
                                    if hasattr(cashbook_data, col) and pd.notna(getattr(cashbook_data, col, None)):
                                        ledger_ref = str(getattr(cashbook_data, col))
                                        if not reference:
                                            reference = ledger_ref
                                        break
                            except:
                                pass
                        
                        # Determine transaction type and confidence
                        transaction_type = 'matched' if result_type in ['100% MATCH', '85% FUZZY', '60% FUZZY'] else 'unmatched_ledger'
                        match_confidence = 1.0 if result_type == '100% MATCH' else (0.85 if result_type == '85% FUZZY' else 0.60)
                        
                        self.add_transaction(
                            session_id=session_id,
                            transaction_data={
                                'type': transaction_type,
                                'metadata': {
                                    'statement_data': statement_data.to_dict() if hasattr(statement_data, 'to_dict') else (dict(statement_data) if isinstance(statement_data, dict) else str(statement_data)),
                                    'cashbook_data': cashbook_data.to_dict() if hasattr(cashbook_data, 'to_dict') else (dict(cashbook_data) if isinstance(cashbook_data, dict) else str(cashbook_data)),
                                    'match_type': result_type
                                },
                                'amount': amount,
                                'reference': reference,
                                'ledger_reference': ledger_ref,
                                'statement_reference': statement_ref,
                                'confidence': match_confidence
                            }
                        )
                    else:
                        # Single unmatched transaction
                        transaction_type = 'unmatched_statement' if result_type == 'UNMATCHED' else 'foreign_credit'

                        amount = 0.0
                        reference = ""

                        try:
                            if hasattr(transaction_data, 'to_dict'):
                                data_dict = transaction_data.to_dict()
                            else:
                                data_dict = dict(transaction_data) if isinstance(transaction_data, dict) else str(transaction_data)

                            if isinstance(data_dict, dict):
                                # Try to extract amount and reference
                                amount_cols = ['Amount', 'AMOUNT', 'amount', 'Credit Amount', 'Debit Amount']
                                for col in amount_cols:
                                    if col in data_dict and pd.notna(data_dict[col]):
                                        amount_str = str(data_dict[col]).replace(',', '').replace('(', '-').replace(')', '')
                                        amount = float(amount_str)
                                        break

                                ref_cols = ['Reference', 'REFERENCE', 'reference', 'Description', 'DESCRIPTION']
                                for col in ref_cols:
                                    if col in data_dict and pd.notna(data_dict[col]):
                                        reference = str(data_dict[col])
                                        break
                        except Exception as e:
                            data_dict = {'error': str(e), 'raw_data': str(transaction_data)}
                        
                        self.add_transaction(
                            session_id=session_id,
                            transaction_data={
                                'type': transaction_type,
                                'metadata': {'data': data_dict, 'match_type': result_type},
                                'amount': amount,
                                'reference': reference
                            }
                        )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error posting reconciliation results: {e}")
            self.conn.rollback()
            return False

    def get_all_transactions(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all transactions from the database"""
        sql = '''
            SELECT id, session_id, transaction_type, amount, reference,
                   ledger_reference, statement_reference, match_confidence,
                   status, comments, created_at, updated_at
            FROM collaborative_transactions
            ORDER BY created_at DESC
        '''
        if limit:
            sql += f' LIMIT {limit}'

        cursor = self.conn.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def post_data(self, data: Dict) -> bool:
        """Post data to the database (stub)"""
        # This would implement posting arbitrary data
        return True

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()