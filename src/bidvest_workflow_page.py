import tkinter as tk
from tkinter import messagebox, ttk
import re
import platform
from datetime import datetime

# Import collaboration features
try:
    from enhanced_export_dialog import EnhancedExportDialog
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False

# Web dashboard integration removed as requested

class BidvestWorkflowPage(tk.Frame):
    def manage_results(self):
        from results_db import ResultsDB
        import pandas as pd
        db = ResultsDB()
        results = db.list_reconciliation_results()
        win = tk.Toplevel(self)
        win.title("Manage Saved Results")
        win.state('zoomed')
        search_var = tk.StringVar()
        def filter_table(*_):
            val = search_var.get().lower()
            for iid in tree.get_children():
                values = tree.item(iid)['values']
                if any(val in str(v).lower() for v in values):
                    tree.reattach(iid, '', 'end')
                else:
                    tree.detach(iid)
        topbar = tk.Frame(win)
        topbar.pack(fill='x', pady=8)
        tk.Label(topbar, text="Search:", font=("Segoe UI", 10)).pack(side='left', padx=(10,2))
        search_entry = tk.Entry(topbar, textvariable=search_var, font=("Segoe UI", 10), width=30)
        search_entry.pack(side='left')
        search_var.trace_add('write', filter_table)
        tree = ttk.Treeview(win, columns=("id", "name", "date", "type"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("name", text="Name")
        tree.heading("date", text="Date")
        tree.heading("type", text="Type")
        tree.pack(fill='both', expand=True, padx=20, pady=10)
        for r in results:
            tree.insert('', 'end', values=r)
        def on_view():
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])['values']
            result_id = item[0]
            result = db.get_reconciliation_result(result_id)
            if result:
                df = result['result_data']
                view_win = tk.Toplevel(win)
                view_win.title(f"Result: {result['name']} ({result['result_type']})")
                txt = tk.Text(view_win, wrap='none')
                txt.pack(expand=True, fill='both')
                txt.insert('end', df.to_string(index=False))
        def on_delete():
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])['values']
            result_id = item[0]
            if messagebox.askyesno("Delete", "Delete this result?"):
                db.delete_reconciliation_result(result_id)
                tree.delete(sel[0])
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill='x', pady=8)
        tk.Button(btn_frame, text="View", command=on_view, font=("Segoe UI", 10)).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Delete", command=on_delete, font=("Segoe UI", 10)).pack(side='left', padx=10)
    def save_results(self):
        from tkinter import simpledialog
        from results_db import ResultsDB
        import uuid
        import pandas as pd
        if not hasattr(self, 'ledger_df') or not hasattr(self, 'statement_df') or self.ledger_df is None or self.statement_df is None:
            messagebox.showwarning("No Data", "Please import and reconcile data first.", parent=self)
            return
        name = simpledialog.askstring("Save Results", "Enter a name for these reconciliation results:")
        if not name:
            return
        batch_id = str(uuid.uuid4())
        db = ResultsDB()
        
        # Get all matched pairs (100% exact matches)
        exact_matched_pairs = getattr(self, 'matched_pairs', [])
        # Get grouped matches
        grouped_matched_pairs = getattr(self, 'grouped_pairs', [])
        
        # Safely extract column names and convert to strings
        ledger_cols = [str(col) for col in self.ledger_df.columns if col is not None]
        stmt_cols = [str(col) for col in self.statement_df.columns if col is not None]
        
        # Build 100% exact matched results
        exact_matched_rows = []
        for li, si in exact_matched_pairs:
            lrow = self.ledger_df.loc[li, ledger_cols].copy()
            srow = self.statement_df.loc[si, stmt_cols].copy()
            lrow.index = [f"Ledger_{col}" for col in ledger_cols]
            srow.index = [f"Statement_{col}" for col in stmt_cols]
            row = pd.concat([lrow, srow])
            exact_matched_rows.append(row)
        exact_matched_df = pd.DataFrame(exact_matched_rows) if exact_matched_rows else pd.DataFrame()
        
        # Build grouped matched results
        grouped_matched_rows = []
        for li, si in grouped_matched_pairs:
            lrow = self.ledger_df.loc[li, ledger_cols].copy()
            srow = self.statement_df.loc[si, stmt_cols].copy()
            lrow.index = [f"Ledger_{col}" for col in ledger_cols]
            srow.index = [f"Statement_{col}" for col in stmt_cols]
            row = pd.concat([lrow, srow])
            grouped_matched_rows.append(row)
        grouped_matched_df = pd.DataFrame(grouped_matched_rows) if grouped_matched_rows else pd.DataFrame()
        
        # Unmatched results
        unmatched_ledger = self.ledger_df[self.ledger_df['Matched']==False]
        unmatched_stmt = self.statement_df[self.statement_df['Matched']==False]
        
        # Save 100% exact matches
        if not exact_matched_df.empty:
            meta = {'source': 'Bidvest', 'type': 'exact_matched', 'match_rule': 'date_plus_1_exact_amount'}
            db.save_reconciliation_result(name, 'exact_matched', exact_matched_df, meta, batch_id=batch_id)
        
        # Save grouped matches
        if not grouped_matched_df.empty:
            meta_grouped = {'source': 'Bidvest', 'type': 'grouped_matched', 'match_rule': 'same_date_same_amount'}
            db.save_reconciliation_result(name, 'grouped_matched', grouped_matched_df, meta_grouped, batch_id=batch_id)
        
        # Save unmatched ledger
        if not unmatched_ledger.empty:
            meta_ledger = {'source': 'Bidvest', 'type': 'unmatched_ledger'}
            db.save_reconciliation_result(name, 'unmatched_ledger', unmatched_ledger, meta_ledger, batch_id=batch_id)
        
        # Save unmatched statement
        if not unmatched_stmt.empty:
            meta_stmt = {'source': 'Bidvest', 'type': 'unmatched_statement'}
            db.save_reconciliation_result(name, 'unmatched_statement', unmatched_stmt, meta_stmt, batch_id=batch_id)
        
        exact_count = len(exact_matched_pairs)
        grouped_count = len(grouped_matched_pairs)
        unmatched_l_count = len(unmatched_ledger)
        unmatched_s_count = len(unmatched_stmt)
        
        summary = f"✅ Reconciliation results saved successfully!\n\n"
        summary += f"📊 Results Summary:\n"
        summary += f"• 100% Exact Matches: {exact_count}\n"
        summary += f"• Grouped Matches: {grouped_count}\n"
        summary += f"• Unmatched Ledger: {unmatched_l_count}\n"
        summary += f"• Unmatched Statement: {unmatched_s_count}\n\n"
        summary += f"🔄 Batch ID: {batch_id[:8]}..."
        
        messagebox.showinfo("Results Saved", summary)

    


    def export_results_popup_enhanced(self):
        """Enhanced export with collaboration post functionality for Bidvest"""
        # Check if we have reconciliation results in Bidvest format
        has_matched_pairs = hasattr(self, 'matched_pairs') and self.matched_pairs
        has_grouped_pairs = hasattr(self, 'grouped_pairs') and self.grouped_pairs
        has_ledger_data = hasattr(self, 'ledger_df') and self.ledger_df is not None and not self.ledger_df.empty
        has_statement_data = hasattr(self, 'statement_df') and self.statement_df is not None and not self.statement_df.empty
        
        if not (has_matched_pairs or has_grouped_pairs or has_ledger_data or has_statement_data):
            messagebox.showwarning("No Results", "Please run reconciliation first or upload data files.", parent=self)
            return
        
        # Prepare results data for export
        results_data = self.prepare_bidvest_export_data()
        
        # Get collaboration manager from main app if available
        collab_mgr = None
        if hasattr(self, 'app') and hasattr(self.app, 'collab_mgr') and self.app.collaboration_enabled:
            collab_mgr = self.app.collab_mgr
        
        # Show enhanced export dialog with collaboration features
        try:
            if COLLABORATION_AVAILABLE and collab_mgr:
                export_dialog = EnhancedExportDialog(self, "Bidvest", results_data, collab_mgr)
                export_dialog.show()
            else:
                # Fallback to original export
                self.export_results_popup()
        except Exception as e:
            print(f"Enhanced export failed: {e}")
            # Fallback to original export
            self.export_results_popup()
    
    def prepare_bidvest_reconcile_results(self):
        """Convert Bidvest data to standard reconciliation results format for Post System"""
        try:
            # Convert Bidvest-specific results to standard format
            reconcile_results = {
                'matched': [],
                'foreign_credits': [],
                'split_matches': [],
                'unmatched_statement': [],
                'unmatched_ledger': []
            }
            
            # Process exact matches (matched_pairs)
            if hasattr(self, 'matched_pairs') and self.matched_pairs:
                for pair in self.matched_pairs:
                    if len(pair) >= 2:
                        ledger_idx, statement_idx = pair[0], pair[1]
                        
                        match_data = {
                            'type': 'exact_match',
                            'ledger_idx': ledger_idx,
                            'statement_idx': statement_idx,
                            'similarity': 100.0
                        }
                        
                        # Add ledger data if available
                        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                            try:
                                ledger_row = self.ledger_df.iloc[ledger_idx].to_dict()
                                match_data.update({f'ledger_{k}': v for k, v in ledger_row.items()})
                                # Extract amount for analysis
                                if 'Amount' in ledger_row:
                                    match_data['Amount'] = ledger_row['Amount']
                                elif 'amount' in ledger_row:
                                    match_data['Amount'] = ledger_row['amount']
                            except Exception as e:
                                match_data['ledger_error'] = str(e)
                        
                        # Add statement data if available
                        if hasattr(self, 'statement_df') and self.statement_df is not None:
                            try:
                                statement_row = self.statement_df.iloc[statement_idx].to_dict()
                                match_data.update({f'statement_{k}': v for k, v in statement_row.items()})
                                # Use statement amount if ledger amount not found
                                if 'Amount' not in match_data and 'Amount' in statement_row:
                                    match_data['Amount'] = statement_row['Amount']
                                elif 'Amount' not in match_data and 'amount' in statement_row:
                                    match_data['Amount'] = statement_row['amount']
                            except Exception as e:
                                match_data['statement_error'] = str(e)
                        
                        # Check if this should be classified as foreign credit (high value)
                        amount = abs(match_data.get('Amount', 0))
                        if amount > 10000:  # Foreign credit threshold
                            match_data['foreign_credit_candidate'] = True
                            reconcile_results['foreign_credits'].append(match_data)
                        else:
                            reconcile_results['matched'].append(match_data)
            
            # Process grouped matches (grouped_pairs) - these could be split transactions
            if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                for pair in self.grouped_pairs:
                    if len(pair) >= 2:
                        ledger_idx, statement_idx = pair[0], pair[1]
                        
                        split_data = {
                            'type': 'grouped_match',
                            'ledger_idx': ledger_idx,
                            'statement_idx': statement_idx,
                            'similarity': 100.0,
                            'is_grouped': True
                        }
                        
                        # Add ledger data
                        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                            try:
                                ledger_row = self.ledger_df.iloc[ledger_idx].to_dict()
                                split_data.update({f'ledger_{k}': v for k, v in ledger_row.items()})
                                if 'Amount' in ledger_row:
                                    split_data['Amount'] = ledger_row['Amount']
                                elif 'amount' in ledger_row:
                                    split_data['Amount'] = ledger_row['amount']
                            except Exception as e:
                                split_data['ledger_error'] = str(e)
                        
                        # Add statement data
                        if hasattr(self, 'statement_df') and self.statement_df is not None:
                            try:
                                statement_row = self.statement_df.iloc[statement_idx].to_dict()
                                split_data.update({f'statement_{k}': v for k, v in statement_row.items()})
                                if 'Amount' not in split_data and 'Amount' in statement_row:
                                    split_data['Amount'] = statement_row['Amount']
                                elif 'Amount' not in split_data and 'amount' in statement_row:
                                    split_data['Amount'] = statement_row['amount']
                            except Exception as e:
                                split_data['statement_error'] = str(e)
                        
                        # Classify grouped matches as potential split transactions
                        reconcile_results['split_matches'].append(split_data)
            
            # Process unmatched ledger items
            if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                matched_ledger_indices = set()
                
                # Collect all matched ledger indices
                if hasattr(self, 'matched_pairs') and self.matched_pairs:
                    for pair in self.matched_pairs:
                        if len(pair) >= 1:
                            matched_ledger_indices.add(pair[0])
                
                if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                    for pair in self.grouped_pairs:
                        if len(pair) >= 1:
                            matched_ledger_indices.add(pair[0])
                
                # Add unmatched ledger rows
                for idx, row in self.ledger_df.iterrows():
                    if idx not in matched_ledger_indices:
                        unmatched_data = row.to_dict()
                        unmatched_data['source'] = 'ledger'
                        unmatched_data['index'] = idx
                        # Ensure Amount field exists
                        if 'Amount' not in unmatched_data and 'amount' in unmatched_data:
                            unmatched_data['Amount'] = unmatched_data['amount']
                        reconcile_results['unmatched_ledger'].append(unmatched_data)
            
            # Process unmatched statement items
            if hasattr(self, 'statement_df') and self.statement_df is not None:
                matched_statement_indices = set()
                
                # Collect all matched statement indices
                if hasattr(self, 'matched_pairs') and self.matched_pairs:
                    for pair in self.matched_pairs:
                        if len(pair) >= 2:
                            matched_statement_indices.add(pair[1])
                
                if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                    for pair in self.grouped_pairs:
                        if len(pair) >= 2:
                            matched_statement_indices.add(pair[1])
                
                # Add unmatched statement rows
                for idx, row in self.statement_df.iterrows():
                    if idx not in matched_statement_indices:
                        unmatched_data = row.to_dict()
                        unmatched_data['source'] = 'statement'
                        unmatched_data['index'] = idx
                        # Ensure Amount field exists
                        if 'Amount' not in unmatched_data and 'amount' in unmatched_data:
                            unmatched_data['Amount'] = unmatched_data['amount']
                        reconcile_results['unmatched_statement'].append(unmatched_data)
            
            return reconcile_results
            
        except Exception as e:
            print(f"Error preparing Bidvest reconcile results: {e}")
            return {
                'matched': [],
                'foreign_credits': [],
                'split_matches': [],
                'unmatched_statement': [],
                'unmatched_ledger': []
            }

    def prepare_bidvest_export_data(self):
        """Prepare Bidvest reconciliation results data for export"""
        try:
            import pandas as pd
            
            all_results = []
            
            # Process exact matches (matched_pairs)
            if hasattr(self, 'matched_pairs') and self.matched_pairs:
                for pair in self.matched_pairs:
                    result_row = {
                        'Match_Type': 'Exact Match',
                        'Similarity': '100.0%',
                        'Status': 'Matched'
                    }
                    
                    # Handle different pair structures
                    if len(pair) >= 2:
                        ledger_idx, statement_idx = pair[0], pair[1]
                        
                        # Add ledger data if available
                        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                            try:
                                ledger_row = self.ledger_df.iloc[ledger_idx]
                                for key, value in ledger_row.items():
                                    result_row[f'Ledger_{key}'] = value
                            except:
                                result_row['Ledger_Index'] = ledger_idx
                        
                        # Add statement data if available
                        if hasattr(self, 'statement_df') and self.statement_df is not None:
                            try:
                                statement_row = self.statement_df.iloc[statement_idx]
                                for key, value in statement_row.items():
                                    result_row[f'Statement_{key}'] = value
                            except:
                                result_row['Statement_Index'] = statement_idx
                    
                    all_results.append(result_row)
            
            # Process grouped matches (grouped_pairs)
            if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                for pair in self.grouped_pairs:
                    result_row = {
                        'Match_Type': 'Grouped Match',
                        'Similarity': '100.0%',
                        'Status': 'Grouped'
                    }
                    
                    # Handle different pair structures
                    if len(pair) >= 2:
                        ledger_idx, statement_idx = pair[0], pair[1]
                        
                        # Add ledger data if available
                        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                            try:
                                ledger_row = self.ledger_df.iloc[ledger_idx]
                                for key, value in ledger_row.items():
                                    result_row[f'Ledger_{key}'] = value
                            except:
                                result_row['Ledger_Index'] = ledger_idx
                        
                        # Add statement data if available
                        if hasattr(self, 'statement_df') and self.statement_df is not None:
                            try:
                                statement_row = self.statement_df.iloc[statement_idx]
                                for key, value in statement_row.items():
                                    result_row[f'Statement_{key}'] = value
                            except:
                                result_row['Statement_Index'] = statement_idx
                    
                    all_results.append(result_row)
            
            # Add unmatched ledger data
            if hasattr(self, 'ledger_df') and self.ledger_df is not None:
                matched_ledger_indices = set()
                
                # Collect all matched ledger indices
                if hasattr(self, 'matched_pairs') and self.matched_pairs:
                    for pair in self.matched_pairs:
                        if len(pair) >= 1:
                            matched_ledger_indices.add(pair[0])
                
                if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                    for pair in self.grouped_pairs:
                        if len(pair) >= 1:
                            matched_ledger_indices.add(pair[0])
                
                # Add unmatched ledger rows
                for idx, row in self.ledger_df.iterrows():
                    if idx not in matched_ledger_indices:
                        result_row = {
                            'Match_Type': 'Unmatched Ledger',
                            'Similarity': '0.0%',
                            'Status': 'Unmatched'
                        }
                        
                        for key, value in row.items():
                            result_row[f'Ledger_{key}'] = value
                        
                        all_results.append(result_row)
            
            # Add unmatched statement data
            if hasattr(self, 'statement_df') and self.statement_df is not None:
                matched_statement_indices = set()
                
                # Collect all matched statement indices
                if hasattr(self, 'matched_pairs') and self.matched_pairs:
                    for pair in self.matched_pairs:
                        if len(pair) >= 2:
                            matched_statement_indices.add(pair[1])
                
                if hasattr(self, 'grouped_pairs') and self.grouped_pairs:
                    for pair in self.grouped_pairs:
                        if len(pair) >= 2:
                            matched_statement_indices.add(pair[1])
                
                # Add unmatched statement rows
                for idx, row in self.statement_df.iterrows():
                    if idx not in matched_statement_indices:
                        result_row = {
                            'Match_Type': 'Unmatched Statement',
                            'Similarity': '0.0%',
                            'Status': 'Unmatched'
                        }
                        
                        for key, value in row.items():
                            result_row[f'Statement_{key}'] = value
                        
                        all_results.append(result_row)
            
            # Convert to DataFrame
            if all_results:
                return pd.DataFrame(all_results)
            else:
                # If no results yet, create a basic summary DataFrame
                summary_data = {
                    'Summary': ['Data Available'],
                    'Ledger_Records': [len(self.ledger_df) if hasattr(self, 'ledger_df') and self.ledger_df is not None else 0],
                    'Statement_Records': [len(self.statement_df) if hasattr(self, 'statement_df') and self.statement_df is not None else 0],
                    'Exact_Matches': [len(self.matched_pairs) if hasattr(self, 'matched_pairs') and self.matched_pairs else 0],
                    'Grouped_Matches': [len(self.grouped_pairs) if hasattr(self, 'grouped_pairs') and self.grouped_pairs else 0]
                }
                return pd.DataFrame(summary_data)
                
        except Exception as e:
            print(f"Error preparing Bidvest export data: {e}")
            # Return a basic DataFrame with error info
            return pd.DataFrame({'Error': [f'Error preparing data: {str(e)}']})

    def export_results_popup(self):
        import tempfile
        import os
        import pandas as pd
        from tkinter import filedialog

        def manage_results(self):
            from results_db import ResultsDB
            import pandas as pd
            from tkinter import simpledialog
            from tkinter import filedialog
            import uuid
            db = ResultsDB()
            results = db.list_reconciliation_results()
            win = tk.Toplevel(self)
            win.title("Manage Saved Results")
            win.state('zoomed')
            search_var = tk.StringVar()
            def filter_table(*_):
                val = search_var.get().lower()
                for iid in tree.get_children():
                    values = tree.item(iid)['values']
                    if any(val in str(v).lower() for v in values):
                        tree.reattach(iid, '', 'end')
                    else:
                        tree.detach(iid)
            topbar = tk.Frame(win)
            topbar.pack(fill='x', pady=8)
            tk.Label(topbar, text="Search:", font=("Segoe UI", 10)).pack(side='left', padx=(10,2))
            search_entry = tk.Entry(topbar, textvariable=search_var, font=("Segoe UI", 10), width=30)
            search_entry.pack(side='left')
            search_var.trace_add('write', filter_table)
            tree = ttk.Treeview(win, columns=("id", "name", "date", "type", "notes", "batch_id"), show="headings", selectmode="extended")
            for col, label in zip(["id", "name", "date", "type", "notes", "batch_id"], ["ID", "Name", "Date", "Type", "Notes", "Batch"]):
                tree.heading(col, text=label)
            tree.pack(fill='both', expand=True, padx=20, pady=10)
            for r in results:
                tree.insert('', 'end', values=r)
            def on_view():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                result_id = item[0]
                result = db.get_reconciliation_result(result_id)
                if result:
                    df = result['result_data']
                    view_win = tk.Toplevel(win)
                    view_win.title(f"Result: {result['name']} ({result['result_type']})")
                    txt = tk.Text(view_win, wrap='none')
                    txt.pack(expand=True, fill='both')
                    txt.insert('end', df.to_string(index=False))
                    # Show metadata
                    meta_txt = f"Notes: {result.get('notes','')}\nBatch: {result.get('batch_id','')}"
                    tk.Label(view_win, text=meta_txt, font=("Segoe UI", 9, "italic")).pack(anchor='w')
            def on_export():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                result_id = item[0]
                result = db.get_reconciliation_result(result_id)
                if result:
                    df = result['result_data']
                    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel','*.xlsx'),('CSV','*.csv')])
                    if file_path:
                        if file_path.endswith('.csv'):
                            df.to_csv(file_path, index=False)
                        else:
                            df.to_excel(file_path, index=False)
                        messagebox.showinfo("Exported", f"Result exported to {file_path}")
            def on_export_batch():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                batch_id = item[5]
                if not batch_id:
                    messagebox.showwarning("No Batch", "This result is not part of a batch.")
                    return
                results_dict = db.get_batch_results(batch_id)
                if not results_dict:
                    messagebox.showwarning("No Batch Results", "No results found for this batch.")
                    return
                file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel','*.xlsx')])
                if file_path:
                    with pd.ExcelWriter(file_path) as writer:
                        for key, df in results_dict.items():
                            df.to_excel(writer, sheet_name=key[:31], index=False)
                    messagebox.showinfo("Exported", f"Batch exported to {file_path}")
            def on_delete():
                sel = tree.selection()
                if not sel:
                    return
                if not messagebox.askyesno("Delete", "Delete selected result(s)?"):
                    return
                for iid in sel:
                    item = tree.item(iid)['values']
                    result_id = item[0]
                    db.delete_reconciliation_result(result_id)
                    tree.delete(iid)
            def on_rename():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                result_id = item[0]
                new_name = simpledialog.askstring("Rename Result", "Enter new name:")
                if new_name:
                    db.rename_result(result_id, new_name)
                    tree.set(sel[0], 'name', new_name)
            def on_edit_notes():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                result_id = item[0]
                notes = simpledialog.askstring("Edit Notes", "Enter notes:")
                if notes is not None:
                    db.update_notes(result_id, notes)
                    tree.set(sel[0], 'notes', notes)
            def on_load():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])['values']
                result_id = item[0]
                result = db.get_reconciliation_result(result_id)
                if result:
                    # Load result into workspace (for demo, just show a message)
                    messagebox.showinfo("Loaded", f"Result '{result['name']}' loaded to workspace.")
                    # You can implement actual loading logic as needed
            btn_frame = tk.Frame(win)
            btn_frame.pack(fill='x', pady=8)
            tk.Button(btn_frame, text="View", command=on_view, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Export", command=on_export, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Export Batch", command=on_export_batch, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Delete", command=on_delete, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Rename", command=on_rename, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Edit Notes", command=on_edit_notes, font=("Segoe UI", 10)).pack(side='left', padx=10)
            tk.Button(btn_frame, text="Load to Workspace", command=on_load, font=("Segoe UI", 10)).pack(side='left', padx=10)
        # Ensure title_frame, title_label, popup are defined before use
        # If not already defined, define them here
        if 'popup' not in locals():
            popup = tk.Toplevel(self)
            popup.title("Export Results - Bidvest Reconciliation")
            popup.state('zoomed')  # Full screen without hiding taskbar
            popup.configure(bg="#f4f8fb")
        if 'title_frame' not in locals():
            title_frame = tk.Frame(popup, bg="#0ea5e9")
            title_frame.pack(fill="x")
        title_label = tk.Label(title_frame, text="EXPORT RESULTS", font=("Segoe UI", 24, "bold"), bg="#0ea5e9", fg="white")
        title_label.pack(side="left", pady=15)
        subtitle_label = tk.Label(title_frame, text="Select columns and export format for reconciliation results", font=("Segoe UI", 11), bg="#0ea5e9", fg="#cbd5e1")
        subtitle_label.pack(side="left", padx=(20, 0), pady=(25, 0))
        close_btn = tk.Button(title_frame, text="✕", font=("Segoe UI", 16, "bold"), bg="#dc2626", fg="white", bd=0, padx=15, pady=8, command=popup.destroy)
        close_btn.pack(side="right", padx=(0, 30), pady=15)

        # Define ledger_cols and stmt_cols at the start of the popup
        ledger_cols = []
        stmt_cols = []
        
        # Safely extract column names and convert to strings
        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
            ledger_cols = [str(col) for col in self.ledger_df.columns if col is not None]
            
        if hasattr(self, 'statement_df') and self.statement_df is not None:
            stmt_cols = [str(col) for col in self.statement_df.columns if col is not None]
        # Main content
        main_container = tk.Frame(popup, bg="#f8f9fc")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        content_frame = tk.Frame(main_container, bg="#f8f9fc")
        content_frame.pack(fill="both", expand=True)
        left_frame = tk.Frame(content_frame, bg="#f8f9fc")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        right_frame = tk.Frame(content_frame, bg="#f8f9fc", width=450)
        right_frame.pack(side="right", fill="y", padx=(15, 0))
        right_frame.pack_propagate(False)
        # Instructions
        instructions_frame = tk.Frame(left_frame, bg="white", relief="flat", bd=0)
        instructions_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        instructions_frame.pack(fill="x", pady=(0, 20))
        inst_content = tk.Frame(instructions_frame, bg="white")
        inst_content.pack(fill="x", padx=20, pady=15)
        inst_title = tk.Label(inst_content, text="📋 Export Instructions", font=("Segoe UI", 14, "bold"), bg="white", fg="#1e293b")
        inst_title.pack(anchor="w")
        inst_text = tk.Label(inst_content, text="• Select columns to include in export\n• Use manual editing for complex transactions", font=("Segoe UI", 10), bg="white", fg="#64748b", justify="left")
        inst_text.pack(anchor="w", pady=(8, 0))
        # Column selection
        selection_frame = tk.Frame(left_frame, bg="white", relief="flat", bd=0)
        selection_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        selection_frame.pack(fill="both", expand=True)
        sel_header = tk.Frame(selection_frame, bg="#f1f5f9")
        sel_header.pack(fill="x")
        sel_title = tk.Label(sel_header, text="🎯 Column Selection", font=("Segoe UI", 14, "bold"), bg="#f1f5f9", fg="#1e293b")
        sel_title.pack(anchor="w", padx=20, pady=12)
        canvas = tk.Canvas(selection_frame, bg="white", highlightthickness=0, height=400)
        scrollbar = tk.Scrollbar(selection_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        scrollbar.pack(side="right", fill="y")
        grid_frame = tk.Frame(scrollable_frame, bg="white")
        grid_frame.pack(fill="both", expand=True, padx=10)
        font_header = ("Segoe UI", 12, "bold")
        font_label = ("Segoe UI", 11, "bold")
        font_cb = ("Segoe UI", 10)
        # Ledger section
        ledger_section = tk.Frame(grid_frame, bg="white")
        ledger_section.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        ledger_header = tk.Frame(ledger_section, bg="#3b82f6", relief="flat")
        ledger_header.pack(fill="x", pady=(0, 15))
        tk.Label(ledger_header, text="📊 Ledger Columns", font=font_header, bg="#3b82f6", fg="white").pack(anchor="w", padx=20, pady=12)
        ledger_vars = []
        ledger_order = []
        def update_ledger_btn():
            if all(v.get() for v in ledger_vars):
                ledger_btn.config(text="Deselect All", bg="#dc2626")
            else:
                ledger_btn.config(text="Select All", bg="#059669")
        def ledger_cb_cmd(idx):
            def cb():
                if ledger_vars[idx].get():
                    if idx not in ledger_order:
                        ledger_order.append(idx)
                else:
                    if idx in ledger_order:
                        ledger_order.remove(idx)
                update_ledger_btn()
            return cb
        for i, col in enumerate(ledger_cols):
            var = tk.BooleanVar(value=True)
            ledger_vars.append(var)
            ledger_order.append(i)
            cb = ledger_cb_cmd(i)
            cb_frame = tk.Frame(ledger_section, bg="white")
            cb_frame.pack(fill="x", pady=2)
            checkbox = tk.Checkbutton(cb_frame, text=f"  {col}", variable=var, font=font_cb, bg="white", fg="#374151", activebackground="#f3f4f6", command=cb, anchor="w")
            checkbox.pack(fill="x", padx=10)

        # Statement section (leave unchanged)
        # ...existing code for statement section...


        # --- Place WhatsApp send button after both column selection sections ---
        def send_csv_via_whatsapp():
            from tkinter import simpledialog
            # Show user instructions before sending
            messagebox.showinfo(
                "WhatsApp Web Required",
                "Please ensure WhatsApp Web is open, logged in, and your browser is in the foreground before sending.\n\nAfter clicking OK, do not minimize your browser until the message is sent.",
                parent=popup
            )
            number = simpledialog.askstring("WhatsApp Number", "Enter WhatsApp number (with country code, e.g. +27...):", parent=popup)
            if not number:
                return
            # Gather selected columns
            selected_ledger = [ledger_cols[i] for i, v in enumerate(ledger_vars) if v.get()]
            selected_stmt = [stmt_cols[i] for i, v in enumerate(stmt_vars) if v.get()]
            if not selected_ledger and not selected_stmt:
                messagebox.showwarning("No Columns", "Please select at least one column to export.", parent=popup)
                return
            # Export to a temporary CSV file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8') as tmpfile:
                tmp_path = tmpfile.name
                self._export_to_file_bidvest(tmp_path, selected_ledger, selected_stmt, 'csv')
            msg = f"Bidvest Reconciliation Results (CSV file):\n{tmp_path}\nPlease open the file on your computer."
            try:
                import pywhatkit
                # Try to check if WhatsApp Web is open by sending a test message (pywhatkit does not provide a direct check, so rely on error handling)
                pywhatkit.sendwhatmsg_instantly(number, msg, wait_time=25, tab_close=True)
                messagebox.showinfo("WhatsApp", f"CSV file path sent to {number} via WhatsApp.\nFile: {tmp_path}")
            except Exception as e:
                messagebox.showerror(
                    "WhatsApp Error",
                    f"Failed to send message.\n\nPossible reasons:\n- WhatsApp Web is not open or not logged in.\n- Your browser is minimized or not in the foreground.\n- Pop-up blockers or automation restrictions.\n\nError details: {e}",
                    parent=popup
                )

        whatsapp_csv_btn = tk.Button(popup, text="Send Results as CSV via WhatsApp", font=("Segoe UI", 11, "bold"), bg="#25D366", fg="white", bd=0, padx=20, pady=12, command=send_csv_via_whatsapp, cursor="hand2")
        whatsapp_csv_btn.pack(side="top", pady=(20, 0))
        def select_all_ledger():
            if all(v.get() for v in ledger_vars):
                for v in ledger_vars:
                    v.set(False)
                ledger_order.clear()
            else:
                for i, v in enumerate(ledger_vars):
                    v.set(True)
                    if i not in ledger_order:
                        ledger_order.append(i)
            update_ledger_btn()
        ledger_btn = tk.Button(ledger_section, text="Deselect All", font=("Segoe UI", 10, "bold"), command=select_all_ledger, bg="#dc2626", fg="white", bd=0, pady=8)
        ledger_btn.pack(fill="x", padx=10, pady=(15, 10))
        # Statement section
        stmt_section = tk.Frame(grid_frame, bg="white")
        stmt_section.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=10)
        stmt_header = tk.Frame(stmt_section, bg="#10b981", relief="flat")
        stmt_header.pack(fill="x", pady=(0, 15))
        tk.Label(stmt_header, text="🏦 Statement Columns", font=font_header, bg="#10b981", fg="white").pack(anchor="w", padx=20, pady=12)
        stmt_vars = []
        stmt_order = []
        def update_stmt_btn():
            if all(v.get() for v in stmt_vars):
                stmt_btn.config(text="Deselect All", bg="#dc2626")
            else:
                stmt_btn.config(text="Select All", bg="#059669")
        def stmt_cb_cmd(idx):
            def cb():
                if stmt_vars[idx].get():
                    if idx not in stmt_order:
                        stmt_order.append(idx)
                else:
                    if idx in stmt_order:
                        stmt_order.remove(idx)
                update_stmt_btn()
            return cb
        for i, col in enumerate(stmt_cols):
            var = tk.BooleanVar(value=True)
            stmt_vars.append(var)
            stmt_order.append(i)
            cb = stmt_cb_cmd(i)
            cb_frame = tk.Frame(stmt_section, bg="white")
            cb_frame.pack(fill="x", pady=2)
            checkbox = tk.Checkbutton(cb_frame, text=f"  {col}", variable=var, font=font_cb, bg="white", fg="#374151", activebackground="#f3f4f6", command=cb, anchor="w")
            checkbox.pack(fill="x", padx=10)
        def select_all_stmt():
            if all(v.get() for v in stmt_vars):
                for v in stmt_vars:
                    v.set(False)
                stmt_order.clear()
            else:
                for i, v in enumerate(stmt_vars):
                    v.set(True)
                    if i not in stmt_order:
                        stmt_order.append(i)
            update_stmt_btn()
        stmt_btn = tk.Button(stmt_section, text="Deselect All", font=("Segoe UI", 10, "bold"), command=select_all_stmt, bg="#dc2626", fg="white", bd=0, pady=8)
        stmt_btn.pack(fill="x", padx=10, pady=(15, 10))
        # Export buttons section
        export_frame = tk.Frame(right_frame, bg="white", relief="flat", bd=0)
        export_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        export_frame.pack(fill="x", pady=(0, 15))
        export_header = tk.Frame(export_frame, bg="#6366f1")
        export_header.pack(fill="x")
        tk.Label(export_header, text="💾 Export Options", font=("Segoe UI", 14, "bold"), bg="#6366f1", fg="white").pack(anchor="w", padx=20, pady=12)
        def do_export(fmt):
            # Always run reconciliation before exporting to ensure results are up to date
            self.reconcile_bidvest()
            selected_ledger = [ledger_cols[i] for i in ledger_order if ledger_vars[i].get()]
            selected_stmt = [stmt_cols[i] for i in stmt_order if stmt_vars[i].get()]
            if not selected_ledger and not selected_stmt:
                messagebox.showwarning("No Columns", "Please select at least one column to export.", parent=popup)
                return
            filetypes = [("Excel files", "*.xlsx")] if fmt == 'excel' else [("CSV files", "*.csv")]
            ext = '.xlsx' if fmt == 'excel' else '.csv'
            file_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=filetypes, parent=popup)
            if not file_path:
                return
            self._export_to_file_bidvest(file_path, selected_ledger, selected_stmt, fmt)
            messagebox.showinfo("Export Successful", f"✅ Results exported successfully to:\n{file_path}", parent=popup)
            popup.destroy()
        btn_container = tk.Frame(export_frame, bg="white")
        btn_container.pack(fill="x", padx=20, pady=20)
        excel_btn = tk.Button(btn_container, text="📊 Export as Excel", font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white", bd=0, padx=20, pady=12, command=lambda: do_export('excel'), cursor="hand2")
        excel_btn.pack(fill="x", pady=(0, 10))
        csv_btn = tk.Button(btn_container, text="📄 Export as CSV", font=("Segoe UI", 11, "bold"), bg="#e74c3c", fg="white", bd=0, padx=20, pady=12, command=lambda: do_export('csv'), cursor="hand2")
        csv_btn.pack(fill="x", pady=(0, 10))
        
        # Collaborative Dashboard Integration - PROFESSIONAL SYSTEM
        dashboard_frame = tk.Frame(btn_container, bg="white", relief="flat", bd=0)
        dashboard_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        dashboard_frame.pack(fill="x", pady=(10, 0))
        
        # Dashboard header
        dashboard_header = tk.Frame(dashboard_frame, bg="#3b82f6")
        dashboard_header.pack(fill="x")
        tk.Label(dashboard_header, text="🚀 Collaborative Dashboard", 
                font=("Segoe UI", 12, "bold"), bg="#3b82f6", fg="white").pack(anchor="w", padx=20, pady=10)
        
        # Dashboard content
        dashboard_content = tk.Frame(dashboard_frame, bg="white")
        dashboard_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(dashboard_content, text="Post reconciliation results to the collaborative web dashboard:", 
                font=("Segoe UI", 10), bg="white", fg="#64748b", 
                wraplength=380, justify="left").pack(anchor="w", pady=(0, 12))
        
        def post_to_collaborative_dashboard():
            """Post current reconciliation results to collaborative dashboard"""
            try:
                popup.destroy()
                
                # Import collaborative system
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from collaborative_dashboard_db import CollaborativeDashboardDB
                
                # Get current reconciliation results
                if not hasattr(self, 'reconciliation_results') or not self.reconciliation_results:
                    messagebox.showerror("No Results", "❌ No reconciliation results to post.\nPlease run reconciliation first.")
                    return
                
                # Initialize collaborative database
                db = CollaborativeDashboardDB()
                
                # Create session for this reconciliation
                from datetime import datetime
                session_name = f"Bidvest Reconciliation - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                # Get counts from reconciliation results
                total_results = len(self.reconciliation_results)
                matched_results = len([r for r in self.reconciliation_results if r.get('matched')])
                session_desc = f"Automated Bidvest workflow reconciliation\nTotal transactions: {total_results}\nMatched: {matched_results}"
                
                session_id = db.create_session(
                    session_name=session_name,
                    description=session_desc,
                    workflow_type="bidvest",
                    created_by="admin"  # Default user
                )
                
                # Convert and post transactions
                posted_count = 0
                for result in self.reconciliation_results:
                    # Convert reconciliation result to transaction format
                    transaction_data = {
                        'reference': result.get('ledger_ref', ''),
                        'amount': float(result.get('amount', 0)),
                        'date': result.get('date', datetime.now().isoformat()),
                        'description': result.get('description', ''),
                        'type': 'bidvest_reconciliation',
                        'status': 'matched' if result.get('matched') else 'unmatched',
                        'metadata': {
                            'ledger_entry': result.get('ledger_entry', {}),
                            'statement_entry': result.get('statement_entry', {}),
                            'confidence_score': result.get('confidence_score', 0),
                            'workflow': 'bidvest'
                        }
                    }
                    
                    # Add transaction to collaborative session
                    db.add_transaction(session_id, transaction_data)
                    posted_count += 1
                
                # Show success message with dashboard link
                success_msg = f"""✅ Successfully posted to Collaborative Dashboard!

📊 Session Created: {session_name}
💰 Transactions Posted: {posted_count}
🆔 Session ID: {session_id}

🌐 View in Dashboard: http://localhost:5000
🔐 Login: admin / admin123

The collaborative dashboard is now updated with your reconciliation results.
Team members can view, comment, and collaborate on these transactions."""
                
                result = messagebox.askyesno("Post Successful", 
                    success_msg + "\n\n🚀 Would you like to open the dashboard now?", 
                    icon='question')
                
                if result:
                    # Open collaborative dashboard in browser
                    import webbrowser
                    webbrowser.open("http://localhost:5000")
                    
            except ImportError:
                messagebox.showerror("Dashboard Error", 
                    "❌ Collaborative dashboard system not available.\n\n" +
                    "Please ensure the dashboard server is running:\n" +
                    "• Run: launch_web_maximized.bat\n" +
                    "• Or: python launch_web_dashboard.py")
            except Exception as e:
                messagebox.showerror("Post Error", f"❌ Failed to post to dashboard:\n\n{str(e)}")
        
        # POST button
        post_btn = tk.Button(dashboard_content, text="🚀 POST to Dashboard", 
                           font=("Segoe UI", 11, "bold"), bg="#10b981", fg="white", 
                           bd=0, padx=20, pady=12, cursor="hand2",
                           command=post_to_collaborative_dashboard)
        post_btn.pack(fill="x", pady=(0, 5))
        
        # Info label
        tk.Label(dashboard_content, text="💡 Dashboard server must be running (launch_web_maximized.bat)", 
                font=("Segoe UI", 9), bg="white", fg="#9ca3af", 
                wraplength=380, justify="left").pack(anchor="w", pady=(5, 0))
        

        # Manual editing section
        manual_frame = tk.Frame(right_frame, bg="white", relief="flat", bd=0)
        manual_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        manual_frame.pack(fill="x", pady=(0, 15))
        manual_header = tk.Frame(manual_frame, bg="#f59e0b")
        manual_header.pack(fill="x")
        tk.Label(manual_header, text="✏️ Manual Editing", font=("Segoe UI", 14, "bold"), bg="#f59e0b", fg="white").pack(anchor="w", padx=20, pady=12)
        manual_content = tk.Frame(manual_frame, bg="white")
        manual_content.pack(fill="x", padx=20, pady=15)
        manual_desc = tk.Label(manual_content, text="For complex transactions like split entries or partial matches:", font=("Segoe UI", 10), bg="white", fg="#64748b", wraplength=380, justify="left")
        manual_desc.pack(anchor="w", pady=(0, 12))
        def open_excel_editing():
            popup.destroy()
            self.open_in_excel_for_editing()
        def import_manual_changes():
            popup.destroy()
            self.import_manual_changes()
        open_excel_btn = tk.Button(manual_content, text="📊 Open in Excel for Editing", font=("Segoe UI", 11, "bold"), bg="#0ea5e9", fg="white", bd=0, padx=20, pady=12, command=open_excel_editing, cursor="hand2")
        open_excel_btn.pack(fill="x", pady=(0, 10))
        import_btn = tk.Button(manual_content, text="📥 Import Manual Changes", font=("Segoe UI", 11, "bold"), bg="#059669", fg="white", bd=0, padx=20, pady=12, command=import_manual_changes, cursor="hand2")
        import_btn.pack(fill="x")
        # Summary section
        summary_frame = tk.Frame(right_frame, bg="white", relief="flat", bd=0)
        summary_frame.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        summary_frame.pack(fill="both", expand=True)
        summary_header = tk.Frame(summary_frame, bg="#8b5cf6")
        summary_header.pack(fill="x")
        tk.Label(summary_header, text="📊 Quick Summary", font=("Segoe UI", 14, "bold"), bg="#8b5cf6", fg="white").pack(anchor="w", padx=20, pady=12)
        summary_content = tk.Frame(summary_frame, bg="white")
        summary_content.pack(fill="both", expand=True, padx=20, pady=15)
        # Add reconciliation summary with new match types
        if hasattr(self, 'ledger_df') and hasattr(self, 'statement_df') and self.ledger_df is not None and self.statement_df is not None:
            # Count exact matches (100%)
            exact_matches = len(getattr(self, 'matched_pairs', []))
            # Count grouped matches
            grouped_matches = len(getattr(self, 'grouped_pairs', []))
            # Count unmatched
            total_matched = exact_matches + grouped_matches
            unmatched_ledger = len(self.ledger_df) - total_matched
            unmatched_stmt = len(self.statement_df) - total_matched
            
            summary_text = f"🎯 RECONCILIATION SUMMARY\n\n"
            summary_text += f"✅ 100% Exact Matches: {exact_matches}\n"
            summary_text += f"🔄 Grouped Matches: {grouped_matches}\n"
            summary_text += f"❌ Unmatched Ledger: {unmatched_ledger}\n"
            summary_text += f"❌ Unmatched Statement: {unmatched_stmt}\n\n"
            summary_text += f"📊 Total Efficiency: {((total_matched / len(self.ledger_df)) * 100):.1f}%"
            
            tk.Label(summary_content, text=summary_text, font=("Segoe UI", 10), bg="white", fg="#374151", justify="left").pack(anchor="w")
        update_ledger_btn()
        update_stmt_btn()
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def on_destroy():
            try:
                canvas.unbind_all("<MouseWheel>")
            except (tk.TclError, AttributeError):
                pass
            popup.protocol("WM_DELETE_WINDOW", on_destroy)

    def _export_to_file_bidvest(self, file_path, ledger_cols, stmt_cols, fmt):
        import pandas as pd
        import os
        import subprocess
        import sys
        ledger = self.ledger_df
        stmt = self.statement_df
        
        # Helper to build export DataFrame
        def build_batch(pairs, label=None):
            rows = []
            if label and pairs:
                header_row = [label] + [''] * (len(ledger_cols) - 1) + [''] + [''] * len(stmt_cols)
                rows.append(header_row)
            for li, si in pairs:
                lrow = ledger.loc[li, ledger_cols] if ledger_cols else pd.Series()
                srow = stmt.loc[si, stmt_cols] if stmt_cols else pd.Series()
                row = list(lrow) + [''] + list(srow)
                rows.append(row)
            return rows
        
        # 100% exact matched pairs
        exact_pairs = getattr(self, 'matched_pairs', [])
        batch_100 = build_batch(exact_pairs, label='100% EXACT MATCHES')
        
        # Grouped matches (same date/amount but not following +1 day rule)
        grouped_pairs = getattr(self, 'grouped_pairs', [])
        batch_grouped = build_batch(grouped_pairs, label='GROUPED MATCHES (Same Date & Amount)')
        
        # Manual matches (placeholder for future manual matching feature)
        batch_manual = []
        
        # Unmatched transactions
        unmatched_ledger_100 = ledger[ledger['Matched'] == False]
        unmatched_stmt_100 = stmt[stmt['Matched'] == False]
        
        # Build separate lists for export
        unmatched_ledger_rows = []
        unmatched_stmt_rows = []
        
        for i in unmatched_ledger_100.index:
            unmatched_ledger_rows.append(list(ledger.loc[i, ledger_cols]) if ledger_cols else [])
            
        for i in unmatched_stmt_100.index:
            unmatched_stmt_rows.append(list(stmt.loc[i, stmt_cols]) if stmt_cols else [])
        
        # Pad to same length
        max_unmatched = max(len(unmatched_ledger_rows), len(unmatched_stmt_rows))
        while len(unmatched_ledger_rows) < max_unmatched:
            unmatched_ledger_rows.append([''] * len(ledger_cols))
        while len(unmatched_stmt_rows) < max_unmatched:
            unmatched_stmt_rows.append([''] * len(stmt_cols))
        
        # Build final export DataFrame
        export_rows = []
        
        # Add column headers
        header_row = ledger_cols + [''] + stmt_cols
        export_rows.append(header_row)
        
        # Add 100% matches
        export_rows.extend(batch_100)
        
        # Add spacing and grouped matches if any
        if batch_grouped:
            export_rows.extend([[""] * (len(ledger_cols) + 1 + len(stmt_cols))] * 2)  # 2 empty rows
            export_rows.extend(batch_grouped)
        
        # Add spacing and manual matches if any (future feature)
        if batch_manual:
            export_rows.extend([[""] * (len(ledger_cols) + 1 + len(stmt_cols))] * 2)  # 2 empty rows
            export_rows.extend(batch_manual)
        
        # Add spacing and unmatched section
        if unmatched_ledger_rows or unmatched_stmt_rows:
            export_rows.extend([[""] * (len(ledger_cols) + 1 + len(stmt_cols))] * 3)  # 3 empty rows
            export_rows.append(["UNMATCHED TRANSACTIONS"] + [""] * (len(ledger_cols) - 1) + [""] + [""] * len(stmt_cols))
            
            # Add unmatched rows side by side
            for lrow, srow in zip(unmatched_ledger_rows, unmatched_stmt_rows):
                export_rows.append(lrow + [''] + srow)
        
        # Create DataFrame and export
        df_export = pd.DataFrame(export_rows)
        
        if fmt == 'excel':
            df_export.to_excel(file_path, index=False, header=False)
        else:
            df_export.to_csv(file_path, index=False, header=False)
        
        # Auto-open the file after saving
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            print(f"Could not auto-open file: {e}")


    def save_column_config(self, config_name=None):
        import json, os
        CONFIG_FILE = 'bidvest_column_configs.json'
        if not hasattr(self, 'match_config'):
            messagebox.showwarning("No Config", "No column configuration to save.")
            return
        if not config_name:
            from tkinter import simpledialog
            config_name = simpledialog.askstring("Save Config", "Enter a name for this column config:")
        if not config_name:
            return
        configs = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                try:
                    configs = json.load(f)
                except Exception:
                    configs = {}
        configs[config_name] = self.match_config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2)
        messagebox.showinfo("Saved", f"Config '{config_name}' saved.")

    def load_column_config(self):
        import json, os
        CONFIG_FILE = 'bidvest_column_configs.json'
        if not os.path.exists(CONFIG_FILE):
            messagebox.showinfo("No Configs", "No saved column configs found.")
            return
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        if not configs:
            messagebox.showinfo("No Configs", "No saved column configs found.")
            return
        from tkinter import simpledialog
        names = list(configs.keys())
        config_name = simpledialog.askstring("Load Config", f"Available configs:\n{chr(10).join(names)}\nEnter config name to load:")
        if not config_name or config_name not in configs:
            return
        self.match_config = configs[config_name]
        messagebox.showinfo("Loaded", f"Config '{config_name}' loaded.")

    def configure_columns_page(self):
        import pandas as pd
        win = tk.Toplevel(self)
        win.title("Configure Columns to be Matched")
        win.attributes('-fullscreen', True)
        win.configure(bg="#f4f8fb")
        header = tk.Frame(win, bg="#0ea5e9")
        header.pack(fill="x")
        tk.Label(header, text="🛠️ Configure Columns to be Matched", font=("Segoe UI", 20, "bold"), fg="white", bg="#0ea5e9", pady=18).pack(side="left", padx=40)
        tk.Button(header, text="✖ Close", command=win.destroy, font=("Segoe UI", 12, "bold"), bg="#e11d48", fg="white", relief="flat", padx=16, pady=4, cursor="hand2").pack(side="right", padx=40)
        # Get columns from both ledger and statement
        ledger_cols = []
        statement_cols = []
        
        # Safely extract column names and convert to strings
        if hasattr(self, 'ledger_df') and self.ledger_df is not None:
            ledger_cols = [str(col) for col in self.ledger_df.columns if col is not None]
            
        if hasattr(self, 'statement_df') and self.statement_df is not None:
            statement_cols = [str(col) for col in self.statement_df.columns if col is not None]
        # Auto-detect likely date/amount columns
        def guess_col(cols, keywords):
            if not cols:
                return ""
                
            for k in keywords:
                for c in cols:
                    # Convert column name to string and handle non-string types
                    try:
                        col_str = str(c).lower() if c is not None else ""
                        if k.lower() in col_str:
                            return str(c)  # Return as string
                    except (AttributeError, TypeError, ValueError):
                        # Skip columns that can't be converted to string
                        continue
            # Return first valid column as string, or empty string if none
            return str(cols[0]) if cols else ""
        date_keys = ["date", "transaction date", "value date"]
        debit_keys = ["foreign debit", "debit", "dr", "foreign dr"]
        credit_keys = ["foreign credit", "credit", "cr", "foreign cr"]
        amt_keys = ["amount", "amt", "value"]
        ledger_date_guess = guess_col(ledger_cols, date_keys)
        statement_date_guess = guess_col(statement_cols, date_keys)
        ledger_debit_guess = guess_col(ledger_cols, debit_keys)
        ledger_credit_guess = guess_col(ledger_cols, credit_keys)
        statement_amt_guess = guess_col(statement_cols, amt_keys)
        # Main content frame
        content = tk.Frame(win, bg="#f4f8fb")
        content.pack(expand=True, fill="both", padx=60, pady=40)
        table = tk.Frame(content, bg="#f4f8fb")
        table.pack(expand=True)
        tk.Label(table, text="", bg="#f4f8fb").grid(row=0, column=0, padx=20)
        tk.Label(table, text="Ledger", font=("Segoe UI", 14, "bold"), fg="#0ea5e9", bg="#f4f8fb").grid(row=0, column=1, padx=40, pady=10)
        tk.Label(table, text="Statement", font=("Segoe UI", 14, "bold"), fg="#0ea5e9", bg="#f4f8fb").grid(row=0, column=2, padx=40, pady=10)
        # Row 1: Dates
        tk.Label(table, text="📅 Date Column", font=("Segoe UI", 13, "bold"), fg="#0ea5e9", bg="#f4f8fb").grid(row=1, column=0, sticky="e", padx=20, pady=30)
        self.ledger_date_var = tk.StringVar(value=ledger_date_guess)
        ledger_date_menu = ttk.Combobox(table, textvariable=self.ledger_date_var, values=ledger_cols, state="readonly", font=("Segoe UI", 12))
        ledger_date_menu.grid(row=1, column=1, padx=40, pady=30, ipadx=10)
        self.statement_date_var = tk.StringVar(value=statement_date_guess)
        statement_date_menu = ttk.Combobox(table, textvariable=self.statement_date_var, values=statement_cols, state="readonly", font=("Segoe UI", 12))
        statement_date_menu.grid(row=1, column=2, padx=40, pady=30, ipadx=10)
        # Row 2: Foreign Debits
        tk.Label(table, text="💳 Foreign Debits", font=("Segoe UI", 13, "bold"), fg="#dc2626", bg="#f4f8fb").grid(row=2, column=0, sticky="e", padx=20, pady=30)
        self.ledger_debit_var = tk.StringVar(value=ledger_debit_guess)
        ledger_debit_menu = ttk.Combobox(table, textvariable=self.ledger_debit_var, values=ledger_cols, state="readonly", font=("Segoe UI", 12))
        ledger_debit_menu.grid(row=2, column=1, padx=40, pady=30, ipadx=10)
        tk.Label(table, text="↔ Positive Amounts", font=("Segoe UI", 11, "italic"), fg="#059669", bg="#f4f8fb").grid(row=2, column=2, padx=40, pady=30)
        # Row 3: Foreign Credits
        tk.Label(table, text="💰 Foreign Credits", font=("Segoe UI", 13, "bold"), fg="#059669", bg="#f4f8fb").grid(row=3, column=0, sticky="e", padx=20, pady=30)
        self.ledger_credit_var = tk.StringVar(value=ledger_credit_guess)
        ledger_credit_menu = ttk.Combobox(table, textvariable=self.ledger_credit_var, values=ledger_cols, state="readonly", font=("Segoe UI", 12))
        ledger_credit_menu.grid(row=3, column=1, padx=40, pady=30, ipadx=10)
        tk.Label(table, text="↔ Negative Amounts", font=("Segoe UI", 11, "italic"), fg="#dc2626", bg="#f4f8fb").grid(row=3, column=2, padx=40, pady=30)
        # Row 4: Statement Amount
        tk.Label(table, text="💵 Statement Amount", font=("Segoe UI", 13, "bold"), fg="#0ea5e9", bg="#f4f8fb").grid(row=4, column=0, sticky="e", padx=20, pady=30)
        tk.Label(table, text="(Matches both above)", font=("Segoe UI", 11, "italic"), fg="#6b7280", bg="#f4f8fb").grid(row=4, column=1, padx=40, pady=30)
        self.statement_amt_var = tk.StringVar(value=statement_amt_guess)
        statement_amt_menu = ttk.Combobox(table, textvariable=self.statement_amt_var, values=statement_cols, state="readonly", font=("Segoe UI", 12))
        statement_amt_menu.grid(row=4, column=2, padx=40, pady=30, ipadx=10)
        # Preview mapping
        preview_frame = tk.Frame(content, bg="#f4f8fb")
        preview_frame.pack(pady=20)
        preview_label = tk.Label(preview_frame, text="Preview: ", font=("Segoe UI", 11, "bold"), fg="#0ea5e9", bg="#f4f8fb")
        preview_label.pack(side="left")
        preview_text = tk.Label(preview_frame, text="", font=("Segoe UI", 11), fg="#334155", bg="#f4f8fb", wraplength=800, justify="left")
        preview_text.pack(side="left")
        def update_preview(*_):
            preview_text.config(text=f"Dates: {self.ledger_date_var.get()} + 1 day ↔ {self.statement_date_var.get()}\n"
                                     f"Debits: {self.ledger_debit_var.get()} (positive) ↔ {self.statement_amt_var.get()} (positive)\n"
                                     f"Credits: {self.ledger_credit_var.get()} (positive) ↔ {self.statement_amt_var.get()} (negative)")
        self.ledger_date_var.trace_add('write', update_preview)
        self.statement_date_var.trace_add('write', update_preview)
        self.ledger_debit_var.trace_add('write', update_preview)
        self.ledger_credit_var.trace_add('write', update_preview)
        self.statement_amt_var.trace_add('write', update_preview)
        update_preview()
        # Save/load config buttons
        btn_frame = tk.Frame(content, bg="#f4f8fb")
        btn_frame.pack(pady=30)
        def save_config():
            self.match_config = {
                'ledger_date': self.ledger_date_var.get(),
                'statement_date': self.statement_date_var.get(),
                'ledger_debit': self.ledger_debit_var.get(),
                'ledger_credit': self.ledger_credit_var.get(),
                'statement_amt': self.statement_amt_var.get()
            }
            messagebox.showinfo("Saved", "Column mapping saved for dual-amount matching.")
            win.destroy()
        tk.Button(btn_frame, text="💾 Save Column Mapping", command=save_config, bg="#38bdf8", fg="white", font=("Segoe UI", 13, "bold"), padx=30, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Save Config...", command=self.save_column_config, bg="#fbbf24", fg="#1e293b", font=("Segoe UI", 13, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Load Config...", command=self.load_column_config, bg="#a3e635", fg="#1e293b", font=("Segoe UI", 13, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=10)

    def reconcile_bidvest(self):
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        from collections import defaultdict
        import json
        
        if not hasattr(self, 'match_config'):
            messagebox.showwarning("No Config", "Please configure columns to be matched first.")
            return
        if self.ledger_df is None or self.statement_df is None:
            messagebox.showwarning("Missing Data", "Please import both ledger and statement.")
            return
            
        cfg = self.match_config
        l_date_col = cfg.get('ledger_date')
        s_date_col = cfg.get('statement_date')
        l_debit_col = cfg.get('ledger_debit')
        l_credit_col = cfg.get('ledger_credit')
        s_amt_col = cfg.get('statement_amt')
        
        if not all([l_date_col, s_date_col, l_debit_col, l_credit_col, s_amt_col]):
            messagebox.showerror("Config Error", "Please configure all required columns (date, debit, credit, statement amount).")
            return

        # Create progress window
        import time
        start_time = time.time()
        
        progress_win = tk.Toplevel(self)
        progress_win.title("Bidvest Reconciliation Progress")
        progress_win.geometry("600x280")
        progress_win.resizable(False, False)
        progress_win.grab_set()  # Make modal
        progress_win.configure(bg="#f8f9fc")
        
        # Configure custom progress bar style
        style = ttk.Style(progress_win)
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor='#e2e8f0',
                       background='#059669',
                       borderwidth=0,
                       lightcolor='#059669',
                       darkcolor='#059669')
        
        # Center the window
        progress_win.update_idletasks()
        x = (progress_win.winfo_screenwidth() // 2) - (600 // 2)
        y = (progress_win.winfo_screenheight() // 2) - (280 // 2)
        progress_win.geometry(f"600x280+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(progress_win, bg="#0ea5e9", height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔄 Reconciliation in Progress", 
                font=("Segoe UI", 16, "bold"), bg="#0ea5e9", fg="white").pack(pady=15)
        
        progress_frame = tk.Frame(progress_win, bg="#f8f9fc", padx=30, pady=25)
        progress_frame.pack(fill="both", expand=True)
        
        status_label = tk.Label(progress_frame, text="Initializing reconciliation process...", 
                               font=("Segoe UI", 12, "bold"), bg="#f8f9fc", fg="#1e293b")
        status_label.pack(pady=(0, 15))
        
        # Progress bar with percentage
        progress_container = tk.Frame(progress_frame, bg="#f8f9fc")
        progress_container.pack(fill="x", pady=(0, 10))
        
        progress_bar = ttk.Progressbar(progress_container, length=500, mode='determinate', 
                                     style="Custom.Horizontal.TProgressbar")
        progress_bar.pack(side="left", fill="x", expand=True)
        
        percentage_label = tk.Label(progress_container, text="0%", 
                                   font=("Segoe UI", 11, "bold"), bg="#f8f9fc", fg="#059669", width=5)
        percentage_label.pack(side="right", padx=(10, 0))
        
        detail_label = tk.Label(progress_frame, text="", font=("Segoe UI", 10), 
                               fg="#64748b", bg="#f8f9fc", wraplength=500, justify="left")
        detail_label.pack(pady=(0, 15))
        
        # Time tracking
        time_frame = tk.Frame(progress_frame, bg="#f8f9fc")
        time_frame.pack(fill="x")
        
        time_elapsed_label = tk.Label(time_frame, text="⏱️ Time Elapsed: 0.0s", 
                                     font=("Segoe UI", 10), bg="#f8f9fc", fg="#6b7280")
        time_elapsed_label.pack(side="left")
        
        eta_label = tk.Label(time_frame, text="📅 ETA: Calculating...", 
                            font=("Segoe UI", 10), bg="#f8f9fc", fg="#6b7280")
        eta_label.pack(side="right")
        
        def update_progress(step, total, message, detail=""):
            current_time = time.time()
            elapsed = current_time - start_time
            percentage = (step / total) * 100
            
            progress_bar['value'] = percentage
            percentage_label.config(text=f"{percentage:.0f}%")
            status_label.config(text=message)
            detail_label.config(text=detail)
            time_elapsed_label.config(text=f"⏱️ Time Elapsed: {elapsed:.1f}s")
            
            # Calculate ETA
            if step > 0:
                avg_time_per_step = elapsed / step
                remaining_steps = total - step
                eta = avg_time_per_step * remaining_steps
                eta_label.config(text=f"📅 ETA: {eta:.1f}s remaining")
            else:
                eta_label.config(text="📅 ETA: Calculating...")
            
            progress_win.update()

        try:
            # Step 1: Data preparation (10%)
            update_progress(1, 10, "Preparing data...", "Copying dataframes")
            ledger = self.ledger_df.copy()
            statement = self.statement_df.copy()
            
            # Step 2: Date parsing (20%)
            update_progress(2, 10, "Parsing dates...", "Processing date formats")
            
            def try_parse_date_fast(val, formats):
                if pd.isnull(val):
                    return None
                s = str(val).split()[0].replace('-', '/').strip()
                for fmt in formats:
                    try:
                        return datetime.strptime(s, fmt)
                    except:
                        continue
                try:
                    return pd.to_datetime(s, errors='coerce')
                except:
                    return None

            date_formats = ["%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y", "%m/%d/%y"]
            
            # Vectorized date parsing for better performance
            ledger['__date'] = ledger[l_date_col].apply(lambda v: try_parse_date_fast(v, date_formats))
            statement['__date'] = statement[s_date_col].apply(lambda v: try_parse_date_fast(v, date_formats))
            
            # Step 3: Amount parsing (30%)
            update_progress(3, 10, "Parsing amounts...", "Converting to numeric values")
            
            # Parse amounts - handle both debits and credits from ledger
            ledger['__debit'] = pd.to_numeric(ledger[l_debit_col], errors='coerce').fillna(0)
            ledger['__credit'] = pd.to_numeric(ledger[l_credit_col], errors='coerce').fillna(0)
            statement['__amt'] = pd.to_numeric(statement[s_amt_col], errors='coerce')
            
            # Step 4: Error detection (40%)
            update_progress(4, 10, "Detecting errors...", "Identifying problematic rows")
            
            ledger_errors = ledger[ledger['__date'].isnull() | 
                                 (ledger['__debit'].isnull() & ledger['__credit'].isnull())]
            statement_errors = statement[statement['__date'].isnull() | statement['__amt'].isnull()]
            
            # Step 5: Building fast indexes (50%)
            update_progress(5, 10, "Building indexes...", "Creating lookup tables for matching")
            
            # Build super-fast index for statement: (date, amount) -> list of indices
            stmt_debit_idx = defaultdict(list)  # For positive amounts (matching debits)
            stmt_credit_idx = defaultdict(list)  # For negative amounts (matching credits)
            
            for si, srow in statement.iterrows():
                stmt_amt = srow['__amt']
                stmt_date = srow['__date']
                
                if pd.isnull(stmt_date) or pd.isnull(stmt_amt):
                    continue
                    
                try:
                    stmt_date_clean = pd.to_datetime(str(stmt_date).strip(), errors='coerce')
                except:
                    stmt_date_clean = stmt_date
                    
                if pd.isnull(stmt_date_clean):
                    continue
                    
                key = (stmt_date_clean.date(), round(abs(stmt_amt), 2))
                
                if stmt_amt > 0:
                    stmt_debit_idx[key].append(si)  # Positive amounts match debits
                else:
                    stmt_credit_idx[key].append(si)  # Negative amounts match credits
            
            # Step 6: Fast matching - Debits (60%)
            update_progress(6, 10, "Matching debits...", "Processing debit transactions")
            
            matched_pairs = []
            matched_statement = set()
            debug_matches = []
            
            # Match debits (positive ledger debits with positive statement amounts)
            for i, lrow in ledger.iterrows():
                ldate = lrow['__date']
                ldebit = lrow['__debit']
                
                if pd.isnull(ldate) or pd.isnull(ldebit) or ldebit <= 0:
                    continue
                    
                try:
                    ldate_clean = pd.to_datetime(str(ldate).strip(), errors='coerce')
                except:
                    ldate_clean = ldate
                    
                if pd.isnull(ldate_clean):
                    continue
                
                # Expected statement date (ledger date + 1 day)
                sdate = ldate_clean + timedelta(days=1)
                key = (sdate.date(), round(ldebit, 2))
                
                if key in stmt_debit_idx:
                    for si in stmt_debit_idx[key]:
                        if si in matched_statement:
                            continue
                            
                        stmt_amt = statement.at[si, '__amt']
                        stmt_date = statement.at[si, '__date']
                        
                        try:
                            stmt_date_clean = pd.to_datetime(str(stmt_date).strip(), errors='coerce')
                        except:
                            stmt_date_clean = stmt_date
                        
                        # Match if statement date is 1 day after ledger and amounts match exactly
                        if (not pd.isnull(stmt_date_clean) and 
                            (stmt_date_clean.date() - ldate_clean.date()).days == 1 and
                            round(ldebit, 2) == round(stmt_amt, 2) and stmt_amt > 0):
                            
                            matched_pairs.append((i, si, 'debit'))
                            matched_statement.add(si)
                            debug_matches.append({
                                'type': 'debit',
                                'ledger_idx': i,
                                'statement_idx': si,
                                'ledger_date': ldate,
                                'statement_date': stmt_date,
                                'ledger_amount': ldebit,
                                'statement_amount': stmt_amt
                            })
                            break
            
            # Step 7: Fast matching - Credits (70%)
            update_progress(7, 10, "Matching credits...", "Processing credit transactions")
            
            # Match credits (positive ledger credits with negative statement amounts)
            for i, lrow in ledger.iterrows():
                ldate = lrow['__date']
                lcredit = lrow['__credit']
                
                if pd.isnull(ldate) or pd.isnull(lcredit) or lcredit <= 0:
                    continue
                    
                try:
                    ldate_clean = pd.to_datetime(str(ldate).strip(), errors='coerce')
                except:
                    ldate_clean = ldate
                    
                if pd.isnull(ldate_clean):
                    continue
                
                # Expected statement date (ledger date + 1 day)
                sdate = ldate_clean + timedelta(days=1)
                key = (sdate.date(), round(lcredit, 2))
                
                if key in stmt_credit_idx:
                    for si in stmt_credit_idx[key]:
                        if si in matched_statement:
                            continue
                            
                        stmt_amt = statement.at[si, '__amt']
                        stmt_date = statement.at[si, '__date']
                        
                        try:
                            stmt_date_clean = pd.to_datetime(str(stmt_date).strip(), errors='coerce')
                        except:
                            stmt_date_clean = stmt_date
                        
                        # Match if statement date is 1 day after ledger and amounts match (credit = negative)
                        if (not pd.isnull(stmt_date_clean) and 
                            (stmt_date_clean.date() - ldate_clean.date()).days == 1 and
                            round(lcredit, 2) == round(abs(stmt_amt), 2) and stmt_amt < 0):
                            
                            matched_pairs.append((i, si, 'credit'))
                            matched_statement.add(si)
                            debug_matches.append({
                                'type': 'credit',
                                'ledger_idx': i,
                                'statement_idx': si,
                                'ledger_date': ldate,
                                'statement_date': stmt_date,
                                'ledger_amount': lcredit,
                                'statement_amount': stmt_amt
                            })
                            break
            
            # Step 8: Grouping transactions (80%)
            update_progress(8, 10, "Grouping transactions...", "Creating transaction groups")
            
            # Group unmatched transactions by date and amount
            matched_ledger_idx = {pair[0] for pair in matched_pairs}
            matched_stmt_idx = {pair[1] for pair in matched_pairs}
            
            unmatched_ledger = ledger[~ledger.index.isin(matched_ledger_idx)]
            unmatched_statement = statement[~statement.index.isin(matched_stmt_idx)]
            
            # Group by date and amount
            ledger_groups = defaultdict(list)
            stmt_groups = defaultdict(list)
            
            # Group unmatched ledger entries
            for idx, row in unmatched_ledger.iterrows():
                if pd.isnull(row['__date']):
                    continue
                    
                # Group debits
                if not pd.isnull(row['__debit']) and row['__debit'] > 0:
                    date_key = row['__date'].date() if hasattr(row['__date'], 'date') else str(row['__date'])[:10]
                    key = (date_key, round(row['__debit'], 2), 'debit')
                    ledger_groups[key].append(idx)
                
                # Group credits
                if not pd.isnull(row['__credit']) and row['__credit'] > 0:
                    date_key = row['__date'].date() if hasattr(row['__date'], 'date') else str(row['__date'])[:10]
                    key = (date_key, round(row['__credit'], 2), 'credit')
                    ledger_groups[key].append(idx)
            
            # Group unmatched statement entries
            for idx, row in unmatched_statement.iterrows():
                if pd.isnull(row['__date']) or pd.isnull(row['__amt']):
                    continue
                    
                date_key = row['__date'].date() if hasattr(row['__date'], 'date') else str(row['__date'])[:10]
                amt_type = 'debit' if row['__amt'] > 0 else 'credit'
                key = (date_key, round(abs(row['__amt']), 2), amt_type)
                stmt_groups[key].append(idx)
            
            # Find grouped matches (same date, same amount, but not necessarily +1 day rule)
            grouped_matches = []
            for key in ledger_groups:
                if key in stmt_groups and len(ledger_groups[key]) > 0 and len(stmt_groups[key]) > 0:
                    # Match groups (could be multiple to multiple)
                    for l_idx in ledger_groups[key]:
                        for s_idx in stmt_groups[key]:
                            if s_idx not in matched_statement:
                                grouped_matches.append((l_idx, s_idx, f'group_{key[2]}'))
                                matched_statement.add(s_idx)
                                break  # One-to-one matching within groups
                        if len(grouped_matches) > 0 and grouped_matches[-1][0] == l_idx:
                            continue  # This ledger entry was matched
            
            # Step 9: Finalizing results (90%)
            update_progress(9, 10, "Finalizing results...", "Marking matched transactions")
            
            # Store all matched pairs
            self.matched_pairs = [(pair[0], pair[1]) for pair in matched_pairs]  # Remove type for compatibility
            self.grouped_pairs = [(pair[0], pair[1]) for pair in grouped_matches]
            
            # Mark results in dataframes
            ledger['Matched'] = False
            ledger['MatchType'] = ''
            statement['Matched'] = False
            statement['MatchType'] = ''
            
            # Mark 100% matches
            for li, si, match_type in matched_pairs:
                ledger.at[li, 'Matched'] = True
                ledger.at[li, 'MatchType'] = f'100%_{match_type}'
                statement.at[si, 'Matched'] = True
                statement.at[si, 'MatchType'] = f'100%_{match_type}'
            
            # Mark grouped matches
            for li, si, match_type in grouped_matches:
                if not ledger.at[li, 'Matched']:  # Don't overwrite 100% matches
                    ledger.at[li, 'Matched'] = True
                    ledger.at[li, 'MatchType'] = match_type
                if not statement.at[si, 'Matched']:
                    statement.at[si, 'Matched'] = True
                    statement.at[si, 'MatchType'] = match_type
            
            # Update original dataframes
            self.ledger_df['Matched'] = ledger['Matched']
            self.ledger_df['MatchType'] = ledger['MatchType']
            self.statement_df['Matched'] = statement['Matched']
            self.statement_df['MatchType'] = statement['MatchType']
            
            # Step 10: Completion (100%)
            total_time = time.time() - start_time
            update_progress(10, 10, "✅ Reconciliation Complete!", f"Total time: {total_time:.2f} seconds")
            
            # Brief pause to show completion
            progress_win.after(1500, progress_win.destroy)  # Auto-close after 1.5 seconds
            
            # Save debug information
            with open('bidvest_debug_matches.json', 'w', encoding='utf-8') as f:
                json.dump(debug_matches, f, default=str, indent=2)
            
            # Show results
            total_ledger = len(ledger)
            total_statement = len(statement)
            exact_matches = len(matched_pairs)
            group_matches = len(grouped_matches)
            unmatched_ledger = total_ledger - exact_matches - group_matches
            unmatched_statement = total_statement - exact_matches - group_matches
            
            summary = f"🎯 RECONCILIATION COMPLETE\n\n"
            summary += f"⏱️ Processing Time: {total_time:.2f} seconds\n"
            summary += f"🚀 Performance: {(total_ledger + total_statement)/total_time:.0f} records/sec\n\n"
            summary += f"✅ 100% Exact Matches: {exact_matches}\n"
            summary += f"🔄 Grouped Matches: {group_matches}\n"
            summary += f"❌ Unmatched Ledger: {unmatched_ledger}\n"
            summary += f"❌ Unmatched Statement: {unmatched_statement}\n\n"
            summary += f"📊 Total Processed:\n"
            summary += f"   Ledger: {total_ledger} | Statement: {total_statement}"
            
            if not ledger_errors.empty or not statement_errors.empty:
                summary += f"\n\n⚠️ Rows with errors:\n"
                summary += f"Ledger: {list(ledger_errors.index)}\n"
                summary += f"Statement: {list(statement_errors.index)}"
            
            messagebox.showinfo("Reconciliation Complete", summary)
            
        except Exception as e:
            total_time = time.time() - start_time
            progress_win.destroy()
            error_msg = f"An error occurred during reconciliation:\n\n{str(e)}\n\n"
            error_msg += f"Time elapsed before error: {total_time:.2f} seconds"
            messagebox.showerror("Reconciliation Error", error_msg)
            raise
    def add_rj_number_and_ref(self):
        import re
        import pandas as pd
        if self.ledger_df is None:
            messagebox.showwarning("No Ledger", "Please import a ledger first.")
            return
        df = self.ledger_df.copy()
        cols = list(df.columns)
        if len(cols) < 2:
            messagebox.showerror("Ledger Format Error", "Ledger must have at least two columns.")
            return
        # Insert RJ-Number and Payment Ref after column B (index 1)
        if 'RJ-Number' in df.columns or 'Payment Ref' in df.columns:
            messagebox.showinfo("Already Added", "RJ-Number and Payment Ref columns already exist.")
            return
        def extract_rj_and_ref(comment):
            if not isinstance(comment, str):
                return '', ''
            # RJ-Number: look for RJ or TX followed by digits
            rj_match = re.search(r'(RJ|TX)[-]?(\d{6,})', comment, re.IGNORECASE)
            rj = rj_match.group(0).replace('-', '') if rj_match else ''
            payref = ''
            payref_match = re.search(r'Payment Ref[#:]?\s*([\w\s\-\.,&]+)', comment, re.IGNORECASE)
            if payref_match:
                payref = payref_match.group(1).strip()
            elif rj_match:
                after = comment[rj_match.end():]
                after = after.lstrip(' .:-#')
                payref = re.split(r'[.,\n\r]', after)[0].strip()
            else:
                # No RJ-Number found, use the whole comment as Payment Ref
                payref = comment.strip()
            return rj, payref
        rj_numbers = []
        pay_refs = []
        for val in df.iloc[:,1]:
            rj, ref = extract_rj_and_ref(val)
            rj_numbers.append(rj)
            pay_refs.append(ref)
        # Insert columns after column B (index 1)
        df.insert(2, 'RJ-Number', rj_numbers)
        df.insert(3, 'Payment Ref', pay_refs)
        # Move other columns to the right
        self.ledger_df = df
        messagebox.showinfo("Success", "RJ-Number and Payment Ref columns added to the ledger.")

    def _log_audit(self, action, file_id=None, file_type=None, extra=None):
        import getpass, datetime
        user = getpass.getuser()
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('bidvest_audit.log', 'a', encoding='utf-8') as f:
            f.write(f"{ts} | {user} | {action} | file_id={file_id} | file_type={file_type} | {extra or ''}\n")

    def save_originals(self):
        from tkinter import simpledialog
        import uuid
        from results_db import ResultsDB
        if self.ledger_df is None or self.statement_df is None:
            messagebox.showwarning("Missing Data", "Please import both ledger and statement before saving originals.")
            return
        pair_id = str(uuid.uuid4())
        name = simpledialog.askstring("Save Originals", "Enter a name for this file pair:")
        if not name:
            return
        db = ResultsDB()
        ledger_id = db.save_original_file(name, 'ledger', self.ledger_df, {'source': 'Bidvest'}, pair_id=pair_id)
        statement_id = db.save_original_file(name, 'statement', self.statement_df, {'source': 'Bidvest'}, pair_id=pair_id)
        self._log_audit('save', ledger_id, 'ledger')
        self._log_audit('save', statement_id, 'statement')
        messagebox.showinfo("Saved", "Ledger and Statement saved as originals.")

    def manage_originals(self):
        from results_db import ResultsDB
        import pandas as pd
        db = ResultsDB()
        originals = db.list_original_files()
        win = tk.Toplevel(self)
        win.title("Manage Saved Originals")
        win.state('zoomed')
        search_var = tk.StringVar()
        def filter_table(*_):
            val = search_var.get().lower()
            for iid in tree.get_children():
                values = tree.item(iid)['values']
                if any(val in str(v).lower() for v in values):
                    tree.reattach(iid, '', 'end')
                else:
                    tree.detach(iid)
        topbar = tk.Frame(win)
        topbar.pack(fill='x', pady=8)
        tk.Label(topbar, text="Search:", font=("Segoe UI", 10)).pack(side='left', padx=(10,2))
        search_entry = tk.Entry(topbar, textvariable=search_var, font=("Segoe UI", 10), width=30)
        search_entry.pack(side='left')
        search_var.trace_add('write', filter_table)
        tree = ttk.Treeview(win, columns=("ID", "Pair ID", "Name", "Date", "Type"), show="headings", selectmode="browse")
        for col in ("ID", "Pair ID", "Name", "Date", "Type"):
            tree.heading(col, text=col)
            tree.column(col, width=180 if col!="ID" else 60, anchor="center")
        for row in originals:
            tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4]))
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        btnbar = tk.Frame(win)
        btnbar.pack(fill='x', pady=8)
        def show_audit():
            import os
            if not os.path.exists('bidvest_audit.log'):
                messagebox.showinfo("Audit Trail", "No audit log found.")
                return
            with open('bidvest_audit.log', 'r', encoding='utf-8') as f:
                log = f.read()
            win2 = tk.Toplevel(win)
            win2.title("Bidvest Audit Trail")
            txt = tk.Text(win2, wrap='none', font=("Consolas", 10))
            txt.pack(fill='both', expand=True)
            txt.insert('1.0', log)
            txt.config(state='disabled')
        def download_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a file to download.")
                return
            file_id = tree.item(sel[0])['values'][0]
            file_info = db.get_original_file(file_id)
            if not file_info:
                messagebox.showerror("Not Found", "File not found in database.")
                return
            file_type = file_info['file_type']
            df = file_info['file_data']
            from tkinter import filedialog
            ext = 'xlsx' if file_type == 'ledger' else 'csv'
            file_path = filedialog.asksaveasfilename(defaultextension=f'.{ext}', filetypes=[("Excel","*.xlsx"),("CSV","*.csv"),("All files","*.*")])
            if not file_path:
                return
            try:
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False)
                else:
                    df.to_excel(file_path, index=False)
                self._log_audit('download', file_id, file_type, f'downloaded to {file_path}')
                messagebox.showinfo("Downloaded", f"File saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a file to delete.")
                return
            file_id = tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Delete", "Are you sure you want to delete this file?"):
                self._log_audit('delete', file_id)
                db.delete_original_file(file_id)
                tree.delete(sel[0])
        tk.Button(btnbar, text="Download", command=download_selected, bg="#38bdf8", fg="white", font=("Segoe UI", 10, "bold")).pack(side='left', padx=10)
        tk.Button(btnbar, text="Delete", command=delete_selected, bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold")).pack(side='left', padx=10)
        tk.Button(btnbar, text="Audit Trail", command=show_audit, bg="#fbbf24", fg="#1e293b", font=("Segoe UI", 10, "bold")).pack(side='right', padx=10)
        tk.Button(btnbar, text="Close", command=win.destroy, bg="#64748b", fg="white", font=("Segoe UI", 10)).pack(side='right', padx=10)
    def view_edit_ledger(self):
        if self.ledger_df is None:
            messagebox.showwarning("No Ledger", "Please import a ledger first.")
            return
        self._open_dataframe_editor(self.ledger_df, "Ledger", self._save_ledger_changes)

    def view_edit_statement(self):
        if self.statement_df is None:
            messagebox.showwarning("No Statement", "Please import a statement first.")
            return
        self._open_dataframe_editor(self.statement_df, "Statement", self._save_statement_changes)

    def _open_dataframe_editor(self, df, title, save_callback):
        import pandas as pd
        editor = tk.Toplevel(self)
        editor.title(f"Edit {title}")
        editor.state('zoomed')  # Open maximized/full screen
        frame = tk.Frame(editor)
        frame.pack(fill="both", expand=True)
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=28)
        tree = ttk.Treeview(frame, show="headings", style="Custom.Treeview")
        tree.pack(side="left", fill="both", expand=True)
        vsb = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        # Alternate row colors for grid effect
        for idx, row in df.iterrows():
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", "end", iid=str(idx), values=list(row), tags=(tag,))
        tree.tag_configure('evenrow', background='#f1f5f9')
        tree.tag_configure('oddrow', background='#e2e8f0')
        # Add border to headings for column separation
        style.configure("Custom.Treeview.Heading", borderwidth=1, relief="solid")
        def on_double_click(event):
            item = tree.identify_row(event.y)
            col = tree.identify_column(event.x)
            if not item or not col:
                return
            col_idx = int(col.replace('#','')) - 1
            old_val = tree.set(item, tree["columns"][col_idx])
            entry = tk.Entry(editor)
            entry.insert(0, old_val)
            entry.place(x=event.x_root-editor.winfo_rootx(), y=event.y_root-editor.winfo_rooty())
            entry.focus()
            def save_edit(e=None):
                new_val = entry.get()
                tree.set(item, tree["columns"][col_idx], new_val)
                entry.destroy()
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: entry.destroy())
        tree.bind("<Double-1>", on_double_click)
        save_btn = tk.Button(editor, text="Save Changes", command=lambda: save_callback(tree, editor), bg="#059669", fg="white", font=("Segoe UI", 10, "bold"))
        save_btn.pack(pady=8)

    def _save_ledger_changes(self, tree, editor):
        import pandas as pd
        data = [tree.item(iid)["values"] for iid in tree.get_children()]
        self.ledger_df = pd.DataFrame(data, columns=self.ledger_df.columns)
        messagebox.showinfo("Ledger Saved", "Ledger changes saved.")
        editor.destroy()

    def _save_statement_changes(self, tree, editor):
        import pandas as pd
        data = [tree.item(iid)["values"] for iid in tree.get_children()]
        self.statement_df = pd.DataFrame(data, columns=self.statement_df.columns)
        messagebox.showinfo("Statement Saved", "Statement changes saved.")
        editor.destroy()
    def __init__(self, master, show_back):
        super().__init__(master, bg="#f8f9fc")
        self.master = master
        self.show_back = show_back
        self.ledger_df = None
        self.statement_df = None
        self.pack(fill="both", expand=True)
        self.create_header()
        self.create_main_content()
        self.create_footer()

    def import_ledger(self):
        from tkinter import filedialog
        import pandas as pd
        file_path = filedialog.askopenfilename(
            title="Select Ledger File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl' if file_path.lower().endswith('x') else None)
            elif file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, low_memory=False)
            else:
                messagebox.showerror("Unsupported Format", "Please select a CSV or Excel file.")
                return
            self.ledger_df = df
            messagebox.showinfo("Ledger Imported", f"Ledger loaded successfully! Rows: {len(df)} Columns: {len(df.columns)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load ledger file:\n{str(e)}")

    def import_statement(self):
        from tkinter import filedialog
        import pandas as pd
        file_path = filedialog.askopenfilename(
            title="Select Statement File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl' if file_path.lower().endswith('x') else None)
            elif file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, low_memory=False)
            else:
                messagebox.showerror("Unsupported Format", "Please select a CSV or Excel file.")
                return
            self.statement_df = df
            messagebox.showinfo("Statement Imported", f"Statement loaded successfully! Rows: {len(df)} Columns: {len(df.columns)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load statement file:\n{str(e)}")

    def create_header(self):
        # Premium deep orange header with white text
        header_frame = tk.Frame(self, bg="#b45309", height=90)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        # Back button
        back_btn = tk.Button(header_frame, text="← Back", font=("Segoe UI", 12, "bold"),
                            bg="#fff", fg="#b45309", relief="flat", bd=0,
                            padx=18, pady=8, command=self.show_back, cursor="hand2", activebackground="#fde68a", activeforeground="#b45309")
        back_btn.pack(side="left", padx=30, pady=25)
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#fde68a"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fff"))
        # Title and icon
        title_frame = tk.Frame(header_frame, bg="#b45309")
        title_frame.pack(expand=True)
        icon_label = tk.Label(title_frame, text="💼", font=("Segoe UI Emoji", 32), bg="#b45309", fg="#fbbf24")
        icon_label.pack(side="left", padx=(0, 10))
        title_label = tk.Label(title_frame, text="Bidvest Workflow", font=("Segoe UI", 26, "bold"), fg="#fff", bg="#b45309")
        title_label.pack(side="left")

    def create_main_content(self):
        # Premium orange/white main content with better contrast
        main_frame = tk.Frame(self, bg="#fff")
        main_frame.pack(expand=True, fill="both", padx=40, pady=30)
        section_title = tk.Label(main_frame, text="Bidvest Features", font=("Segoe UI", 17, "bold"), fg="#b45309", bg="#fff")
        section_title.pack(anchor="w", pady=(0, 10))

        features = [
            ("📥 Import Ledger", "Import your ledger file", self.import_ledger),
            ("📄 Import Statement", "Import your bank statement", self.import_statement),
            ("👁️ View/Edit Ledger", "View and edit the imported ledger", self.view_edit_ledger),
            ("👁️ View/Edit Statement", "View and edit the imported statement", self.view_edit_statement),
            ("💾 Save Originals", "Save original files for audit", self.save_originals),
            ("🗂️ Manage Originals", "View, search, edit, download, or delete saved originals", self.manage_originals),
            ("🔢 Add RJ-Number & Ref", "Add RJ-Number and Payment Reference", self.add_rj_number_and_ref),
            ("🛠️ Configure Columns", "Choose columns to match", self.configure_columns_page),
            ("🤝 Reconcile", "Run reconciliation", self.reconcile_bidvest),
            ("📤 Export Results", "Export reconciliation results", self.export_results_popup),
            ("✅ Save Results", "Save reconciliation results", self.save_results),
            ("📚 Manage Results", "View, search, or delete saved reconciliation results", self.manage_results)
        ]
        
        # Create a scrollable frame to ensure all features are visible
        canvas = tk.Canvas(main_frame, bg="#fff", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#fff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create the grid frame inside the scrollable frame
        grid_frame = tk.Frame(scrollable_frame, bg="#fff")
        grid_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Calculate the number of rows needed for all features
        num_features = len(features)
        num_cols = 4
        num_rows = (num_features + num_cols - 1) // num_cols  # Ceiling division
        
        # Configure grid to have uniform columns and rows
        for col in range(num_cols):
            grid_frame.grid_columnconfigure(col, weight=1, minsize=280, uniform="column")
        for row in range(num_rows):  # This ensures we have enough rows for all features
            grid_frame.grid_rowconfigure(row, weight=1, minsize=180, uniform="row")
        
        for i, (title, desc, action) in enumerate(features):
            row, col = divmod(i, 4)
            print(f"🔧 Creating feature {i+1}: {title} at row {row}, col {col}")  # Debug info
            
            # Create card with consistent sizing
            card = tk.Frame(grid_frame, bg="#fff7ed", relief="groove", bd=2, 
                           highlightbackground="#fbbf24", highlightcolor="#fbbf24", highlightthickness=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Create inner frame with consistent padding
            inner_frame = tk.Frame(card, bg="#fff7ed")
            inner_frame.pack(fill="both", expand=True, padx=12, pady=12)
            
            # Configure inner frame layout
            inner_frame.grid_rowconfigure(0, weight=0)  # Title
            inner_frame.grid_rowconfigure(1, weight=1)  # Description (expandable)
            inner_frame.grid_rowconfigure(2, weight=0)  # Button
            inner_frame.grid_columnconfigure(0, weight=1)
            
            # Feature title - fixed position at top
            feature_title = tk.Label(inner_frame, text=title, font=("Segoe UI", 11, "bold"), 
                                   fg="#b45309", bg="#fff7ed", anchor="center")
            feature_title.grid(row=0, column=0, sticky="ew", pady=(0, 8))
            
            # Feature description - center area (expandable)
            feature_desc = tk.Label(inner_frame, text=desc, font=("Segoe UI", 9), 
                                  fg="#92400e", bg="#fff7ed", wraplength=220, 
                                  justify="center", anchor="center")
            feature_desc.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
            
            # Button container for precise positioning
            button_frame = tk.Frame(inner_frame, bg="#fff7ed")
            button_frame.grid(row=2, column=0, sticky="ew", pady=(0, 0))
            
            # Always create and show the Select button with uniform sizing
            btn = tk.Button(button_frame, text="Select", font=("Segoe UI", 10, "bold"),
                            bg="#b45309", fg="#fff", relief="raised", bd=2,
                            cursor="hand2", activebackground="#fbbf24", activeforeground="#b45309",
                            height=2)  # Fixed height for all buttons
            
            # Assign action if available, otherwise show a message
            if action:
                btn.config(command=action)
            else:
                btn.config(command=lambda: messagebox.showinfo("Feature", "This feature is available. Click Select to use it."))
            
            # Pack button with consistent sizing and positioning
            btn.pack(fill="x", padx=15, pady=2)  # Uniform padding from edges
            
            
            # Hover effects for all components
            def on_enter(e, c=card, if_=inner_frame, ft=feature_title, fd=feature_desc, bf=button_frame):
                c.config(bg="#fbbf24")
                if_.config(bg="#fbbf24")
                ft.config(bg="#fbbf24")
                fd.config(bg="#fbbf24")
                bf.config(bg="#fbbf24")
                
            def on_leave(e, c=card, if_=inner_frame, ft=feature_title, fd=feature_desc, bf=button_frame):
                c.config(bg="#fff7ed")
                if_.config(bg="#fff7ed")
                ft.config(bg="#fff7ed")
                fd.config(bg="#fff7ed")
                bf.config(bg="#fff7ed")
            
            # Bind hover events to all components
            for widget in [card, inner_frame, feature_title, feature_desc, button_frame, btn]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
        
        # Add mouse wheel scrolling support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#fff")
        footer_frame.pack(fill="x", padx=40, pady=(0, 24))
        footer_line = tk.Frame(footer_frame, bg="#fbbf24", height=2)
        footer_line.pack(fill="x", pady=(0, 8))
        help_label = tk.Label(footer_frame,
                             text="Tip: Use the features above to complete your Bidvest reconciliation workflow.",
                             font=("Segoe UI", 10, "italic"), fg="#b45309", bg="#fff")
        help_label.pack()

    # POST features removed as requested by user
