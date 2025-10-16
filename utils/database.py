"""
Database Utility for Saving Reconciliation Results
==================================================
Stores reconciliation results in SQLite database for history and retrieval
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
from pathlib import Path


class ReconciliationDB:
    """Database manager for reconciliation results"""

    def __init__(self, db_path='streamlit-app/data/reconciliation_results.db'):
        """Initialize database connection"""
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables"""

        # Results table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                date_created TEXT NOT NULL,
                metadata TEXT,
                data TEXT,
                summary TEXT
            )
        ''')

        # Results details table for matched pairs
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS matched_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER,
                match_score REAL,
                ledger_data TEXT,
                statement_data TEXT,
                FOREIGN KEY (result_id) REFERENCES results (id)
            )
        ''')

        # Unmatched ledger transactions
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS unmatched_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER,
                transaction_data TEXT,
                FOREIGN KEY (result_id) REFERENCES results (id)
            )
        ''')

        # Unmatched statement transactions
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS unmatched_statement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER,
                transaction_data TEXT,
                FOREIGN KEY (result_id) REFERENCES results (id)
            )
        ''')

        self.conn.commit()

    def save_result(self, name, workflow_type, results, metadata=None):
        """
        Save reconciliation results to database

        Args:
            name: Result name/identifier
            workflow_type: Type of workflow (FNB, Bidvest, Corporate)
            results: Dictionary containing reconciliation results
            metadata: Additional metadata dictionary

        Returns:
            result_id: ID of saved result
        """
        try:
            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Prepare metadata
            meta_json = json.dumps(metadata) if metadata else '{}'

            # Prepare summary
            summary = {}
            if 'summary' in results:
                if isinstance(results['summary'], pd.DataFrame):
                    summary = results['summary'].iloc[0].to_dict() if len(results['summary']) > 0 else {}
                else:
                    summary = results['summary']

            summary_json = json.dumps(summary)

            # Serialize full results (excluding large dataframes but including counts and split info)
            data_light = {
                'has_matched': 'matched' in results and not results['matched'].empty,
                'has_unmatched_ledger': 'unmatched_ledger' in results and not results['unmatched_ledger'].empty,
                'has_unmatched_statement': 'unmatched_statement' in results and not results['unmatched_statement'].empty,
                'matched_count': len(results.get('matched', [])),
                'unmatched_ledger_count': len(results.get('unmatched_ledger', [])),
                'unmatched_statement_count': len(results.get('unmatched_statement', [])),
                'split_count': len(results.get('split_matches', [])),
                'perfect_match_count': results.get('perfect_match_count', 0),
                'fuzzy_match_count': results.get('fuzzy_match_count', 0),
                'foreign_credits_count': results.get('foreign_credits_count', 0),
                'total_matched': results.get('total_matched', 0),
                'split_matches': results.get('split_matches', [])  # Include split matches
            }
            data_json = json.dumps(data_light, default=str)

            # Insert main result record
            cursor = self.conn.execute(
                '''INSERT INTO results (name, workflow_type, date_created, metadata, data, summary)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (name, workflow_type, date_created, meta_json, data_json, summary_json)
            )
            result_id = cursor.lastrowid

            # Save matched transactions
            if 'matched' in results and not results['matched'].empty:
                for _, row in results['matched'].iterrows():
                    match_score = row.get('Match_Score', 0)
                    ledger_data = {k: v for k, v in row.items() if k.startswith('Ledger_')}
                    statement_data = {k: v for k, v in row.items() if k.startswith('Statement_')}

                    self.conn.execute(
                        '''INSERT INTO matched_transactions (result_id, match_score, ledger_data, statement_data)
                           VALUES (?, ?, ?, ?)''',
                        (result_id, match_score, json.dumps(ledger_data), json.dumps(statement_data))
                    )

            # Save unmatched ledger
            if 'unmatched_ledger' in results and not results['unmatched_ledger'].empty:
                for _, row in results['unmatched_ledger'].iterrows():
                    transaction_data = row.to_dict()
                    self.conn.execute(
                        '''INSERT INTO unmatched_ledger (result_id, transaction_data)
                           VALUES (?, ?)''',
                        (result_id, json.dumps(transaction_data))
                    )

            # Save unmatched statement
            if 'unmatched_statement' in results and not results['unmatched_statement'].empty:
                for _, row in results['unmatched_statement'].iterrows():
                    transaction_data = row.to_dict()
                    self.conn.execute(
                        '''INSERT INTO unmatched_statement (result_id, transaction_data)
                           VALUES (?, ?)''',
                        (result_id, json.dumps(transaction_data))
                    )

            self.conn.commit()
            return result_id

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to save result: {str(e)}")

    def list_results(self, workflow_type=None, limit=50):
        """
        List saved reconciliation results

        Args:
            workflow_type: Filter by workflow type (optional)
            limit: Maximum number of results to return

        Returns:
            List of result records
        """
        query = 'SELECT id, name, workflow_type, date_created, summary FROM results'
        params = []

        if workflow_type:
            query += ' WHERE workflow_type = ?'
            params.append(workflow_type)

        query += ' ORDER BY date_created DESC LIMIT ?'
        params.append(limit)

        cursor = self.conn.execute(query, params)
        return cursor.fetchall()

    def get_result(self, result_id):
        """
        Retrieve a specific reconciliation result

        Args:
            result_id: ID of the result to retrieve

        Returns:
            Dictionary containing full result data
        """
        # Get main result
        cursor = self.conn.execute(
            'SELECT id, name, workflow_type, date_created, metadata, data, summary FROM results WHERE id = ?',
            (result_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        # Parse data to restore counts and split matches
        data = json.loads(row[5]) if row[5] else {}
        
        result = {
            'id': row[0],
            'name': row[1],
            'workflow_type': row[2],
            'date_created': row[3],
            'metadata': json.loads(row[4]) if row[4] else {},
            'data': data,
            'summary': json.loads(row[6]) if row[6] else {},
            # Restore count keys for dashboard
            'perfect_match_count': data.get('perfect_match_count', 0),
            'fuzzy_match_count': data.get('fuzzy_match_count', 0),
            'foreign_credits_count': data.get('foreign_credits_count', 0),
            'split_count': data.get('split_count', 0),
            'total_matched': data.get('total_matched', 0),
            'unmatched_ledger_count': data.get('unmatched_ledger_count', 0),
            'unmatched_statement_count': data.get('unmatched_statement_count', 0),
            'split_matches': data.get('split_matches', []),
            'timestamp': row[3]
        }

        # Get matched transactions
        cursor = self.conn.execute(
            'SELECT match_score, ledger_data, statement_data FROM matched_transactions WHERE result_id = ?',
            (result_id,)
        )
        matched_rows = cursor.fetchall()
        if matched_rows:
            matched_data = []
            for match_score, ledger_data, statement_data in matched_rows:
                row_data = {'Match_Score': match_score}
                row_data.update(json.loads(ledger_data))
                row_data.update(json.loads(statement_data))
                matched_data.append(row_data)
            result['matched'] = pd.DataFrame(matched_data)
        else:
            result['matched'] = pd.DataFrame()

        # Get unmatched ledger
        cursor = self.conn.execute(
            'SELECT transaction_data FROM unmatched_ledger WHERE result_id = ?',
            (result_id,)
        )
        unmatched_ledger_rows = cursor.fetchall()
        if unmatched_ledger_rows:
            result['unmatched_ledger'] = pd.DataFrame([json.loads(row[0]) for row in unmatched_ledger_rows])
        else:
            result['unmatched_ledger'] = pd.DataFrame()

        # Get unmatched statement
        cursor = self.conn.execute(
            'SELECT transaction_data FROM unmatched_statement WHERE result_id = ?',
            (result_id,)
        )
        unmatched_statement_rows = cursor.fetchall()
        if unmatched_statement_rows:
            result['unmatched_statement'] = pd.DataFrame([json.loads(row[0]) for row in unmatched_statement_rows])
        else:
            result['unmatched_statement'] = pd.DataFrame()

        return result

    def delete_result(self, result_id):
        """Delete a reconciliation result and all associated data"""
        try:
            self.conn.execute('DELETE FROM matched_transactions WHERE result_id = ?', (result_id,))
            self.conn.execute('DELETE FROM unmatched_ledger WHERE result_id = ?', (result_id,))
            self.conn.execute('DELETE FROM unmatched_statement WHERE result_id = ?', (result_id,))
            self.conn.execute('DELETE FROM results WHERE id = ?', (result_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to delete result: {str(e)}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global database instance
_db_instance = None


def get_db():
    """Get or create database instance (singleton pattern)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ReconciliationDB()
    return _db_instance
