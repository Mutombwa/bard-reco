"""
Enhanced FNB Export & Collaboration Features
==========================================
Modern, professional export and collaboration system for FNB workflow
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import pandas as pd
from datetime import datetime
import os
import json

class EnhancedFNBExportSystem:
    """Enhanced FNB Export with modern collaboration features"""
    
    def __init__(self, parent_workflow):
        self.parent = parent_workflow
        self.app = parent_workflow.app if hasattr(parent_workflow, 'app') else None
        self.window = None
        self.results_tree = None
        self.current_results = None
        
    def show_enhanced_export_center(self):
        """Show the enhanced export and collaboration center"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("🚀 FNB Export & Collaboration Center")
        self.window.geometry("1400x900")
        self.window.configure(bg="#f8fafc")
        self.window.transient(self.parent)
        
        # Make it modal
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() - 100,
            self.parent.winfo_rooty() - 50
        ))
        
        self.create_header()
        self.create_main_content()
        
    def create_header(self):
        """Create modern header with gradient effect"""
        header_frame = tk.Frame(self.window, bg="#1e40af", height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title section
        title_container = tk.Frame(header_frame, bg="#1e40af")
        title_container.pack(expand=True, fill='both')
        
        # Main title
        title_label = tk.Label(title_container, text="🚀 FNB Export & Collaboration Center", 
                              font=("Segoe UI", 20, "bold"), bg="#1e40af", fg="white")
        title_label.pack(pady=(20, 5))
        
        # Subtitle with status
        subtitle_text = "Advanced reconciliation results management with live collaboration"
        if hasattr(self.parent, 'reconcile_results') and self.parent.reconcile_results:
            matches = len(self.parent.reconcile_results.get('matched', []))
            subtitle_text += f" • {matches} matches ready for export"
        
        subtitle_label = tk.Label(title_container, text=subtitle_text, 
                                 font=("Segoe UI", 12), bg="#1e40af", fg="#bfdbfe")
        subtitle_label.pack()
        
        # Close button
        close_btn = tk.Button(title_container, text="✖", font=("Segoe UI", 14, "bold"), 
                             bg="#dc2626", fg="white", bd=0, padx=15, pady=5,
                             command=self.close_center)
        close_btn.place(relx=0.98, rely=0.1, anchor='ne')
        
    def create_main_content(self):
        """Create main content with modern tabbed interface"""
        main_frame = tk.Frame(self.window, bg="#f8fafc")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Results Preview Tab
        self.create_results_tab()
        
        # Export Options Tab
        self.create_export_tab()
        
        # Collaboration Tab
        self.create_collaboration_tab()
        
        # Analytics Tab
        self.create_analytics_tab()
        
    def create_results_tab(self):
        """Create results preview tab with live data"""
        results_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(results_frame, text="📊 Results Preview")
        
        # Toolbar
        toolbar = tk.Frame(results_frame, bg="#f1f5f9", height=60)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)
        
        # Refresh button
        refresh_btn = tk.Button(toolbar, text="🔄 Refresh Data", font=("Segoe UI", 11), 
                               bg="#3b82f6", fg="white", padx=20, pady=8,
                               command=self.refresh_results_data)
        refresh_btn.pack(side='left', padx=20, pady=15)
        
        # Results count label
        self.results_count_label = tk.Label(toolbar, text="Loading results...", 
                                           font=("Segoe UI", 11, "bold"), bg="#f1f5f9")
        self.results_count_label.pack(side='left', padx=(20, 0), pady=15)
        
        # Export quick button
        quick_export_btn = tk.Button(toolbar, text="⚡ Quick Export", font=("Segoe UI", 11), 
                                    bg="#10b981", fg="white", padx=20, pady=8,
                                    command=self.quick_export_current)
        quick_export_btn.pack(side='right', padx=20, pady=15)
        
        # Results display area
        display_frame = tk.Frame(results_frame, bg="#ffffff")
        display_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for results
        columns = ('Type', 'Similarity', 'Ledger_Amount', 'Statement_Amount', 'Date', 'Reference', 'Status')
        self.results_tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_config = {
            'Type': {'width': 120, 'heading': 'Match Type'},
            'Similarity': {'width': 80, 'heading': 'Similarity'},
            'Ledger_Amount': {'width': 100, 'heading': 'Ledger Amount'},
            'Statement_Amount': {'width': 120, 'heading': 'Statement Amount'},
            'Date': {'width': 100, 'heading': 'Date'},
            'Reference': {'width': 150, 'heading': 'Reference'},
            'Status': {'width': 100, 'heading': 'Status'}
        }
        
        for col, config in column_config.items():
            self.results_tree.heading(col, text=config['heading'])
            self.results_tree.column(col, width=config['width'])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.results_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Load initial data
        self.refresh_results_data()
        
    def create_export_tab(self):
        """Create enhanced export options tab"""
        export_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(export_frame, text="📤 Export Options")
        
        # Export options container
        options_container = tk.Frame(export_frame, bg="#ffffff")
        options_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Export format selection
        format_frame = tk.LabelFrame(options_container, text="📁 Export Format", 
                                   font=("Segoe UI", 12, "bold"), bg="#ffffff")
        format_frame.pack(fill='x', pady=(0, 20))
        
        format_inner = tk.Frame(format_frame, bg="#ffffff")
        format_inner.pack(fill='x', padx=20, pady=15)
        
        self.export_format = tk.StringVar(value="xlsx")
        
        xlsx_radio = tk.Radiobutton(format_inner, text="📊 Excel (.xlsx) - Recommended", 
                                   variable=self.export_format, value="xlsx", 
                                   font=("Segoe UI", 11), bg="#ffffff")
        xlsx_radio.pack(anchor='w', pady=5)
        
        csv_radio = tk.Radiobutton(format_inner, text="📄 CSV (.csv) - Universal", 
                                  variable=self.export_format, value="csv", 
                                  font=("Segoe UI", 11), bg="#ffffff")
        csv_radio.pack(anchor='w', pady=5)
        
        json_radio = tk.Radiobutton(format_inner, text="🔧 JSON (.json) - Technical", 
                                   variable=self.export_format, value="json", 
                                   font=("Segoe UI", 11), bg="#ffffff")
        json_radio.pack(anchor='w', pady=5)
        
        # Export content selection
        content_frame = tk.LabelFrame(options_container, text="📋 Content Selection", 
                                    font=("Segoe UI", 12, "bold"), bg="#ffffff")
        content_frame.pack(fill='x', pady=(0, 20))
        
        content_inner = tk.Frame(content_frame, bg="#ffffff")
        content_inner.pack(fill='x', padx=20, pady=15)
        
        self.include_matches = tk.BooleanVar(value=True)
        self.include_unmatched = tk.BooleanVar(value=True)
        self.include_foreign_credits = tk.BooleanVar(value=True)
        self.include_summary = tk.BooleanVar(value=True)
        
        matches_cb = tk.Checkbutton(content_inner, text="✅ Matched Transactions", 
                                   variable=self.include_matches, font=("Segoe UI", 11), bg="#ffffff")
        matches_cb.pack(anchor='w', pady=3)
        
        unmatched_cb = tk.Checkbutton(content_inner, text="❌ Unmatched Items", 
                                     variable=self.include_unmatched, font=("Segoe UI", 11), bg="#ffffff")
        unmatched_cb.pack(anchor='w', pady=3)
        
        foreign_cb = tk.Checkbutton(content_inner, text="🌍 Foreign Credits", 
                                   variable=self.include_foreign_credits, font=("Segoe UI", 11), bg="#ffffff")
        foreign_cb.pack(anchor='w', pady=3)
        
        summary_cb = tk.Checkbutton(content_inner, text="📊 Summary Statistics", 
                                   variable=self.include_summary, font=("Segoe UI", 11), bg="#ffffff")
        summary_cb.pack(anchor='w', pady=3)
        
        # Export buttons
        button_frame = tk.Frame(options_container, bg="#ffffff")
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Standard export
        standard_btn = tk.Button(button_frame, text="📁 Export to File", 
                               font=("Segoe UI", 12, "bold"), bg="#059669", fg="white",
                               padx=30, pady=12, command=self.export_to_file)
        standard_btn.pack(side='left', padx=(0, 15))
        
        # Quick export to desktop
        desktop_btn = tk.Button(button_frame, text="⚡ Quick Desktop Export", 
                               font=("Segoe UI", 12, "bold"), bg="#0891b2", fg="white",
                               padx=30, pady=12, command=self.quick_export_desktop)
        desktop_btn.pack(side='left', padx=(0, 15))
        
        # Preview export
        preview_btn = tk.Button(button_frame, text="👁️ Preview Export", 
                               font=("Segoe UI", 12), bg="#6366f1", fg="white",
                               padx=30, pady=12, command=self.preview_export)
        preview_btn.pack(side='left', padx=(0, 15))
        
        # POST to Dashboard
        post_btn = tk.Button(button_frame, text="🚀 POST to Dashboard", 
                            font=("Segoe UI", 12, "bold"), bg="#10b981", fg="white",
                            padx=30, pady=12, command=self.post_to_collaborative_dashboard)
        post_btn.pack(side='left')
        
    def create_collaboration_tab(self):
        """Create enhanced collaboration tab"""
        collab_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(collab_frame, text="🤝 Collaboration")
        
        # Check if collaboration is available
        collab_available = (hasattr(self.app, 'collab_mgr') and 
                           hasattr(self.app, 'collaboration_enabled') and 
                           self.app.collaboration_enabled)
        
        if not collab_available:
            # Show collaboration not available message
            not_available_frame = tk.Frame(collab_frame, bg="#ffffff")
            not_available_frame.pack(expand=True, fill='both')
            
            icon_label = tk.Label(not_available_frame, text="🤝", font=("Segoe UI", 48), bg="#ffffff")
            icon_label.pack(pady=(100, 20))
            
            msg_label = tk.Label(not_available_frame, text="Collaboration features not available", 
                               font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#6b7280")
            msg_label.pack()
            
            submsg_label = tk.Label(not_available_frame, text="Please restart the application to enable collaboration", 
                                  font=("Segoe UI", 12), bg="#ffffff", fg="#9ca3af")
            submsg_label.pack(pady=10)
            return
        
        # Collaboration controls
        controls_frame = tk.Frame(collab_frame, bg="#f8fafc")
        controls_frame.pack(fill='x', padx=20, pady=20)
        
        # Session management
        session_frame = tk.LabelFrame(controls_frame, text="📋 Session Management", 
                                    font=("Segoe UI", 12, "bold"), bg="#ffffff")
        session_frame.pack(fill='x', pady=(0, 15))
        
        session_inner = tk.Frame(session_frame, bg="#ffffff")
        session_inner.pack(fill='x', padx=20, pady=15)
        
        # Active sessions display
        self.session_combo = ttk.Combobox(session_inner, font=("Segoe UI", 11), width=60, state='readonly')
        self.session_combo.pack(side='left', padx=(0, 10))
        
        refresh_sessions_btn = tk.Button(session_inner, text="🔄", font=("Segoe UI", 11), 
                                       bg="#3b82f6", fg="white", padx=10, pady=5,
                                       command=self.refresh_sessions)
        refresh_sessions_btn.pack(side='left', padx=(0, 10))
        
        new_session_btn = tk.Button(session_inner, text="➕ New Session", font=("Segoe UI", 11), 
                                   bg="#10b981", fg="white", padx=15, pady=5,
                                   command=self.create_new_session)
        new_session_btn.pack(side='left')
        
        # Post configuration
        post_frame = tk.LabelFrame(controls_frame, text="🚀 Post Configuration", 
                                 font=("Segoe UI", 12, "bold"), bg="#ffffff")
        post_frame.pack(fill='x', pady=(0, 15))
        
        post_inner = tk.Frame(post_frame, bg="#ffffff")
        post_inner.pack(fill='x', padx=20, pady=15)
        
        # Result name
        tk.Label(post_inner, text="Result Name:", font=("Segoe UI", 11, "bold"), bg="#ffffff").grid(row=0, column=0, sticky='w', pady=5)
        self.result_name_var = tk.StringVar(value=f"FNB_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        name_entry = tk.Entry(post_inner, textvariable=self.result_name_var, font=("Segoe UI", 11), width=50)
        name_entry.grid(row=0, column=1, columnspan=2, sticky='w', padx=(10, 0), pady=5)
        
        # Notes
        tk.Label(post_inner, text="Notes:", font=("Segoe UI", 11, "bold"), bg="#ffffff").grid(row=1, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(post_inner, height=4, width=50, font=("Segoe UI", 10))
        self.notes_text.grid(row=1, column=1, columnspan=2, sticky='w', padx=(10, 0), pady=5)
        
        # Post buttons
        post_button_frame = tk.Frame(controls_frame, bg="#f8fafc")
        post_button_frame.pack(fill='x', pady=(15, 0))
        
        post_btn = tk.Button(post_button_frame, text="🚀 Post to Collaboration", 
                           font=("Segoe UI", 12, "bold"), bg="#7c3aed", fg="white",
                           padx=30, pady=12, command=self.post_to_collaboration)
        post_btn.pack(side='left', padx=(0, 15))
        
        post_export_btn = tk.Button(post_button_frame, text="📤 Post & Export", 
                                   font=("Segoe UI", 12, "bold"), bg="#059669", fg="white",
                                   padx=30, pady=12, command=self.post_and_export)
        post_export_btn.pack(side='left')
        
        # Posted results section
        posted_frame = tk.LabelFrame(collab_frame, text="📋 Recently Posted Results", 
                                   font=("Segoe UI", 12, "bold"), bg="#ffffff")
        posted_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Posted results tree
        posted_inner = tk.Frame(posted_frame, bg="#ffffff")
        posted_inner.pack(fill='both', expand=True, padx=15, pady=15)
        
        posted_columns = ('Post_ID', 'Session', 'Posted_Date', 'Size', 'Notes')
        self.posted_tree = ttk.Treeview(posted_inner, columns=posted_columns, show='headings', height=8)
        
        for col in posted_columns:
            self.posted_tree.heading(col, text=col.replace('_', ' '))
            
        posted_scrollbar = ttk.Scrollbar(posted_inner, orient='vertical', command=self.posted_tree.yview)
        self.posted_tree.configure(yscrollcommand=posted_scrollbar.set)
        
        self.posted_tree.pack(side='left', fill='both', expand=True)
        posted_scrollbar.pack(side='right', fill='y')
        
        # Load sessions and posted results
        self.refresh_sessions()
        self.refresh_posted_results()
        
    def create_analytics_tab(self):
        """Create analytics and insights tab"""
        analytics_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(analytics_frame, text="📈 Analytics")
        
        # Analytics content
        analytics_container = tk.Frame(analytics_frame, bg="#ffffff")
        analytics_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Summary statistics
        stats_frame = tk.LabelFrame(analytics_container, text="📊 Reconciliation Statistics", 
                                  font=("Segoe UI", 12, "bold"), bg="#ffffff")
        stats_frame.pack(fill='x', pady=(0, 20))
        
        self.create_statistics_display(stats_frame)
        
        # Match quality analysis
        quality_frame = tk.LabelFrame(analytics_container, text="🎯 Match Quality Analysis", 
                                    font=("Segoe UI", 12, "bold"), bg="#ffffff")
        quality_frame.pack(fill='x', pady=(0, 20))
        
        self.create_quality_analysis(quality_frame)
        
        # Trend analysis
        trend_frame = tk.LabelFrame(analytics_container, text="📈 Processing Trends", 
                                  font=("Segoe UI", 12, "bold"), bg="#ffffff")
        trend_frame.pack(fill='both', expand=True)
        
        self.create_trend_analysis(trend_frame)
        
    def refresh_results_data(self):
        """Refresh the results data display"""
        # Clear existing data
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        try:
            if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
                self.results_count_label.config(text="No reconciliation results available")
                return
            
            results = self.parent.reconcile_results
            matched = results.get('matched', [])
            foreign_credits = results.get('foreign_credits', [])
            unmatched_statement = results.get('unmatched_statement', None)
            unmatched_ledger = results.get('unmatched_ledger', None)
            
            total_count = 0
            
            # Add matched transactions
            for match in matched:
                similarity = match.get('similarity', 0)
                match_type = 'Perfect Match' if similarity >= 100 else f'Fuzzy Match'
                
                ledger_amount = self.safe_get_amount(match.get('ledger', {}))
                stmt_amount = self.safe_get_amount(match.get('statement', {}))
                date = self.safe_get_date(match.get('ledger', {}) or match.get('statement', {}))
                reference = self.safe_get_reference(match.get('ledger', {}) or match.get('statement', {}))
                
                self.results_tree.insert('', 'end', values=(
                    match_type, f"{similarity:.1f}%", ledger_amount, stmt_amount, date, reference, 'Matched'
                ))
                total_count += 1
            
            # Add foreign credits
            for fc in foreign_credits:
                amount = self.safe_get_amount(fc)
                date = self.safe_get_date(fc)
                reference = self.safe_get_reference(fc)
                
                self.results_tree.insert('', 'end', values=(
                    'Foreign Credit', '100.0%', amount, amount, date, reference, 'Foreign Credit'
                ))
                total_count += 1
            
            # Add unmatched items (sample)
            if unmatched_statement is not None and not unmatched_statement.empty:
                for i, (_, row) in enumerate(unmatched_statement.iterrows()):
                    if i >= 10:  # Limit display for performance
                        break
                    amount = self.safe_get_amount(row.to_dict())
                    date = self.safe_get_date(row.to_dict())
                    reference = self.safe_get_reference(row.to_dict())
                    
                    self.results_tree.insert('', 'end', values=(
                        'Unmatched Statement', '0.0%', '', amount, date, reference, 'Unmatched'
                    ))
                    total_count += 1
            
            # Update count label
            match_count = len(matched)
            fc_count = len(foreign_credits)
            unmatched_count = (len(unmatched_statement) if unmatched_statement is not None else 0) + \
                            (len(unmatched_ledger) if unmatched_ledger is not None else 0)
            
            self.results_count_label.config(
                text=f"📊 {match_count} matches • {fc_count} foreign credits • {unmatched_count} unmatched"
            )
            
        except Exception as e:
            self.results_count_label.config(text=f"Error loading results: {e}")
            print(f"Error refreshing results: {e}")
    
    def safe_get_amount(self, data_dict):
        """Safely get amount from data dictionary"""
        amount_keys = ['amount', 'Amount', 'AMOUNT', 'debit', 'credit', 'value']
        for key in amount_keys:
            if key in data_dict:
                try:
                    return f"{float(data_dict[key]):,.2f}"
                except:
                    continue
        return "N/A"
    
    def safe_get_date(self, data_dict):
        """Safely get date from data dictionary"""
        date_keys = ['date', 'Date', 'DATE', 'transaction_date', 'value_date']
        for key in date_keys:
            if key in data_dict:
                return str(data_dict[key])[:10]  # First 10 chars for date
        return "N/A"
    
    def safe_get_reference(self, data_dict):
        """Safely get reference from data dictionary"""
        ref_keys = ['reference', 'Reference', 'REF', 'description', 'Description', 'narrative']
        for key in ref_keys:
            if key in data_dict:
                ref = str(data_dict[key])
                return ref[:30] + "..." if len(ref) > 30 else ref
        return "N/A"
    
    def export_to_file(self):
        """Export results to user-selected file"""
        if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
            messagebox.showwarning("No Results", "Please run reconciliation first.", parent=self.window)
            return
        
        # Get export format
        format_ext = self.export_format.get()
        
        # File dialog
        filetypes = []
        default_ext = ""
        
        if format_ext == "xlsx":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            default_ext = ".xlsx"
        elif format_ext == "csv":
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        elif format_ext == "json":
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
            default_ext = ".json"
        
        filename = f"FNB_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"
        file_path = filedialog.asksaveasfilename(
            title="Export FNB Reconciliation Results",
            defaultextension=default_ext,
            filetypes=filetypes,
            initialvalue=filename,
            parent=self.window
        )
        
        if file_path:
            try:
                self.perform_export(file_path, format_ext)
                messagebox.showinfo("Export Successful", 
                                   f"Results exported successfully to:\\n{file_path}", 
                                   parent=self.window)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\\n{str(e)}", 
                                   parent=self.window)
    
    def quick_export_desktop(self):
        """Quick export to desktop"""
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            format_ext = self.export_format.get()
            filename = f"FNB_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_ext}"
            file_path = os.path.join(desktop, filename)
            
            self.perform_export(file_path, format_ext)
            
            messagebox.showinfo("Quick Export Successful", 
                               f"Results exported to desktop:\\n{filename}", 
                               parent=self.window)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\\n{str(e)}", 
                               parent=self.window)
    
    def quick_export_current(self):
        """Quick export current view"""
        self.quick_export_desktop()
    
    def perform_export(self, file_path, format_ext):
        """Perform the actual export"""
        # Prepare comprehensive data
        export_data = self.prepare_comprehensive_export_data()
        
        if format_ext == "xlsx":
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                if self.include_matches.get() and 'matches' in export_data:
                    export_data['matches'].to_excel(writer, sheet_name='Matches', index=False)
                
                if self.include_unmatched.get() and 'unmatched' in export_data:
                    export_data['unmatched'].to_excel(writer, sheet_name='Unmatched', index=False)
                
                if self.include_foreign_credits.get() and 'foreign_credits' in export_data:
                    export_data['foreign_credits'].to_excel(writer, sheet_name='Foreign_Credits', index=False)
                
                if self.include_summary.get() and 'summary' in export_data:
                    export_data['summary'].to_excel(writer, sheet_name='Summary', index=False)
        
        elif format_ext == "csv":
            # Combine all data for CSV
            all_data = []
            for key, df in export_data.items():
                if (key == 'matches' and self.include_matches.get()) or \
                   (key == 'unmatched' and self.include_unmatched.get()) or \
                   (key == 'foreign_credits' and self.include_foreign_credits.get()) or \
                   (key == 'summary' and self.include_summary.get()):
                    all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                combined_df.to_csv(file_path, index=False)
        
        elif format_ext == "json":
            json_data = {}
            for key, df in export_data.items():
                if (key == 'matches' and self.include_matches.get()) or \
                   (key == 'unmatched' and self.include_unmatched.get()) or \
                   (key == 'foreign_credits' and self.include_foreign_credits.get()) or \
                   (key == 'summary' and self.include_summary.get()):
                    json_data[key] = df.to_dict('records')
            
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
    
    def prepare_comprehensive_export_data(self):
        """Prepare comprehensive export data"""
        if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
            return {}
        
        results = self.parent.reconcile_results
        export_data = {}
        
        # Prepare matches data
        matched = results.get('matched', [])
        if matched:
            matches_list = []
            for match in matched:
                match_row = {
                    'Match_Type': 'Perfect Match' if match.get('similarity', 0) >= 100 else 'Fuzzy Match',
                    'Similarity': f"{match.get('similarity', 0):.1f}%",
                    'Status': 'Matched'
                }
                
                # Add ledger data
                if 'ledger' in match:
                    for key, value in match['ledger'].items():
                        match_row[f'Ledger_{key}'] = value
                
                # Add statement data
                if 'statement' in match:
                    for key, value in match['statement'].items():
                        match_row[f'Statement_{key}'] = value
                
                matches_list.append(match_row)
            
            export_data['matches'] = pd.DataFrame(matches_list)
        
        # Prepare foreign credits data
        foreign_credits = results.get('foreign_credits', [])
        if foreign_credits:
            fc_list = []
            for fc in foreign_credits:
                fc_row = {
                    'Type': 'Foreign Credit',
                    'Status': 'Foreign Credit'
                }
                for key, value in fc.items():
                    fc_row[f'ForeignCredit_{key}'] = value
                fc_list.append(fc_row)
            
            export_data['foreign_credits'] = pd.DataFrame(fc_list)
        
        # Prepare unmatched data
        unmatched_list = []
        
        unmatched_statement = results.get('unmatched_statement', None)
        if unmatched_statement is not None and not unmatched_statement.empty:
            for _, row in unmatched_statement.iterrows():
                unmatched_row = {
                    'Type': 'Unmatched Statement',
                    'Status': 'Unmatched'
                }
                for key, value in row.items():
                    unmatched_row[f'Statement_{key}'] = value
                unmatched_list.append(unmatched_row)
        
        unmatched_ledger = results.get('unmatched_ledger', None)
        if unmatched_ledger is not None and not unmatched_ledger.empty:
            for _, row in unmatched_ledger.iterrows():
                unmatched_row = {
                    'Type': 'Unmatched Ledger',
                    'Status': 'Unmatched'
                }
                for key, value in row.items():
                    unmatched_row[f'Ledger_{key}'] = value
                unmatched_list.append(unmatched_row)
        
        if unmatched_list:
            export_data['unmatched'] = pd.DataFrame(unmatched_list)
        
        # Prepare summary data
        summary_data = {
            'Metric': [
                'Total Matches',
                'Perfect Matches',
                'Fuzzy Matches',
                'Foreign Credits',
                'Unmatched Statement',
                'Unmatched Ledger',
                'Match Rate (%)',
                'Export Date'
            ],
            'Value': [
                len(matched),
                len([m for m in matched if m.get('similarity', 0) >= 100]),
                len([m for m in matched if 0 < m.get('similarity', 0) < 100]),
                len(foreign_credits),
                len(unmatched_statement) if unmatched_statement is not None else 0,
                len(unmatched_ledger) if unmatched_ledger is not None else 0,
                f"{(len(matched) / (len(matched) + len(unmatched_statement or []) + len(unmatched_ledger or [])) * 100):.1f}" if matched else "0.0",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        export_data['summary'] = pd.DataFrame(summary_data)
        
        return export_data
    
    def preview_export(self):
        """Preview export data"""
        preview_window = tk.Toplevel(self.window)
        preview_window.title("📋 Export Preview")
        preview_window.geometry("800x600")
        preview_window.configure(bg="#ffffff")
        
        # Preview content
        text_widget = tk.Text(preview_window, wrap='none', font=("Consolas", 10))
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        
        scrollbar_v = ttk.Scrollbar(preview_window, orient='vertical', command=text_widget.yview)
        scrollbar_h = ttk.Scrollbar(preview_window, orient='horizontal', command=text_widget.xview)
        text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Generate preview
        try:
            export_data = self.prepare_comprehensive_export_data()
            preview_text = f"FNB RECONCILIATION EXPORT PREVIEW\\n"
            preview_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
            preview_text += "=" * 50 + "\\n\\n"
            
            for data_type, df in export_data.items():
                if not df.empty:
                    preview_text += f"{data_type.upper().replace('_', ' ')}:\\n"
                    preview_text += f"Records: {len(df)}\\n"
                    preview_text += df.head(10).to_string(index=False) + "\\n\\n"
            
            text_widget.insert('1.0', preview_text)
            
        except Exception as e:
            text_widget.insert('1.0', f"Error generating preview: {e}")
    
    def refresh_sessions(self):
        """Refresh collaboration sessions"""
        if not (hasattr(self.app, 'collab_mgr') and self.app.collaboration_enabled):
            return
        
        try:
            sessions = self.app.collab_mgr.get_active_sessions()
            session_options = [f"{s['session_name']} ({s['session_id'][:8]}...)" for s in sessions]
            
            if not session_options:
                session_options = ["No active sessions - Create one below"]
            
            self.session_combo.config(values=session_options)
            if session_options and "No active sessions" not in session_options[0]:
                self.session_combo.set(session_options[0])
                
        except Exception as e:
            print(f"Error refreshing sessions: {e}")
    
    def create_new_session(self):
        """Create new collaboration session"""
        if not (hasattr(self.app, 'collab_mgr') and self.app.collaboration_enabled):
            messagebox.showwarning("Not Available", "Collaboration not available", parent=self.window)
            return
        
        session_name = simpledialog.askstring("New Session", 
                                             "Enter session name for this FNB reconciliation batch:",
                                             parent=self.window)
        if session_name:
            description = simpledialog.askstring("Session Description", 
                                                "Enter description (optional):",
                                                parent=self.window) or ""
            
            session_id = self.app.collab_mgr.create_session(session_name, "Current User", description)
            if session_id:
                messagebox.showinfo("Session Created", 
                                   f"Session '{session_name}' created successfully!\\n\\nSession ID: {session_id}", 
                                   parent=self.window)
                self.refresh_sessions()
            else:
                messagebox.showerror("Error", "Failed to create session", parent=self.window)
    
    def post_to_collaboration(self):
        """Post results to collaboration"""
        if not (hasattr(self.app, 'collab_mgr') and self.app.collaboration_enabled):
            messagebox.showwarning("Not Available", "Collaboration not available", parent=self.window)
            return
        
        if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
            messagebox.showwarning("No Results", "Please run reconciliation first.", parent=self.window)
            return
        
        # Get selected session
        session_selection = self.session_combo.get()
        if not session_selection or "No active sessions" in session_selection:
            messagebox.showwarning("No Session", "Please select or create a collaboration session", 
                                 parent=self.window)
            return
        
        # Extract session ID
        session_id = session_selection.split('(')[1].split(')')[0].replace('...', '')
        
        # Find full session ID
        sessions = self.app.collab_mgr.get_active_sessions()
        full_session_id = None
        for session in sessions:
            if session['session_id'].startswith(session_id):
                full_session_id = session['session_id']
                break
        
        if not full_session_id:
            messagebox.showerror("Session Error", "Could not find the selected session", 
                               parent=self.window)
            return
        
        # Prepare data for posting
        results_data = self.parent.prepare_export_data()
        result_name = self.result_name_var.get().strip()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        if not result_name:
            messagebox.showwarning("Missing Name", "Please enter a result name", parent=self.window)
            return
        
        try:
            post_id = self.app.collab_mgr.post_workflow_results(
                session_id=full_session_id,
                workflow_type="FNB",
                result_data=results_data,
                posted_by="Current User",
                result_name=result_name,
                notes=notes,
                export_format="xlsx"
            )
            
            if post_id:
                messagebox.showinfo("Posted Successfully", 
                                   f"Results posted to collaboration!\\n\\nPost ID: {post_id}\\nSession: {session_selection}", 
                                   parent=self.window)
                self.refresh_posted_results()
            else:
                messagebox.showerror("Post Failed", "Failed to post results to collaboration", 
                                   parent=self.window)
                
        except Exception as e:
            messagebox.showerror("Post Error", f"Failed to post results:\\n{str(e)}", 
                               parent=self.window)
    
    def post_and_export(self):
        """Post to collaboration and export locally"""
        self.post_to_collaboration()
        self.export_to_file()
    
    def refresh_posted_results(self):
        """Refresh posted results display"""
        if not (hasattr(self.app, 'collab_mgr') and self.app.collaboration_enabled):
            return
        
        # Clear existing items
        for item in self.posted_tree.get_children():
            self.posted_tree.delete(item)
        
        try:
            sessions = self.app.collab_mgr.get_active_sessions()
            for session in sessions:
                posts = self.app.collab_mgr.get_session_posts(session['session_id'])
                fnb_posts = [p for p in posts if p['workflow_type'] == 'FNB']
                
                for post in fnb_posts[:10]:  # Show last 10 FNB posts
                    post_id_short = post['post_id'][:15] + '...'
                    session_name_short = session['session_name'][:20] + '...' if len(session['session_name']) > 20 else session['session_name']
                    date_short = post['posted_date'][:16] if post['posted_date'] else ''
                    size_kb = round(post['file_size'] / 1024, 1) if post['file_size'] else 0
                    notes_short = post['notes'][:30] + '...' if len(post['notes']) > 30 else post['notes']
                    
                    self.posted_tree.insert('', 'end', values=(
                        post_id_short, session_name_short, date_short, f"{size_kb} KB", notes_short
                    ))
                    
        except Exception as e:
            print(f"Error refreshing posted results: {e}")
    
    def create_statistics_display(self, parent):
        """Create statistics display"""
        stats_inner = tk.Frame(parent, bg="#ffffff")
        stats_inner.pack(fill='x', padx=20, pady=15)
        
        if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
            no_data_label = tk.Label(stats_inner, text="📊 No reconciliation data available", 
                                   font=("Segoe UI", 12), bg="#ffffff", fg="#6b7280")
            no_data_label.pack(pady=20)
            return
        
        results = self.parent.reconcile_results
        matched = results.get('matched', [])
        foreign_credits = results.get('foreign_credits', [])
        unmatched_statement = results.get('unmatched_statement', None)
        unmatched_ledger = results.get('unmatched_ledger', None)
        
        # Calculate statistics
        total_matches = len(matched)
        perfect_matches = len([m for m in matched if m.get('similarity', 0) >= 100])
        fuzzy_matches = total_matches - perfect_matches
        total_unmatched = (len(unmatched_statement) if unmatched_statement is not None else 0) + \
                         (len(unmatched_ledger) if unmatched_ledger is not None else 0)
        
        # Display statistics in a grid
        stats_grid = tk.Frame(stats_inner, bg="#ffffff")
        stats_grid.pack(fill='x')
        
        stats_data = [
            ("🎯 Perfect Matches", perfect_matches, "#10b981"),
            ("🔍 Fuzzy Matches", fuzzy_matches, "#f59e0b"),
            ("🌍 Foreign Credits", len(foreign_credits), "#3b82f6"),
            ("❌ Unmatched Items", total_unmatched, "#ef4444")
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_grid, bg=color, relief="raised", bd=2)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            value_label = tk.Label(stat_frame, text=str(value), font=("Segoe UI", 16, "bold"), 
                                 bg=color, fg="white")
            value_label.pack(pady=(10, 5))
            
            desc_label = tk.Label(stat_frame, text=label, font=("Segoe UI", 10), 
                                bg=color, fg="white")
            desc_label.pack(pady=(0, 10))
            
            stats_grid.columnconfigure(i, weight=1)
    
    def create_quality_analysis(self, parent):
        """Create match quality analysis"""
        quality_inner = tk.Frame(parent, bg="#ffffff")
        quality_inner.pack(fill='x', padx=20, pady=15)
        
        if not hasattr(self.parent, 'reconcile_results') or not self.parent.reconcile_results:
            no_data_label = tk.Label(quality_inner, text="🎯 No match quality data available", 
                                   font=("Segoe UI", 12), bg="#ffffff", fg="#6b7280")
            no_data_label.pack(pady=20)
            return
        
        # Analyze match quality
        matched = self.parent.reconcile_results.get('matched', [])
        if not matched:
            return
        
        quality_ranges = {
            "Excellent (95-100%)": 0,
            "Good (85-94%)": 0,
            "Fair (70-84%)": 0,
            "Poor (<70%)": 0
        }
        
        for match in matched:
            similarity = match.get('similarity', 0)
            if similarity >= 95:
                quality_ranges["Excellent (95-100%)"] += 1
            elif similarity >= 85:
                quality_ranges["Good (85-94%)"] += 1
            elif similarity >= 70:
                quality_ranges["Fair (70-84%)"] += 1
            else:
                quality_ranges["Poor (<70%)"] += 1
        
        # Display quality analysis
        for quality, count in quality_ranges.items():
            if count > 0:
                quality_row = tk.Frame(quality_inner, bg="#ffffff")
                quality_row.pack(fill='x', pady=5)
                
                quality_label = tk.Label(quality_row, text=quality, font=("Segoe UI", 11), 
                                       bg="#ffffff", anchor='w')
                quality_label.pack(side='left')
                
                count_label = tk.Label(quality_row, text=f"{count} matches", 
                                     font=("Segoe UI", 11, "bold"), bg="#ffffff")
                count_label.pack(side='right')
    
    def create_trend_analysis(self, parent):
        """Create processing trend analysis"""
        trend_inner = tk.Frame(parent, bg="#ffffff")
        trend_inner.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Simple trend display
        trend_label = tk.Label(trend_inner, text="📈 Processing Trends", 
                             font=("Segoe UI", 12, "bold"), bg="#ffffff")
        trend_label.pack(pady=10)
        
        info_label = tk.Label(trend_inner, 
                            text="Trend analysis will be available after multiple reconciliation sessions.\\n" +
                                 "Keep using the system to build processing history!", 
                            font=("Segoe UI", 10), bg="#ffffff", fg="#6b7280")
        info_label.pack(pady=20)
    
    def post_to_collaborative_dashboard(self):
        """Post FNB reconciliation results to collaborative dashboard"""
        try:
            if not hasattr(self.parent_workflow, 'reconciliation_results') or not self.parent_workflow.reconciliation_results:
                messagebox.showerror("No Results", 
                                   "❌ No reconciliation results to post.\nPlease run FNB reconciliation first.")
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
            session_name = f"FNB Reconciliation - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Calculate session statistics
            results = self.parent_workflow.reconciliation_results
            total_matches = len(results.get('matched', pd.DataFrame())) if 'matched' in results else 0
            total_unmatched = len(results.get('unmatched_ledger', pd.DataFrame())) if 'unmatched_ledger' in results else 0
            total_foreign = len(results.get('foreign_credits', pd.DataFrame())) if 'foreign_credits' in results else 0
            
            session_desc = f"FNB Bank reconciliation\nMatched: {total_matches}\nUnmatched: {total_unmatched}\nForeign Credits: {total_foreign}"
            
            session_id = db.create_session(
                session_name=session_name,
                description=session_desc,
                workflow_type="fnb_reconciliation",
                created_by="admin"  # Default user
            )
            
            # Convert and post transactions
            posted_count = 0
            
            # Post matched transactions
            if 'matched' in results and not results['matched'].empty:
                for _, row in results['matched'].iterrows():
                    transaction_data = {
                        'reference': str(row.get('Reference', '')),
                        'amount': float(row.get('Amount', 0)),
                        'date': str(row.get('Date', datetime.now().isoformat())),
                        'description': str(row.get('Description', '')),
                        'type': 'fnb_reconciliation',
                        'status': 'matched',
                        'metadata': {
                            'ledger_data': row.to_dict(),
                            'workflow': 'fnb_reconciliation'
                        }
                    }
                    db.add_transaction(session_id, transaction_data)
                    posted_count += 1
            
            # Post unmatched ledger entries
            if 'unmatched_ledger' in results and not results['unmatched_ledger'].empty:
                for _, row in results['unmatched_ledger'].iterrows():
                    transaction_data = {
                        'reference': str(row.get('Reference', '')),
                        'amount': float(row.get('Amount', 0)),
                        'date': str(row.get('Date', datetime.now().isoformat())),
                        'description': str(row.get('Description', '')),
                        'type': 'fnb_reconciliation',
                        'status': 'unmatched_ledger',
                        'metadata': {
                            'ledger_data': row.to_dict(),
                            'workflow': 'fnb_reconciliation'
                        }
                    }
                    db.add_transaction(session_id, transaction_data)
                    posted_count += 1
            
            # Close export window
            if hasattr(self, 'window') and self.window:
                self.window.destroy()
            
            # Show success message with dashboard link
            success_msg = f"""✅ Successfully posted to Collaborative Dashboard!

📊 Session Created: {session_name}
💰 Transactions Posted: {posted_count}
✅ Matched: {total_matches}
❌ Unmatched: {total_unmatched}
🌍 Foreign Credits: {total_foreign}
🆔 Session ID: {session_id}

🌐 View in Dashboard: http://localhost:5000
🔐 Login: admin / admin123

The collaborative dashboard is now updated with your FNB reconciliation results.
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
    
    def close_center(self):
        """Close the export center"""
        if self.window:
            self.window.destroy()

def add_enhanced_fnb_export_features(fnb_workflow):
    """Add enhanced export features to FNB workflow"""
    
    # Create enhanced export system
    fnb_workflow.enhanced_export = EnhancedFNBExportSystem(fnb_workflow)
    
    # Replace the existing export method
    def enhanced_export_results():
        fnb_workflow.enhanced_export.show_enhanced_export_center()
    
    # Add to FNB workflow
    fnb_workflow.export_results_popup_enhanced = enhanced_export_results
    
    print("✅ Enhanced FNB export features added successfully!")
    
    return True
