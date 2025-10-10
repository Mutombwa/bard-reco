"""
Outstanding Transactions Manager
=================================
Professional system with batch tracking, historical archiving, and smart copy functionality.

FEATURES:
1. Batch Identifier System - Each reconciliation batch has unique ID and account identifier
2. Historical Archiving - When transactions are copied for new recon, they move to history
3. Smart Copy - Copies with/without headers based on whether new data is imported
4. Account-based Filtering - View outstanding transactions by specific account/batch
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import pandas as pd
import sqlite3
from datetime import datetime
import os
import json
import uuid


class OutstandingTransactionsDB:
    """Enhanced database manager with batch tracking and historical archiving"""
    
    def __init__(self, db_path="outstanding_transactions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database tables with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist and need migration
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ledger_outstanding'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check if old schema (without batch_id)
            cursor.execute("PRAGMA table_info(ledger_outstanding)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'batch_id' not in columns:
                print("🔄 Migrating old outstanding transactions database...")
                self.migrate_old_database(conn, cursor)
                print("✅ Migration complete!")
        
        # Enhanced ledger outstanding transactions table with batch tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledger_outstanding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL DEFAULT 'MIGRATED',
                account_identifier TEXT NOT NULL DEFAULT 'Default Account',
                recon_date TEXT NOT NULL,
                recon_name TEXT,
                transaction_date TEXT,
                reference TEXT,
                description TEXT,
                debit REAL,
                credit REAL,
                amount REAL,
                original_data TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced statement outstanding transactions table with batch tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statement_outstanding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL DEFAULT 'MIGRATED',
                account_identifier TEXT NOT NULL DEFAULT 'Default Account',
                recon_date TEXT NOT NULL,
                recon_name TEXT,
                transaction_date TEXT,
                reference TEXT,
                description TEXT,
                amount REAL,
                original_data TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Historical archive for ledger transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledger_outstanding_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER,
                batch_id TEXT NOT NULL,
                account_identifier TEXT NOT NULL,
                recon_date TEXT NOT NULL,
                recon_name TEXT,
                transaction_date TEXT,
                reference TEXT,
                description TEXT,
                debit REAL,
                credit REAL,
                amount REAL,
                original_data TEXT,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived_reason TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Historical archive for statement transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statement_outstanding_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER,
                batch_id TEXT NOT NULL,
                account_identifier TEXT NOT NULL,
                recon_date TEXT NOT NULL,
                recon_name TEXT,
                transaction_date TEXT,
                reference TEXT,
                description TEXT,
                amount REAL,
                original_data TEXT,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived_reason TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Batch metadata table to track reconciliation batches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_batches (
                batch_id TEXT PRIMARY KEY,
                account_identifier TEXT NOT NULL,
                recon_date TEXT NOT NULL,
                recon_name TEXT,
                ledger_count INTEGER DEFAULT 0,
                statement_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def migrate_old_database(self, conn, cursor):
        """Migrate old database schema to new schema with batch tracking"""
        try:
            # Create backup batch for old transactions
            default_batch_id = 'OLD_' + str(uuid.uuid4())[:8]
            default_account = 'Migrated Transactions'
            
            print(f"🔄 Starting migration to batch: {default_batch_id}")
            
            # Add new columns to ledger_outstanding (no NOT NULL, no DEFAULT with params)
            try:
                cursor.execute('ALTER TABLE ledger_outstanding ADD COLUMN batch_id TEXT')
                print("  ✓ Added batch_id column to ledger")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ ledger batch_id: {e}")
            
            try:
                cursor.execute('ALTER TABLE ledger_outstanding ADD COLUMN account_identifier TEXT')
                print("  ✓ Added account_identifier column to ledger")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ ledger account_identifier: {e}")
            
            try:
                cursor.execute('ALTER TABLE ledger_outstanding ADD COLUMN is_active INTEGER DEFAULT 1')
                print("  ✓ Added is_active column to ledger")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ ledger is_active: {e}")
            
            try:
                cursor.execute('ALTER TABLE ledger_outstanding ADD COLUMN updated_at TIMESTAMP')
                print("  ✓ Added updated_at column to ledger")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ ledger updated_at: {e}")
            
            # Add new columns to statement_outstanding
            try:
                cursor.execute('ALTER TABLE statement_outstanding ADD COLUMN batch_id TEXT')
                print("  ✓ Added batch_id column to statement")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ statement batch_id: {e}")
            
            try:
                cursor.execute('ALTER TABLE statement_outstanding ADD COLUMN account_identifier TEXT')
                print("  ✓ Added account_identifier column to statement")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ statement account_identifier: {e}")
            
            try:
                cursor.execute('ALTER TABLE statement_outstanding ADD COLUMN is_active INTEGER DEFAULT 1')
                print("  ✓ Added is_active column to statement")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ statement is_active: {e}")
            
            try:
                cursor.execute('ALTER TABLE statement_outstanding ADD COLUMN updated_at TIMESTAMP')
                print("  ✓ Added updated_at column to statement")
            except sqlite3.OperationalError as e:
                if 'duplicate column' not in str(e).lower():
                    print(f"  ⚠️ statement updated_at: {e}")
            
            # Now UPDATE existing rows with default values
            timestamp = datetime.now().isoformat()
            
            cursor.execute('UPDATE ledger_outstanding SET batch_id = ? WHERE batch_id IS NULL', (default_batch_id,))
            print(f"  ✓ Updated {cursor.rowcount} ledger rows with batch_id")
            
            cursor.execute('UPDATE ledger_outstanding SET account_identifier = ? WHERE account_identifier IS NULL', (default_account,))
            print(f"  ✓ Updated {cursor.rowcount} ledger rows with account_identifier")
            
            cursor.execute('UPDATE ledger_outstanding SET is_active = 1 WHERE is_active IS NULL')
            print(f"  ✓ Updated {cursor.rowcount} ledger rows with is_active")
            
            cursor.execute('UPDATE ledger_outstanding SET updated_at = ? WHERE updated_at IS NULL', (timestamp,))
            print(f"  ✓ Updated {cursor.rowcount} ledger rows with updated_at")
            
            cursor.execute('UPDATE statement_outstanding SET batch_id = ? WHERE batch_id IS NULL', (default_batch_id,))
            print(f"  ✓ Updated {cursor.rowcount} statement rows with batch_id")
            
            cursor.execute('UPDATE statement_outstanding SET account_identifier = ? WHERE account_identifier IS NULL', (default_account,))
            print(f"  ✓ Updated {cursor.rowcount} statement rows with account_identifier")
            
            cursor.execute('UPDATE statement_outstanding SET is_active = 1 WHERE is_active IS NULL')
            print(f"  ✓ Updated {cursor.rowcount} statement rows with is_active")
            
            cursor.execute('UPDATE statement_outstanding SET updated_at = ? WHERE updated_at IS NULL', (timestamp,))
            print(f"  ✓ Updated {cursor.rowcount} statement rows with updated_at")
            
            # Create batch record for migrated transactions
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO reconciliation_batches 
                    (batch_id, account_identifier, recon_date, recon_name, ledger_count, statement_count)
                    VALUES (?, ?, ?, ?, 
                        (SELECT COUNT(*) FROM ledger_outstanding WHERE batch_id = ?),
                        (SELECT COUNT(*) FROM statement_outstanding WHERE batch_id = ?))
                ''', (default_batch_id, default_account, datetime.now().strftime('%Y-%m-%d'), 
                      'Migrated from Old System', default_batch_id, default_batch_id))
                print(f"  ✓ Created batch record")
            except Exception as e:
                print(f"  ⚠️ Batch record: {e}")
            
            conn.commit()
            print(f"✅ Migration complete! All transactions assigned to batch: {default_batch_id}")
        except Exception as e:
            print(f"❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
    
    def generate_batch_id(self):
        """Generate a unique batch ID"""
        return str(uuid.uuid4())[:8]
    
    def create_batch(self, account_identifier, recon_date, recon_name=None):
        """Create a new reconciliation batch"""
        batch_id = self.generate_batch_id()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reconciliation_batches (batch_id, account_identifier, recon_date, recon_name)
            VALUES (?, ?, ?, ?)
        ''', (batch_id, account_identifier, recon_date, recon_name))
        
        conn.commit()
        conn.close()
        return batch_id
    
    def get_or_create_batch(self, account_identifier, recon_date, recon_name=None):
        """Get existing batch or create new one for this account/date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if batch exists for this account and date
        cursor.execute('''
            SELECT batch_id FROM reconciliation_batches
            WHERE account_identifier = ? AND recon_date = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (account_identifier, recon_date))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        else:
            return self.create_batch(account_identifier, recon_date, recon_name)
    
    def get_all_batches(self):
        """Get all reconciliation batches"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT batch_id, account_identifier, recon_date, recon_name, 
                   ledger_count, statement_count, created_at, last_used_at
            FROM reconciliation_batches
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_accounts(self):
        """Get list of all unique account identifiers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT account_identifier 
            FROM reconciliation_batches
            ORDER BY account_identifier
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    def save_ledger_outstanding(self, batch_id, account_identifier, recon_date, recon_name, transactions_df):
        """Save ledger outstanding transactions with batch tracking"""
        if transactions_df is None or transactions_df.empty:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for _, row in transactions_df.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO ledger_outstanding 
                    (batch_id, account_identifier, recon_date, recon_name, transaction_date, 
                     reference, description, debit, credit, amount, original_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    batch_id,
                    account_identifier,
                    recon_date,
                    recon_name,
                    str(row.get('Date', '')),
                    str(row.get('Reference', '')),
                    str(row.get('Description', '')),
                    float(row.get('Debit', 0) if pd.notna(row.get('Debit')) else 0),
                    float(row.get('Credit', 0) if pd.notna(row.get('Credit')) else 0),
                    float(row.get('Amount', 0) if pd.notna(row.get('Amount')) else 0),
                    json.dumps(row.to_dict(), default=str)
                ))
                saved_count += 1
            except Exception as e:
                print(f"Error saving ledger transaction: {e}")
        
        # Update batch count
        cursor.execute('''
            UPDATE reconciliation_batches 
            SET ledger_count = ledger_count + ?, last_used_at = CURRENT_TIMESTAMP
            WHERE batch_id = ?
        ''', (saved_count, batch_id))
        
        conn.commit()
        conn.close()
        return saved_count
    
    def save_statement_outstanding(self, batch_id, account_identifier, recon_date, recon_name, transactions_df):
        """Save statement outstanding transactions with batch tracking"""
        if transactions_df is None or transactions_df.empty:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for _, row in transactions_df.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO statement_outstanding 
                    (batch_id, account_identifier, recon_date, recon_name, transaction_date, 
                     reference, description, amount, original_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    batch_id,
                    account_identifier,
                    recon_date,
                    recon_name,
                    str(row.get('Date', '')),
                    str(row.get('Reference', '')),
                    str(row.get('Description', '')),
                    float(row.get('Amount', 0) if pd.notna(row.get('Amount')) else 0),
                    json.dumps(row.to_dict(), default=str)
                ))
                saved_count += 1
            except Exception as e:
                print(f"Error saving statement transaction: {e}")
        
        # Update batch count
        cursor.execute('''
            UPDATE reconciliation_batches 
            SET statement_count = statement_count + ?, last_used_at = CURRENT_TIMESTAMP
            WHERE batch_id = ?
        ''', (saved_count, batch_id))
        
        conn.commit()
        conn.close()
        return saved_count
    
    def get_ledger_transactions_as_dataframe(self, account_identifier=None, batch_id=None, active_only=True):
        """Get ledger outstanding transactions as DataFrame with filtering options"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(ledger_outstanding)")
        columns = [col[1] for col in cursor.fetchall()]
        has_batch_id = 'batch_id' in columns
        has_account = 'account_identifier' in columns
        has_is_active = 'is_active' in columns
        
        # Build query based on available columns
        if has_batch_id and has_account:
            query = '''
                SELECT id, batch_id, account_identifier, recon_date, recon_name, original_data
                FROM ledger_outstanding
                WHERE 1=1
            '''
        else:
            # Fallback for old schema
            query = '''
                SELECT id, 'LEGACY', 'Default Account', recon_date, recon_name, original_data
                FROM ledger_outstanding
                WHERE 1=1
            '''
        
        params = []
        
        if active_only and has_is_active:
            query += ' AND is_active = 1'
        
        if account_identifier and has_account:
            query += ' AND account_identifier = ?'
            params.append(account_identifier)
        
        if batch_id and has_batch_id:
            query += ' AND batch_id = ?'
            params.append(batch_id)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return pd.DataFrame()
        
        # Reconstruct DataFrame from original_data JSON
        transactions = []
        for row in rows:
            transaction_id, batch_id, account_id, recon_date, recon_name, original_json = row
            try:
                original_dict = json.loads(original_json)
                # Add metadata columns
                original_dict['_id'] = transaction_id
                original_dict['_batch_id'] = batch_id
                original_dict['_account'] = account_id
                original_dict['_recon_date'] = recon_date
                original_dict['_recon_name'] = recon_name
                transactions.append(original_dict)
            except Exception as e:
                print(f"Warning: Could not parse original_data for transaction {transaction_id}: {e}")
        
        if not transactions:
            return pd.DataFrame()
        
        # Create DataFrame with original columns
        df = pd.DataFrame(transactions)
        
        # Move metadata columns to front
        metadata_cols = ['_id', '_batch_id', '_account', '_recon_date', '_recon_name']
        other_cols = [col for col in df.columns if col not in metadata_cols]
        df = df[metadata_cols + other_cols]
        
        return df
    
    def get_statement_transactions_as_dataframe(self, account_identifier=None, batch_id=None, active_only=True):
        """Get statement outstanding transactions as DataFrame with filtering options"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(statement_outstanding)")
        columns = [col[1] for col in cursor.fetchall()]
        has_batch_id = 'batch_id' in columns
        has_account = 'account_identifier' in columns
        has_is_active = 'is_active' in columns
        
        # Build query based on available columns
        if has_batch_id and has_account:
            query = '''
                SELECT id, batch_id, account_identifier, recon_date, recon_name, original_data
                FROM statement_outstanding
                WHERE 1=1
            '''
        else:
            # Fallback for old schema
            query = '''
                SELECT id, 'LEGACY', 'Default Account', recon_date, recon_name, original_data
                FROM statement_outstanding
                WHERE 1=1
            '''
        
        params = []
        
        if active_only and has_is_active:
            query += ' AND is_active = 1'
        
        if account_identifier and has_account:
            query += ' AND account_identifier = ?'
            params.append(account_identifier)
        
        if batch_id and has_batch_id:
            query += ' AND batch_id = ?'
            params.append(batch_id)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return pd.DataFrame()
        
        # Reconstruct DataFrame from original_data JSON
        transactions = []
        for row in rows:
            transaction_id, batch_id, account_id, recon_date, recon_name, original_json = row
            try:
                original_dict = json.loads(original_json)
                # Add metadata columns
                original_dict['_id'] = transaction_id
                original_dict['_batch_id'] = batch_id
                original_dict['_account'] = account_id
                original_dict['_recon_date'] = recon_date
                original_dict['_recon_name'] = recon_name
                transactions.append(original_dict)
            except Exception as e:
                print(f"Warning: Could not parse original_data for transaction {transaction_id}: {e}")
        
        if not transactions:
            return pd.DataFrame()
        
        # Create DataFrame with original columns
        df = pd.DataFrame(transactions)
        
        # Move metadata columns to front
        metadata_cols = ['_id', '_batch_id', '_account', '_recon_date', '_recon_name']
        other_cols = [col for col in df.columns if col not in metadata_cols]
        df = df[metadata_cols + other_cols]
        
        return df
    
    def archive_transactions(self, transaction_ids, transaction_type, reason="Copied for new reconciliation"):
        """Move transactions to historical archive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_name = f"{transaction_type}_outstanding"
        history_table = f"{transaction_type}_outstanding_history"
        
        archived_count = 0
        for trans_id in transaction_ids:
            try:
                # Get transaction data
                cursor.execute(f'''
                    SELECT id, batch_id, account_identifier, recon_date, recon_name,
                           transaction_date, reference, description, 
                           {"debit, credit, " if transaction_type == "ledger" else ""}
                           amount, original_data, created_at
                    FROM {table_name}
                    WHERE id = ?
                ''', (trans_id,))
                
                row = cursor.fetchone()
                if not row:
                    continue
                
                # Insert into history
                if transaction_type == "ledger":
                    cursor.execute(f'''
                        INSERT INTO {history_table}
                        (original_id, batch_id, account_identifier, recon_date, recon_name,
                         transaction_date, reference, description, debit, credit, amount,
                         original_data, archived_reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (*row, reason))
                else:
                    cursor.execute(f'''
                        INSERT INTO {history_table}
                        (original_id, batch_id, account_identifier, recon_date, recon_name,
                         transaction_date, reference, description, amount,
                         original_data, archived_reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (*row, reason))
                
                # Mark as inactive (soft delete)
                cursor.execute(f'''
                    UPDATE {table_name}
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (trans_id,))
                
                archived_count += 1
            except Exception as e:
                print(f"Error archiving transaction {trans_id}: {e}")
        
        conn.commit()
        conn.close()
        return archived_count
    
    def delete_ledger_transaction(self, transaction_id):
        """Delete a ledger outstanding transaction (mark as inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ledger_outstanding 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (transaction_id,))
        conn.commit()
        conn.close()
    
    def delete_statement_transaction(self, transaction_id):
        """Delete a statement outstanding transaction (mark as inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE statement_outstanding 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (transaction_id,))
        conn.commit()
        conn.close()


class OutstandingTransactionsViewer(tk.Toplevel):
    """Professional viewer with account filtering and smart copy functionality"""
    
    def __init__(self, parent, transaction_type, db, workflow_instance=None):
        super().__init__(parent)
        self.transaction_type = transaction_type  # "ledger" or "statement"
        self.db = db
        self.workflow_instance = workflow_instance
        self.df = None  # Full DataFrame with metadata
        
        # Account filter
        self.selected_account = tk.StringVar(value="All Accounts")
        self.selected_batch = tk.StringVar(value="All Batches")
        
        self.create_interface()
        self.load_transactions()
    
    def create_interface(self):
        """Create the enhanced user interface"""
        title_text = f"Outstanding Transactions - {self.transaction_type.title()}"
        self.title(f"BARD-RECO {title_text}")
        self.state('zoomed')
        self.configure(bg="#f5f6fa")
        
        # Main container
        main_frame = tk.Frame(self, bg="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with filters
        header_frame = tk.Frame(main_frame, bg="#2c3e50", relief="flat", bd=0)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, text=title_text, 
                              font=("Segoe UI", 16, "bold"),
                              bg="#2c3e50", fg="white")
        title_label.pack(side="left", padx=20, pady=15)
        
        # Filter frame
        filter_frame = tk.Frame(header_frame, bg="#2c3e50")
        filter_frame.pack(side="right", padx=20, pady=10)
        
        # Account filter
        tk.Label(filter_frame, text="Account:", font=("Segoe UI", 10),
                bg="#2c3e50", fg="white").grid(row=0, column=0, padx=5, sticky="e")
        
        account_combo = ttk.Combobox(filter_frame, textvariable=self.selected_account,
                                    state="readonly", width=20)
        account_combo.grid(row=0, column=1, padx=5)
        account_combo.bind('<<ComboboxSelected>>', lambda e: self.load_transactions())
        self.account_combo = account_combo
        
        # Batch filter
        tk.Label(filter_frame, text="Batch:", font=("Segoe UI", 10),
                bg="#2c3e50", fg="white").grid(row=0, column=2, padx=5, sticky="e")
        
        batch_combo = ttk.Combobox(filter_frame, textvariable=self.selected_batch,
                                  state="readonly", width=15)
        batch_combo.grid(row=0, column=3, padx=5)
        batch_combo.bind('<<ComboboxSelected>>', lambda e: self.load_transactions())
        self.batch_combo = batch_combo
        
        # Active/Archived toggle
        self.show_active_only = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(filter_frame, text="Active Only",
                                     variable=self.show_active_only,
                                     command=self.load_transactions,
                                     font=("Segoe UI", 9, "bold"),
                                     bg="#2c3e50", fg="white",
                                     selectcolor="#34495e",
                                     activebackground="#2c3e50",
                                     activeforeground="white")
        active_check.grid(row=0, column=4, padx=10)
        
        # Refresh button
        refresh_btn = tk.Button(filter_frame, text="🔄 Refresh", 
                               command=self.load_transactions,
                               font=("Segoe UI", 9, "bold"),
                               bg="#3498db", fg="white",
                               relief="flat", padx=10, pady=5,
                               cursor="hand2")
        refresh_btn.grid(row=0, column=5, padx=5)
        
        # Archive History button
        archive_btn = tk.Button(filter_frame, text="📚 Batch History",
                               command=self.show_archive_history,
                               font=("Segoe UI", 9, "bold"),
                               bg="#8e44ad", fg="white",
                               relief="flat", padx=10, pady=5,
                               cursor="hand2")
        archive_btn.grid(row=0, column=6, padx=5)
        
        # Toolbar
        toolbar_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        toolbar_frame.pack(fill="x", pady=(0, 5))
        
        btn_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # Copy button with smart functionality
        copy_btn = tk.Button(toolbar_frame, text="📋 Copy to New Reconciliation",
                            command=self.copy_for_new_reconciliation,
                            bg="#27ae60", fg="white", **btn_style)
        copy_btn.pack(side="left", padx=5, pady=5)
        
        # Copy selected
        copy_selected_btn = tk.Button(toolbar_frame, text="📄 Copy Selected",
                                     command=self.copy_selected_transactions,
                                     bg="#3498db", fg="white", **btn_style)
        copy_selected_btn.pack(side="left", padx=5)
        
        # Edit button
        edit_btn = tk.Button(toolbar_frame, text="✏️ Edit Selected",
                           command=self.edit_selected,
                           bg="#f39c12", fg="white", **btn_style)
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = tk.Button(toolbar_frame, text="🗑️ Delete Selected",
                             command=self.delete_selected,
                             bg="#e74c3c", fg="white", **btn_style)
        delete_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = tk.Button(toolbar_frame, text="💾 Export to Excel",
                             command=self.export_to_excel,
                             bg="#9b59b6", fg="white", **btn_style)
        export_btn.pack(side="left", padx=5)
        
        # Info label
        self.info_label = tk.Label(toolbar_frame, text="", 
                                   font=("Segoe UI", 9),
                                   bg="white", fg="#7f8c8d")
        self.info_label.pack(side="right", padx=15)
        
        # Treeview frame
        tree_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        
        # Treeview (columns will be created dynamically based on data)
        self.tree = ttk.Treeview(tree_frame, 
                                yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set,
                                selectmode="extended")
        self.tree.pack(fill="both", expand=True)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Style
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    
    def load_transactions(self):
        """Load transactions with filtering"""
        # Get filter values
        account = None if self.selected_account.get() == "All Accounts" else self.selected_account.get()
        batch = None if self.selected_batch.get() == "All Batches" else self.selected_batch.get()
        active_only = self.show_active_only.get() if hasattr(self, 'show_active_only') else True
        
        # Get transactions based on type
        if self.transaction_type == "ledger":
            df = self.db.get_ledger_transactions_as_dataframe(account_identifier=account, batch_id=batch, active_only=active_only)
        else:
            df = self.db.get_statement_transactions_as_dataframe(account_identifier=account, batch_id=batch, active_only=active_only)
        
        if df.empty:
            self.info_label.config(text="No outstanding transactions found")
            # Update filter combos
            self.update_filters()
            return
        
        # Store FULL DataFrame for internal operations
        self.df = df
        
        # Get column names - EXCLUDE metadata columns starting with '_'
        all_columns = df.columns.tolist()
        display_columns = [col for col in all_columns if not col.startswith('_')]
        
        # Create display DataFrame without metadata
        display_df = df[display_columns]
        
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure tree columns dynamically
        self.tree["columns"] = display_columns
        self.tree["show"] = "tree headings"
        
        # Configure column #0 (tree column) as row number
        self.tree.column("#0", width=50, anchor="center")
        self.tree.heading("#0", text="#")
        
        # Configure dynamic columns with intelligent widths
        for col in display_columns:
            col_lower = col.lower()
            
            # Set width based on column type
            if any(x in col_lower for x in ['description', 'comment', 'sender', 'receiver']):
                width = 300
            elif any(x in col_lower for x in ['reference', 'source', 'journal']):
                width = 150
            elif any(x in col_lower for x in ['amount', 'debit', 'credit', 'balance']):
                width = 100
                anchor = "e"
            elif 'date' in col_lower:
                width = 100
            elif 'currency' in col_lower:
                width = 70
            else:
                width = 120
            
            anchor = "e" if any(x in col_lower for x in ['amount', 'debit', 'credit', 'balance']) else "w"
            
            self.tree.column(col, width=width, anchor=anchor)
            self.tree.heading(col, text=col)
        
        # Insert data with row index as tag (for mapping to full DataFrame)
        for idx, row in display_df.iterrows():
            values = [str(v) if pd.notna(v) else "" for v in row]
            # Store DataFrame index as tag for mapping to full data
            self.tree.insert('', 'end', text=str(idx+1), values=values, tags=(str(idx),))
        
        # Update info
        self.info_label.config(text=f"Showing {len(df)} transactions")
        
        # Update filter combos
        self.update_filters()
    
    def update_filters(self):
        """Update filter dropdowns"""
        # Get all accounts
        accounts = self.db.get_accounts()
        self.account_combo['values'] = ["All Accounts"] + accounts
        
        # Get all batches
        batches = self.db.get_all_batches()
        batch_ids = ["All Batches"] + [b[0] for b in batches]
        self.batch_combo['values'] = batch_ids
    
    def copy_for_new_reconciliation(self):
        """Smart copy function - copies outstanding transactions for new reconciliation"""
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "No outstanding transactions to copy", parent=self)
            return
        
        if not self.workflow_instance:
            messagebox.showwarning("No Workflow", 
                                 "This feature requires integration with the workflow instance",
                                 parent=self)
            return
        
        # Ask user what they want to do
        dialog = tk.Toplevel(self)
        dialog.title("Copy Outstanding Transactions")
        dialog.state('zoomed')  # Maximize to show all features
        dialog.geometry("900x600")  # Larger fallback size
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Label(dialog, text="Copy Outstanding Transactions for New Reconciliation",
                         font=("Segoe UI", 14, "bold"), bg="#2c3e50", fg="white", pady=15)
        header.pack(fill="x")
        
        # Content frame
        content = tk.Frame(dialog, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = tk.Label(content, 
                              text="Choose how to copy outstanding transactions:",
                              font=("Segoe UI", 11),
                              bg="white", justify="left")
        instructions.pack(anchor="w", pady=(0, 20))
        
        # Option 1: Append to existing import
        option1_frame = tk.Frame(content, bg="#ecf0f1", relief="solid", bd=1)
        option1_frame.pack(fill="x", pady=5)
        
        option1_label = tk.Label(option1_frame,
                                text="📎 Append to New Import (Without Headers)",
                                font=("Segoe UI", 11, "bold"),
                                bg="#ecf0f1", fg="#2c3e50")
        option1_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        option1_desc = tk.Label(option1_frame,
                               text="• Use when you've already imported NEW ledger/statement data\n"
                                    "• Adds outstanding transactions to existing data\n"
                                    "• Continues with current workflow (no headers needed)",
                               font=("Segoe UI", 9),
                               bg="#ecf0f1", fg="#34495e", justify="left")
        option1_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        option1_btn = tk.Button(option1_frame, text="✓ Append to Existing Import",
                               command=lambda: self.execute_smart_copy(dialog, append_mode=True),
                               font=("Segoe UI", 10, "bold"),
                               bg="#27ae60", fg="white",
                               relief="flat", padx=20, pady=10,
                               cursor="hand2")
        option1_btn.pack(anchor="center", pady=(0, 10))
        
        # Option 2: Start fresh
        option2_frame = tk.Frame(content, bg="#ecf0f1", relief="solid", bd=1)
        option2_frame.pack(fill="x", pady=5)
        
        option2_label = tk.Label(option2_frame,
                                text="🔄 Start Fresh Reconciliation (With Headers)",
                                font=("Segoe UI", 11, "bold"),
                                bg="#ecf0f1", fg="#2c3e50")
        option2_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        option2_desc = tk.Label(option2_frame,
                               text="• Use when you want to reconcile ONLY outstanding transactions\n"
                                    "• No new import needed\n"
                                    "• Starts fresh workflow (includes headers for column configuration)",
                               font=("Segoe UI", 9),
                               bg="#ecf0f1", fg="#34495e", justify="left")
        option2_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        option2_btn = tk.Button(option2_frame, text="✓ Start Fresh Workflow",
                               command=lambda: self.execute_smart_copy(dialog, append_mode=False),
                               font=("Segoe UI", 10, "bold"),
                               bg="#3498db", fg="white",
                               relief="flat", padx=20, pady=10,
                               cursor="hand2")
        option2_btn.pack(anchor="center", pady=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(content, text="Cancel",
                              command=dialog.destroy,
                              font=("Segoe UI", 9),
                              bg="#95a5a6", fg="white",
                              relief="flat", padx=15, pady=5,
                              cursor="hand2")
        cancel_btn.pack(pady=15)
    
    def execute_smart_copy(self, dialog, append_mode=True):
        """Execute the smart copy operation"""
        dialog.destroy()
        
        # Get transactions to copy (without metadata columns)
        display_columns = [col for col in self.df.columns if not col.startswith('_')]
        copy_df = self.df[display_columns].copy()
        
        # Drop specific columns based on transaction type
        columns_to_drop = []
        if self.transaction_type == "ledger":
            # For Ledger: Drop RJ-Number and Payment Ref columns
            for col in ['RJ-Number', 'Payment Ref']:
                if col in copy_df.columns:
                    columns_to_drop.append(col)
        else:  # statement
            # For Statement: Drop Reference column
            if 'Reference' in copy_df.columns:
                columns_to_drop.append('Reference')
        
        # Drop the identified columns
        if columns_to_drop:
            copy_df = copy_df.drop(columns=columns_to_drop)
            print(f"✓ Dropped columns for clean reconciliation: {', '.join(columns_to_drop)}")
        
        # Get transaction IDs for archiving
        transaction_ids = self.df['_id'].tolist()
        
        if append_mode:
            # Append mode: Add to existing data WITHOUT headers
            # Check if there's existing data
            if self.transaction_type == "ledger":
                # Handle different workflow types (direct attribute or app.attribute)
                if hasattr(self.workflow_instance, 'ledger_df'):
                    existing_df = self.workflow_instance.ledger_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'ledger_df'):
                    existing_df = self.workflow_instance.app.ledger_df
                else:
                    existing_df = None
                
                if existing_df is None or existing_df.empty:
                    messagebox.showwarning("No Import",
                                         "No existing ledger data found!\n"
                                         "Please import ledger data first, or choose 'Start Fresh' option.",
                                         parent=self)
                    return
                
                # Append outstanding transactions to existing import
                combined_df = pd.concat([existing_df, copy_df], ignore_index=True)
                
                # Assign back to correct location
                if hasattr(self.workflow_instance, 'ledger_df'):
                    self.workflow_instance.ledger_df = combined_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'ledger_df'):
                    self.workflow_instance.app.ledger_df = combined_df
                
                messagebox.showinfo("Success",
                                  f"✓ Appended {len(copy_df)} outstanding transactions to existing ledger!\n"
                                  f"Total transactions: {len(combined_df)}",
                                  parent=self)
            else:  # statement
                # Handle different workflow types (direct attribute or app.attribute)
                if hasattr(self.workflow_instance, 'statement_df'):
                    existing_df = self.workflow_instance.statement_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'statement_df'):
                    existing_df = self.workflow_instance.app.statement_df
                else:
                    existing_df = None
                
                if existing_df is None or existing_df.empty:
                    messagebox.showwarning("No Import",
                                         "No existing statement data found!\n"
                                         "Please import statement data first, or choose 'Start Fresh' option.",
                                         parent=self)
                    return
                
                # Append outstanding transactions to existing import
                combined_df = pd.concat([existing_df, copy_df], ignore_index=True)
                
                # Assign back to correct location
                if hasattr(self.workflow_instance, 'statement_df'):
                    self.workflow_instance.statement_df = combined_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'statement_df'):
                    self.workflow_instance.app.statement_df = combined_df
                
                messagebox.showinfo("Success",
                                  f"✓ Appended {len(copy_df)} outstanding transactions to existing statement!\n"
                                  f"Total transactions: {len(combined_df)}",
                                  parent=self)
        else:
            # Fresh start mode: Load as NEW data WITH headers
            if self.transaction_type == "ledger":
                # Assign to correct location
                if hasattr(self.workflow_instance, 'ledger_df'):
                    self.workflow_instance.ledger_df = copy_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'ledger_df'):
                    self.workflow_instance.app.ledger_df = copy_df
                
                messagebox.showinfo("Success",
                                  f"✓ Loaded {len(copy_df)} outstanding transactions as NEW ledger!\n"
                                  "You can now configure columns and start reconciliation.",
                                  parent=self)
            else:  # statement
                # Assign to correct location
                if hasattr(self.workflow_instance, 'statement_df'):
                    self.workflow_instance.statement_df = copy_df
                elif hasattr(self.workflow_instance, 'app') and hasattr(self.workflow_instance.app, 'statement_df'):
                    self.workflow_instance.app.statement_df = copy_df
                
                messagebox.showinfo("Success",
                                  f"✓ Loaded {len(copy_df)} outstanding transactions as NEW statement!\n"
                                  "You can now configure columns and start reconciliation.",
                                  parent=self)
        
        # Archive copied transactions
        archived = self.db.archive_transactions(
            transaction_ids, 
            self.transaction_type,
            reason="Copied for new reconciliation"
        )
        
        # Refresh display
        self.load_transactions()
        
        # Trigger workflow view refresh if possible
        try:
            if hasattr(self.workflow_instance, 'refresh_data_display'):
                self.workflow_instance.refresh_data_display()
            elif hasattr(self.workflow_instance, 'update_status'):
                self.workflow_instance.update_status()
        except Exception as e:
            print(f"Note: Could not refresh workflow display: {e}")
        
        # Close dialog and viewer
        dialog.destroy()
        
        # Show summary and guide user to next steps
        next_step = ""
        if append_mode:
            next_step = "\n\n💡 Next: Configure columns and start reconciliation!"
        else:
            if self.transaction_type == "ledger":
                next_step = "\n\n💡 Next: Click 'View Ledger' to see the loaded data, then configure columns and reconcile!"
            else:
                next_step = "\n\n💡 Next: Click 'View Statement' to see the loaded data, then configure columns and reconcile!"
        
        messagebox.showinfo("✅ Complete",
                          f"✓ {len(copy_df)} transactions copied successfully!\n"
                          f"✓ {archived} transactions moved to history{next_step}",
                          parent=self)
        
        # Close the viewer window after successful copy
        self.destroy()
    
    def copy_selected_transactions(self):
        """Copy selected transactions to clipboard"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select transactions to copy", parent=self)
            return
        
        # Get selected rows without metadata
        display_columns = [col for col in self.df.columns if not col.startswith('_')]
        selected_indices = [int(self.tree.item(item)['tags'][0]) for item in selected]
        selected_df = self.df.iloc[selected_indices][display_columns]
        
        # Copy to clipboard
        selected_df.to_clipboard(index=False)
        messagebox.showinfo("Copied", f"Copied {len(selected)} transactions to clipboard", parent=self)
    
    def edit_selected(self):
        """Edit selected transaction"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to edit", parent=self)
            return
        
        if len(selected) > 1:
            messagebox.showwarning("Multiple Selection", 
                                 "Please select only one transaction to edit", parent=self)
            return
        
        # Get transaction ID from full DataFrame using tags
        item = self.tree.item(selected[0])
        tags = item['tags']
        df_index = int(tags[0])
        transaction_id = self.df.iloc[df_index]['_id']
        
        # Get transaction data (without metadata for editing)
        display_columns = [col for col in self.df.columns if not col.startswith('_')]
        transaction_data = self.df.iloc[df_index][display_columns].to_dict()
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("Edit Transaction")
        edit_dialog.geometry("500x600")
        edit_dialog.transient(self)
        
        # Create form
        form_frame = tk.Frame(edit_dialog, bg="white")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        entries = {}
        row = 0
        for col, value in transaction_data.items():
            tk.Label(form_frame, text=f"{col}:", font=("Segoe UI", 10),
                    bg="white").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            
            entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
            entry.insert(0, str(value) if pd.notna(value) else "")
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            entries[col] = entry
            row += 1
        
        # Save button
        def save_changes():
            # TODO: Implement save logic
            messagebox.showinfo("Info", "Edit functionality coming soon!", parent=edit_dialog)
            edit_dialog.destroy()
        
        save_btn = tk.Button(form_frame, text="Save Changes", command=save_changes,
                           font=("Segoe UI", 10, "bold"),
                           bg="#27ae60", fg="white",
                           relief="flat", padx=20, pady=10)
        save_btn.grid(row=row, column=0, columnspan=2, pady=20)
    
    def delete_selected(self):
        """Delete selected transactions"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select transactions to delete", parent=self)
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete",
                                  f"Are you sure you want to delete {len(selected)} transaction(s)?",
                                  parent=self):
            return
        
        # Get transaction IDs from full DataFrame using tags
        for item in selected:
            tags = self.tree.item(item)['tags']
            df_index = int(tags[0])
            transaction_id = self.df.iloc[df_index]['_id']
            
            # Delete transaction
            if self.transaction_type == "ledger":
                self.db.delete_ledger_transaction(transaction_id)
            else:
                self.db.delete_statement_transaction(transaction_id)
        
        messagebox.showinfo("Deleted", f"Deleted {len(selected)} transaction(s)", parent=self)
        self.load_transactions()
    
    def show_archive_history(self):
        """Show comprehensive archive history with batch details"""
        BatchHistoryBrowser(self, self.db, self.transaction_type)
    
    def export_to_excel(self):
        """Export transactions to Excel"""
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "No transactions to export", parent=self)
            return
        
        # Get export path
        file_path = filedialog.asksaveasfilename(
            title="Export to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            parent=self
        )
        
        if not file_path:
            return
        
        try:
            # Export without metadata columns
            display_columns = [col for col in self.df.columns if not col.startswith('_')]
            export_df = self.df[display_columns]
            export_df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Exported {len(export_df)} transactions to:\n{file_path}",
                              parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{e}", parent=self)


class BatchHistoryBrowser(tk.Toplevel):
    """Comprehensive batch history browser showing all archived transactions by batch"""
    
    def __init__(self, parent, db, default_transaction_type="ledger"):
        super().__init__(parent)
        self.db = db
        self.current_type = default_transaction_type
        
        # Setup window
        self.title("BARD-RECO - Batch History & Archive Manager")
        self.state('zoomed')  # Maximized
        self.configure(bg="#ecf0f1")
        
        self.create_interface()
        self.load_batch_list()
    
    def create_interface(self):
        """Create the batch history interface"""
        # Initialize data storage
        self.current_data = []
        self.display_cols = []
        self.batches = []
        
        # Header
        header = tk.Frame(self, bg="#2c3e50", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = tk.Label(header, text="📚 Batch History & Archive Manager",
                        font=("Segoe UI", 18, "bold"),
                        bg="#2c3e50", fg="white")
        title.pack(side="left", padx=30, pady=20)
        
        subtitle = tk.Label(header, text="View all reconciliation batches and archived transactions",
                           font=("Segoe UI", 11),
                           bg="#2c3e50", fg="#bdc3c7")
        subtitle.pack(side="left", padx=(0, 30))
        
        # Main content
        content = tk.Frame(self, bg="#ecf0f1")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Batch list
        left_panel = tk.Frame(content, bg="white", relief="solid", bd=2, width=400)
        left_panel.pack(side="left", fill="both", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)
        
        # Batch list header
        batch_header = tk.Frame(left_panel, bg="#34495e", height=50)
        batch_header.pack(fill="x")
        batch_header.pack_propagate(False)
        
        tk.Label(batch_header, text="📦 Reconciliation Batches",
                font=("Segoe UI", 12, "bold"),
                bg="#34495e", fg="white").pack(side="left", padx=15, pady=10)
        
        refresh_btn = tk.Button(batch_header, text="🔄",
                               command=self.load_batch_list,
                               font=("Segoe UI", 10, "bold"),
                               bg="#3498db", fg="white",
                               relief="flat", padx=8, pady=2,
                               cursor="hand2")
        refresh_btn.pack(side="right", padx=10)
        
        # Batch listbox
        batch_frame = tk.Frame(left_panel, bg="white")
        batch_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        batch_scroll = ttk.Scrollbar(batch_frame)
        batch_scroll.pack(side="right", fill="y")
        
        self.batch_listbox = tk.Listbox(batch_frame,
                                        font=("Consolas", 10),
                                        yscrollcommand=batch_scroll.set,
                                        selectmode="single",
                                        bg="white",
                                        fg="#2c3e50",
                                        selectbackground="#3498db",
                                        selectforeground="white",
                                        relief="flat")
        self.batch_listbox.pack(side="left", fill="both", expand=True)
        self.batch_listbox.bind('<<ListboxSelect>>', self.on_batch_select)
        
        batch_scroll.config(command=self.batch_listbox.yview)
        
        # Right panel - Batch details
        right_panel = tk.Frame(content, bg="white", relief="solid", bd=2)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)
        
        # Details header
        details_header = tk.Frame(right_panel, bg="#34495e", height=50)
        details_header.pack(fill="x")
        details_header.pack_propagate(False)
        
        tk.Label(details_header, text="📊 Batch Details",
                font=("Segoe UI", 12, "bold"),
                bg="#34495e", fg="white").pack(side="left", padx=15, pady=10)
        
        # Type toggle
        type_frame = tk.Frame(details_header, bg="#34495e")
        type_frame.pack(side="right", padx=15)
        
        tk.Button(type_frame, text="📊 Ledger",
                 command=lambda: self.switch_type("ledger"),
                 font=("Segoe UI", 9, "bold"),
                 bg="#3b82f6", fg="white",
                 relief="flat", padx=10, pady=5,
                 cursor="hand2").pack(side="left", padx=2)
        
        tk.Button(type_frame, text="🏦 Statement",
                 command=lambda: self.switch_type("statement"),
                 font=("Segoe UI", 9, "bold"),
                 bg="#10b981", fg="white",
                 relief="flat", padx=10, pady=5,
                 cursor="hand2").pack(side="left", padx=2)
        
        # Batch info panel
        info_panel = tk.Frame(right_panel, bg="#f8f9fa", relief="flat", bd=0)
        info_panel.pack(fill="x", padx=15, pady=15)
        
        self.batch_info_label = tk.Label(info_panel, text="Select a batch to view details",
                                         font=("Segoe UI", 11),
                                         bg="#f8f9fa", fg="#7f8c8d",
                                         justify="left", anchor="w")
        self.batch_info_label.pack(fill="x", padx=10, pady=10)
        
        # Transactions view
        tree_frame = tk.Frame(right_panel, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame,
                                yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set,
                                selectmode="extended")
        self.tree.pack(fill="both", expand=True)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Search/Filter bar
        search_frame = tk.Frame(right_panel, bg="#f8f9fa")
        search_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10, "bold"),
                bg="#f8f9fa", fg="#2c3e50").pack(side="left", padx=(5, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_transactions())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=("Segoe UI", 10), width=40)
        search_entry.pack(side="left", padx=5)
        
        tk.Button(search_frame, text="✖", command=lambda: self.search_var.set(''),
                 font=("Segoe UI", 9, "bold"), bg="#e74c3c", fg="white",
                 relief="flat", padx=8, pady=2, cursor="hand2").pack(side="left", padx=5)
        
        # Selection info
        self.selection_label = tk.Label(search_frame, text="0 selected",
                                       font=("Segoe UI", 10, "italic"),
                                       bg="#f8f9fa", fg="#7f8c8d")
        self.selection_label.pack(side="right", padx=10)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.update_selection_count)
        
        # Action buttons - First row
        button_frame1 = tk.Frame(right_panel, bg="white")
        button_frame1.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Button(button_frame1, text="☑️ Select All",
                 command=self.select_all,
                 font=("Segoe UI", 10, "bold"),
                 bg="#9b59b6", fg="white",
                 relief="flat", padx=15, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame1, text="☐ Deselect All",
                 command=self.deselect_all,
                 font=("Segoe UI", 10, "bold"),
                 bg="#95a5a6", fg="white",
                 relief="flat", padx=15, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame1, text="✏️ Edit Selected",
                 command=self.edit_selected_transactions,
                 font=("Segoe UI", 10, "bold"),
                 bg="#f39c12", fg="white",
                 relief="flat", padx=15, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame1, text="🗑️ Delete Selected",
                 command=self.delete_selected_transactions,
                 font=("Segoe UI", 10, "bold"),
                 bg="#e74c3c", fg="white",
                 relief="flat", padx=15, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        # Action buttons - Second row
        button_frame2 = tk.Frame(right_panel, bg="white")
        button_frame2.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Button(button_frame2, text="♻️ Restore Selected to Active",
                 command=self.restore_selected,
                 font=("Segoe UI", 10, "bold"),
                 bg="#27ae60", fg="white",
                 relief="flat", padx=20, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame2, text="💾 Export Batch to Excel",
                 command=self.export_batch,
                 font=("Segoe UI", 10, "bold"),
                 bg="#3498db", fg="white",
                 relief="flat", padx=20, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame2, text="⚠️ Permanently Delete Batch",
                 command=self.delete_batch,
                 font=("Segoe UI", 10, "bold"),
                 bg="#c0392b", fg="white",
                 relief="flat", padx=20, pady=10,
                 cursor="hand2").pack(side="left", padx=5)
    
    def load_batch_list(self):
        """Load all batches"""
        self.batch_listbox.delete(0, tk.END)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT batch_id, account_identifier, recon_date, recon_name, 
                   ledger_count, statement_count, created_at
            FROM reconciliation_batches
            ORDER BY created_at DESC
        ''')
        
        self.batches = cursor.fetchall()
        conn.close()
        
        if not self.batches:
            # Show message when no batches
            self.batch_listbox.insert(tk.END, "No batches found")
            self.batch_info_label.config(text="No reconciliation batches available.\n\nRun a reconciliation to create batches.")
            return
        
        for batch in self.batches:
            batch_id, account, date, name, ledger_cnt, stmt_cnt, created = batch
            display = f"{batch_id} | {account} | {date} | L:{ledger_cnt} S:{stmt_cnt}"
            self.batch_listbox.insert(tk.END, display)
    
    def on_batch_select(self, event):
        """Handle batch selection"""
        selection = self.batch_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        batch = self.batches[idx]
        batch_id, account, date, name, ledger_cnt, stmt_cnt, created = batch
        
        # Update info
        info_text = f"""
