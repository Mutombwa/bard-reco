import sqlite3
import json
import pandas as pd
from datetime import datetime

class ResultsDB:
    DB_PATH = 'reco_results.db'
    def __init__(self):
        self.conn = sqlite3.connect(self.DB_PATH)
        self._create_table()
    def _create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS original_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            file_type TEXT,
            file_data BLOB,
            file_metadata TEXT,
            pair_id TEXT
        )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS reconciliation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            result_type TEXT,
            result_data BLOB,
            result_metadata TEXT
        )''')
        # Add missing columns if needed (migration)
        cur = self.conn.execute("PRAGMA table_info(reconciliation_results)")
        cols = [row[1] for row in cur.fetchall()]
        if 'notes' not in cols:
            self.conn.execute('ALTER TABLE reconciliation_results ADD COLUMN notes TEXT')
        if 'batch_id' not in cols:
            self.conn.execute('ALTER TABLE reconciliation_results ADD COLUMN batch_id TEXT')
        self.conn.commit()
    def save_reconciliation_result(self, name, result_type, result_data, metadata, notes=None, batch_id=None):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        meta_json = json.dumps(metadata)
        result_json = result_data.to_json(orient='records', date_format='iso')
        cursor = self.conn.execute(
            'INSERT INTO reconciliation_results (name, date, result_type, result_data, result_metadata, notes, batch_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, date, result_type, result_json, meta_json, notes, batch_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_reconciliation_results(self):
        return self.conn.execute(
            'SELECT id, name, date, result_type, notes, batch_id FROM reconciliation_results ORDER BY id DESC'
        ).fetchall()

    def get_reconciliation_result(self, result_id):
        row = self.conn.execute(
            'SELECT name, result_type, result_data, notes, batch_id FROM reconciliation_results WHERE id=?', (result_id,)
        ).fetchone()
        if row:
            import io
            return {
                'name': row[0],
                'result_type': row[1],
                'result_data': pd.read_json(io.StringIO(row[2]), orient='records'),
                'notes': row[3],
                'batch_id': row[4]
            }
        return None

    def update_notes(self, result_id, notes):
        self.conn.execute('UPDATE reconciliation_results SET notes=? WHERE id=?', (notes, result_id))
        self.conn.commit()

    def rename_result(self, result_id, new_name):
        self.conn.execute('UPDATE reconciliation_results SET name=? WHERE id=?', (new_name, result_id))
        self.conn.commit()

    def get_batch_results(self, batch_id):
        rows = self.conn.execute('SELECT id, name, result_type, result_data FROM reconciliation_results WHERE batch_id=?', (batch_id,)).fetchall()
        import io
        import pandas as pd
        results = {}
        for row in rows:
            results[row[2]] = pd.read_json(io.StringIO(row[3]), orient='records')
        return results

    def delete_reconciliation_result(self, result_id):
        cursor = self.conn.execute('DELETE FROM reconciliation_results WHERE id=?', (result_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    def save_original_file(self, name, file_type, file_data, metadata, pair_id=None):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        meta_json = json.dumps(metadata)
        file_json = file_data.to_json(orient='records', date_format='iso')
        cursor = self.conn.execute(
            'INSERT INTO original_files (pair_id, name, date, file_type, file_data, file_metadata) VALUES (?, ?, ?, ?, ?, ?)',
            (pair_id, name, date, file_type, file_json, meta_json)
        )
        self.conn.commit()
        return cursor.lastrowid
    def list_original_files(self):
        return self.conn.execute(
            'SELECT id, pair_id, name, date, file_type FROM original_files ORDER BY id DESC'
        ).fetchall()
    def get_original_file(self, file_id):
        row = self.conn.execute(
            'SELECT name, file_type, file_data FROM original_files WHERE id=?', (file_id,)
        ).fetchone()
        if row:
            import io
            return {
                'name': row[0],
                'file_type': row[1],
                'file_data': pd.read_json(io.StringIO(row[2]), orient='records')
            }
        return None
    def delete_original_file(self, file_id):
        cursor = self.conn.execute('DELETE FROM original_files WHERE id=?', (file_id,))
        self.conn.commit()
        return cursor.rowcount > 0
