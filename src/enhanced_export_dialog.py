"""
Enhanced Export Dialog with Collaboration Post Feature
====================================================
Professional export dialog with collaboration posting capabilities
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import pandas as pd
from datetime import datetime
import os

class EnhancedExportDialog:
    """Enhanced export dialog with collaboration posting"""
    
    def __init__(self, parent, workflow_type, results_data, collab_mgr=None):
        self.parent = parent
        self.workflow_type = workflow_type
        self.results_data = results_data
        self.collab_mgr = collab_mgr
        self.window = None
        
    def show(self):
        """Show the enhanced export dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"📤 Export & Post {self.workflow_type} Results")
        self.window.geometry("800x600")
        self.window.configure(bg="#f8fafc")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Header
        header_frame = tk.Frame(self.window, bg="#1e40af", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=f"📤 Export & Post {self.workflow_type} Results", 
                              font=("Segoe UI", 16, "bold"), bg="#1e40af", fg="white")
        title_label.pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.window, bg="#f8fafc")
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Data summary
        self.create_data_summary(main_frame)
        
        # Export options
        self.create_export_section(main_frame)
        
        # Collaboration section
        if self.collab_mgr:
            self.create_collaboration_section(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_data_summary(self, parent):
        """Create data summary section"""
        summary_frame = tk.LabelFrame(parent, text="📊 Data Summary", font=("Segoe UI", 12, "bold"), 
                                     bg="#ffffff", fg="#1f2937", relief="raised", bd=2)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        inner_frame = tk.Frame(summary_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Calculate summary statistics
        if isinstance(self.results_data, pd.DataFrame) and not self.results_data.empty:
            total_records = len(self.results_data)
            
            # Try to find amount-related columns
            amount_cols = [col for col in self.results_data.columns if 'amount' in col.lower() or 'value' in col.lower()]
            if amount_cols:
                total_amount = self.results_data[amount_cols[0]].sum() if pd.api.types.is_numeric_dtype(self.results_data[amount_cols[0]]) else 0
            else:
                total_amount = 0
                
            # Summary info
            info_text = f"Workflow Type: {self.workflow_type}\\n"
            info_text += f"Total Records: {total_records:,}\\n"
            if total_amount:
                info_text += f"Total Amount: {total_amount:,.2f}\\n"
            info_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        else:
            info_text = f"Workflow Type: {self.workflow_type}\\nNo data available"
        
        info_label = tk.Label(inner_frame, text=info_text, font=("Segoe UI", 11), 
                             bg="#ffffff", fg="#374151", justify='left')
        info_label.pack(anchor='w')
    
    def create_export_section(self, parent):
        """Create export options section"""
        export_frame = tk.LabelFrame(parent, text="💾 Export Options", font=("Segoe UI", 12, "bold"), 
                                    bg="#ffffff", fg="#1f2937", relief="raised", bd=2)
        export_frame.pack(fill='x', pady=(0, 20))
        
        inner_frame = tk.Frame(export_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Export format selection
        format_frame = tk.Frame(inner_frame, bg="#ffffff")
        format_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(format_frame, text="Export Format:", font=("Segoe UI", 11, "bold"), 
                bg="#ffffff").pack(side='left')
        
        self.export_format = tk.StringVar(value="xlsx")
        xlsx_radio = tk.Radiobutton(format_frame, text="Excel (.xlsx)", variable=self.export_format, 
                                   value="xlsx", font=("Segoe UI", 10), bg="#ffffff")
        xlsx_radio.pack(side='left', padx=(20, 10))
        
        csv_radio = tk.Radiobutton(format_frame, text="CSV (.csv)", variable=self.export_format, 
                                  value="csv", font=("Segoe UI", 10), bg="#ffffff")
        csv_radio.pack(side='left')
        
        # Export buttons
        btn_frame = tk.Frame(inner_frame, bg="#ffffff")
        btn_frame.pack(fill='x', pady=(10, 0))
        
        export_btn = tk.Button(btn_frame, text="📁 Export to File", font=("Segoe UI", 11, "bold"), 
                              bg="#059669", fg="white", padx=20, pady=8, 
                              command=self.export_to_file)
        export_btn.pack(side='left', padx=(0, 10))
        
        quick_export_btn = tk.Button(btn_frame, text="⚡ Quick Export", font=("Segoe UI", 11), 
                                    bg="#0891b2", fg="white", padx=20, pady=8, 
                                    command=self.quick_export)
        quick_export_btn.pack(side='left')
    
    def create_collaboration_section(self, parent):
        """Create collaboration posting section"""
        collab_frame = tk.LabelFrame(parent, text="🤝 Collaboration Posting", font=("Segoe UI", 12, "bold"), 
                                    bg="#ffffff", fg="#1f2937", relief="raised", bd=2)
        collab_frame.pack(fill='x', pady=(0, 20))
        
        inner_frame = tk.Frame(collab_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Session selection
        session_frame = tk.Frame(inner_frame, bg="#ffffff")
        session_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(session_frame, text="Collaboration Session:", font=("Segoe UI", 11, "bold"), 
                bg="#ffffff").pack(anchor='w')
        
        # Get active sessions
        sessions = self.collab_mgr.get_active_sessions()
        session_options = [f"{s['session_name']} ({s['session_id'][:8]}...)" for s in sessions]
        
        if not session_options:
            session_options = ["No active sessions"]
        
        self.session_combo = ttk.Combobox(session_frame, values=session_options, 
                                         state='readonly', width=50, font=("Segoe UI", 10))
        self.session_combo.pack(anchor='w', pady=(5, 0))
        
        if session_options and "No active sessions" not in session_options[0]:
            self.session_combo.set(session_options[0])
        
        # Result name and notes
        name_frame = tk.Frame(inner_frame, bg="#ffffff")
        name_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(name_frame, text="Result Name:", font=("Segoe UI", 11, "bold"), 
                bg="#ffffff").pack(anchor='w')
        
        self.result_name_var = tk.StringVar(value=f"{self.workflow_type}_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        result_name_entry = tk.Entry(name_frame, textvariable=self.result_name_var, 
                                   font=("Segoe UI", 10), width=50)
        result_name_entry.pack(anchor='w', pady=(5, 0))
        
        notes_frame = tk.Frame(inner_frame, bg="#ffffff")
        notes_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(notes_frame, text="Notes (optional):", font=("Segoe UI", 11, "bold"), 
                bg="#ffffff").pack(anchor='w')
        
        self.notes_text = tk.Text(notes_frame, height=3, font=("Segoe UI", 10), width=60)
        self.notes_text.pack(anchor='w', pady=(5, 0))
        
        # Post buttons
        post_btn_frame = tk.Frame(inner_frame, bg="#ffffff")
        post_btn_frame.pack(fill='x', pady=(15, 0))
        
        post_btn = tk.Button(post_btn_frame, text="🚀 Post to Collaboration", font=("Segoe UI", 11, "bold"), 
                            bg="#7c3aed", fg="white", padx=20, pady=8, 
                            command=self.post_to_collaboration)
        post_btn.pack(side='left', padx=(0, 10))
        
        create_session_btn = tk.Button(post_btn_frame, text="➕ New Session", font=("Segoe UI", 10), 
                                      bg="#f59e0b", fg="white", padx=15, pady=8, 
                                      command=self.create_new_session)
        create_session_btn.pack(side='left')
    
    def create_buttons(self, parent):
        """Create dialog buttons"""
        btn_frame = tk.Frame(parent, bg="#f8fafc")
        btn_frame.pack(fill='x', pady=(20, 0))
        
        close_btn = tk.Button(btn_frame, text="✖️ Close", font=("Segoe UI", 11), 
                             bg="#6b7280", fg="white", padx=20, pady=8, 
                             command=self.close_dialog)
        close_btn.pack(side='right')
    
    def export_to_file(self):
        """Export results to a selected file"""
        if not isinstance(self.results_data, pd.DataFrame) or self.results_data.empty:
            messagebox.showwarning("No Data", "No results data to export", parent=self.window)
            return
        
        # Get file path
        format_ext = self.export_format.get()
        if format_ext == "xlsx":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            default_ext = ".xlsx"
        else:
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        
        filename = f"{self.workflow_type}_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"
        file_path = filedialog.asksaveasfilename(
            title=f"Export {self.workflow_type} Results",
            defaultextension=default_ext,
            filetypes=filetypes,
            initialvalue=filename,
            parent=self.window
        )
        
        if file_path:
            try:
                if format_ext == "xlsx":
                    self.results_data.to_excel(file_path, index=False)
                else:
                    self.results_data.to_csv(file_path, index=False)
                
                messagebox.showinfo("Export Successful", 
                                   f"Results exported successfully to:\\n{file_path}", 
                                   parent=self.window)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\\n{str(e)}", 
                                   parent=self.window)
    
    def quick_export(self):
        """Quick export to desktop"""
        if not isinstance(self.results_data, pd.DataFrame) or self.results_data.empty:
            messagebox.showwarning("No Data", "No results data to export", parent=self.window)
            return
        
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            format_ext = self.export_format.get()
            filename = f"{self.workflow_type}_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_ext}"
            file_path = os.path.join(desktop, filename)
            
            if format_ext == "xlsx":
                self.results_data.to_excel(file_path, index=False)
            else:
                self.results_data.to_csv(file_path, index=False)
            
            messagebox.showinfo("Quick Export Successful", 
                               f"Results exported to desktop:\\n{filename}", 
                               parent=self.window)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\\n{str(e)}", 
                               parent=self.window)
    
    def post_to_collaboration(self):
        """Post results to collaboration session"""
        if not self.collab_mgr:
            messagebox.showwarning("Not Available", "Collaboration features not available", 
                                 parent=self.window)
            return
        
        if not isinstance(self.results_data, pd.DataFrame) or self.results_data.empty:
            messagebox.showwarning("No Data", "No results data to post", parent=self.window)
            return
        
        # Get selected session
        session_selection = self.session_combo.get()
        if not session_selection or "No active sessions" in session_selection:
            messagebox.showwarning("No Session", "Please select a collaboration session", 
                                 parent=self.window)
            return
        
        # Extract session ID from selection
        session_id = session_selection.split('(')[1].split(')')[0].replace('...', '')
        
        # Find the full session ID
        sessions = self.collab_mgr.get_active_sessions()
        full_session_id = None
        for session in sessions:
            if session['session_id'].startswith(session_id):
                full_session_id = session['session_id']
                break
        
        if not full_session_id:
            messagebox.showerror("Session Error", "Could not find the selected session", 
                               parent=self.window)
            return
        
        # Get result details
        result_name = self.result_name_var.get().strip()
        notes = self.notes_text.get(1.0, tk.END).strip()
        export_format = self.export_format.get()
        
        if not result_name:
            messagebox.showwarning("Missing Name", "Please enter a result name", parent=self.window)
            return
        
        try:
            # Post to collaboration
            post_id = self.collab_mgr.post_workflow_results(
                session_id=full_session_id,
                workflow_type=self.workflow_type,
                result_data=self.results_data,
                posted_by="Current User",
                result_name=result_name,
                notes=notes,
                export_format=export_format
            )
            
            if post_id:
                messagebox.showinfo("Posted Successfully", 
                                   f"Results posted to collaboration!\\n\\nPost ID: {post_id}\\nSession: {session_selection}", 
                                   parent=self.window)
            else:
                messagebox.showerror("Post Failed", "Failed to post results to collaboration", 
                                   parent=self.window)
                
        except Exception as e:
            messagebox.showerror("Post Error", f"Failed to post results:\\n{str(e)}", 
                               parent=self.window)
    
    def create_new_session(self):
        """Create a new collaboration session"""
        if not self.collab_mgr:
            messagebox.showwarning("Not Available", "Collaboration features not available", 
                                 parent=self.window)
            return
        
        session_name = simpledialog.askstring("New Session", 
                                             "Enter session name for this reconciliation batch:",
                                             parent=self.window)
        if session_name:
            description = simpledialog.askstring("Session Description", 
                                                "Enter description (optional):",
                                                parent=self.window) or ""
            
            session_id = self.collab_mgr.create_session(session_name, "Current User", description)
            if session_id:
                messagebox.showinfo("Session Created", 
                                   f"Session '{session_name}' created successfully!\\n\\nSession ID: {session_id}", 
                                   parent=self.window)
                
                # Refresh session list
                sessions = self.collab_mgr.get_active_sessions()
                session_options = [f"{s['session_name']} ({s['session_id'][:8]}...)" for s in sessions]
                self.session_combo.config(values=session_options)
                
                # Select the new session
                for option in session_options:
                    if session_id[:8] in option:
                        self.session_combo.set(option)
                        break
            else:
                messagebox.showerror("Error", "Failed to create session", parent=self.window)
    
    def close_dialog(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
