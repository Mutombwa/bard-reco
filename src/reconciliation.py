# reconciliation.py

import pandas as pd
import numpy as np
from rapidfuzz.fuzz import ratio
from utils.excel_utils import read_excel, write_excel

class Reconciliation:
    def __init__(self, st_data_path, cb_data_path):
        self.st_data = read_excel(st_data_path)
        self.cb_data = read_excel(cb_data_path)
        self.results = {
            '100% MATCH': [],
            'BALANCED': [],
            '85% FUZZY': [],
            '60% FUZZY': [],
            'UNMATCHED': []
        }
        self.matched_cb_indices = set()
        self.matched_st_indices = set()

    def fuzzy_ratio(self, a, b):
        return ratio(str(a).lower(), str(b).lower()) / 100.0

    def reconcile(self, match_cols=None, fuzzy_flags=None, progress_callback=None, mode="Bank"):
        st_used = set()
        cb_used = set()
        st_col_map = {col.strip().lower(): col for col in self.st_data.columns}
        cb_col_map = {col.strip().lower(): col for col in self.cb_data.columns}
        def get_col(col, col_map):
            return col_map.get(col.strip().lower(), col)
        total = len(self.st_data)
        processed = 0
        # Branch mode: special amount matching logic
        if mode == "Branch" and match_cols and len(match_cols) >= 3:
            cb_amt_col = match_cols[0][0]  # Cashbook amount col
            st_recv_col = match_cols[0][1]  # Statement Received col
            st_paid_col = match_cols[1][1]  # Statement Paid col
            date_pair = match_cols[1]  # (cb_date, st_date)
            ref_pair = match_cols[2]   # (cb_ref, st_ref)
            # --- Further Optimization: Aggressive filtering and full vectorization ---
            cb_df = self.cb_data.copy()
            st_df = self.st_data.copy()
            # Precompute amounts and dates
            def parse_amt(val):
                try:
                    return float(str(val).replace('(', '-').replace(')', '').replace(',', ''))
                except Exception:
                    return 0
            cb_df['__amt'] = cb_df[cb_amt_col].apply(parse_amt)
            st_df['__recv'] = st_df[st_recv_col].apply(parse_amt)
            st_df['__paid'] = st_df[st_paid_col].apply(parse_amt)
            cb_df['__date'] = pd.to_datetime(cb_df[date_pair[0]], errors='coerce')
            st_df['__date'] = pd.to_datetime(st_df[date_pair[1]], errors='coerce')
            cb_df['__ref'] = cb_df[ref_pair[0]].astype(str).str.lower()
            st_df['__ref'] = st_df[ref_pair[1]].astype(str).str.lower()

            # Use pandas merge to join on date, then filter by amount tolerance (vectorized, no Python loops)
            tolerance = 0.01  # Amount tolerance
            st_df = st_df.reset_index().rename(columns={'index': 'st_idx'})
            cb_df = cb_df.reset_index().rename(columns={'index': 'cb_idx'})
            merged = pd.merge(st_df, cb_df, on='__date', suffixes=('_st', '_cb'))
            # Only keep rows where amounts are close (received or paid)
            mask = ((merged['__amt'] >= 0) & (abs(merged['__amt'] - merged['__recv']) <= tolerance)) | \
                   ((merged['__amt'] < 0) & (abs(merged['__amt'] - merged['__paid']) <= tolerance))
            merged = merged[mask]

            if merged.empty:
                for st_idx, st_row in self.st_data.iterrows():
                    if st_idx not in st_used:
                        self.results['UNMATCHED'].append((st_row, None))
                for cb_idx, cb_row in self.cb_data.iterrows():
                    if cb_idx not in cb_used:
                        self.results['UNMATCHED'].append((None, cb_row))
                return

            # Now, only fuzzy match references for these candidates
            from rapidfuzz.process import cdist
            st_refs = merged['__ref_st'].tolist()
            cb_refs = merged['__ref_cb'].tolist()
            scores = cdist(st_refs, cb_refs, scorer=ratio, score_cutoff=90)
            # Assign matches greedily (one-to-one)
            matched_st = set()
            matched_cb = set()
            for idx, row in merged.iterrows():
                i = idx  # row index in merged
                st_idx = row['st_idx']
                cb_idx = row['cb_idx']
                if st_idx in matched_st or cb_idx in matched_cb:
                    continue
                # Use the diagonal of the score matrix (since merge is 1:1)
                if i < scores.shape[0] and i < scores.shape[1] and scores[i, i] >= 90:
                    self.results['100% MATCH'].append((self.st_data.loc[st_idx], self.cb_data.loc[cb_idx]))
                    cb_used.add(cb_idx)
                    st_used.add(st_idx)
                    matched_cb.add(cb_idx)
                    matched_st.add(st_idx)
                processed += 1
                if progress_callback:
                    progress_callback(processed, total)
            # Unmatched
            for st_idx, st_row in self.st_data.iterrows():
                if st_idx not in st_used:
                    self.results['UNMATCHED'].append((st_row, None))
            for cb_idx, cb_row in self.cb_data.iterrows():
                if cb_idx not in cb_used:
                    self.results['UNMATCHED'].append((None, cb_row))
            return
        # 1. 100% MATCH: all selected pairs, per-pair fuzzy/exact (strict)
        for st_idx, st_row in self.st_data.iterrows():
            for cb_idx, cb_row in self.cb_data.iterrows():
                if cb_idx in cb_used or st_idx in st_used:
                    continue
                all_match = True
                for i, pair in enumerate(match_cols or []):
                    st_col, cb_col = pair
                    st_real = get_col(st_col, st_col_map)
                    cb_real = get_col(cb_col, cb_col_map)
                    st_val = st_row.get(st_real, '')
                    cb_val = cb_row.get(cb_real, '')
                    fuzzy = fuzzy_flags[i] if fuzzy_flags and i < len(fuzzy_flags) else False
                    # Try to parse as date if possible
                    try:
                        st_val_dt = pd.to_datetime(st_val, errors='coerce')
                        cb_val_dt = pd.to_datetime(cb_val, errors='coerce')
                        if not pd.isnull(st_val_dt) and not pd.isnull(cb_val_dt):
                            if st_val_dt != cb_val_dt:
                                all_match = False
                                break
                            continue
                    except Exception:
                        pass
                    # Compare as float if possible
                    try:
                        if float(st_val) == float(cb_val):
                            continue
                    except Exception:
                        pass
                    # Fuzzy or exact
                    if fuzzy:
                        if self.fuzzy_ratio(st_val, cb_val) < 0.85:
                            all_match = False
                            break
                    else:
                        if str(st_val).strip().lower() != str(cb_val).strip().lower():
                            all_match = False
                            break
                if all_match:
                    self.results['100% MATCH'].append((st_row, cb_row))
                    cb_used.add(cb_idx)
                    st_used.add(st_idx)
                    break
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
        # 2. BALANCED: all selected pairs, per-pair fuzzy/exact, but allow one mismatch (for fallback grouping)
        for st_idx, st_row in self.st_data.iterrows():
            if st_idx in st_used:
                continue
            for cb_idx, cb_row in self.cb_data.iterrows():
                if cb_idx in cb_used:
                    continue
                matches = 0
                for i, pair in enumerate(match_cols or []):
                    st_col, cb_col = pair
                    st_real = get_col(st_col, st_col_map)
                    cb_real = get_col(cb_col, cb_col_map)
                    st_val = st_row.get(st_real, '')
                    cb_val = cb_row.get(cb_real, '')
                    fuzzy = fuzzy_flags[i] if fuzzy_flags and i < len(fuzzy_flags) else False
                    # Try to parse as date if possible
                    try:
                        st_val_dt = pd.to_datetime(st_val, errors='coerce')
                        cb_val_dt = pd.to_datetime(cb_val, errors='coerce')
                        if not pd.isnull(st_val_dt) and not pd.isnull(cb_val_dt):
                            if st_val_dt == cb_val_dt:
                                matches += 1
                                continue
                    except Exception:
                        pass
                    try:
                        if float(st_val) == float(cb_val):
                            matches += 1
                            continue
                    except Exception:
                        pass
                    if fuzzy:
                        if self.fuzzy_ratio(st_val, cb_val) >= 0.85:
                            matches += 1
                    else:
                        if str(st_val).strip().lower() == str(cb_val).strip().lower():
                            matches += 1
                if matches == len(match_cols) - 1 and len(match_cols) > 1:
                    self.results['BALANCED'].append((st_row, cb_row))
                    cb_used.add(cb_idx)
                    st_used.add(st_idx)
                    break
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
        # 3. 85% FUZZY: at least one fuzzy pair >=0.85, others exact
        for st_idx, st_row in self.st_data.iterrows():
            if st_idx in st_used:
                continue
            for cb_idx, cb_row in self.cb_data.iterrows():
                if cb_idx in cb_used:
                    continue
                fuzzy_match = False
                all_others_exact = True
                for i, pair in enumerate(match_cols or []):
                    st_col, cb_col = pair
                    st_real = get_col(st_col, st_col_map)
                    cb_real = get_col(cb_col, cb_col_map)
                    st_val = st_row.get(st_real, '')
                    cb_val = cb_row.get(cb_real, '')
                    fuzzy = fuzzy_flags[i] if fuzzy_flags and i < len(fuzzy_flags) else False
                    if fuzzy:
                        if self.fuzzy_ratio(st_val, cb_val) >= 0.85:
                            fuzzy_match = True
                        else:
                            all_others_exact = False
                            break
                    else:
                        if str(st_val).strip().lower() != str(cb_val).strip().lower():
                            all_others_exact = False
                            break
                if fuzzy_match and all_others_exact:
                    self.results['85% FUZZY'].append((st_row, cb_row))
                    cb_used.add(cb_idx)
                    st_used.add(st_idx)
                    break
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
        # 4. 60% FUZZY: at least one fuzzy pair >=0.6, others exact
        for st_idx, st_row in self.st_data.iterrows():
            if st_idx in st_used:
                continue
            for cb_idx, cb_row in self.cb_data.iterrows():
                if cb_idx in cb_used:
                    continue
                fuzzy_match = False
                all_others_exact = True
                for i, pair in enumerate(match_cols or []):
                    st_col, cb_col = pair
                    st_real = get_col(st_col, st_col_map)
                    cb_real = get_col(cb_col, cb_col_map)
                    st_val = st_row.get(st_real, '')
                    cb_val = cb_row.get(cb_real, '')
                    fuzzy = fuzzy_flags[i] if fuzzy_flags and i < len(fuzzy_flags) else False
                    if fuzzy:
                        if self.fuzzy_ratio(st_val, cb_val) >= 0.6:
                            fuzzy_match = True
                        else:
                            all_others_exact = False
                            break
                    else:
                        if str(st_val).strip().lower() != str(cb_val).strip().lower():
                            all_others_exact = False
                            break
                if fuzzy_match and all_others_exact:
                    self.results['60% FUZZY'].append((st_row, cb_row))
                    cb_used.add(cb_idx)
                    st_used.add(st_idx)
                    break
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
        # 5. UNMATCHED
        for st_idx, st_row in self.st_data.iterrows():
            if st_idx not in st_used:
                self.results['UNMATCHED'].append((st_row, None))
        for cb_idx, cb_row in self.cb_data.iterrows():
            if cb_idx not in cb_used:
                self.results['UNMATCHED'].append((None, cb_row))

    def output_results(self, output_path, selected_cb=None, selected_st=None):
        import pandas as pd
        import openpyxl
        cb_cols = selected_cb if selected_cb else list(self.cb_data.columns)
        st_cols = selected_st if selected_st else list(self.st_data.columns)
        # Ensure RJ_Number and Payment_Ref columns are up-to-date in cb_data
        for col in ['RJ_Number', 'Payment_Ref']:
            if col in self.cb_data.columns and col not in cb_cols:
                cb_cols.append(col)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "All Results"
        # Insert a blank column between cashbook and statement columns
        headers = cb_cols + [''] + st_cols + ['Batch']
        ws.append(headers)
        row_idx = 2  # Start from row 2
        # Write BALANCED (all matches) first, then two empty rows, then UNMATCHED
        # Gather all balanced batches
        balanced_batches = ['100% MATCH', 'BALANCED', '85% FUZZY', '60% FUZZY']
        for batch_key in balanced_batches:
            batch = self.results[batch_key]
            if not batch:
                continue
            for pair in batch:
                st_row, cb_row = pair if pair[1] is not None else (pair[0], None)
                row = []
                for col in cb_cols:
                    # Always pull from cb_data for RJ_Number and Payment_Ref
                    if col in ['RJ_Number', 'Payment_Ref']:
                        val = cb_row[col] if cb_row is not None and col in cb_row else ''
                        if not val and cb_row is not None and 'Comment' in cb_row:
                            import re
                            if col == 'RJ_Number':
                                m = re.search(r'(TX\d{8,}|RJ\d{8,})', str(cb_row['Comment']))
                                val = m.group(1) if m else ''
                            elif col == 'Payment_Ref':
                                m = re.search(r'Payment Ref #\s*([A-Za-z0-9_\- ]+)', str(cb_row['Comment']))
                                if m:
                                    val = m.group(1).strip().strip(',')
                                else:
                                    m2 = re.search(r'RJ\d{8,}\}?\s*([A-Za-z0-9_\- ]+)', str(cb_row['Comment']))
                                    val = m2.group(1).strip().strip(',') if m2 else ''
                        row.append(val)
                    else:
                        row.append(cb_row[col] if cb_row is not None and col in cb_row else '')
                row.append('')  # separator column
                for col in st_cols:
                    row.append(st_row[col] if st_row is not None and col in st_row else '')
                row.append('BALANCED')
                ws.append(row)
                row_idx += 1
        # Two empty rows before unmatched
        ws.append([])
        ws.append([])
        row_idx += 2
        # Write unmatched
        for pair in self.results['UNMATCHED']:
            st_row, cb_row = pair if pair[1] is not None else (pair[0], None)
            row = []
            for col in cb_cols:
                if col in ['RJ_Number', 'Payment_Ref']:
                    val = cb_row[col] if cb_row is not None and col in cb_row else ''
                    if not val and cb_row is not None and 'Comment' in cb_row:
                        import re
                        if col == 'RJ_Number':
                            m = re.search(r'(TX\d{8,}|RJ\d{8,})', str(cb_row['Comment']))
                            val = m.group(1) if m else ''
                        elif col == 'Payment_Ref':
                            m = re.search(r'Payment Ref #\s*([A-Za-z0-9_\- ]+)', str(cb_row['Comment']))
                            if m:
                                val = m.group(1).strip().strip(',')
                            else:
                                m2 = re.search(r'RJ\d{8,}\}?\s*([A-Za-z0-9_\- ]+)', str(cb_row['Comment']))
                                val = m2.group(1).strip().strip(',') if m2 else ''
                    row.append(val)
                else:
                    row.append(cb_row[col] if cb_row is not None and col in cb_row else '')
            row.append('')
            for col in st_cols:
                row.append(st_row[col] if st_row is not None and col in st_row else '')
            row.append('UNBALANCED')
            ws.append(row)
            row_idx += 1
        wb.save(output_path)

def reconcile_transactions(st_data_path, cb_data_path, match_cols=None, selected_columns=None, progress_callback=None):
    recon = Reconciliation(st_data_path, cb_data_path)
    recon.reconcile(match_cols=match_cols, progress_callback=progress_callback)
    return recon.results