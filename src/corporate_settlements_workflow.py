"""
Corporate Settlements Workflow - Professional Settlement Matching System
=========================================================================

This module provides ultra-fast settlement matching for corporate transactions
with advanced batch processing and professional export features.

Key Features:
- Ultra-fast file import (Excel/CSV)
- Configurable column mapping 
- 5-tier batch matching system
- Professional results display
- Export to Excel/CSV with batch separation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import os
import subprocess
import platform
from datetime import datetime
import threading
import time
from typing import Optional, Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import psutil


class CorporateSettlementsWorkflowPage(tk.Frame):
    """Professional Corporate Settlements workflow with ultra-fast matching engine"""
    
    def __init__(self, master, show_types):
        super().__init__(master, bg="#f8f9fc")
        self.master = master
        self.show_types = show_types
        self.pack(fill="both", expand=True)
        
        # Configure window title
        master.title("BARD-RECO - Corporate Settlements Workflow")
        
        # Initialize data variables
        self.settlement_df: Optional[pd.DataFrame] = None
        self.matched_results: Optional[Dict] = None
        self.column_mapping = {
            'foreign_debits': None,
            'foreign_credits': None,
            'reference': None
        }
        
        # Matching parameters
        self.tolerance = 0.5  # Default tolerance
        self.percentage_threshold = 7.0  # 7% threshold
        
        # Performance optimization variables
        self.data_cache = {}
        self.processing_stats = {}
        self.chunk_size = 10000  # Process in chunks for large files
        self.use_multiprocessing = True
        self.max_workers = min(4, psutil.cpu_count())
        
        # UI responsiveness
        self.ui_update_interval = 100  # milliseconds
        self.last_update_time = 0
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to import settlement file")
        
        # Create the UI
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
    
    def create_header(self):
        """Create professional header with navigation and title"""
        header_frame = tk.Frame(self, bg="#1e40af", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#1e40af")
        header_content.pack(expand=True, fill="both", padx=30, pady=15)
        
        # Back button
        back_btn = tk.Button(header_content, text="← Back to Types", 
                            font=("Segoe UI", 11, "bold"),
                            bg="white", fg="#1e40af", relief="flat", bd=0,
                            padx=20, pady=8, command=self.show_types, cursor="hand2")
        back_btn.pack(side="left")
        
        # Hover effects
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#f1f5f9"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="white"))
        
        # Title section
        title_section = tk.Frame(header_content, bg="#1e40af")
        title_section.pack(expand=True)
        
        title_label = tk.Label(title_section, text="💼 Corporate Settlements Workflow", 
                              font=("Segoe UI", 20, "bold"), fg="white", bg="#1e40af")
        title_label.pack()
        
        subtitle_label = tk.Label(title_section, 
                                 text="Professional Settlement Matching • Ultra-Fast Processing • Advanced Batch Analysis",
                                 font=("Segoe UI", 11), fg="#cbd5e1", bg="#1e40af")
        subtitle_label.pack(pady=(5, 0))
    
    def create_main_content(self):
        """Create main workflow content area"""
        # Main container with padding
        main_container = tk.Frame(self, bg="#f8f9fc")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create workflow steps in a grid layout
        self.create_import_section(main_container)
        self.create_configuration_section(main_container)
        self.create_processing_section(main_container)
        self.create_results_section(main_container)
    
    def create_import_section(self, parent):
        """Create file import section"""
        # Import section frame
        import_frame = tk.LabelFrame(parent, text="📁 Step 1: Import Settlement File", 
                                    font=("Segoe UI", 12, "bold"), 
                                    fg="#1e40af", bg="#ffffff", 
                                    relief="solid", bd=1, padx=20, pady=15)
        import_frame.pack(fill="x", pady=(0, 15))
        
        # Import description
        desc_label = tk.Label(import_frame, 
                             text="Import your corporate settlement file (Excel or CSV format). Optimized for large files with ultra-fast processing.",
                             font=("Segoe UI", 10), fg="#64748b", bg="#ffffff",
                             wraplength=800, justify="left")
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Import controls frame
        import_controls = tk.Frame(import_frame, bg="#ffffff")
        import_controls.pack(fill="x")
        
        # File path display
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("No file selected")
        
        path_frame = tk.Frame(import_controls, bg="#ffffff")
        path_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(path_frame, text="Selected File:", font=("Segoe UI", 10, "bold"), 
                fg="#374151", bg="#ffffff").pack(side="left")
        
        path_label = tk.Label(path_frame, textvariable=self.file_path_var, 
                             font=("Segoe UI", 10), fg="#059669", bg="#ffffff")
        path_label.pack(side="left", padx=(10, 0))
        
        # Import buttons
        button_frame = tk.Frame(import_controls, bg="#ffffff")
        button_frame.pack(fill="x")
        
        # Import button
        import_btn = tk.Button(button_frame, text="📁 Import Settlement File", 
                              font=("Segoe UI", 11, "bold"),
                              bg="#059669", fg="white", relief="flat", bd=0,
                              padx=25, pady=12, command=self.import_settlement_file, 
                              cursor="hand2")
        import_btn.pack(side="left")
        
        # File info display
        self.file_info_var = tk.StringVar()
        info_label = tk.Label(button_frame, textvariable=self.file_info_var, 
                             font=("Segoe UI", 10), fg="#6b7280", bg="#ffffff")
        info_label.pack(side="left", padx=(20, 0))
        
        # Sample data preview button
        preview_btn = tk.Button(button_frame, text="👁️ Preview Data", 
                               font=("Segoe UI", 11, "bold"),
                               bg="#3b82f6", fg="white", relief="flat", bd=0,
                               padx=20, pady=12, command=self.preview_data, 
                               cursor="hand2", state="disabled")
        preview_btn.pack(side="right")
        
        self.preview_btn = preview_btn
    
    def create_configuration_section(self, parent):
        """Create column configuration section"""
        config_frame = tk.LabelFrame(parent, text="⚙️ Step 2: Configure Column Mapping", 
                                    font=("Segoe UI", 12, "bold"), 
                                    fg="#1e40af", bg="#ffffff", 
                                    relief="solid", bd=1, padx=20, pady=15)
        config_frame.pack(fill="x", pady=(0, 15))
        
        # Configuration description
        desc_label = tk.Label(config_frame, 
                             text="Map your file columns to the required fields for settlement matching. Three columns are essential for accurate matching.",
                             font=("Segoe UI", 10), fg="#64748b", bg="#ffffff",
                             wraplength=800, justify="left")
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Column mapping grid
        mapping_grid = tk.Frame(config_frame, bg="#ffffff")
        mapping_grid.pack(fill="x")
        
        # Configure grid weights
        mapping_grid.grid_columnconfigure(1, weight=1)
        
        # Foreign Debits mapping
        tk.Label(mapping_grid, text="Foreign Debits Column:", 
                font=("Segoe UI", 10, "bold"), fg="#374151", bg="#ffffff").grid(
                row=0, column=0, sticky="w", padx=(0, 15), pady=8)
        
        self.fd_combo = ttk.Combobox(mapping_grid, font=("Segoe UI", 10), 
                                    width=25, state="readonly")
        self.fd_combo.grid(row=0, column=1, sticky="w", pady=8)
        
        # Foreign Credits mapping
        tk.Label(mapping_grid, text="Foreign Credits Column:", 
                font=("Segoe UI", 10, "bold"), fg="#374151", bg="#ffffff").grid(
                row=1, column=0, sticky="w", padx=(0, 15), pady=8)
        
        self.fc_combo = ttk.Combobox(mapping_grid, font=("Segoe UI", 10), 
                                    width=25, state="readonly")
        self.fc_combo.grid(row=1, column=1, sticky="w", pady=8)
        
        # Reference mapping
        tk.Label(mapping_grid, text="Reference Column:", 
                font=("Segoe UI", 10, "bold"), fg="#374151", bg="#ffffff").grid(
                row=2, column=0, sticky="w", padx=(0, 15), pady=8)
        
        self.ref_combo = ttk.Combobox(mapping_grid, font=("Segoe UI", 10), 
                                     width=25, state="readonly")
        self.ref_combo.grid(row=2, column=1, sticky="w", pady=8)
        
        # Tolerance settings
        tolerance_frame = tk.Frame(config_frame, bg="#ffffff")
        tolerance_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(tolerance_frame, text="Matching Parameters:", 
                font=("Segoe UI", 11, "bold"), fg="#1e40af", bg="#ffffff").pack(anchor="w")
        
        params_grid = tk.Frame(tolerance_frame, bg="#ffffff")
        params_grid.pack(fill="x", pady=(10, 0))
        
        # Amount tolerance
        tk.Label(params_grid, text="Amount Tolerance (±):", 
                font=("Segoe UI", 10), fg="#374151", bg="#ffffff").grid(
                row=0, column=0, sticky="w", padx=(20, 10), pady=5)
        
        self.tolerance_var = tk.DoubleVar(value=0.5)
        tolerance_spin = tk.Spinbox(params_grid, from_=0.0, to=10.0, increment=0.1,
                                   textvariable=self.tolerance_var, font=("Segoe UI", 10),
                                   width=10)
        tolerance_spin.grid(row=0, column=1, sticky="w", pady=5)
        
        # Percentage threshold
        tk.Label(params_grid, text="Percentage Threshold (%):", 
                font=("Segoe UI", 10), fg="#374151", bg="#ffffff").grid(
                row=0, column=2, sticky="w", padx=(20, 10), pady=5)
        
        self.percentage_var = tk.DoubleVar(value=7.0)
        percentage_spin = tk.Spinbox(params_grid, from_=1.0, to=20.0, increment=0.5,
                                    textvariable=self.percentage_var, font=("Segoe UI", 10),
                                    width=10)
        percentage_spin.grid(row=0, column=3, sticky="w", pady=5)
    
    def create_processing_section(self, parent):
        """Create processing control section"""
        process_frame = tk.LabelFrame(parent, text="⚡ Step 3: Execute Settlement Matching", 
                                     font=("Segoe UI", 12, "bold"), 
                                     fg="#1e40af", bg="#ffffff", 
                                     relief="solid", bd=1, padx=20, pady=15)
        process_frame.pack(fill="x", pady=(0, 15))
        
        # Processing description
        desc_label = tk.Label(process_frame, 
                             text="Start the ultra-fast settlement matching process. Transactions will be automatically categorized into 5 professional batches.",
                             font=("Segoe UI", 10), fg="#64748b", bg="#ffffff",
                             wraplength=800, justify="left")
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Processing controls
        controls_frame = tk.Frame(process_frame, bg="#ffffff")
        controls_frame.pack(fill="x")
        
        # Reconcile button
        self.reconcile_btn = tk.Button(controls_frame, text="⚡ Start Reconciliation", 
                                      font=("Segoe UI", 12, "bold"),
                                      bg="#dc2626", fg="white", relief="flat", bd=0,
                                      padx=30, pady=15, command=self.start_reconciliation, 
                                      cursor="hand2", state="disabled")
        self.reconcile_btn.pack(side="left")
        
        # Progress bar
        progress_frame = tk.Frame(controls_frame, bg="#ffffff")
        progress_frame.pack(side="left", fill="x", expand=True, padx=(20, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=300, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # Progress percentage label
        self.progress_percentage_var = tk.StringVar()
        self.progress_percentage_var.set("0%")
        progress_label = tk.Label(progress_frame, textvariable=self.progress_percentage_var,
                                 font=("Segoe UI", 9, "bold"), fg="#1e40af", bg="#ffffff")
        progress_label.pack()
        
        # Processing stats
        stats_frame = tk.Frame(controls_frame, bg="#ffffff")
        stats_frame.pack(side="right")
        
        self.processing_stats_label = tk.Label(stats_frame, text="Ready", 
                                              font=("Segoe UI", 10, "bold"), 
                                              fg="#059669", bg="#ffffff")
        self.processing_stats_label.pack()
    
    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = tk.LabelFrame(parent, text="📊 Step 4: Reconciliation Results", 
                                     font=("Segoe UI", 12, "bold"), 
                                     fg="#1e40af", bg="#ffffff", 
                                     relief="solid", bd=1, padx=20, pady=15)
        results_frame.pack(fill="both", expand=True)
        
        # Results description
        desc_label = tk.Label(results_frame, 
                             text="View your settlement matching results organized in professional batches with export capabilities.",
                             font=("Segoe UI", 10), fg="#64748b", bg="#ffffff",
                             wraplength=800, justify="left")
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Results controls
        results_controls = tk.Frame(results_frame, bg="#ffffff")
        results_controls.pack(fill="x", pady=(0, 15))
        
        # Export buttons
        export_excel_btn = tk.Button(results_controls, text="📊 Export to Excel", 
                                    font=("Segoe UI", 11, "bold"),
                                    bg="#059669", fg="white", relief="flat", bd=0,
                                    padx=20, pady=10, command=self.export_to_excel, 
                                    cursor="hand2", state="disabled")
        export_excel_btn.pack(side="left", padx=(0, 10))
        
        export_csv_btn = tk.Button(results_controls, text="📄 Export to CSV", 
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#3b82f6", fg="white", relief="flat", bd=0,
                                  padx=20, pady=10, command=self.export_to_csv, 
                                  cursor="hand2", state="disabled")
        export_csv_btn.pack(side="left", padx=(0, 10))
        
        # Collaborative Dashboard POST Button
        post_dashboard_btn = tk.Button(results_controls, text="🚀 POST to Dashboard", 
                                     font=("Segoe UI", 11, "bold"),
                                     bg="#10b981", fg="white", relief="flat", bd=0,
                                     padx=20, pady=10, command=self.post_to_collaborative_dashboard, 
                                     cursor="hand2", state="disabled")
        post_dashboard_btn.pack(side="left", padx=(0, 10))
        
        # View details button
        view_btn = tk.Button(results_controls, text="👁️ View Detailed Results", 
                            font=("Segoe UI", 11, "bold"),
                            bg="#8b5cf6", fg="white", relief="flat", bd=0,
                            padx=20, pady=10, command=self.view_detailed_results, 
                            cursor="hand2", state="disabled")
        view_btn.pack(side="right")
        
        self.export_excel_btn = export_excel_btn
        self.export_csv_btn = export_csv_btn
        self.post_dashboard_btn = post_dashboard_btn
        self.view_btn = view_btn
        
        # Results summary area
        self.results_summary = tk.Frame(results_frame, bg="#f8fafc", relief="solid", bd=1)
        self.results_summary.pack(fill="both", expand=True)
        
        # Initial results placeholder
        placeholder_label = tk.Label(self.results_summary, 
                                    text="🎯 Results will appear here after reconciliation\n\n"
                                         "Professional 5-Tier Batch System:\n\n"
                                         "• Batch 1: Perfect Matches (FD = FC exactly + Same Reference)\n"
                                         "• Batch 2: FD > FC (within 7% threshold)\n" 
                                         "• Batch 3: FC > FD (within 7% threshold)\n"
                                         "• Batch 4: Same Reference (amount difference >7%)\n"
                                         "• Batch 5: Unmatched or single transactions",
                                    font=("Segoe UI", 11), fg="#6b7280", bg="#f8fafc",
                                    justify="left")
        placeholder_label.pack(expand=True)
    
    def create_status_bar(self):
        """Create status bar with progress information"""
        status_frame = tk.Frame(self, bg="#e5e7eb", height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=("Segoe UI", 9), bg="#e5e7eb", fg="#374151",
                               anchor="w", padx=15)
        status_label.pack(side="left", fill="x", expand=True, pady=5)
        
        # Processing time display
        self.time_var = tk.StringVar()
        time_label = tk.Label(status_frame, textvariable=self.time_var,
                             font=("Segoe UI", 9), bg="#e5e7eb", fg="#6b7280",
                             anchor="e", padx=15)
        time_label.pack(side="right", pady=5)
    
    def import_settlement_file(self):
        """Import settlement file with proper threading for UI responsiveness"""
        try:
            # File dialog must be on main thread
            file_path = filedialog.askopenfilename(
                title="Select Settlement File",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                self.status_var.set("Import cancelled.")
                return
            
            # Check cache first (quick operation)
            self.status_var.set("Checking cache...")
            self.progress_var.set(5)
            self.master.update()
            
            file_stat = os.stat(file_path)
            cache_key = f"{file_path}_{file_stat.st_mtime}_{file_stat.st_size}"
            
            if cache_key in self.data_cache:
                self.settlement_df = self.data_cache[cache_key]
                self._post_import_setup(file_path, 0.001, self.settlement_df)
                return
            
            # Heavy import work in background thread
            def do_heavy_import():
                try:
                    self.master.after(0, lambda: self.status_var.set("Importing file..."))
                    self.master.after(0, lambda: self.progress_var.set(10))
                    self.master.after(0, lambda: self.progress_percentage_var.set("10%"))
                    start_time = time.time()
                    
                    # Read file (heavy operation)
                    if file_path.lower().endswith(('.xlsx', '.xls')):
                        self.master.after(0, lambda: self.status_var.set("Reading Excel file... This may take a moment..."))
                        self.master.after(0, lambda: self.progress_var.set(30))
                        self.master.after(0, lambda: self.progress_percentage_var.set("30%"))
                        try:
                            # Try multiple approaches for Excel reading
                            df = pd.read_excel(
                                file_path, 
                                engine='openpyxl',
                                dtype=str,
                                na_filter=False
                            )
                        except Exception as excel_error:
                            # Try with different sheet or engine
                            try:
                                df = pd.read_excel(
                                    file_path, 
                                    engine='openpyxl',
                                    sheet_name=0,  # First sheet explicitly
                                    dtype=str,
                                    na_filter=False
                                )
                            except Exception:
                                # Final fallback
                                try:
                                    df = pd.read_excel(file_path, engine='openpyxl')
                                except Exception:
                                    raise Exception(f"Cannot read Excel file. Original error: {str(excel_error)}")
                    else:
                        self.master.after(0, lambda: self.status_var.set("Reading CSV file... This may take a moment..."))
                        self.master.after(0, lambda: self.progress_var.set(30))
                        self.master.after(0, lambda: self.progress_percentage_var.set("30%"))
                        try:
                            df = pd.read_csv(
                                file_path, 
                                low_memory=False,
                                dtype=str,
                                na_filter=False,
                                encoding='utf-8-sig'
                            )
                        except Exception as csv_error:
                            # Try different encodings
                            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                                try:
                                    df = pd.read_csv(file_path, encoding=encoding)
                                    break
                                except Exception:
                                    continue
                            else:
                                raise Exception(f"Cannot read CSV file. Original error: {str(csv_error)}")
                    
                    self.master.after(0, lambda: self.status_var.set("Processing data structure..."))
                    self.master.after(0, lambda: self.progress_var.set(60))
                    self.master.after(0, lambda: self.progress_percentage_var.set("60%"))
                    # Optimize data structure
                    df = self._optimize_dataframe(df)
                    
                    self.master.after(0, lambda: self.status_var.set("Optimizing memory usage..."))
                    self.master.after(0, lambda: self.progress_var.set(80))
                    self.master.after(0, lambda: self.progress_percentage_var.set("80%"))
                    
                    # Cache the result
                    self.data_cache[cache_key] = df.copy()
                    load_time = time.time() - start_time
                    
                    self.master.after(0, lambda: self.status_var.set("Finalizing import..."))
                    self.master.after(0, lambda: self.progress_var.set(95))
                    self.master.after(0, lambda: self.progress_percentage_var.set("95%"))
                    
                    # Complete on main thread
                    self.master.after(0, lambda: self._post_import_setup(file_path, load_time, df))
                    
                except Exception as e:
                    error_msg = str(e)
                    self.master.after(0, lambda: [
                        self.progress_var.set(0),
                        self.status_var.set("Import failed"),
                        messagebox.showerror("Import Error", f"Failed to import file:\n{error_msg}\n\nFile: {file_path}")
                    ])
            
            # Start background import
            threading.Thread(target=do_heavy_import, daemon=True).start()
            
        except Exception as e:
            self.progress_var.set(0)
            self.status_var.set("Import failed")
            messagebox.showerror("Import Error", f"Failed to start import:\n{str(e)}")

    def _post_import_setup(self, file_path, load_time, df=None):
        """Complete the import setup process (UI thread)"""
        if df is not None:
            self.settlement_df = df
        # Update UI with file information
        self.file_path_var.set(os.path.basename(file_path))
        # Get processing stats
        memory_reduction = self.processing_stats.get('memory_reduction', 0)
        memory_info = f"Memory optimized: {memory_reduction:.1f}% reduction"
        self.file_info_var.set(f"✅ {len(self.settlement_df):,} rows • {len(self.settlement_df.columns)} columns • {load_time:.3f}s • {memory_info}")
        # Populate column dropdowns with intelligent defaults
        columns = list(self.settlement_df.columns)
        self.fd_combo['values'] = columns
        self.fc_combo['values'] = columns  
        self.ref_combo['values'] = columns
        self._auto_detect_columns(columns)
        self.preview_btn.config(state="normal")
        self.reconcile_btn.config(state="normal")
        self.status_var.set(f"✅ File imported - {len(self.settlement_df):,} transactions ready • Auto-detection applied")
        self.progress_var.set(100)
        self.progress_percentage_var.set("100%")
        
        # Reset progress after 2 seconds
        self.master.after(2000, lambda: [
            self.progress_var.set(0),
            self.progress_percentage_var.set("0%")
        ])
    
    def _optimize_dataframe(self, df):
        """Optimize DataFrame memory usage"""
        try:
            # Processing stats should already exist from constructor
            
            # Strip whitespaces from string columns
            string_cols = df.select_dtypes(include=['object']).columns
            for col in string_cols:
                df[col] = df[col].astype(str).str.strip()
            
            # Optimize memory usage
            try:
                original_memory = df.memory_usage(deep=True).sum()
            except Exception:
                original_memory = 0
            
            # Convert to appropriate dtypes where possible
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric if possible
                    try:
                        numeric_test = pd.to_numeric(df[col], errors='coerce')
                        if not numeric_test.isna().all():
                            non_null_numeric = numeric_test.dropna()
                            if len(non_null_numeric) > 0:
                                # Check if can be integer
                                if (non_null_numeric % 1 == 0).all():
                                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                                else:
                                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
                    except Exception:
                        # If conversion fails, keep as string
                        continue
            
            try:
                optimized_memory = df.memory_usage(deep=True).sum()
                memory_reduction = (original_memory - optimized_memory) / original_memory * 100 if original_memory > 0 else 0
            except Exception:
                memory_reduction = 0
            
            self.processing_stats['memory_reduction'] = memory_reduction
            return df
            
        except Exception as e:
            # If optimization fails, return original dataframe
            print(f"Warning: DataFrame optimization failed: {e}")
            self.processing_stats['memory_reduction'] = 0
            return df
    

    
    def _auto_detect_columns(self, columns):
        """Automatically detect common column patterns"""
        # Common patterns for different column types
        fd_patterns = ['foreign_debit', 'fd', 'debit', 'dr', 'debits', 'foreign debits']
        fc_patterns = ['foreign_credit', 'fc', 'credit', 'cr', 'credits', 'foreign credits']
        ref_patterns = ['reference', 'ref', 'transaction_ref', 'trx_ref', 'transaction reference']
        
        # Auto-select columns based on patterns
        for col in columns:
            col_lower = col.lower().replace(' ', '_').replace('-', '_')
            
            if any(pattern in col_lower for pattern in fd_patterns):
                self.fd_combo.set(col)
            elif any(pattern in col_lower for pattern in fc_patterns):
                self.fc_combo.set(col)
            elif any(pattern in col_lower for pattern in ref_patterns):
                self.ref_combo.set(col)
    
    def preview_data(self):
        """Show data preview window"""
        if self.settlement_df is None:
            messagebox.showwarning("No Data", "Please import a settlement file first.")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.master)
        preview_window.title("Settlement Data Preview")
        preview_window.geometry("1000x600")
        preview_window.configure(bg="#ffffff")
        
        # Preview header
        header_frame = tk.Frame(preview_window, bg="#1e40af", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text=f"📊 Data Preview - {len(self.settlement_df):,} rows × {len(self.settlement_df.columns)} columns",
                               font=("Segoe UI", 14, "bold"), fg="white", bg="#1e40af")
        header_label.pack(expand=True)
        
        # Create treeview for data display
        tree_frame = tk.Frame(preview_window, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview with scrollbars
        columns = list(self.settlement_df.columns)
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='w')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Populate with sample data (first 100 rows for performance)
        sample_data = self.settlement_df.head(100)
        for index, row in sample_data.iterrows():
            values = [str(row[col])[:50] for col in columns]  # Truncate long values
            tree.insert('', 'end', values=values)
    
    def start_reconciliation(self):
        """Start the ultra-fast reconciliation process"""
        try:
            # Validate inputs
            if self.settlement_df is None:
                messagebox.showwarning("No Data", "Please import a settlement file first.")
                return
            
            # Get column mappings
            fd_col = self.fd_combo.get()
            fc_col = self.fc_combo.get()
            ref_col = self.ref_combo.get()
            
            if not all([fd_col, fc_col, ref_col]):
                messagebox.showwarning("Missing Configuration", 
                                     "Please select all required columns:\n"
                                     "• Foreign Debits\n• Foreign Credits\n• Reference")
                return
            
            # Update parameters
            self.tolerance = self.tolerance_var.get()
            self.percentage_threshold = self.percentage_var.get()
            
            # Store column mapping
            self.column_mapping = {
                'foreign_debits': fd_col,
                'foreign_credits': fc_col,
                'reference': ref_col
            }
            
            # Disable reconcile button during processing
            self.reconcile_btn.config(state="disabled", text="Processing...")
            
            # Start reconciliation in separate thread for UI responsiveness
            threading.Thread(target=self._execute_reconciliation, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Reconciliation Error", f"Failed to start reconciliation:\n{str(e)}")
            self.reconcile_btn.config(state="normal", text="⚡ Start Reconciliation")
    
    def _execute_reconciliation(self):
        """Execute the ultra-fast matching algorithm with enhanced performance"""
        try:
            start_time = time.time()
            
            # Update status with non-blocking UI updates
            self._update_ui_safe("Executing ultra-fast settlement matching...", 10)
            
            # Get working columns
            fd_col = self.column_mapping['foreign_debits']
            fc_col = self.column_mapping['foreign_credits'] 
            ref_col = self.column_mapping['reference']
            
            # Create working dataframe with optimized processing
            self._update_ui_safe("Preparing data for matching...", 20)
            
            df = self.settlement_df.copy()
            
            # Optimized numeric conversion with vectorized operations
            self._update_ui_safe("Converting numeric columns...", 25)
            df[fd_col] = pd.to_numeric(df[fd_col], errors='coerce').fillna(0).astype('float32')
            df[fc_col] = pd.to_numeric(df[fc_col], errors='coerce').fillna(0).astype('float32')
            
            # Optimized string processing
            df[ref_col] = df[ref_col].astype(str).str.strip()
            
            self._update_ui_safe("Optimizing data structure...", 30)
            
            # Initialize result batches
            batches = {
                'batch_1': [],  # Perfect matches: FD = FC exactly + Same Reference
                'batch_2': [],  # FD > FC within tolerance/7%
                'batch_3': [],  # FC > FD within tolerance/7%
                'batch_4': [],  # Same ref, amount differences >7%
                'batch_5': []   # Unmatched or different references
            }
            
            # Group by reference with optimized processing
            self._update_ui_safe("Grouping transactions by reference...", 40)
            ref_groups = df.groupby(ref_col, sort=False)  # Don't sort for speed
            total_groups = len(ref_groups)
            
            # Process in chunks for better performance and UI responsiveness
            if total_groups > self.chunk_size and self.use_multiprocessing:
                self._process_groups_parallel(ref_groups, batches, fd_col, fc_col, total_groups)
            else:
                self._process_groups_sequential(ref_groups, batches, fd_col, fc_col, total_groups)
            
            # Finalize results
            self._update_ui_safe("Finalizing results...", 90)
            
            # Store results
            self.matched_results = batches
            
            # Calculate statistics
            total_transactions = len(df)
            batch_counts = {k: len(v) for k, v in batches.items()}
            
            processing_time = time.time() - start_time
            
            # Store performance stats
            self.processing_stats.update({
                'processing_time': processing_time,
                'total_transactions': total_transactions,
                'transactions_per_second': total_transactions / processing_time if processing_time > 0 else 0
            })
            
            # Update UI with final results
            self._finalize_reconciliation_ui(processing_time, total_transactions, batch_counts)
            
            # Force garbage collection for memory optimization
            gc.collect()
            
        except Exception as e:
            self._handle_reconciliation_error(e)
    
    def _update_ui_safe(self, message, progress):
        """Thread-safe UI update with rate limiting"""
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_update_time >= self.ui_update_interval:
            self.master.after(0, lambda: self._do_ui_update(message, progress))
            self.last_update_time = current_time
    
    def _do_ui_update(self, message, progress):
        """Actual UI update on main thread"""
        try:
            self.status_var.set(message)
            self.progress_var.set(progress)
            self.progress_percentage_var.set(f"{progress:.0f}%")
            self.master.update_idletasks()
        except:
            pass  # Ignore UI update errors
    
    def _process_groups_parallel(self, ref_groups, batches, fd_col, fc_col, total_groups):
        """Process reference groups in parallel for large datasets"""
        self._update_ui_safe("Processing matches (parallel mode)...", 50)
        
        # Convert groups to list for parallel processing
        group_list = [(ref, group) for ref, group in ref_groups]
        
        # Process in chunks
        chunk_size = max(100, len(group_list) // self.max_workers)
        chunks = [group_list[i:i + chunk_size] for i in range(0, len(group_list), chunk_size)]
        
        processed = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_chunk = {
                executor.submit(self._process_chunk, chunk, fd_col, fc_col): chunk 
                for chunk in chunks
            }
            
            for future in as_completed(future_to_chunk):
                try:
                    chunk_results = future.result()
                    
                    # Merge results
                    for batch_key, transactions in chunk_results.items():
                        batches[batch_key].extend(transactions)
                    
                    processed += len(future_to_chunk[future])
                    progress = 50 + (processed / len(group_list)) * 35
                    self._update_ui_safe(f"Processing matches... {processed:,}/{len(group_list):,}", progress)
                    
                except Exception as e:
                    print(f"Chunk processing error: {e}")
    
    def _process_groups_sequential(self, ref_groups, batches, fd_col, fc_col, total_groups):
        """Process reference groups sequentially"""
        self._update_ui_safe("Processing settlement matches...", 50)
        
        processed = 0
        for ref, group in ref_groups:
            processed += 1
            
            # Update progress with rate limiting
            if processed % max(1, total_groups // 50) == 0:
                progress = 50 + (processed / total_groups) * 35
                self._update_ui_safe(f"Processing matches... {processed:,}/{total_groups:,}", progress)
            
            if len(group) == 1:
                # Single transaction - goes to batch 5 (unmatched)
                batches['batch_5'].extend(group.to_dict('records'))
            else:
                # Multiple transactions with same reference
                self._process_reference_group(group, batches, fd_col, fc_col)
    
    def _process_chunk(self, chunk, fd_col, fc_col):
        """Process a chunk of reference groups"""
        chunk_batches = {
            'batch_1': [],
            'batch_2': [],
            'batch_3': [],
            'batch_4': [],
            'batch_5': []
        }
        
        for ref, group in chunk:
            if len(group) == 1:
                chunk_batches['batch_5'].extend(group.to_dict('records'))
            else:
                self._process_reference_group(group, chunk_batches, fd_col, fc_col)
        
        return chunk_batches
    
    def _finalize_reconciliation_ui(self, processing_time, total_transactions, batch_counts):
        """Finalize the reconciliation UI updates"""
        # Update progress and status
        self.progress_var.set(100)
        self.progress_percentage_var.set("100%")
        tps = self.processing_stats.get('transactions_per_second', 0)
        self.status_var.set(f"✅ Reconciliation completed in {processing_time:.2f}s - {total_transactions:,} transactions ({tps:,.0f} TPS)")
        self.time_var.set(f"⚡ Ultra-fast processing: {processing_time:.2f}s")
        
        # Enable export buttons
        self.export_excel_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
        self.post_dashboard_btn.config(state="normal")
        self.view_btn.config(state="normal")
        self.reconcile_btn.config(state="normal", text="⚡ Start Reconciliation")
        
        # Update results display
        self._update_results_display(batch_counts, total_transactions)
        
        # Show success message confirming results are ready for export
        success_msg = (
            f"🎉 Reconciliation Completed Successfully!\n\n"
            f"📊 Processing Summary:\n"
            f"• Total Transactions: {total_transactions:,}\n"
            f"• Processing Time: {processing_time:.2f} seconds\n"
            f"• Speed: {tps:,.0f} transactions per second\n\n"
            f"📁 Batch Results:\n"
            f"• Batch 1 (Perfect Match: FD=FC + Same Ref): {batch_counts['batch_1']:,}\n"
            f"• Batch 2 (FD > FC, within 7%): {batch_counts['batch_2']:,}\n"
            f"• Batch 3 (FC > FD, within 7%): {batch_counts['batch_3']:,}\n"
            f"• Batch 4 (Same Ref, over 7% difference): {batch_counts['batch_4']:,}\n"
            f"• Batch 5 (Unmatched/Single transactions): {batch_counts['batch_5']:,}\n\n"
            f"✅ Your results are now ready for export!\n"
            f"Use the Export buttons to save your reconciliation results."
        )
        messagebox.showinfo("Reconciliation Complete", success_msg)
    
    def _handle_reconciliation_error(self, error):
        """Handle reconciliation errors gracefully"""
        self.progress_var.set(0)
        self.reconcile_btn.config(state="normal", text="⚡ Start Reconciliation")
        error_msg = f"Reconciliation failed:\n{str(error)}"
        self.master.after(0, lambda: messagebox.showerror("Reconciliation Error", error_msg))
        self.status_var.set("❌ Reconciliation failed")
    
    def _process_reference_group(self, group, batches, fd_col, fc_col):
        """Process a group of transactions with the same reference - Professional Logic"""
        # Convert group to list for easier processing
        transactions = group.to_dict('records')
        
        # BATCH 1: PERFECT MATCHES - Same amounts AND same reference (already grouped by reference)
        # Look for pairs/groups where FD = FC exactly
        perfect_matches = []
        remaining_transactions = []
        
        for transaction in transactions:
            fd_amount = transaction[fd_col]
            fc_amount = transaction[fc_col]
            
            # Batch 1 criteria: FD exactly equals FC AND same reference (already guaranteed by grouping)
            if abs(fd_amount - fc_amount) < 0.01:  # Use small epsilon for float comparison
                perfect_matches.append(transaction)
            else:
                remaining_transactions.append(transaction)
        
        # Add perfect matches to Batch 1
        batches['batch_1'].extend(perfect_matches)
        
        # Process remaining transactions with same reference but different FD/FC amounts
        for transaction in remaining_transactions:
            fd_amount = transaction[fd_col]
            fc_amount = transaction[fc_col]
            
            # Calculate difference and percentage (use LARGER amount as denominator for consistency)
            difference = abs(fd_amount - fc_amount)
            larger_amount = max(fd_amount, fc_amount)
            percentage_diff = (difference / larger_amount) * 100 if larger_amount != 0 else 100
            
            # Batch 2: FD > FC within threshold (≤7%)
            if fd_amount > fc_amount:
                if percentage_diff <= self.percentage_threshold or difference <= self.tolerance:
                    transaction['_variance_percent'] = round(percentage_diff, 2)
                    transaction['_variance_amount'] = round(difference, 2)
                    batches['batch_2'].append(transaction)
                else:
                    # Same reference but high difference (>7%)
                    transaction['_variance_percent'] = round(percentage_diff, 2)
                    transaction['_variance_amount'] = round(difference, 2)
                    batches['batch_4'].append(transaction)
            
            # Batch 3: FC > FD within threshold (≤7%)
            elif fc_amount > fd_amount:
                if percentage_diff <= self.percentage_threshold or difference <= self.tolerance:
                    transaction['_variance_percent'] = round(percentage_diff, 2)
                    transaction['_variance_amount'] = round(difference, 2)
                    batches['batch_3'].append(transaction)
                else:
                    # Same reference but high difference (>7%)
                    transaction['_variance_percent'] = round(percentage_diff, 2)
                    transaction['_variance_amount'] = round(difference, 2)
                    batches['batch_4'].append(transaction)
    
    def _update_results_display(self, batch_counts, total_transactions):
        """Update the results display with batch statistics"""
        # Clear existing content
        for widget in self.results_summary.winfo_children():
            widget.destroy()
        
        # Create results summary
        summary_frame = tk.Frame(self.results_summary, bg="#f8fafc")
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(summary_frame, text="🎯 Settlement Matching Results", 
                              font=("Segoe UI", 16, "bold"), fg="#1e40af", bg="#f8fafc")
        title_label.pack(pady=(0, 20))
        
        # Statistics grid
        stats_grid = tk.Frame(summary_frame, bg="#f8fafc")
        stats_grid.pack(fill="x")
        
        # Configure grid
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        batch_info = [
            ("Batch 1", "Perfect: FD=FC + Same Ref", batch_counts['batch_1'], "#059669", "✅"),
            ("Batch 2", "FD > FC (Within 7%)", batch_counts['batch_2'], "#3b82f6", "📈"),
            ("Batch 3", "FC > FD (Within 7%)", batch_counts['batch_3'], "#8b5cf6", "📉"),
            ("Batch 4", "Same Ref (Over 7%)", batch_counts['batch_4'], "#f59e0b", "⚠️"),
            ("Batch 5", "Unmatched/Single", batch_counts['batch_5'], "#dc2626", "❌")
        ]
        
        row = 0
        col = 0
        
        for batch_name, description, count, color, icon in batch_info:
            # Batch card
            card_frame = tk.Frame(stats_grid, bg="white", relief="solid", bd=1)
            card_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=8)
            
            # Card content
            card_content = tk.Frame(card_frame, bg="white")
            card_content.pack(fill="both", expand=True, padx=15, pady=12)
            
            # Icon and title
            header_frame = tk.Frame(card_content, bg="white")
            header_frame.pack(fill="x")
            
            icon_label = tk.Label(header_frame, text=icon, font=("Segoe UI Emoji", 16), 
                                 fg=color, bg="white")
            icon_label.pack(side="left")
            
            batch_label = tk.Label(header_frame, text=batch_name, 
                                  font=("Segoe UI", 12, "bold"), fg=color, bg="white")
            batch_label.pack(side="left", padx=(8, 0))
            
            # Description
            desc_label = tk.Label(card_content, text=description, 
                                 font=("Segoe UI", 9), fg="#6b7280", bg="white")
            desc_label.pack(anchor="w", pady=(2, 8))
            
            # Count
            count_label = tk.Label(card_content, text=f"{count:,} transactions", 
                                  font=("Segoe UI", 11, "bold"), fg="#1f2937", bg="white")
            count_label.pack(anchor="w")
            
            # Percentage
            percentage = (count / total_transactions) * 100 if total_transactions > 0 else 0
            perc_label = tk.Label(card_content, text=f"{percentage:.1f}% of total", 
                                 font=("Segoe UI", 9), fg="#9ca3af", bg="white")
            perc_label.pack(anchor="w")
            
            # Move to next position
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Total summary
        total_frame = tk.Frame(summary_frame, bg="#1e40af", relief="solid", bd=1)
        total_frame.pack(fill="x", pady=(20, 0))
        
        total_content = tk.Frame(total_frame, bg="#1e40af")
        total_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(total_content, text=f"📊 Total Transactions Processed: {total_transactions:,}", 
                font=("Segoe UI", 14, "bold"), fg="white", bg="#1e40af").pack(side="left")
        
        # Processing stats
        matched = batch_counts['batch_1'] + batch_counts['batch_2'] + batch_counts['batch_3']
        match_rate = (matched / total_transactions) * 100 if total_transactions > 0 else 0
        
        tk.Label(total_content, text=f"✅ Match Rate: {match_rate:.1f}%", 
                font=("Segoe UI", 12, "bold"), fg="white", bg="#1e40af").pack(side="right")
    
    def export_to_excel(self):
        """Export results to Excel with batch separation and auto-opening"""
        if not self.matched_results:
            messagebox.showwarning("No Results", "Please run reconciliation first.")
            return
        
        try:
            # Get file path on main thread
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Corporate_Settlements_Export_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                title="Export Settlement Results to Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if not file_path:
                return
            
            # Start export in separate thread with file path
            threading.Thread(target=self._execute_excel_export, args=(file_path,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to start Excel export:\n{str(e)}")
    
    def _execute_excel_export(self, file_path):
        """Execute Excel export in separate thread"""
        try:
            
            # Show progress
            self._update_ui_safe("🚀 Exporting to Excel (optimized)...", 10)
            
            # Ensure we have data to export
            total_transactions = len(self.settlement_df) if self.settlement_df is not None else 0
            if total_transactions == 0:
                self.master.after(0, lambda: messagebox.showwarning("No Data", "No data available to export."))
                return
            
            start_time = time.time()
            
            # Create Excel writer with optimizations
            self._update_ui_safe("Creating Excel file structure...", 20)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # Create summary sheet
                self._update_ui_safe("Creating summary sheet...", 30)
                summary_data = []
                batch_display = {
                    'batch_1': 'Batch 1 - Perfect Matches (FD = FC + Same Ref)',
                    'batch_2': 'Batch 2 - FD > FC (≤7%)',
                    'batch_3': 'Batch 3 - FC > FD (≤7%)',
                    'batch_4': 'Batch 4 - Same Ref (>7%)',
                    'batch_5': 'Batch 5 - Unmatched/Single'
                }
                
                for batch_name, transactions in self.matched_results.items():
                    summary_data.append({
                        'Batch': batch_display.get(batch_name, batch_name),
                        'Transaction Count': len(transactions),
                        'Percentage': f"{(len(transactions) / total_transactions) * 100:.1f}%" if total_transactions > 0 else "0.0%"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Create combined sheet with batch separations
                self._update_ui_safe("Creating combined batches sheet...", 50)
                combined_data = []
                
                batch_names = {
                    'batch_1': 'BATCH 1 - PERFECT MATCHES (FD = FC EXACTLY + SAME REFERENCE)',
                    'batch_2': 'BATCH 2 - FD > FC (WITHIN 7% THRESHOLD)',
                    'batch_3': 'BATCH 3 - FC > FD (WITHIN 7% THRESHOLD)',  
                    'batch_4': 'BATCH 4 - SAME REFERENCE (DIFFERENCE > 7%)',
                    'batch_5': 'BATCH 5 - UNMATCHED OR SINGLE TRANSACTIONS'
                }
                
                # Get column names from original data
                columns = list(self.settlement_df.columns) if self.settlement_df is not None else []
                
                for batch_key, batch_name in batch_names.items():
                    batch_transactions = self.matched_results.get(batch_key, [])
                    
                    if batch_transactions:
                        # Add batch header with 3 empty rows separation
                        if combined_data:  # Add separation if not first batch
                            for _ in range(3):
                                empty_row = {col: "" for col in columns}
                                combined_data.append(empty_row)
                        
                        # Add batch title row
                        title_row = {col: "" for col in columns}
                        if columns:
                            title_row[columns[0]] = f"=== {batch_name} ==="
                        combined_data.append(title_row)
                        
                        # Add empty row
                        empty_row = {col: "" for col in columns}
                        combined_data.append(empty_row)
                        
                        # Add batch transactions efficiently
                        combined_data.extend(batch_transactions)
                
                if combined_data:
                    # Create DataFrame in chunks for large datasets
                    if len(combined_data) > 50000:
                        # Process in chunks to avoid memory issues
                        chunk_size = 10000
                        combined_df = pd.concat([
                            pd.DataFrame(combined_data[i:i + chunk_size]) 
                            for i in range(0, len(combined_data), chunk_size)
                        ], ignore_index=True)
                    else:
                        combined_df = pd.DataFrame(combined_data)
                    
                    combined_df.to_excel(writer, sheet_name='All_Batches', index=False)
                
                # Create individual sheets for each batch
                progress_step = 30 / len(batch_names)
                current_progress = 60
                
                for batch_key, batch_name in batch_names.items():
                    batch_transactions = self.matched_results.get(batch_key, [])
                    if batch_transactions:
                        self._update_ui_safe(f"Creating {batch_name} sheet...", current_progress)
                        try:
                            batch_df = pd.DataFrame(batch_transactions)
                            if not batch_df.empty:
                                sheet_name = f"Batch_{batch_key[-1]}"
                                batch_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        except Exception as e:
                            print(f"Warning: Could not create sheet for {batch_key}: {e}")
                    
                    current_progress += progress_step
            
            export_time = time.time() - start_time
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            self._update_ui_safe(f"✅ Excel export completed ({export_time:.1f}s, {file_size:.1f}MB)", 100)
            
            # Auto-open the file
            success_msg = (f"Settlement results exported successfully!\n\n"
                         f"File: {os.path.basename(file_path)}\n"
                         f"Location: {file_path}\n"
                         f"Size: {file_size:.1f}MB\n"
                         f"Export time: {export_time:.1f}s\n"
                         f"Sheets: Summary + All Batches + Individual Batches")
            
            def show_success_and_open():
                if messagebox.askyesno("Export Complete", 
                                     success_msg + "\n\nWould you like to open the file now?"):
                    self._open_file(file_path)
            
            self.master.after(0, show_success_and_open)
            
        except Exception as e:
            error_msg = f"Failed to export to Excel:\n{str(e)}"
            self.master.after(0, lambda: messagebox.showerror("Export Error", error_msg))
            self._update_ui_safe("❌ Excel export failed", 0)
    
    def _get_export_file_path(self, default_filename, export_type):
        """Get export file path from user"""
        if export_type == "excel":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            title = "Export Settlement Results to Excel"
        else:
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            title = "Export Settlement Results to CSV"
        
        file_path = filedialog.asksaveasfilename(
            title=title,
            defaultextension=".xlsx" if export_type == "excel" else ".csv",
            filetypes=filetypes,
            initialfile=default_filename
        )
        
        self._export_file_path = file_path
    
    def _open_file(self, file_path):
        """Open file with default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            messagebox.showwarning("Cannot Open File", 
                                 f"File exported successfully but cannot open automatically:\n{str(e)}\n\n"
                                 f"Please open manually: {file_path}")
    
    def export_to_csv(self):
        """Export results to CSV files with auto-opening"""
        if not self.matched_results:
            messagebox.showwarning("No Results", "Please run reconciliation first.")
            return
        
        try:
            # Get folder path on main thread
            folder_path = filedialog.askdirectory(title="Select Folder for CSV Export")
            
            if not folder_path:
                return
            
            # Start export in separate thread with folder path
            threading.Thread(target=self._execute_csv_export, args=(folder_path,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to start CSV export:\n{str(e)}")
    
    def _execute_csv_export(self, folder_path):
        """Execute CSV export in separate thread"""
        try:
            
            self._update_ui_safe("🚀 Exporting to CSV files (optimized)...", 10)
            
            start_time = time.time()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export each batch to separate CSV with progress tracking
            batch_names = {
                'batch_1': 'Perfect_Matches',
                'batch_2': 'FD_Greater_FC',
                'batch_3': 'FC_Greater_FD',
                'batch_4': 'Same_Ref_High_Diff',
                'batch_5': 'Unmatched'
            }
            
            exported_files = []
            total_batches = len([k for k in batch_names.keys() if self.matched_results.get(k)])
            current_batch = 0
            
            for batch_key, batch_name in batch_names.items():
                batch_transactions = self.matched_results.get(batch_key, [])
                if batch_transactions:
                    current_batch += 1
                    progress = 20 + (current_batch / total_batches) * 60
                    self._update_ui_safe(f"Exporting {batch_name.replace('_', ' ')}...", progress)
                    
                    try:
                        batch_df = pd.DataFrame(batch_transactions)
                        if not batch_df.empty:
                            filename = f"Corporate_Settlements_{batch_name}_{timestamp}.csv"
                            file_path = os.path.join(folder_path, filename)
                            
                            # Use optimized CSV writing
                            batch_df.to_csv(file_path, index=False, encoding='utf-8-sig', 
                                           float_format='%.2f', date_format='%Y-%m-%d')
                            exported_files.append((filename, file_path))
                    except Exception as e:
                        print(f"Warning: Could not export batch {batch_key}: {e}")
                        continue
            
            # Export summary
            self._update_ui_safe("Creating summary file...", 85)
            summary_data = []
            total_transactions = len(self.settlement_df) if self.settlement_df is not None else 0
            
            for batch_key, batch_name in batch_names.items():
                transactions = self.matched_results.get(batch_key, [])
                summary_data.append({
                    'Batch': batch_name.replace('_', ' '),
                    'Transaction_Count': len(transactions),
                    'Percentage': f"{(len(transactions) / total_transactions) * 100:.1f}%" if total_transactions > 0 else "0.0%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_file = f"Corporate_Settlements_Summary_{timestamp}.csv"
            summary_path = os.path.join(folder_path, summary_file)
            summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
            exported_files.append((summary_file, summary_path))
            
            export_time = time.time() - start_time
            total_size = sum(os.path.getsize(path) for _, path in exported_files) / (1024 * 1024)  # MB
            
            self._update_ui_safe(f"✅ CSV export completed ({export_time:.1f}s, {total_size:.1f}MB)", 100)
            
            # Show success message and offer to open folder
            success_msg = (f"Settlement results exported to CSV files!\n\n"
                         f"Folder: {folder_path}\n"
                         f"Files: {len(exported_files)} CSV files created\n"
                         f"Total size: {total_size:.1f}MB\n"
                         f"Export time: {export_time:.1f}s")
            
            def show_success_and_open():
                if messagebox.askyesno("Export Complete", 
                                     success_msg + "\n\nWould you like to open the export folder?"):
                    self._open_file(folder_path)
            
            self.master.after(0, show_success_and_open)
            
        except Exception as e:
            error_msg = f"Failed to export to CSV:\n{str(e)}"
            self.master.after(0, lambda: messagebox.showerror("Export Error", error_msg))
            self._update_ui_safe("❌ CSV export failed", 0)
    
    def _get_export_folder(self):
        """Get export folder from user"""
        folder_path = filedialog.askdirectory(title="Select Folder for CSV Export")
        self._export_folder_path = folder_path
    
    def view_detailed_results(self):
        """Open detailed results viewer window"""
        if not self.matched_results:
            messagebox.showwarning("No Results", "Please run reconciliation first.")
            return
        
        # Create results viewer window
        results_window = tk.Toplevel(self.master)
        results_window.title("Corporate Settlements - Detailed Results")
        results_window.geometry("1400x800")
        results_window.configure(bg="#ffffff")
        results_window.state('zoomed')  # Maximize window
        
        # Results viewer header
        header_frame = tk.Frame(results_window, bg="#1e40af", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#1e40af")
        header_content.pack(expand=True, fill="both", padx=30, pady=20)
        
        title_label = tk.Label(header_content, text="📊 Corporate Settlements - Detailed Results Viewer", 
                              font=("Segoe UI", 18, "bold"), fg="white", bg="#1e40af")
        title_label.pack(side="left")
        
        close_btn = tk.Button(header_content, text="✖ Close", 
                             font=("Segoe UI", 12, "bold"),
                             bg="#dc2626", fg="white", relief="flat", bd=0,
                             padx=20, pady=8, command=results_window.destroy, cursor="hand2")
        close_btn.pack(side="right")
        
        # Create notebook for batch tabs
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        batch_info = [
            ("batch_1", "Batch 1 - Perfect Matches", "#059669"),
            ("batch_2", "Batch 2 - FD > FC (≤7%)", "#3b82f6"),
            ("batch_3", "Batch 3 - FC > FD (≤7%)", "#8b5cf6"),
            ("batch_4", "Batch 4 - Same Ref (>7%)", "#f59e0b"),
            ("batch_5", "Batch 5 - Unmatched", "#dc2626")
        ]
        
        for batch_key, batch_name, color in batch_info:
            batch_transactions = self.matched_results[batch_key]
            
            # Create tab frame
            tab_frame = tk.Frame(notebook, bg="#ffffff")
            notebook.add(tab_frame, text=f"{batch_name} ({len(batch_transactions)})")
            
            if batch_transactions:
                # Create treeview for batch data
                self._create_batch_treeview(tab_frame, batch_transactions, batch_name, color)
            else:
                # Empty batch message
                empty_label = tk.Label(tab_frame, text=f"No transactions in {batch_name}", 
                                      font=("Segoe UI", 14), fg="#6b7280", bg="#ffffff")
                empty_label.pack(expand=True)
    
    def _create_batch_treeview(self, parent, transactions, batch_name, color):
        """Create treeview for displaying batch transactions"""
        # Batch header
        header_frame = tk.Frame(parent, bg=color, height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text=f"{batch_name} - {len(transactions):,} Transactions", 
                               font=("Segoe UI", 12, "bold"), fg="white", bg=color)
        header_label.pack(expand=True)
        
        # Treeview frame
        tree_frame = tk.Frame(parent, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get columns from first transaction
        if transactions:
            columns = list(transactions[0].keys())
            
            # Create treeview
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=25)
            
            # Configure columns
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor='w')
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack elements
            tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Populate with transaction data
            for transaction in transactions:
                values = [str(transaction.get(col, '')) for col in columns]
                tree.insert('', 'end', values=values)
            
            # Status bar for batch
            status_frame = tk.Frame(parent, bg="#f1f5f9", height=30)
            status_frame.pack(fill="x")
            status_frame.pack_propagate(False)
            
            status_label = tk.Label(status_frame, text=f"📊 Showing {len(transactions):,} transactions in {batch_name}", 
                                   font=("Segoe UI", 10), fg="#374151", bg="#f1f5f9")
            status_label.pack(side="left", padx=10, pady=5)
    
    def show_performance_monitor(self):
        """Show performance statistics and system information"""
        monitor_window = tk.Toplevel(self.master)
        monitor_window.title("Performance Monitor - Corporate Settlements")
        monitor_window.geometry("600x500")
        monitor_window.configure(bg="#f8f9fc")
        
        # Header
        header_frame = tk.Frame(monitor_window, bg="#1e40af", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📊 Performance Monitor", 
                              font=("Segoe UI", 16, "bold"), bg="#1e40af", fg="white")
        title_label.pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(monitor_window, bg="#f8f9fc")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # System information
        system_frame = tk.LabelFrame(main_frame, text="System Information", 
                                    font=("Segoe UI", 12, "bold"), bg="#f8f9fc", fg="#1e40af")
        system_frame.pack(fill="x", pady=(0, 15))
        
        system_info = f"""CPU Cores: {psutil.cpu_count()} physical, {psutil.cpu_count(logical=True)} logical
CPU Usage: {psutil.cpu_percent(interval=1):.1f}%
Memory: {psutil.virtual_memory().used / (1024**3):.1f}GB / {psutil.virtual_memory().total / (1024**3):.1f}GB ({psutil.virtual_memory().percent:.1f}% used)
Available Memory: {psutil.virtual_memory().available / (1024**3):.1f}GB"""
        
        system_label = tk.Label(system_frame, text=system_info, font=("Consolas", 10), 
                               bg="#f8f9fc", fg="#374151", justify="left")
        system_label.pack(padx=15, pady=10, anchor="w")
        
        # Processing statistics
        if self.processing_stats:
            stats_frame = tk.LabelFrame(main_frame, text="Last Reconciliation Statistics", 
                                       font=("Segoe UI", 12, "bold"), bg="#f8f9fc", fg="#1e40af")
            stats_frame.pack(fill="x", pady=(0, 15))
            
            processing_time = self.processing_stats.get('processing_time', 0)
            total_transactions = self.processing_stats.get('total_transactions', 0)
            tps = self.processing_stats.get('transactions_per_second', 0)
            memory_reduction = self.processing_stats.get('memory_reduction', 0)
            
            stats_info = f"""Processing Time: {processing_time:.3f} seconds
Total Transactions: {total_transactions:,}
Throughput: {tps:,.0f} transactions per second
Memory Optimization: {memory_reduction:.1f}% reduction
Parallel Processing: {'Enabled' if self.use_multiprocessing else 'Disabled'}
Max Workers: {self.max_workers}
Chunk Size: {self.chunk_size:,}"""
            
            stats_label = tk.Label(stats_frame, text=stats_info, font=("Consolas", 10), 
                                  bg="#f8f9fc", fg="#374151", justify="left")
            stats_label.pack(padx=15, pady=10, anchor="w")
        
        # Cache information
        cache_frame = tk.LabelFrame(main_frame, text="Data Cache", 
                                   font=("Segoe UI", 12, "bold"), bg="#f8f9fc", fg="#1e40af")
        cache_frame.pack(fill="x", pady=(0, 15))
        
        cache_count = len(self.data_cache)
        cache_info = f"Cached Files: {cache_count}\nCache Hit Rate: {'N/A' if cache_count == 0 else 'Available for repeated imports'}"
        
        cache_label = tk.Label(cache_frame, text=cache_info, font=("Consolas", 10), 
                              bg="#f8f9fc", fg="#374151", justify="left")
        cache_label.pack(padx=15, pady=10, anchor="w")
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg="#f8f9fc")
        button_frame.pack(fill="x", pady=(15, 0))
        
        clear_cache_btn = tk.Button(button_frame, text="🗑️ Clear Cache", 
                                   font=("Segoe UI", 10, "bold"), bg="#dc2626", fg="white",
                                   relief="flat", bd=0, padx=20, pady=8,
                                   command=self.clear_cache)
        clear_cache_btn.pack(side="left", padx=(0, 10))
        
        force_gc_btn = tk.Button(button_frame, text="♻️ Force Garbage Collection", 
                                font=("Segoe UI", 10, "bold"), bg="#059669", fg="white",
                                relief="flat", bd=0, padx=20, pady=8,
                                command=self.force_garbage_collection)
        force_gc_btn.pack(side="left", padx=(0, 10))
        
        close_btn = tk.Button(button_frame, text="Close", 
                             font=("Segoe UI", 10, "bold"), bg="#6b7280", fg="white",
                             relief="flat", bd=0, padx=20, pady=8,
                             command=monitor_window.destroy)
        close_btn.pack(side="right")
    
    def clear_cache(self):
        """Clear data cache to free memory"""
        cache_count = len(self.data_cache)
        self.data_cache.clear()
        messagebox.showinfo("Cache Cleared", f"Cleared {cache_count} cached file(s) from memory.")
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory"""
        before_memory = psutil.virtual_memory().used / (1024**3)
        collected = gc.collect()
        after_memory = psutil.virtual_memory().used / (1024**3)
        freed = before_memory - after_memory
        
        messagebox.showinfo("Garbage Collection", 
                           f"Garbage collection completed.\n"
                           f"Objects collected: {collected}\n"
                           f"Memory freed: {freed:.2f}GB")
    
    def post_to_collaborative_dashboard(self):
        """Post reconciliation results to collaborative dashboard"""
        try:
            if not self.matched_results:
                messagebox.showerror("No Results", 
                                   "❌ No reconciliation results to post.\nPlease run reconciliation first.")
                return
            
            # Import collaborative system
            import sys
            import os
            from datetime import datetime
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from collaborative_dashboard_db import CollaborativeDashboardDB
            
            # Initialize collaborative database
            db = CollaborativeDashboardDB()
            
            # Create session for this reconciliation
            session_name = f"Corporate Settlements - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Calculate session statistics
            total_batches = len(self.matched_results.get('batch_results', {}))
            total_transactions = sum(len(batch.get('matched_pairs', [])) for batch in self.matched_results.get('batch_results', {}).values())
            
            session_desc = f"Corporate settlements reconciliation\nBatches processed: {total_batches}\nTotal transactions: {total_transactions}"
            
            session_id = db.create_session(
                session_name=session_name,
                description=session_desc,
                workflow_type="corporate_settlements",
                created_by="admin"  # Default user
            )
            
            # Convert and post transactions
            posted_count = 0
            for batch_name, batch_data in self.matched_results.get('batch_results', {}).items():
                for match in batch_data.get('matched_pairs', []):
                    # Convert match to transaction format
                    ledger_entry = match.get('ledger_entry', {})
                    stmt_entry = match.get('statement_entry', {})
                    
                    transaction_data = {
                        'reference': ledger_entry.get('Reference', stmt_entry.get('Reference', '')),
                        'amount': float(ledger_entry.get('Amount', stmt_entry.get('Amount', 0))),
                        'date': ledger_entry.get('Date', stmt_entry.get('Date', datetime.now().isoformat())),
                        'description': ledger_entry.get('Description', stmt_entry.get('Description', '')),
                        'type': 'corporate_settlements',
                        'status': 'matched',
                        'metadata': {
                            'batch_name': batch_name,
                            'ledger_entry': ledger_entry,
                            'statement_entry': stmt_entry,
                            'confidence_score': match.get('confidence_score', 0),
                            'workflow': 'corporate_settlements'
                        }
                    }
                    
                    # Add transaction to collaborative session
                    db.add_transaction(session_id, transaction_data)
                    posted_count += 1
            
            # Show success message with dashboard link
            success_msg = f"""✅ Successfully posted to Collaborative Dashboard!

📊 Session Created: {session_name}
💰 Transactions Posted: {posted_count}
📦 Batches Posted: {total_batches}
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
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.data_cache.clear()
            gc.collect()
        except:
            pass
