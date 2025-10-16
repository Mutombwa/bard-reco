"""
Enhanced FNB Workflow with Outstanding Transactions Management
================================================================
Complete integration adding outstanding transactions management to export page
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import pandas as pd
from datetime import datetime
import os

# Import the outstanding transactions manager
from outstanding_transactions_manager import (
    OutstandingTransactionsDB, 
    OutstandingTransactionsViewer
)


def add_outstanding_transactions_to_export(workflow_instance):
    """
    Add Outstanding Transactions Management to Export Page
    This modifies the _export_results method to include outstanding transactions features
    """
    
    # Initialize outstanding transactions database
    db_path = os.path.join(os.path.dirname(__file__), "outstanding_transactions.db")
    workflow_instance.outstanding_db = OutstandingTransactionsDB(db_path)
    
    # Store for pending outstanding transactions to be added to next import
    workflow_instance.pending_ledger_outstanding = []
    workflow_instance.pending_statement_outstanding = []
    
    # Store original _export_results if it exists
    original_export = getattr(workflow_instance, '_export_results', None)
    
    def enhanced_export_results():
        """Enhanced export results with Outstanding Transactions Management"""
        
        # Create export window
        export_window = tk.Toplevel(workflow_instance.parent if hasattr(workflow_instance, 'parent') else workflow_instance)
        export_window.title("📤 Export Results & Outstanding Transactions")
        
        # Set window to maximized but not fullscreen (keeps taskbar visible)
        export_window.state('zoomed')
        export_window.minsize(1200, 800)
        export_window.configure(bg="#f8fafc")
        
        # Make it modal
        export_window.transient(workflow_instance.parent if hasattr(workflow_instance, 'parent') else workflow_instance)
        export_window.grab_set()
        
        # Header
        header_frame = tk.Frame(export_window, bg="#1e40af", height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#1e40af")
        header_content.pack(expand=True, fill='both', padx=30, pady=20)
        
        title_label = tk.Label(header_content, 
                              text="📤 EXPORT RESULTS & OUTSTANDING TRANSACTIONS", 
                              font=("Segoe UI", 22, "bold"), bg="#1e40af", fg="white")
        title_label.pack(side="left")
        
        subtitle = tk.Label(header_content, 
                          text="Manage Export, Outstanding Ledger & Statement Transactions", 
                          font=("Segoe UI", 13), bg="#1e40af", fg="#bfdbfe")
        subtitle.pack(side="left", padx=(30, 0))
        
        close_btn = tk.Button(header_content, text="✖ Close", font=("Segoe UI", 12, "bold"), 
                             bg="#dc2626", fg="white", padx=25, pady=10, 
                             command=export_window.destroy, cursor="hand2")
        close_btn.pack(side="right")
        
        # Create main content with three sections
        main_content = tk.Frame(export_window, bg="#f8fafc")
        main_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section 1: Export Options
        create_export_section(main_content, workflow_instance)
        
        # Section 2: Outstanding Ledger Transactions
        create_outstanding_ledger_section(main_content, workflow_instance)
        
        # Section 3: Outstanding Statement Transactions
        create_outstanding_statement_section(main_content, workflow_instance)
        
        # Save outstanding transactions after reconciliation (if results exist)
        if hasattr(workflow_instance, 'reconciliation_results') and workflow_instance.reconciliation_results:
            save_current_outstanding_transactions(workflow_instance)
    
    def create_export_section(parent, workflow_instance):
        """Create the export options section"""
        export_frame = tk.LabelFrame(parent, text="📤 EXPORT CURRENT RESULTS", 
                                    font=("Segoe UI", 14, "bold"), bg="#ffffff", 
                                    fg="#1f2937", relief="raised", bd=2)
        export_frame.pack(fill='x', pady=(0, 15))
        
        inner_frame = tk.Frame(export_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=30, pady=20)
        
        # Check if we have reconciliation results
        has_results = (hasattr(workflow_instance, 'reconciliation_results') and 
                      workflow_instance.reconciliation_results is not None)
        
        if has_results:
            # Show results summary
            results = workflow_instance.reconciliation_results
            matched = results.get('matched', [])
            unmatched_ledger = results.get('unmatched_ledger', None)
            unmatched_statement = results.get('unmatched_statement', None)
            foreign_credits = results.get('foreign_credits', [])
            
            summary_text = f"""
            ✅ Matched Transactions: {len(matched)}
            ❌ Unmatched Ledger: {len(unmatched_ledger) if unmatched_ledger is not None else 0}
            ❌ Unmatched Statement: {len(unmatched_statement) if unmatched_statement is not None else 0}
            🌍 Foreign Credits: {len(foreign_credits)}
            """
            
            summary_label = tk.Label(inner_frame, text=summary_text, 
                                   font=("Segoe UI", 11), bg="#ffffff", fg="#374151", justify='left')
            summary_label.pack(anchor='w', pady=(0, 15))
            
            # Export buttons
            button_frame = tk.Frame(inner_frame, bg="#ffffff")
            button_frame.pack(fill='x')
            
            tk.Button(button_frame, text="📊 Export to Excel", font=("Segoe UI", 12, "bold"), 
                     bg="#059669", fg="white", padx=30, pady=12, 
                     command=lambda: export_results_to_file(workflow_instance, "excel")).pack(side='left', padx=(0, 15))
            
            tk.Button(button_frame, text="📄 Export to CSV", font=("Segoe UI", 12, "bold"), 
                     bg="#3b82f6", fg="white", padx=30, pady=12, 
                     command=lambda: export_results_to_file(workflow_instance, "csv")).pack(side='left', padx=(0, 15))
            
            tk.Button(button_frame, text="⚡ Quick Export (Desktop)", font=("Segoe UI", 12, "bold"), 
                     bg="#0891b2", fg="white", padx=30, pady=12, 
                     command=lambda: quick_export_desktop(workflow_instance)).pack(side='left')
        else:
            # No results yet - show informative message instead of error
            info_frame = tk.Frame(inner_frame, bg="#fef3c7", relief="solid", bd=2)
            info_frame.pack(fill='x', pady=10)
            
            info_content = tk.Frame(info_frame, bg="#fef3c7")
            info_content.pack(fill='x', padx=20, pady=15)
            
            icon_label = tk.Label(info_content, text="ℹ️", font=("Segoe UI", 24), bg="#fef3c7")
            icon_label.pack(side='left', padx=(0, 15))
            
            message_text = """No reconciliation results yet.
            
