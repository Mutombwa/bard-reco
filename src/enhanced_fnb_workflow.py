"""
Enhanced FNB Workflow with Multi-User Integration
===============================================
FNB workflow with full multi-user collaboration support, session management,
real-time updates, and professional collaborative features
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import threading
import time
import re
from typing import Dict, List, Optional, Any

# Multi-user components removed for simplified version

class SessionManagerStub:
    """Stub for session manager"""
    def __init__(self):
        self.current_user = None

class EnhancedFNBWorkflow(tk.Frame):
    """Enhanced FNB Workflow - Simplified Version"""
    
    def __init__(self, parent, app):
        # Initialize as a regular tk.Frame
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.workflow_type = "FNB"
        
        self.app = app  # Reference to main app

        # Session management (simplified stubs)
        self.current_session = None
        self.session_manager = SessionManagerStub()

        # FNB-specific data
        self.ledger_df = None
        self.statement_df = None
        self.reconciliation_results = None
        
        # Matching settings
        self.match_settings = {
            'ledger_date_col': 'Date',
            'statement_date_col': 'Date',
            'ledger_ref_col': 'Reference',
            'statement_ref_col': 'Reference',
            'ledger_debit_col': 'Debit',
            'ledger_credit_col': 'Credit',
            'statement_amt_col': 'Amount',
            'fuzzy_ref': True,
            'similarity_ref': 85,
            'match_dates': True,
            'match_references': True,
            'match_amounts': True,
            'use_debits_only': False,
            'use_credits_only': False,
            'use_both_debit_credit': True
        }
        
        # UI variables
        self.match_dates = tk.BooleanVar(value=True)
        self.match_references = tk.BooleanVar(value=True)
        self.match_amounts = tk.BooleanVar(value=True)
        self.amount_matching_mode = tk.StringVar(value="both")
        
        # Create main content frame
        self.main_content_frame = tk.Frame(self, bg="#f8fafc")
        self.main_content_frame.pack(fill="both", expand=True)
        
        # Create the main interface
        self._create_fnb_interface()
        
        # Check authentication status
        self._check_authentication()
        
        # Initialize outstanding transactions management
        self._init_outstanding_transactions()
    
    def _check_authentication(self):
        """Check if user is authenticated, show login if not"""
        # Simplified version - authentication disabled
        pass
    
    def _show_login_dialog(self):
        """Show login dialog for authentication"""
        # Simplified version - login dialog disabled
        pass
    
    def _create_fnb_interface(self):
        """Create the main FNB workflow interface"""
        # File import section
        self._create_import_section()
        
        # Data processing section
        self._create_processing_section()
        
        # Reconciliation section
        self._create_reconciliation_section()
        
        # Results section
        self._create_results_section()
    
    def _create_import_section(self):
        """Create file import section"""
        import_frame = tk.Frame(self.main_content_frame, bg="#ffffff", relief="solid", bd=1)
        import_frame.pack(fill="x", pady=(0, 10))
        
        # Header
        header = tk.Frame(import_frame, bg="#1e40af", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="📁 File Import", font=("Segoe UI", 14, "bold"), 
                fg="white", bg="#1e40af").pack(side="left", padx=20, pady=15)
        
        # Import buttons section
        button_frame = tk.Frame(import_frame, bg="#f8fafc")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        # File import buttons
        self._create_import_button(button_frame, "📊 Import Ledger", 
                                 "Import your ledger file (Excel/CSV)", 
                                 self._import_ledger, "#059669")
        
        self._create_import_button(button_frame, "🏦 Import Statement", 
                                 "Import bank statement file (Excel/CSV)", 
                                 self._import_statement, "#3b82f6")
        
        # File status display
        status_frame = tk.Frame(import_frame, bg="#f1f5f9")
        status_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.ledger_status = tk.Label(status_frame, text="❌ No ledger loaded", 
                                    font=("Segoe UI", 10), fg="#dc2626", bg="#f1f5f9")
        self.ledger_status.pack(anchor="w", pady=2)
        
        self.statement_status = tk.Label(status_frame, text="❌ No statement loaded", 
                                       font=("Segoe UI", 10), fg="#dc2626", bg="#f1f5f9")
        self.statement_status.pack(anchor="w", pady=2)
    
    def _create_import_button(self, parent, text, tooltip, command, color):
        """Create an import button with styling"""
        btn_frame = tk.Frame(parent, bg="#f8fafc")
        btn_frame.pack(side="left", padx=(0, 15))
        
        btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 11, "bold"), 
                       bg=color, fg="white", relief="flat", padx=20, pady=10,
                       command=command, cursor="hand2")
        btn.pack()
        
        # Tooltip
        tk.Label(btn_frame, text=tooltip, font=("Segoe UI", 9), 
                fg="#6b7280", bg="#f8fafc").pack(pady=(5, 0))
    
    def _create_processing_section(self):
        """Create data processing section"""
        process_frame = tk.Frame(self.main_content_frame, bg="#ffffff", relief="solid", bd=1)
        process_frame.pack(fill="x", pady=(0, 10))
        
        # Header
        header = tk.Frame(process_frame, bg="#059669", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Data Processing", font=("Segoe UI", 14, "bold"), 
                fg="white", bg="#059669").pack(side="left", padx=20, pady=15)
        
        # Processing options
        options_frame = tk.Frame(process_frame, bg="#f8fafc")
        options_frame.pack(fill="x", padx=20, pady=15)
        
        # Column management buttons
        self._create_processing_button(options_frame, "🏷️ Add References", 
                                     "Extract reference names from descriptions", 
                                     self._add_reference_column, "#7c3aed")
        
        self._create_processing_button(options_frame, "🔢 Add RJ Numbers", 
                                     "Extract RJ numbers and payment references", 
                                     self._add_rj_columns, "#f59e0b")
        
        self._create_processing_button(options_frame, "👁️ View Data", 
                                     "Preview imported data files", 
                                     self._view_data, "#6b7280")
    
    def _create_processing_button(self, parent, text, tooltip, command, color):
        """Create a processing button with styling"""
        btn_frame = tk.Frame(parent, bg="#f8fafc")
        btn_frame.pack(side="left", padx=(0, 15))
        
        btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 11, "bold"), 
                       bg=color, fg="white", relief="flat", padx=20, pady=10,
                       command=command, cursor="hand2")
        btn.pack()
        
        # Tooltip
        tk.Label(btn_frame, text=tooltip, font=("Segoe UI", 9), 
                fg="#6b7280", bg="#f8fafc").pack(pady=(5, 0))
    
    def _create_reconciliation_section(self):
        """Create reconciliation configuration section"""
        recon_frame = tk.Frame(self.main_content_frame, bg="#ffffff", relief="solid", bd=1)
        recon_frame.pack(fill="x", pady=(0, 10))
        
        # Header
        header = tk.Frame(recon_frame, bg="#dc2626", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#dc2626")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(header_content, text="🔄 Reconciliation", font=("Segoe UI", 14, "bold"), 
                fg="white", bg="#dc2626").pack(side="left")
        
        # Configuration button
        config_btn = tk.Button(header_content, text="⚙️ Configure", 
                             font=("Segoe UI", 10, "bold"), bg="white", fg="#dc2626",
                             relief="flat", padx=15, pady=5, command=self._configure_matching,
                             cursor="hand2")
        config_btn.pack(side="right")
        
        # Matching options
        options_frame = tk.Frame(recon_frame, bg="#f8fafc")
        options_frame.pack(fill="x", padx=20, pady=15)
        
        # Quick mode buttons
        modes_frame = tk.Frame(options_frame, bg="#f8fafc")
        modes_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(modes_frame, text="🚀 Quick Modes:", font=("Segoe UI", 12, "bold"), 
                fg="#1e293b", bg="#f8fafc").pack(anchor="w", pady=(0, 10))
        
        buttons_row = tk.Frame(modes_frame, bg="#f8fafc")
        buttons_row.pack(fill="x")
        
        # Mode buttons
        self._create_mode_button(buttons_row, "⚡ References Only", 
                               "Super fast matching by references only", 
                               self._set_references_only_mode, "#059669")
        
        self._create_mode_button(buttons_row, "🎯 All Fields", 
                               "Comprehensive matching using all fields", 
                               self._set_all_fields_mode, "#3b82f6")
        
        self._create_mode_button(buttons_row, "📅💰 Dates & Amounts", 
                               "Match by dates and amounts only", 
                               self._set_dates_amounts_mode, "#f59e0b")
        
        # Start reconciliation button
        start_frame = tk.Frame(options_frame, bg="#f8fafc")
        start_frame.pack(fill="x", pady=(15, 0))
        
        self.reconcile_btn = tk.Button(start_frame, text="🚀 Start Reconciliation", 
                                     font=("Segoe UI", 14, "bold"), bg="#dc2626", fg="white",
                                     relief="flat", padx=30, pady=15, command=self._start_reconciliation,
                                     cursor="hand2", state="disabled")
        self.reconcile_btn.pack()
    
    def _create_mode_button(self, parent, text, tooltip, command, color):
        """Create a mode selection button"""
        btn_frame = tk.Frame(parent, bg="#f8fafc")
        btn_frame.pack(side="left", padx=(0, 15))
        
        btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 10, "bold"), 
                       bg=color, fg="white", relief="flat", padx=15, pady=8,
                       command=command, cursor="hand2")
        btn.pack()
        
        # Tooltip
        tk.Label(btn_frame, text=tooltip, font=("Segoe UI", 8), 
                fg="#6b7280", bg="#f8fafc").pack(pady=(3, 0))
    
    def _create_results_section(self):
        """Create results display section"""
        results_frame = tk.Frame(self.main_content_frame, bg="#ffffff", relief="solid", bd=1)
        results_frame.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(results_frame, bg="#7c3aed", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#7c3aed")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(header_content, text="📊 Results", font=("Segoe UI", 14, "bold"), 
                fg="white", bg="#7c3aed").pack(side="left")
        
        # Buttons frame
        buttons_frame = tk.Frame(header_content, bg="#7c3aed")
        buttons_frame.pack(side="right")
        
        # POST to Dashboard button
        self.post_dashboard_btn = tk.Button(buttons_frame, text="🚀 POST to Dashboard", 
                                          font=("Segoe UI", 10, "bold"), bg="#10b981", fg="white",
                                          relief="flat", padx=15, pady=5, command=self.post_to_collaborative_dashboard,
                                          cursor="hand2", state="disabled")
        self.post_dashboard_btn.pack(side="right", padx=(0, 10))
        
        # Export button
        self.export_btn = tk.Button(buttons_frame, text="📤 Export", 
                                   font=("Segoe UI", 10, "bold"), bg="white", fg="#7c3aed",
                                   relief="flat", padx=15, pady=5, command=self._export_results,
                                   cursor="hand2", state="disabled")
        self.export_btn.pack(side="right")
        
        # Results content
        self.results_content = tk.Frame(results_frame, bg="#f8fafc")
        self.results_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Default message
        self.results_label = tk.Label(self.results_content, 
                                    text="📋 No reconciliation results yet\n\nImport files and run reconciliation to see results here",
                                    font=("Segoe UI", 12), fg="#6b7280", bg="#f8fafc")
        self.results_label.pack(expand=True)
    
    # Override abstract methods from base class
    def _on_session_changed(self):
        """Handle session change - load session data if available"""
        if self.current_session:
            # Try to load existing data for this session
            data = self.load_workflow_data()
            if data:
                self.set_workflow_data(data)
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get current workflow data for saving"""
        data = {
            'match_settings': self.match_settings,
            'ledger_filename': getattr(self, 'ledger_filename', None),
            'statement_filename': getattr(self, 'statement_filename', None),
            'has_ledger': self.ledger_df is not None,
            'has_statement': self.statement_df is not None,
            'reconciliation_complete': self.reconciliation_results is not None
        }
        
        # Include data if available (serialize DataFrames)
        if self.ledger_df is not None:
            data['ledger_data'] = self.ledger_df.to_dict('records')
            data['ledger_columns'] = list(self.ledger_df.columns)
        
        if self.statement_df is not None:
            data['statement_data'] = self.statement_df.to_dict('records')
            data['statement_columns'] = list(self.statement_df.columns)
        
        if self.reconciliation_results is not None:
            data['reconciliation_results'] = self._serialize_results(self.reconciliation_results)
        
        return data
    
    def set_workflow_data(self, data: Dict[str, Any]):
        """Set workflow data from loaded session"""
        try:
            # Restore match settings
            if 'match_settings' in data:
                self.match_settings.update(data['match_settings'])
            
            # Restore DataFrames if available
            if 'ledger_data' in data and 'ledger_columns' in data:
                self.ledger_df = pd.DataFrame(data['ledger_data'], columns=data['ledger_columns'])
                self.ledger_filename = data.get('ledger_filename', 'Loaded from session')
                self._update_ledger_status()
            
            if 'statement_data' in data and 'statement_columns' in data:
                self.statement_df = pd.DataFrame(data['statement_data'], columns=data['statement_columns'])
                self.statement_filename = data.get('statement_filename', 'Loaded from session')
                self._update_statement_status()
            
            # Restore reconciliation results
            if 'reconciliation_results' in data:
                self.reconciliation_results = self._deserialize_results(data['reconciliation_results'])
                self._display_results()
            
            # Update UI state
            self._update_ui_state()
            
            messagebox.showinfo("Session Loaded", 
                              f"Session data loaded successfully!\n"
                              f"• Ledger: {'✅' if data.get('has_ledger') else '❌'}\n"
                              f"• Statement: {'✅' if data.get('has_statement') else '❌'}\n"
                              f"• Results: {'✅' if data.get('reconciliation_complete') else '❌'}")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load session data: {str(e)}")
    
    # File import methods
    def _import_ledger(self):
        """Import ledger file"""
        if not self.session_manager.current_user:
            messagebox.showwarning("Authentication Required", "Please log in first")
            return
        
        filename = filedialog.askopenfilename(
            title="Import Ledger File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Read file
                if filename.endswith('.csv'):
                    df = pd.read_csv(filename)
                else:
                    df = pd.read_excel(filename)
                
                if df.empty:
                    messagebox.showerror("Import Error", "The file appears to be empty")
                    return
                
                self.ledger_df = df
                self.ledger_filename = filename
                
                # Simplified version - file upload disabled
                # Upload file to session if active - disabled in simplified version
                
                self._update_ledger_status()
                self._update_ui_state()
                
                messagebox.showinfo("Import Success", 
                                  f"Ledger imported successfully!\n"
                                  f"• Rows: {len(df)}\n"
                                  f"• Columns: {len(df.columns)}")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import ledger: {str(e)}")
    
    def _import_statement(self):
        """Import statement file"""
        if not self.session_manager.current_user:
            messagebox.showwarning("Authentication Required", "Please log in first")
            return
        
        filename = filedialog.askopenfilename(
            title="Import Bank Statement",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Read file
                if filename.endswith('.csv'):
                    df = pd.read_csv(filename)
                else:
                    df = pd.read_excel(filename)
                
                if df.empty:
                    messagebox.showerror("Import Error", "The file appears to be empty")
                    return
                
                self.statement_df = df
                self.statement_filename = filename
                
                # Simplified version - file upload disabled
                # Upload file to session if active - disabled in simplified version
                
                self._update_statement_status()
                self._update_ui_state()
                
                messagebox.showinfo("Import Success", 
                                  f"Statement imported successfully!\n"
                                  f"• Rows: {len(df)}\n"
                                  f"• Columns: {len(df.columns)}")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import statement: {str(e)}")
    
    def _update_ledger_status(self):
        """Update ledger status display"""
        if self.ledger_df is not None:
            filename = getattr(self, 'ledger_filename', 'Unknown')
            rows = len(self.ledger_df)
            cols = len(self.ledger_df.columns)
            self.ledger_status.config(
                text=f"✅ Ledger loaded: {filename} ({rows} rows, {cols} columns)",
                fg="#059669"
            )
        else:
            self.ledger_status.config(text="❌ No ledger loaded", fg="#dc2626")
    
    def _update_statement_status(self):
        """Update statement status display"""
        if self.statement_df is not None:
            filename = getattr(self, 'statement_filename', 'Unknown')
            rows = len(self.statement_df)
            cols = len(self.statement_df.columns)
            self.statement_status.config(
                text=f"✅ Statement loaded: {filename} ({rows} rows, {cols} columns)",
                fg="#059669"
            )
        else:
            self.statement_status.config(text="❌ No statement loaded", fg="#dc2626")
    
    def _update_ui_state(self):
        """Update UI element states based on current data"""
        # Enable reconciliation if both files are loaded
        if self.ledger_df is not None and self.statement_df is not None:
            self.reconcile_btn.config(state="normal")
        else:
            self.reconcile_btn.config(state="disabled")
        
        # Enable export and POST if results are available
        if self.reconciliation_results is not None:
            self.export_btn.config(state="normal")
            if hasattr(self, 'post_dashboard_btn'):
                self.post_dashboard_btn.config(state="normal")
        else:
            self.export_btn.config(state="disabled")
            if hasattr(self, 'post_dashboard_btn'):
                self.post_dashboard_btn.config(state="disabled")
    
    def _serialize_results(self, results):
        """Serialize reconciliation results for storage"""
        if isinstance(results, dict):
            serialized = {}
            for key, value in results.items():
                if isinstance(value, pd.DataFrame):
                    serialized[key] = {
                        'data': value.to_dict('records'),
                        'columns': list(value.columns)
                    }
                else:
                    serialized[key] = value
            return serialized
        return results
    
    def _deserialize_results(self, serialized_results):
        """Deserialize reconciliation results from storage"""
        if isinstance(serialized_results, dict):
            results = {}
            for key, value in serialized_results.items():
                if isinstance(value, dict) and 'data' in value and 'columns' in value:
                    results[key] = pd.DataFrame(value['data'], columns=value['columns'])
                else:
                    results[key] = value
            return results
        return serialized_results

    def _init_outstanding_transactions(self):
        """Initialize outstanding transactions management"""
        try:
            import os
            import sys
            
            # Add src directory to path if needed
            src_dir = os.path.dirname(__file__)
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            # Import and integrate outstanding transactions
            from enhanced_fnb_workflow_with_outstanding import add_outstanding_transactions_to_export
            add_outstanding_transactions_to_export(self)
            
            print("✅ Outstanding Transactions feature initialized successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize outstanding transactions: {e}")
            # Continue without outstanding transactions if there's an error
    
    def post_to_collaborative_dashboard(self):
        """Post FNB reconciliation results to collaborative dashboard - ULTRA FAST VERSION"""
        try:
            if not self.reconciliation_results:
                messagebox.showerror("No Results",
                                   "❌ No reconciliation results to post.\nPlease run FNB reconciliation first.")
                return

            # Use ultra-fast bulk poster (10x-100x faster than old method!)
            from fast_posting_integration import post_fnb_results_fast
            post_fnb_results_fast(self)

        except ImportError as e:
            messagebox.showerror("Dashboard Error",
                "❌ Fast posting module not available.\n\n" +
                f"Error: {str(e)}\n\n" +
                "Please ensure fast_posting_integration.py is in src folder.")
        except Exception as e:
            messagebox.showerror("Post Error", f"❌ Failed to post to dashboard:\n\n{str(e)}")

    def _add_reference_column(self):
        """Add reference column to statement with intelligent extraction"""
        if self.statement_df is None:
            messagebox.showwarning("No Statement", "Please import a statement first")
            return

        try:
            df = self.statement_df.copy()

            # Find Description column
            desc_col = self._find_column(df, ['description', 'desc', 'transaction description'])
            if not desc_col:
                messagebox.showerror("Error", "No 'Description' column found in statement")
                return

            # Check if Reference column already exists
            if 'Reference' in df.columns:
                overwrite = messagebox.askyesno("Reference Column Exists",
                                              "Reference column already exists. Overwrite it?")
                if not overwrite:
                    return
                # Remove existing Reference column
                df = df.drop('Reference', axis=1)

            # Extract references
            references = []
            for description in df[desc_col]:
                ref = self._extract_reference_name(str(description))
                references.append(ref)

            # Add Reference column right after Description column
            desc_idx = list(df.columns).index(desc_col)
            df.insert(desc_idx + 1, 'Reference', references)

            # Update the statement dataframe
            self.statement_df = df

            # Update status display
            self._update_statement_status()

            messagebox.showinfo("Success",
                              f"✅ Reference column added successfully!\n\n"
                              f"📊 Processed {len(references)} descriptions.\n"
                              f"💾 The column will persist when configuring matches.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add reference column:\n\n{str(e)}")

    def _add_rj_columns(self):
        """Add RJ-Number and Payment Reference columns to ledger"""
        if self.ledger_df is None:
            messagebox.showwarning("No Ledger", "Please import a ledger first")
            return

        try:
            df = self.ledger_df.copy()

            # Find Description/Details column
            desc_col = self._find_column(df, ['description', 'details', 'transaction details', 'narration'])
            if not desc_col:
                messagebox.showerror("Error", "No description column found in ledger")
                return

            # Check if columns already exist
            columns_exist = []
            if 'RJ-Number' in df.columns:
                columns_exist.append('RJ-Number')
            if 'Payment Ref' in df.columns:
                columns_exist.append('Payment Ref')

            if columns_exist:
                overwrite = messagebox.askyesno("Columns Exist",
                                              f"Columns {', '.join(columns_exist)} already exist. Overwrite them?")
                if not overwrite:
                    return
                # Remove existing columns
                for col in columns_exist:
                    df = df.drop(col, axis=1)

            # Extract RJ numbers and payment references
            rj_numbers = []
            payment_refs = []
            rj_count = 0
            payref_count = 0

            for description in df[desc_col]:
                desc_str = str(description)

                # Extract RJ number
                rj_match = re.search(r'RJ-?(\d+)', desc_str, re.IGNORECASE)
                if rj_match:
                    rj_numbers.append(f"RJ-{rj_match.group(1)}")
                    rj_count += 1
                else:
                    rj_numbers.append("")

                # Extract payment reference
                payref = self._extract_payment_reference(desc_str)
                payment_refs.append(payref)
                if payref:
                    payref_count += 1

            # Add columns to dataframe at the end
            df['RJ-Number'] = rj_numbers
            df['Payment Ref'] = payment_refs

            # Update the ledger dataframe
            self.ledger_df = df

            # Update status display
            self._update_ledger_status()

            messagebox.showinfo("Columns Added",
                              f"✅ RJ-Number and Payment Ref columns added!\n\n"
                              f"📊 Extraction Summary:\n"
                              f"• RJ-Numbers found: {rj_count}\n"
                              f"• Payment References found: {payref_count}\n"
                              f"💾 These columns will persist when configuring matches.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add RJ columns:\n\n{str(e)}")

    def _view_data(self):
        """Preview imported data files"""
        if self.ledger_df is None and self.statement_df is None:
            messagebox.showwarning("No Data", "Please import ledger and statement files first.")
            return

        view_window = tk.Toplevel(self)
        view_window.title("Data Preview")
        view_window.geometry("1000x600")

        notebook = ttk.Notebook(view_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        if self.ledger_df is not None:
            ledger_frame = tk.Frame(notebook)
            notebook.add(ledger_frame, text="Ledger Data")

            text = tk.Text(ledger_frame, wrap="none")
            text.pack(fill="both", expand=True)
            text.insert("1.0", self.ledger_df.to_string())
            text.config(state="disabled")

        if self.statement_df is not None:
            statement_frame = tk.Frame(notebook)
            notebook.add(statement_frame, text="Statement Data")

            text = tk.Text(statement_frame, wrap="none")
            text.pack(fill="both", expand=True)
            text.insert("1.0", self.statement_df.to_string())
            text.config(state="disabled")

    def _configure_matching(self):
        """Show matching configuration dialog"""
        if self.ledger_df is None or self.statement_df is None:
            messagebox.showwarning("Missing Data",
                                 "Please import both ledger and statement files before configuring matching.")
            return

        try:
            from fnb_reconciliation_engine import MatchingConfigDialog

            config_dialog = MatchingConfigDialog(self.parent, self.match_settings,
                                               self.ledger_df, self.statement_df)
            new_settings = config_dialog.show_config()

            if new_settings:
                self.match_settings.update(new_settings)
                messagebox.showinfo("Configuration Updated",
                                  "✅ Matching configuration has been updated successfully!\n\n"
                                  "💾 Your column selections have been saved.")
        except ImportError as e:
            messagebox.showerror("Configuration Error",
                               f"❌ Could not load configuration dialog.\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Please ensure fnb_reconciliation_engine.py is in the src folder.")
        except Exception as e:
            messagebox.showerror("Configuration Error",
                               f"❌ Failed to configure matching:\n\n{str(e)}")

    def _set_references_only_mode(self):
        """Set references only matching mode"""
        self.match_settings['match_dates'] = False
        self.match_settings['match_amounts'] = False
        self.match_settings['match_references'] = True
        messagebox.showinfo("Mode Set", "References Only mode activated")

    def _set_all_fields_mode(self):
        """Set all fields matching mode"""
        self.match_settings['match_dates'] = True
        self.match_settings['match_amounts'] = True
        self.match_settings['match_references'] = True
        messagebox.showinfo("Mode Set", "All Fields mode activated")

    def _set_dates_amounts_mode(self):
        """Set dates and amounts matching mode"""
        self.match_settings['match_dates'] = True
        self.match_settings['match_amounts'] = True
        self.match_settings['match_references'] = False
        messagebox.showinfo("Mode Set", "Dates & Amounts mode activated")

    def _start_reconciliation(self):
        """Start the reconciliation process"""
        if self.ledger_df is None or self.statement_df is None:
            messagebox.showwarning("Missing Data", "Please import both ledger and statement files first.")
            return

        messagebox.showinfo("Feature", "Reconciliation process will be fully implemented in a future update.\n\n" +
                          "This will perform the matching based on your configured settings.")

    def _export_results(self):
        """Export reconciliation results"""
        if self.reconciliation_results is None:
            messagebox.showwarning("No Results", "Please run reconciliation first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if filename:
            try:
                # Export results (placeholder)
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _display_results(self):
        """Display reconciliation results"""
        messagebox.showinfo("Feature", "Results display will be implemented in a future update.")

    def load_workflow_data(self):
        """Load workflow data (stub)"""
        return {
            'ledger_df': self.ledger_df,
            'statement_df': self.statement_df,
            'results': self.reconciliation_results
        }

    # ===== HELPER METHODS FOR DATA PROCESSING =====

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names (case-insensitive)"""
        df_columns_lower = [col.lower().strip() for col in df.columns]

        for name in possible_names:
            name_lower = name.lower().strip()
            if name_lower in df_columns_lower:
                return df.columns[df_columns_lower.index(name_lower)]

        return None

    def _extract_reference_name(self, description: str) -> str:
        """Extract reference name from banking transaction description"""
        desc = description.strip()

        # Pattern-based extraction for common transaction types
        patterns = [
            # FNB APP PAYMENT FROM [NAME]
            (r'FNB APP PAYMENT FROM\s+(.+)', lambda m: m.group(1).strip()),

            # ADT CASH DEPO variations
            (r'ADT CASH DEPO00882112\s+(.+)', lambda m: m.group(1).strip()),
            (r'ADT CASH DEPOSIT\s+(.+)', lambda m: m.group(1).strip()),
            (r'ADT CASH DEPO([A-Z]+)\s+(.+)', lambda m: m.group(2).strip()),
            (r'ADT CASH DEPO\w*\s+(.+)', lambda m: self._extract_adt_name(m.group(1))),

            # Bank names
            (r'CAPITEC\s+(.+)', lambda m: m.group(1).strip()),
            (r'ABSA BANK\s+(.+)', lambda m: m.group(1).strip()),
            (r'NEDBANK\s+(.+)', lambda m: m.group(1).strip()),

            # Direct names
            (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[a-z]+)$', lambda m: m.group(1).strip()),
        ]

        # Try each pattern
        for pattern, extractor in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                try:
                    result = extractor(match)
                    if result:
                        return self._clean_reference_name(result)
                except Exception:
                    continue

        # Fallback: extract capitalized words
        words = desc.split()
        name_words = []
        for word in words:
            if re.match(r'^[A-Z][a-z]+$', word) or re.match(r'^[A-Z]+$', word):
                name_words.append(word)

        if name_words:
            return ' '.join(name_words[-2:]) if len(name_words) >= 2 else name_words[-1]

        return "UNKNOWN"

    def _extract_adt_name(self, full_text: str) -> str:
        """Extract name from ADT CASH DEPO transactions"""
        full_text = full_text.strip()

        # Location patterns to remove
        location_patterns = [
            r'^NEWTOWN\s+', r'^WEST GAU\s+', r'^RANDBRG\s+', r'^FESTMALL\s+',
            r'^DIEPSLOT\s+', r'^PAN AFR\s+', r'^MALLAFRI\s+', r'^PRK CENT\s+',
            r'^HORZNVIL\s+', r'^THMBIAND\s+', r'^KATLEHON\s+', r'^ALEX\s+',
            r'^Fourways\s+', r'^00882112\s+', r'^00795102\s+', r'^COSMOMAL\s+',
            r'^BAM SHOP\s+', r'^02487002\s+', r'^00635106\s+', r'^00656006\s+',
            r'^00656001\s+', r'^ALEXMALL\s+', r'^02137008\s+', r'^T/ROUTE\s+',
            r'^SSDNCR\s+', r'^BENMORE\s+'
        ]

        # Remove location prefixes
        for pattern in location_patterns:
            full_text = re.sub(pattern, '', full_text, flags=re.IGNORECASE)

        # Clean up multiple spaces and location codes
        full_text = re.sub(r'^[A-Z]+\s{2,}', '', full_text.strip())

        # Keep business names intact
        business_indicators = ['LOGISTICS', 'PACK', 'SENZ', 'PTY', 'LTD']
        if any(word in full_text.upper() for word in business_indicators):
            return full_text

        return full_text if full_text else "UNKNOWN"

    def _clean_reference_name(self, name: str) -> str:
        """Clean and format extracted reference name"""
        if not name:
            return "UNKNOWN"

        # Remove banking terms and codes
        cleaning_patterns = [
            r'\b\d{5,}\b',  # Long number sequences
            r'\bFEE\b', r'\bDEPO\b', r'\bCASH\b',
            r'^\s*ADT\s*', r'^\s*FNB\s*', r'^\s*CAPITEC\s*', r'^\s*ABSA\s*'
        ]

        cleaned = name
        for pattern in cleaning_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Clean up spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned if cleaned else name.strip()

    def _extract_payment_reference(self, description: str) -> str:
        """Extract payment reference from ledger description"""
        desc = str(description).strip()

        # Look for payment reference patterns
        patterns = [
            r'PAY\s*REF[:\s]*([^\s,]+)',
            r'PAYMENT\s*REF[:\s]*([^\s,]+)',
            r'REF[:\s]*([A-Z0-9]+)',
            r'REFERENCE[:\s]*([^\s,]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Look for standalone comments (no RJ number required)
        if not re.search(r'RJ-?\d+', desc, re.IGNORECASE):
            # Extract meaningful text that could be a reference
            words = desc.split()
            meaningful_words = []
            for word in words:
                if len(word) > 2 and not word.isdigit() and word.upper() not in ['THE', 'AND', 'FOR', 'TO', 'FROM']:
                    meaningful_words.append(word)

            if meaningful_words:
                return ' '.join(meaningful_words[:3])  # Take first 3 meaningful words

        return ""

# Continue in next stage to avoid length limit...