📦 Batch ID: {batch_id}
🏢 Account: {account}
📅 Reconciliation Date: {date}
📝 Name: {name or 'N/A'}
📊 Ledger Transactions: {ledger_cnt}
🏦 Statement Transactions: {stmt_cnt}
🕒 Created: {created}
        """.strip()
        
        self.batch_info_label.config(text=info_text)
        
        # Load transactions
        self.load_batch_transactions(batch_id)
    
    def load_batch_transactions(self, batch_id):
        """Load transactions for selected batch with actual column data from original_data JSON"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear stored data
        self.current_data = []
        self.display_cols = []
        
        # Validate batch_id
        if not batch_id:
            return
        
        # Get transactions
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        table = f"{self.current_type}_outstanding"
        cursor.execute(f'''
            SELECT * FROM {table}
            WHERE batch_id = ?
            ORDER BY created_at DESC
        ''', (batch_id,))
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        
        if not rows:
            # Show message in tree
            self.tree["columns"] = ["Message"]
            self.tree["show"] = "headings"
            self.tree.heading("Message", text="No Transactions Found")
            self.tree.column("Message", width=800, anchor="center")
            self.tree.insert("", tk.END, values=["This batch has no transactions. It may have been deleted or archived."])
            return
        
        # Parse original_data to get actual transaction columns
        original_data_idx = column_names.index('original_data')
        id_idx = column_names.index('id')
        
        # Collect all possible columns from original_data - PRESERVE ORDER
        all_columns_ordered = []  # Use list to maintain insertion order
        all_columns_set = set()   # Use set to track what we've seen
        parsed_data = []
        
        for row in rows:
            row_dict = {'_db_id': row[id_idx]}
            
            # Parse original_data JSON
            if row[original_data_idx]:
                try:
                    original = json.loads(row[original_data_idx])
                    # Preserve the order from JSON (which preserves original DataFrame column order)
                    for key, value in original.items():
                        row_dict[key] = value
                        # Add to ordered list only if not seen before
                        if key not in all_columns_set:
                            all_columns_ordered.append(key)
                            all_columns_set.add(key)
                except:
                    # Fallback to basic columns if JSON parse fails
                    for i, col in enumerate(column_names):
                        if col not in ['id', 'original_data', 'updated_at', 'created_at']:
                            row_dict[col] = row[i]
                            if col not in all_columns_set:
                                all_columns_ordered.append(col)
                                all_columns_set.add(col)
            else:
                # Use basic columns if no original_data
                for i, col in enumerate(column_names):
                    if col not in ['id', 'original_data', 'updated_at', 'created_at']:
                        row_dict[col] = row[i]
                        if col not in all_columns_set:
                            all_columns_ordered.append(col)
                            all_columns_set.add(col)
            
            parsed_data.append(row_dict)
        
        # Keep original column order (as they appear in data) - DO NOT SORT
        # Only filter out internal/unnamed columns
        display_cols = [col for col in all_columns_ordered if not col.startswith('_') and 
                       col not in ['is_active', 'batch_id', 'account_identifier', 'recon_date', 'recon_name'] and
                       not col.startswith('Unnamed')]
        
        # Configure tree columns
        self.tree["columns"] = display_cols
        self.tree["show"] = "headings"
        
        # Configure column headers and widths
        for col in display_cols:
            # Make headers clickable for sorting
            self.tree.heading(col, text=col.replace('_', ' ').title(), 
                            command=lambda c=col: self.sort_by_column(c))
            
            # Auto-size columns based on content
            if col.lower() in ['date', 'transaction_date', 'value_date']:
                width = 100
            elif col.lower() in ['reference', 'ref']:
                width = 150
            elif col.lower() in ['description', 'desc', 'narrative']:
                width = 300
            elif col.lower() in ['amount', 'debit', 'credit', 'balance']:
                width = 120
            else:
                width = 150
            
            self.tree.column(col, width=width, minwidth=80)
        
        # Store data for sorting and filtering
        self.current_data = parsed_data
        self.display_cols = display_cols
        
        # Display rows
        for row_dict in parsed_data:
            values = [row_dict.get(col, '') for col in display_cols]
            # Format numeric values
            formatted_values = []
            for val in values:
                if isinstance(val, (int, float)) and val != 0:
                    formatted_values.append(f"{val:,.2f}")
                else:
                    formatted_values.append(str(val) if val else '')
            
            self.tree.insert("", tk.END, values=formatted_values, tags=(row_dict['_db_id'],))
    
    def switch_type(self, new_type):
        """Switch between ledger and statement view"""
        self.current_type = new_type
        
        # Reload transactions if batch is selected
        selection = self.batch_listbox.curselection()
        if selection:
            idx = selection[0]
            batch_id = self.batches[idx][0]
            self.load_batch_transactions(batch_id)
    
    def restore_selected(self):
        """Restore selected transactions to active"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select transactions to restore", parent=self)
            return
        
        if messagebox.askyesno("Confirm Restore",
                              f"Restore {len(selected)} transactions to active status?",
                              parent=self):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            table = f"{self.current_type}_outstanding"
            
            for item in selected:
                trans_id = int(self.tree.item(item)['tags'][0])
                cursor.execute(f'''
                    UPDATE {table}
                    SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (trans_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"✅ Restored {len(selected)} transactions to active status!",
                              parent=self)
            
            # Reload
            selection = self.batch_listbox.curselection()
            if selection:
                idx = selection[0]
                batch_id = self.batches[idx][0]
                self.load_batch_transactions(batch_id)
    
    def export_batch(self):
        """Export current batch to Excel"""
        selection = self.batch_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch to export", parent=self)
            return
        
        idx = selection[0]
        batch = self.batches[idx]
        batch_id = batch[0]
        
        file_path = filedialog.asksaveasfilename(
            title=f"Export Batch {batch_id}",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"batch_{batch_id}_{self.current_type}.xlsx",
            parent=self
        )
        
        if not file_path:
            return
        
        try:
            # Get data
            conn = sqlite3.connect(self.db.db_path)
            table = f"{self.current_type}_outstanding"
            df = pd.read_sql_query(f"SELECT * FROM {table} WHERE batch_id = ?", 
                                   conn, params=(batch_id,))
            conn.close()
            
            # Export
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"✅ Exported {len(df)} transactions to:\n{file_path}",
                              parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{e}", parent=self)
    
    def delete_batch(self):
        """Permanently delete a batch and its transactions"""
        selection = self.batch_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch to delete", parent=self)
            return
        
        idx = selection[0]
        batch = self.batches[idx]
        batch_id, account, date, name, ledger_cnt, stmt_cnt, created = batch
        
        if messagebox.askyesno("⚠️ Confirm Permanent Deletion",
                              f"PERMANENTLY DELETE this batch and all its transactions?\n\n"
                              f"Batch: {batch_id}\n"
                              f"Account: {account}\n"
                              f"Ledger: {ledger_cnt} transactions\n"
                              f"Statement: {stmt_cnt} transactions\n\n"
                              f"⚠️ THIS CANNOT BE UNDONE!",
                              parent=self):
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Delete transactions
            cursor.execute("DELETE FROM ledger_outstanding WHERE batch_id = ?", (batch_id,))
            cursor.execute("DELETE FROM statement_outstanding WHERE batch_id = ?", (batch_id,))
            
            # Delete batch record
            cursor.execute("DELETE FROM reconciliation_batches WHERE batch_id = ?", (batch_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Deleted", f"✅ Batch {batch_id} permanently deleted!",
                              parent=self)
            
            # Clear tree first
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear batch info
            self.batch_info_label.config(text="Select a batch to view details")
            
            # Clear any stored data
            if hasattr(self, 'current_data'):
                self.current_data = []
            if hasattr(self, 'display_cols'):
                self.display_cols = []
            
            # Reload batch list
            self.load_batch_list()
    
    def select_all(self):
        """Select all visible transactions"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        self.update_selection_count()
    
    def deselect_all(self):
        """Deselect all transactions"""
        self.tree.selection_remove(*self.tree.selection())
        self.update_selection_count()
    
    def update_selection_count(self, event=None):
        """Update the selection count label"""
        count = len(self.tree.selection())
        self.selection_label.config(text=f"{count} selected")
    
    def sort_by_column(self, col):
        """Sort treeview by column"""
        if not hasattr(self, 'current_data'):
            return
        
        # Get current sort direction
        if not hasattr(self, 'sort_reverse'):
            self.sort_reverse = {}
        
        reverse = not self.sort_reverse.get(col, False)
        self.sort_reverse[col] = reverse
        
        # Sort data
        try:
            self.current_data.sort(key=lambda x: x.get(col, ''), reverse=reverse)
        except:
            pass  # Skip sorting if comparison fails
        
        # Refresh display
        self.refresh_tree_display()
    
    def filter_transactions(self):
        """Filter transactions based on search text"""
        if not hasattr(self, 'current_data'):
            return
        
        search_text = self.search_var.get().lower()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display
        for row_dict in self.current_data:
            # Check if any value matches search
            if not search_text or any(search_text in str(v).lower() 
                                     for v in row_dict.values() if v):
                values = [row_dict.get(col, '') for col in self.display_cols]
                formatted_values = []
                for val in values:
                    if isinstance(val, (int, float)) and val != 0:
                        formatted_values.append(f"{val:,.2f}")
                    else:
                        formatted_values.append(str(val) if val else '')
                
                self.tree.insert("", tk.END, values=formatted_values, tags=(row_dict['_db_id'],))
    
    def refresh_tree_display(self):
        """Refresh tree display with current data"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Display rows
        for row_dict in self.current_data:
            values = [row_dict.get(col, '') for col in self.display_cols]
            formatted_values = []
            for val in values:
                if isinstance(val, (int, float)) and val != 0:
                    formatted_values.append(f"{val:,.2f}")
                else:
                    formatted_values.append(str(val) if val else '')
            
            self.tree.insert("", tk.END, values=formatted_values, tags=(row_dict['_db_id'],))
    
    def edit_selected_transactions(self):
        """Edit selected transactions"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select transactions to edit", parent=self)
            return
        
        if len(selected) > 1:
            messagebox.showinfo("Multiple Selection", 
                              "Bulk edit: Select ONE transaction to edit, or use Delete for multiple.",
                              parent=self)
            return
        
        # Get transaction data
        item = selected[0]
        trans_id = int(self.tree.item(item)['tags'][0])
        
        # Find transaction in current_data
        trans_data = None
        for row in self.current_data:
            if row.get('_db_id') == trans_id:
                trans_data = row
                break
        
        if not trans_data:
            messagebox.showerror("Error", "Transaction data not found", parent=self)
            return
        
        # Create edit dialog
        self.show_edit_dialog(trans_id, trans_data)
    
    def show_edit_dialog(self, trans_id, trans_data):
        """Show dialog to edit transaction"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Transaction {trans_id}")
        dialog.geometry("600x700")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg="#3498db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text=f"✏️ Edit Transaction",
                font=("Segoe UI", 14, "bold"),
                bg="#3498db", fg="white").pack(pady=15)
        
        # Scrollable form
        canvas = tk.Canvas(dialog, bg="white")
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg="white")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        canvas_frame = canvas.create_window((0, 0), window=form_frame, anchor="nw")
        
        # Editable fields
        entries = {}
        row = 0
        
        for col in self.display_cols:
            value = trans_data.get(col, '')
            
            tk.Label(form_frame, text=f"{col.replace('_', ' ').title()}:",
                    font=("Segoe UI", 10, "bold"),
                    bg="white", fg="#2c3e50").grid(row=row, column=0, sticky="w", padx=10, pady=8)
            
            entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=40)
            entry.insert(0, str(value) if value else "")
            entry.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
            entries[col] = entry
            row += 1
        
        form_frame.columnconfigure(1, weight=1)
        
        # Update scroll region
        form_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#f8f9fa")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def save_changes():
            # Build updated original_data
            updated_data = {}
            for col, entry in entries.items():
                value = entry.get().strip()
                if value:
                    # Try to convert to number if possible
                    try:
                        if '.' in value or ',' in value:
                            # Remove commas and convert
                            value = value.replace(',', '')
                            updated_data[col] = float(value)
                        else:
                            try:
                                updated_data[col] = int(value)
                            except:
                                updated_data[col] = value
                    except:
                        updated_data[col] = value
                else:
                    updated_data[col] = value
            
            # Update database
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            table = f"{self.current_type}_outstanding"
            cursor.execute(f'''
                UPDATE {table}
                SET original_data = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(updated_data), trans_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "✅ Transaction updated successfully!", parent=dialog)
            dialog.destroy()
            
            # Reload batch
            selection = self.batch_listbox.curselection()
            if selection:
                idx = selection[0]
                batch_id = self.batches[idx][0]
                self.load_batch_transactions(batch_id)
        
        tk.Button(btn_frame, text="💾 Save Changes",
                 command=save_changes,
                 font=("Segoe UI", 11, "bold"),
                 bg="#27ae60", fg="white",
                 relief="flat", padx=30, pady=12,
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="✖ Cancel",
                 command=dialog.destroy,
                 font=("Segoe UI", 11, "bold"),
                 bg="#95a5a6", fg="white",
                 relief="flat", padx=30, pady=12,
                 cursor="hand2").pack(side="left", padx=5)
    
    def delete_selected_transactions(self):
        """Delete selected transactions from batch"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select transactions to delete", parent=self)
            return
        
        if messagebox.askyesno("⚠️ Confirm Deletion",
                              f"Permanently delete {len(selected)} selected transaction(s)?\n\n"
                              f"⚠️ THIS CANNOT BE UNDONE!",
                              parent=self):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            table = f"{self.current_type}_outstanding"
            
            for item in selected:
                trans_id = int(self.tree.item(item)['tags'][0])
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (trans_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Deleted", f"✅ Deleted {len(selected)} transaction(s)!", parent=self)
            
            # Reload batch
            selection = self.batch_listbox.curselection()
            if selection:
                idx = selection[0]
                batch_id = self.batches[idx][0]
                self.load_batch_transactions(batch_id)


# Integration function for existing workflow
def add_outstanding_features(workflow_instance):
    """Add outstanding transactions features to workflow"""
    try:
        # Initialize database
        workflow_instance.outstanding_db = OutstandingTransactionsDB()
        
        # Add methods to workflow for saving with batch tracking
        def save_outstanding_with_batch(self, account_identifier, recon_date, recon_name, 
                                       ledger_unmatched, statement_unmatched):
            """Save outstanding transactions with batch tracking"""
            db = self.outstanding_db
            
            # Create or get batch
            batch_id = db.get_or_create_batch(account_identifier, recon_date, recon_name)
            
            # Save transactions
            ledger_count = db.save_ledger_outstanding(
                batch_id, account_identifier, recon_date, recon_name, ledger_unmatched
            )
            statement_count = db.save_statement_outstanding(
                batch_id, account_identifier, recon_date, recon_name, statement_unmatched
            )
            
            return batch_id, ledger_count, statement_count
        
        # Bind method to instance
        import types
        workflow_instance.save_outstanding_with_batch = types.MethodType(save_outstanding_with_batch, workflow_instance)
    
        # Add viewer methods
        def show_ledger_outstanding():
            """Show ledger outstanding viewer"""
            db = workflow_instance.outstanding_db
            viewer = OutstandingTransactionsViewer(workflow_instance, "ledger", db, workflow_instance)
        
        def show_statement_outstanding():
            """Show statement outstanding viewer"""
            db = workflow_instance.outstanding_db
            viewer = OutstandingTransactionsViewer(workflow_instance, "statement", db, workflow_instance)
        
        workflow_instance.show_ledger_outstanding = show_ledger_outstanding
        workflow_instance.show_statement_outstanding = show_statement_outstanding
        
        return workflow_instance
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize outstanding transactions: {e}")
        return workflow_instance