You can still manage Outstanding Transactions below, or run reconciliation first to export results."""
            
            message_label = tk.Label(info_content, text=message_text, 
                                   font=("Segoe UI", 11), bg="#fef3c7", fg="#92400e", justify='left')
            message_label.pack(side='left', anchor='w')
    
    def create_outstanding_ledger_section(parent, workflow_instance):
        """Create the outstanding ledger transactions section"""
        ledger_frame = tk.LabelFrame(parent, text="📊 OUTSTANDING LEDGER TRANSACTIONS", 
                                    font=("Segoe UI", 14, "bold"), bg="#ffffff", 
                                    fg="#1f2937", relief="raised", bd=2)
        ledger_frame.pack(fill='x', pady=(0, 15))
        
        inner_frame = tk.Frame(ledger_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=30, pady=20)
        
        # Description
        desc_label = tk.Label(inner_frame, 
                            text="View, edit, delete, and copy outstanding ledger transactions from previous reconciliations", 
                            font=("Segoe UI", 11), bg="#ffffff", fg="#6b7280")
        desc_label.pack(anchor='w', pady=(0, 15))
        
        # Statistics
        ledger_count = len(workflow_instance.outstanding_db.get_all_ledger_outstanding())
        stats_text = f"💼 Total Outstanding Ledger Transactions: {ledger_count}"
        
        stats_label = tk.Label(inner_frame, text=stats_text, 
                             font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#059669")
        stats_label.pack(anchor='w', pady=(0, 15))
        
        # Action buttons
        button_frame = tk.Frame(inner_frame, bg="#ffffff")
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text="👁️ View Ledger Outstanding", font=("Segoe UI", 11, "bold"), 
                 bg="#7c3aed", fg="white", padx=25, pady=10, 
                 command=lambda: show_ledger_outstanding_viewer(workflow_instance)).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="📋 Copy to New Ledger", font=("Segoe UI", 11, "bold"), 
                 bg="#10b981", fg="white", padx=25, pady=10, 
                 command=lambda: copy_ledger_to_current(workflow_instance)).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="💾 Export Ledger Outstanding", font=("Segoe UI", 11), 
                 bg="#3b82f6", fg="white", padx=25, pady=10, 
                 command=lambda: export_ledger_outstanding(workflow_instance)).pack(side='left')
    
    def create_outstanding_statement_section(parent, workflow_instance):
        """Create the outstanding statement transactions section"""
        statement_frame = tk.LabelFrame(parent, text="🏦 OUTSTANDING STATEMENT TRANSACTIONS", 
                                       font=("Segoe UI", 14, "bold"), bg="#ffffff", 
                                       fg="#1f2937", relief="raised", bd=2)
        statement_frame.pack(fill='x', pady=(0, 15))
        
        inner_frame = tk.Frame(statement_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=30, pady=20)
        
        # Description
        desc_label = tk.Label(inner_frame, 
                            text="View, edit, delete, and copy outstanding statement transactions from previous reconciliations", 
                            font=("Segoe UI", 11), bg="#ffffff", fg="#6b7280")
        desc_label.pack(anchor='w', pady=(0, 15))
        
        # Statistics
        statement_count = len(workflow_instance.outstanding_db.get_all_statement_outstanding())
        stats_text = f"🏦 Total Outstanding Statement Transactions: {statement_count}"
        
        stats_label = tk.Label(inner_frame, text=stats_text, 
                             font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#3b82f6")
        stats_label.pack(anchor='w', pady=(0, 15))
        
        # Action buttons
        button_frame = tk.Frame(inner_frame, bg="#ffffff")
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text="👁️ View Statement Outstanding", font=("Segoe UI", 11, "bold"), 
                 bg="#7c3aed", fg="white", padx=25, pady=10, 
                 command=lambda: show_statement_outstanding_viewer(workflow_instance)).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="📋 Copy to New Statement", font=("Segoe UI", 11, "bold"), 
                 bg="#10b981", fg="white", padx=25, pady=10, 
                 command=lambda: copy_statement_to_current(workflow_instance)).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="💾 Export Statement Outstanding", font=("Segoe UI", 11), 
                 bg="#3b82f6", fg="white", padx=25, pady=10, 
                 command=lambda: export_statement_outstanding(workflow_instance)).pack(side='left')
    
    def save_current_outstanding_transactions(workflow_instance):
        """Save current reconciliation's unmatched transactions as outstanding"""
        if not hasattr(workflow_instance, 'reconciliation_results') or not workflow_instance.reconciliation_results:
            return
        
        results = workflow_instance.reconciliation_results
        recon_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        recon_name = f"Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save unmatched ledger
        unmatched_ledger = results.get('unmatched_ledger', None)
        if unmatched_ledger is not None and not unmatched_ledger.empty:
            count = workflow_instance.outstanding_db.save_ledger_outstanding(
                recon_date, recon_name, unmatched_ledger
            )
            print(f"✅ Saved {count} ledger outstanding transactions")
        
        # Save unmatched statement
        unmatched_statement = results.get('unmatched_statement', None)
        if unmatched_statement is not None and not unmatched_statement.empty:
            count = workflow_instance.outstanding_db.save_statement_outstanding(
                recon_date, recon_name, unmatched_statement
            )
            print(f"✅ Saved {count} statement outstanding transactions")
    
    def export_results_to_file(workflow_instance, format_type):
        """Export reconciliation results to file"""
        if not hasattr(workflow_instance, 'reconciliation_results') or not workflow_instance.reconciliation_results:
            messagebox.showwarning("No Results", "No reconciliation results to export.")
            return
        
        # Determine file extension and filter
        if format_type == "excel":
            ext = ".xlsx"
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        else:
            ext = ".csv"
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        
        # Get file path
        filename = f"FNB_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        file_path = filedialog.asksaveasfilename(
            title="Export Reconciliation Results",
            defaultextension=ext,
            filetypes=filetypes,
            initialfile=filename
        )
        
        if file_path:
            try:
                # Prepare export data
                results = workflow_instance.reconciliation_results
                
                if format_type == "excel":
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        # Export each result sheet
                        if 'matched' in results and len(results['matched']) > 0:
                            matched_df = pd.DataFrame(results['matched'])
                            matched_df.to_excel(writer, sheet_name='Matched', index=False)
                        
                        if 'unmatched_ledger' in results and results['unmatched_ledger'] is not None:
                            results['unmatched_ledger'].to_excel(writer, sheet_name='Unmatched_Ledger', index=False)
                        
                        if 'unmatched_statement' in results and results['unmatched_statement'] is not None:
                            results['unmatched_statement'].to_excel(writer, sheet_name='Unmatched_Statement', index=False)
                        
                        if 'foreign_credits' in results and len(results['foreign_credits']) > 0:
                            fc_df = pd.DataFrame(results['foreign_credits'])
                            fc_df.to_excel(writer, sheet_name='Foreign_Credits', index=False)
                else:
                    # CSV export - combine all results
                    all_data = []
                    
                    if 'matched' in results:
                        for match in results['matched']:
                            all_data.append({"Type": "Matched", **match})
                    
                    combined_df = pd.DataFrame(all_data)
                    combined_df.to_csv(file_path, index=False)
                
                messagebox.showinfo("Export Success", 
                                  f"✅ Results exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def quick_export_desktop(workflow_instance):
        """Quick export to desktop"""
        if not hasattr(workflow_instance, 'reconciliation_results') or not workflow_instance.reconciliation_results:
            messagebox.showwarning("No Results", "No reconciliation results to export.")
            return
        
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            filename = f"FNB_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = os.path.join(desktop, filename)
            
            # Export to Excel
            results = workflow_instance.reconciliation_results
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                if 'matched' in results and len(results['matched']) > 0:
                    matched_df = pd.DataFrame(results['matched'])
                    matched_df.to_excel(writer, sheet_name='Matched', index=False)
                
                if 'unmatched_ledger' in results and results['unmatched_ledger'] is not None:
                    results['unmatched_ledger'].to_excel(writer, sheet_name='Unmatched_Ledger', index=False)
                
                if 'unmatched_statement' in results and results['unmatched_statement'] is not None:
                    results['unmatched_statement'].to_excel(writer, sheet_name='Unmatched_Statement', index=False)
            
            messagebox.showinfo("Quick Export Success", 
                              f"✅ Results exported to desktop:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    def show_ledger_outstanding_viewer(workflow_instance):
        """Show the ledger outstanding transactions viewer"""
        def on_copy(transactions_data, trans_type):
            workflow_instance.pending_ledger_outstanding = transactions_data
            messagebox.showinfo("Copy Ready", 
                              f"✅ {len(transactions_data)} transactions ready to copy.\n\n"
                              "Import a new ledger file, and these transactions will be automatically added.")
        
        OutstandingTransactionsViewer(
            workflow_instance.parent if hasattr(workflow_instance, 'parent') else workflow_instance,
            "ledger",
            workflow_instance.outstanding_db,
            on_copy
        )
    
    def show_statement_outstanding_viewer(workflow_instance):
        """Show the statement outstanding transactions viewer"""
        def on_copy(transactions_data, trans_type):
            workflow_instance.pending_statement_outstanding = transactions_data
            messagebox.showinfo("Copy Ready", 
                              f"✅ {len(transactions_data)} transactions ready to copy.\n\n"
                              "Import a new statement file, and these transactions will be automatically added.")
        
        OutstandingTransactionsViewer(
            workflow_instance.parent if hasattr(workflow_instance, 'parent') else workflow_instance,
            "statement",
            workflow_instance.outstanding_db,
            on_copy
        )
    
    def copy_ledger_to_current(workflow_instance):
        """Copy all ledger outstanding to current/next import"""
        df = workflow_instance.outstanding_db.get_ledger_transactions_as_dataframe()
        
        if df.empty:
            messagebox.showinfo("No Transactions", "No outstanding ledger transactions to copy.")
            return
        
        # Store for next import
        workflow_instance.pending_ledger_outstanding = df.to_dict('records')
        
        messagebox.showinfo("Copy Ready", 
                          f"✅ {len(df)} ledger transactions ready to copy.\n\n"
                          "Import a new ledger file, and these transactions will be automatically added.")
    
    def copy_statement_to_current(workflow_instance):
        """Copy all statement outstanding to current/next import"""
        df = workflow_instance.outstanding_db.get_statement_transactions_as_dataframe()
        
        if df.empty:
            messagebox.showinfo("No Transactions", "No outstanding statement transactions to copy.")
            return
        
        # Store for next import
        workflow_instance.pending_statement_outstanding = df.to_dict('records')
        
        messagebox.showinfo("Copy Ready", 
                          f"✅ {len(df)} statement transactions ready to copy.\n\n"
                          "Import a new statement file, and these transactions will be automatically added.")
    
    def export_ledger_outstanding(workflow_instance):
        """Export ledger outstanding transactions"""
        df = workflow_instance.outstanding_db.get_ledger_transactions_as_dataframe()
        
        if df.empty:
            messagebox.showinfo("No Data", "No outstanding ledger transactions to export.")
            return
        
        filename = f"Outstanding_Ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            title="Export Outstanding Ledger Transactions",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Export Success", 
                                  f"✅ Outstanding ledger transactions exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    def export_statement_outstanding(workflow_instance):
        """Export statement outstanding transactions"""
        df = workflow_instance.outstanding_db.get_statement_transactions_as_dataframe()
        
        if df.empty:
            messagebox.showinfo("No Data", "No outstanding statement transactions to export.")
            return
        
        filename = f"Outstanding_Statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            title="Export Outstanding Statement Transactions",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Export Success", 
                                  f"✅ Outstanding statement transactions exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    # Replace the _export_results method
    workflow_instance._export_results = enhanced_export_results
    
    # Also update the export button to always be enabled (remove the check for reconciliation results)
    if hasattr(workflow_instance, 'export_btn'):
        workflow_instance.export_btn.config(state="normal")
    
    print("✅ Outstanding Transactions feature integrated successfully!")
    
    return True
