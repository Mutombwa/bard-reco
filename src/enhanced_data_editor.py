# Enhanced Data Viewer/Editor with Excel Paste & Advanced Features
#
# This module provides comprehensive data manipulation capabilities including:
# - Excel copy/paste support
# - Bulk operations
# - Advanced filtering
# - Data validation
# - Undo/Redo
# - Professional UI

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import re


# ============================================================================
# Advanced Dialog Classes for Filter, Sort, and Find/Replace
# ============================================================================

class FilterDialog(tk.Toplevel):
    """Advanced filtering dialog with multiple conditions"""
    
    def __init__(self, parent, df, callback):
        super().__init__(parent)
        self.parent = parent
        self.df = df
        self.callback = callback
        
        self.title("Advanced Filter")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        
        self.filter_conditions = []
        self.create_ui()
    
    def create_ui(self):
        """Create filter UI"""
        # Header
        header = tk.Frame(self, bg="#3498db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🔍 Advanced Filter", font=("Segoe UI", 16, "bold"),
                bg="#3498db", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        tk.Label(content, text="Add filter conditions to narrow down your data:",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(0, 10))
        
        # Filters container with scrollbar
        filter_frame = tk.Frame(content, bg="white")
        filter_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        canvas = tk.Canvas(filter_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(filter_frame, orient="vertical", command=canvas.yview)
        self.filters_container = tk.Frame(canvas, bg="white")
        
        self.filters_container.bind("<Configure>", 
                                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.filters_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add first filter
        self.add_filter_row()
        
        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(btn_frame, text="+ Add Condition", command=self.add_filter_row,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="🔍 Apply Filter", command=self.apply_filter,
                 font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white",
                 relief="flat", padx=20, pady=8, cursor="hand2").pack(side="right", padx=5)
        
        tk.Button(btn_frame, text="Clear All", command=self.clear_filters,
                 font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="right", padx=5)
    
    def add_filter_row(self):
        """Add a filter condition row"""
        row_frame = tk.Frame(self.filters_container, bg="#ecf0f1", relief="solid", bd=1)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        # Column selection
        tk.Label(row_frame, text="Column:", bg="#ecf0f1", font=("Segoe UI", 9)).grid(
            row=0, column=0, padx=5, pady=10, sticky="w")
        
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(row_frame, textvariable=col_var, 
                                values=list(self.df.columns), width=20, state='readonly')
        col_combo.grid(row=0, column=1, padx=5, pady=10)
        
        # Operator selection
        tk.Label(row_frame, text="Operator:", bg="#ecf0f1", font=("Segoe UI", 9)).grid(
            row=0, column=2, padx=5, pady=10, sticky="w")
        
        op_var = tk.StringVar()
        op_combo = ttk.Combobox(row_frame, textvariable=op_var,
                               values=["Contains", "Equals", "Not Equals", "Starts With", 
                                      "Ends With", "Greater Than", "Less Than", "Is Empty", "Not Empty"],
                               width=15, state='readonly')
        op_combo.grid(row=0, column=3, padx=5, pady=10)
        op_combo.set("Contains")
        
        # Value entry
        tk.Label(row_frame, text="Value:", bg="#ecf0f1", font=("Segoe UI", 9)).grid(
            row=0, column=4, padx=5, pady=10, sticky="w")
        
        value_entry = tk.Entry(row_frame, font=("Segoe UI", 10), width=20)
        value_entry.grid(row=0, column=5, padx=5, pady=10)
        
        # Remove button
        tk.Button(row_frame, text="✖", command=lambda: self.remove_filter_row(row_frame),
                 bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=8, pady=4, cursor="hand2").grid(
                     row=0, column=6, padx=5, pady=10)
        
        self.filter_conditions.append({
            'frame': row_frame,
            'column': col_var,
            'operator': op_var,
            'value': value_entry
        })
    
    def remove_filter_row(self, frame):
        """Remove a filter row"""
        for i, condition in enumerate(self.filter_conditions):
            if condition['frame'] == frame:
                frame.destroy()
                self.filter_conditions.pop(i)
                break
    
    def apply_filter(self):
        """Apply the filter conditions"""
        if not self.filter_conditions:
            messagebox.showwarning("No Filters", "Add at least one filter condition", parent=self)
            return
        
        try:
            filtered_df = self.df.copy()
            
            for condition in self.filter_conditions:
                col = condition['column'].get()
                op = condition['operator'].get()
                val = condition['value'].get().strip()
                
                if not col:
                    continue
                
                # Apply operator
                if op == "Contains":
                    if val:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]
                
                elif op == "Equals":
                    if val:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.lower() == val.lower()]
                
                elif op == "Not Equals":
                    if val:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.lower() != val.lower()]
                
                elif op == "Starts With":
                    if val:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.startswith(val, na=False)]
                
                elif op == "Ends With":
                    if val:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.endswith(val, na=False)]
                
                elif op == "Greater Than":
                    if val:
                        try:
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > float(val)]
                        except ValueError:
                            pass
                
                elif op == "Less Than":
                    if val:
                        try:
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') < float(val)]
                        except ValueError:
                            pass
                
                elif op == "Is Empty":
                    filtered_df = filtered_df[filtered_df[col].isna() | (filtered_df[col].astype(str).str.strip() == '')]
                
                elif op == "Not Empty":
                    filtered_df = filtered_df[filtered_df[col].notna() & (filtered_df[col].astype(str).str.strip() != '')]
            
            # Apply to parent
            self.callback(filtered_df)
            messagebox.showinfo("Filter Applied", 
                              f"✓ Filter applied successfully!\n\n"
                              f"Rows before: {len(self.df)}\n"
                              f"Rows after: {len(filtered_df)}",
                              parent=self)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to apply filter:\n{e}", parent=self)
    
    def clear_filters(self):
        """Clear all filters and restore original data"""
        self.callback(self.df)
        messagebox.showinfo("Filters Cleared", "All filters removed. Original data restored.", parent=self)
        self.destroy()


class SortDialog(tk.Toplevel):
    """Advanced sorting dialog with multi-column support"""
    
    def __init__(self, parent, df, callback):
        super().__init__(parent)
        self.parent = parent
        self.df = df
        self.callback = callback
        
        self.title("Advanced Sort")
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        
        self.sort_rules = []
        self.create_ui()
    
    def create_ui(self):
        """Create sort UI"""
        # Header
        header = tk.Frame(self, bg="#e67e22", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="↕️ Advanced Sort", font=("Segoe UI", 16, "bold"),
                bg="#e67e22", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        tk.Label(content, text="Define sort order (first rule has highest priority):",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(0, 10))
        
        # Sort rules container
        sort_frame = tk.Frame(content, bg="white")
        sort_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        canvas = tk.Canvas(sort_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sort_frame, orient="vertical", command=canvas.yview)
        self.rules_container = tk.Frame(canvas, bg="white")
        
        self.rules_container.bind("<Configure>", 
                                 lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.rules_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add first sort rule
        self.add_sort_rule()
        
        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(btn_frame, text="+ Add Sort Level", command=self.add_sort_rule,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="↕️ Apply Sort", command=self.apply_sort,
                 font=("Segoe UI", 10, "bold"), bg="#e67e22", fg="white",
                 relief="flat", padx=20, pady=8, cursor="hand2").pack(side="right", padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=self.destroy,
                 font=("Segoe UI", 10, "bold"), bg="#95a5a6", fg="white",
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="right", padx=5)
    
    def add_sort_rule(self):
        """Add a sort rule row"""
        row_frame = tk.Frame(self.rules_container, bg="#ecf0f1", relief="solid", bd=1)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        # Priority label
        tk.Label(row_frame, text=f"Level {len(self.sort_rules) + 1}:", 
                bg="#ecf0f1", font=("Segoe UI", 10, "bold")).grid(
                    row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Column selection
        tk.Label(row_frame, text="Column:", bg="#ecf0f1", font=("Segoe UI", 9)).grid(
            row=0, column=1, padx=5, pady=10, sticky="w")
        
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(row_frame, textvariable=col_var,
                                values=list(self.df.columns), width=25, state='readonly')
        col_combo.grid(row=0, column=2, padx=5, pady=10)
        
        # Order selection
        tk.Label(row_frame, text="Order:", bg="#ecf0f1", font=("Segoe UI", 9)).grid(
            row=0, column=3, padx=5, pady=10, sticky="w")
        
        order_var = tk.StringVar(value="Ascending")
        order_combo = ttk.Combobox(row_frame, textvariable=order_var,
                                  values=["Ascending", "Descending"], width=12, state='readonly')
        order_combo.grid(row=0, column=4, padx=5, pady=10)
        
        # Remove button
        tk.Button(row_frame, text="✖", command=lambda: self.remove_sort_rule(row_frame),
                 bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=8, pady=4, cursor="hand2").grid(
                     row=0, column=5, padx=5, pady=10)
        
        self.sort_rules.append({
            'frame': row_frame,
            'column': col_var,
            'order': order_var
        })
    
    def remove_sort_rule(self, frame):
        """Remove a sort rule"""
        for i, rule in enumerate(self.sort_rules):
            if rule['frame'] == frame:
                frame.destroy()
                self.sort_rules.pop(i)
                break
        
        # Update level labels
        for i, rule in enumerate(self.sort_rules):
            label = rule['frame'].grid_slaves(row=0, column=0)[0]
            label.config(text=f"Level {i + 1}:")
    
    def apply_sort(self):
        """Apply the sort rules"""
        if not self.sort_rules:
            messagebox.showwarning("No Sort Rules", "Add at least one sort rule", parent=self)
            return
        
        try:
            columns = []
            ascending = []
            
            for rule in self.sort_rules:
                col = rule['column'].get()
                order = rule['order'].get()
                
                if col:
                    columns.append(col)
                    ascending.append(order == "Ascending")
            
            if not columns:
                messagebox.showwarning("No Columns", "Select at least one column to sort", parent=self)
                return
            
            sorted_df = self.df.sort_values(by=columns, ascending=ascending)
            
            self.callback(sorted_df)
            messagebox.showinfo("Sort Applied", 
                              f"✓ Data sorted successfully!\n\n"
                              f"Sorted by: {', '.join(columns)}",
                              parent=self)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort:\n{e}", parent=self)


class FindReplaceDialog(tk.Toplevel):
    """Find and replace dialog with regex support"""
    
    def __init__(self, parent, df, callback):
        super().__init__(parent)
        self.parent = parent
        self.df = df
        self.callback = callback
        
        self.title("Find & Replace")
        self.geometry("650x400")
        self.transient(parent)
        self.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create find/replace UI"""
        # Header
        header = tk.Frame(self, bg="#9b59b6", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🔎 Find & Replace", font=("Segoe UI", 16, "bold"),
                bg="#9b59b6", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, bg="white", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        # Column selection
        col_frame = tk.Frame(content, bg="white")
        col_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(col_frame, text="Search in column:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side="left", padx=(0, 10))
        
        self.col_var = tk.StringVar()
        col_combo = ttk.Combobox(col_frame, textvariable=self.col_var,
                                values=["All Columns"] + list(self.df.columns),
                                width=30, state='readonly')
        col_combo.pack(side="left")
        col_combo.set("All Columns")
        
        # Find field
        find_frame = tk.Frame(content, bg="white")
        find_frame.pack(fill="x", pady=10)
        
        tk.Label(find_frame, text="Find what:", font=("Segoe UI", 10, "bold"),
                bg="white", width=15, anchor="w").pack(side="left")
        
        self.find_entry = tk.Entry(find_frame, font=("Segoe UI", 11), width=40)
        self.find_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Replace field
        replace_frame = tk.Frame(content, bg="white")
        replace_frame.pack(fill="x", pady=10)
        
        tk.Label(replace_frame, text="Replace with:", font=("Segoe UI", 10, "bold"),
                bg="white", width=15, anchor="w").pack(side="left")
        
        self.replace_entry = tk.Entry(replace_frame, font=("Segoe UI", 11), width=40)
        self.replace_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Options
        options_frame = tk.Frame(content, bg="white")
        options_frame.pack(fill="x", pady=20)
        
        self.case_sensitive = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive,
                      bg="white", font=("Segoe UI", 10)).pack(side="left", padx=10)
        
        self.regex_mode = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Use regular expressions", variable=self.regex_mode,
                      bg="white", font=("Segoe UI", 10)).pack(side="left", padx=10)
        
        self.whole_word = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Match whole word", variable=self.whole_word,
                      bg="white", font=("Segoe UI", 10)).pack(side="left", padx=10)
        
        # Results label
        self.results_label = tk.Label(content, text="", font=("Segoe UI", 10),
                                     bg="white", fg="#27ae60")
        self.results_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(btn_frame, text="🔍 Find", command=self.find_text,
                 font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white",
                 relief="flat", padx=20, pady=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Replace", command=self.replace_text,
                 font=("Segoe UI", 10, "bold"), bg="#f39c12", fg="white",
                 relief="flat", padx=20, pady=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Replace All", command=self.replace_all,
                 font=("Segoe UI", 10, "bold"), bg="#e67e22", fg="white",
                 relief="flat", padx=20, pady=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Close", command=self.destroy,
                 font=("Segoe UI", 10, "bold"), bg="#95a5a6", fg="white",
                 relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right", padx=5)
    
    def find_text(self):
        """Find occurrences of text"""
        find_what = self.find_entry.get()
        if not find_what:
            messagebox.showwarning("Empty Search", "Enter text to find", parent=self)
            return
        
        try:
            column = self.col_var.get()
            count = 0
            
            if column == "All Columns":
                for col in self.df.columns:
                    count += self.count_matches(col, find_what)
            else:
                count = self.count_matches(column, find_what)
            
            self.results_label.config(
                text=f"✓ Found {count} occurrence(s)",
                fg="#27ae60" if count > 0 else "#e74c3c"
            )
            
        except Exception as e:
            messagebox.showerror("Find Error", f"Search failed:\n{e}", parent=self)
    
    def count_matches(self, column, find_what):
        """Count matches in a column"""
        try:
            col_data = self.df[column].astype(str)
            
            if self.regex_mode.get():
                flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                return col_data.str.contains(find_what, regex=True, flags=flags, na=False).sum()
            else:
                if self.case_sensitive.get():
                    return col_data.str.contains(find_what, regex=False, na=False).sum()
                else:
                    return col_data.str.lower().str.contains(find_what.lower(), regex=False, na=False).sum()
        except:
            return 0
    
    def replace_text(self):
        """Replace first occurrence"""
        messagebox.showinfo("Replace", 
                          "Replace single occurrence feature:\n\n"
                          "Use 'Replace All' to replace all occurrences.\n"
                          "Single replace coming in next update!",
                          parent=self)
    
    def replace_all(self):
        """Replace all occurrences"""
        find_what = self.find_entry.get()
        replace_with = self.replace_entry.get()
        
        if not find_what:
            messagebox.showwarning("Empty Search", "Enter text to find", parent=self)
            return
        
        if not messagebox.askyesno("Confirm Replace",
                                   f"Replace all occurrences of:\n'{find_what}'\n\n"
                                   f"With:\n'{replace_with}'",
                                   parent=self):
            return
        
        try:
            modified_df = self.df.copy()
            column = self.col_var.get()
            total_replaced = 0
            
            if column == "All Columns":
                columns_to_search = list(self.df.columns)
            else:
                columns_to_search = [column]
            
            for col in columns_to_search:
                if self.regex_mode.get():
                    flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                    modified_df[col] = modified_df[col].astype(str).str.replace(
                        find_what, replace_with, regex=True, flags=flags
                    )
                else:
                    if self.case_sensitive.get():
                        modified_df[col] = modified_df[col].astype(str).str.replace(
                            find_what, replace_with, regex=False
                        )
                    else:
                        # Case-insensitive replace
                        def case_insensitive_replace(text):
                            if pd.isna(text):
                                return text
                            pattern = re.compile(re.escape(find_what), re.IGNORECASE)
                            return pattern.sub(replace_with, str(text))
                        
                        modified_df[col] = modified_df[col].apply(case_insensitive_replace)
            
            # Count replacements
            for col in columns_to_search:
                before_count = self.count_matches(col, find_what)
                total_replaced += before_count
            
            self.callback(modified_df)
            
            messagebox.showinfo("Replace Complete",
                              f"✓ Replaced {total_replaced} occurrence(s)\n\n"
                              f"in {len(columns_to_search)} column(s)",
                              parent=self)
            
            self.results_label.config(text=f"✓ Replaced {total_replaced} occurrence(s)", fg="#27ae60")
            
        except Exception as e:
            messagebox.showerror("Replace Error", f"Replace failed:\n{e}", parent=self)


# ============================================================================
# Main Enhanced Data Editor Class
# ============================================================================

class EnhancedDataEditor(tk.Toplevel):
    """
    Professional Excel-like data editor with paste support and advanced features
    """
    
    def __init__(self, parent, df, title="Data Viewer", data_type="ledger", callback=None):
        super().__init__(parent)
        
        self.parent = parent
        self.original_df = df.copy()
        self.working_df = df.copy()
        self.data_type = data_type  # 'ledger' or 'statement'
        self.callback = callback  # Function to call when saving
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        
        # Selection tracking
        self.selected_rows = set()
        self.clipboard_data = None
        
        # Setup window
        self.title(f"BARD-RECO - {title}")
        self.state('zoomed')
        self.configure(bg="#ffffff")
        
        # Create UI
        self.create_interface()
        self.populate_data()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
    
    def create_interface(self):
        """Create the complete UI interface"""
        # Main container
        main_frame = tk.Frame(self, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create data grid
        self.create_data_grid(main_frame)
        
        # Create status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Create comprehensive toolbar with all operations"""
        toolbar = tk.Frame(parent, bg="#2c3e50", height=120, relief="ridge", bd=2)
        toolbar.pack(fill="x", pady=(0, 5))
        toolbar.pack_propagate(False)
        
        # Row 1: Title and close
        row1 = tk.Frame(toolbar, bg="#2c3e50")
        row1.pack(fill="x", padx=15, pady=(10, 5))
        
        tk.Label(row1, text=f"📊 {self.title().split(' - ')[1]}", 
                font=("Segoe UI", 14, "bold"),
                bg="#2c3e50", fg="white").pack(side="left")
        
        tk.Button(row1, text="✖ Close", command=self.close_editor,
                 font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="right")
        
        # Row 2: Main operations
        row2 = tk.Frame(toolbar, bg="#2c3e50")
        row2.pack(fill="x", padx=15, pady=5)
        
        # Paste section
        paste_frame = self.create_toolbar_section(row2, "📋 Paste")
        tk.Button(paste_frame, text="Paste from Excel", command=self.paste_from_clipboard,
                 font=("Segoe UI", 9, "bold"), bg="#3498db", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(paste_frame, text="Paste Append", command=lambda: self.paste_from_clipboard(append=True),
                 font=("Segoe UI", 9, "bold"), bg="#2980b9", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Row operations
        row_frame = self.create_toolbar_section(row2, "📝 Rows")
        tk.Button(row_frame, text="+ Add Row", command=self.add_row,
                 font=("Segoe UI", 9, "bold"), bg="#27ae60", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(row_frame, text="⬇ Insert Row", command=self.insert_row,
                 font=("Segoe UI", 9, "bold"), bg="#2ecc71", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(row_frame, text="− Delete Selected", command=self.delete_selected_rows,
                 font=("Segoe UI", 9, "bold"), bg="#e74c3c", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(row_frame, text="📋 Duplicate", command=self.duplicate_selected_rows,
                 font=("Segoe UI", 9, "bold"), bg="#16a085", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Column operations
        col_frame = self.create_toolbar_section(row2, "📊 Columns")
        tk.Button(col_frame, text="+ Add Column", command=self.add_column,
                 font=("Segoe UI", 9, "bold"), bg="#9b59b6", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(col_frame, text="➡ Insert Column", command=self.insert_column,
                 font=("Segoe UI", 9, "bold"), bg="#a569bd", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(col_frame, text="✏️ Rename", command=self.rename_column,
                 font=("Segoe UI", 9, "bold"), bg="#8e44ad", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(col_frame, text="− Delete", command=self.delete_column,
                 font=("Segoe UI", 9, "bold"), bg="#c0392b", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Data operations
        data_frame = self.create_toolbar_section(row2, "🔧 Data")
        tk.Button(data_frame, text="🔍 Filter", command=self.show_filter_dialog,
                 font=("Segoe UI", 9, "bold"), bg="#f39c12", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(data_frame, text="↕️ Sort", command=self.show_sort_dialog,
                 font=("Segoe UI", 9, "bold"), bg="#d35400", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(data_frame, text="🔎 Find/Replace", command=self.show_find_replace,
                 font=("Segoe UI", 9, "bold"), bg="#e67e22", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Row 3: Save and export
        row3 = tk.Frame(toolbar, bg="#2c3e50")
        row3.pack(fill="x", padx=15, pady=(5, 10))
        
        # Undo/Redo
        undo_frame = self.create_toolbar_section(row3, "↩️ History")
        tk.Button(undo_frame, text="⬅ Undo", command=self.undo,
                 font=("Segoe UI", 9, "bold"), bg="#34495e", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(undo_frame, text="➡ Redo", command=self.redo,
                 font=("Segoe UI", 9, "bold"), bg="#34495e", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Selection
        select_frame = self.create_toolbar_section(row3, "☑️ Select")
        tk.Button(select_frame, text="Select All", command=self.select_all,
                 font=("Segoe UI", 9, "bold"), bg="#7f8c8d", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        tk.Button(select_frame, text="Clear Selection", command=self.clear_selection,
                 font=("Segoe UI", 9, "bold"), bg="#95a5a6", fg="white",
                 relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=2)
        
        # Save operations
        save_frame = tk.Frame(row3, bg="#2c3e50")
        save_frame.pack(side="right")
        
        tk.Button(save_frame, text="💾 Save Changes", command=self.save_changes,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=5)
        tk.Button(save_frame, text="📤 Export Excel", command=self.export_to_excel,
                 font=("Segoe UI", 10, "bold"), bg="#2ecc71", fg="white",
                 relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=5)
    
    def create_toolbar_section(self, parent, label):
        """Create a labeled section in toolbar"""
        section = tk.Frame(parent, bg="#2c3e50")
        section.pack(side="left", padx=10)
        
        tk.Label(section, text=label, font=("Segoe UI", 9, "bold"),
                bg="#2c3e50", fg="#bdc3c7").pack(anchor="w", pady=(0, 3))
        
        buttons_frame = tk.Frame(section, bg="#2c3e50")
        buttons_frame.pack()
        
        return buttons_frame
    
    def create_data_grid(self, parent):
        """Create the data grid with Excel-like appearance"""
        grid_frame = tk.Frame(parent, bg="#d5d5d5", relief="solid", bd=2)
        grid_frame.pack(fill="both", expand=True)
        
        # Create tree with scrollbars
        tree_container = tk.Frame(grid_frame, bg="white")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ['#'] + list(self.working_df.columns)
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                                yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set,
                                selectmode="extended")
        self.tree.pack(fill="both", expand=True)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading('#', text='#', anchor='center')
        self.tree.column('#', width=60, anchor='center', minwidth=60, stretch=False)
        
        for col in self.working_df.columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=150, anchor='center', minwidth=80)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_cell_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_status_bar(self, parent):
        """Create status bar with info"""
        status_bar = tk.Frame(parent, bg="#34495e", height=35, relief="solid", bd=1)
        status_bar.pack(fill="x", pady=(5, 0))
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(status_bar, text="Ready", 
                                     font=("Segoe UI", 9), bg="#34495e", fg="white")
        self.status_label.pack(side="left", padx=15, pady=8)
        
        self.selection_label = tk.Label(status_bar, text="0 rows selected", 
                                        font=("Segoe UI", 9), bg="#34495e", fg="#bdc3c7")
        self.selection_label.pack(side="right", padx=15, pady=8)
    
    def populate_data(self):
        """Populate tree with data"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add rows
        for row_num, (idx, row) in enumerate(self.working_df.iterrows()):
            values = [str(row_num + 1)] + [str(val) if pd.notna(val) else '' for val in row]
            tags = ('even_row',) if row_num % 2 == 0 else ('odd_row',)
            self.tree.insert('', 'end', values=values, tags=tags, iid=str(idx))
        
        # Configure tags
        self.tree.tag_configure('even_row', background='#f8f9fa')
        self.tree.tag_configure('odd_row', background='#ffffff')
        
        self.update_status(f"Loaded {len(self.working_df)} rows, {len(self.working_df.columns)} columns")
    
    def paste_from_clipboard(self, append=False):
        """Paste data from clipboard (Excel format)"""
        try:
            # Get clipboard data
            clipboard_text = self.clipboard_get()
            
            if not clipboard_text.strip():
                messagebox.showwarning("Empty Clipboard", "No data in clipboard", parent=self)
                return
            
            # Save state for undo
            self.save_state()
            
            # Parse clipboard data (tab-separated for Excel)
            lines = clipboard_text.strip().split('\n')
            parsed_data = []
            
            for line in lines:
                # Split by tab (Excel) or fallback to comma
                if '\t' in line:
                    row = line.split('\t')
                else:
                    row = line.split(',')
                parsed_data.append(row)
            
            if not parsed_data:
                messagebox.showwarning("No Data", "Could not parse clipboard data", parent=self)
                return
            
            # Check if first row looks like headers
            ask_headers = messagebox.askyesnocancel("Headers", 
                                                     "Does the pasted data include column headers in the first row?",
                                                     parent=self)
            
            if ask_headers is None:  # Cancel
                self.undo()  # Restore previous state
                return
            
            has_headers = ask_headers
            
            if has_headers:
                headers = parsed_data[0]
                data_rows = parsed_data[1:]
            else:
                headers = list(self.working_df.columns)
                data_rows = parsed_data
            
            # Create DataFrame from pasted data
            try:
                paste_df = pd.DataFrame(data_rows, columns=headers[:len(data_rows[0]) if data_rows else 0])
                
                # Clean up data - strip whitespace from string columns
                paste_df = paste_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                
                # ENHANCED: Convert numeric columns with robust parsing for amounts
                for col in paste_df.columns:
                    try:
                        # Check if column might contain numeric data
                        # Try to convert each value, handling common formats
                        def parse_numeric(val):
                            if pd.isna(val) or val == '' or val is None:
                                return None
                            
                            # Convert to string for processing
                            val_str = str(val).strip()
                            
                            # Remove common currency symbols and formatting
                            val_str = val_str.replace('$', '').replace('€', '').replace('£', '').replace('R', '')
                            val_str = val_str.replace(',', '')  # Remove thousand separators
                            val_str = val_str.replace(' ', '')  # Remove spaces
                            
                            # Handle parentheses for negative numbers (accounting format)
                            if val_str.startswith('(') and val_str.endswith(')'):
                                val_str = '-' + val_str[1:-1]
                            
                            # Try to convert to float
                            try:
                                return float(val_str)
                            except (ValueError, TypeError):
                                return val  # Return original if can't convert
                        
                        # Apply numeric parsing
                        converted = paste_df[col].apply(parse_numeric)
                        
                        # Check if at least some values were successfully converted to numeric
                        numeric_count = pd.to_numeric(converted, errors='coerce').notna().sum()
                        if numeric_count > 0:
                            # If any values converted successfully, use the converted column
                            paste_df[col] = pd.to_numeric(converted, errors='coerce').fillna(converted)
                    except Exception as col_error:
                        # Keep original column if conversion fails completely
                        pass
                
            except Exception as e:
                messagebox.showerror("Parse Error", f"Failed to parse data:\n{e}", parent=self)
                self.undo()
                return
            
            # Decide how to integrate pasted data
            if append:
                # Append mode: Add to existing data
                # Match columns or add new ones
                for col in paste_df.columns:
                    if col not in self.working_df.columns:
                        self.working_df[col] = None
                
                for col in self.working_df.columns:
                    if col not in paste_df.columns:
                        paste_df[col] = None
                
                # Append
                if not paste_df.empty:
                    self.working_df = pd.concat([self.working_df, paste_df], ignore_index=True)
                
                messagebox.showinfo("Success", 
                                  f"✓ Appended {len(paste_df)} rows from clipboard!\n"
                                  f"Total rows: {len(self.working_df)}",
                                  parent=self)
            else:
                # Replace mode: Ask where to paste
                choice = messagebox.askyesnocancel("Paste Location",
                                                   "Yes: Replace all data\n"
                                                   "No: Insert at selected position\n"
                                                   "Cancel: Cancel paste",
                                                   parent=self)
                
                if choice is None:  # Cancel
                    self.undo()
                    return
                elif choice:  # Replace all
                    self.working_df = paste_df
                    messagebox.showinfo("Success", f"✓ Replaced with {len(paste_df)} rows", parent=self)
                else:  # Insert at position
                    # Get selected row index
                    selection = self.tree.selection()
                    if selection:
                        insert_idx = int(selection[0])
                    else:
                        insert_idx = len(self.working_df)
                    
                    # Match columns
                    for col in paste_df.columns:
                        if col not in self.working_df.columns:
                            self.working_df[col] = None
                    
                    for col in self.working_df.columns:
                        if col not in paste_df.columns:
                            paste_df[col] = None
                    
                    # Insert
                    before_df = self.working_df.iloc[:insert_idx]
                    after_df = self.working_df.iloc[insert_idx:]
                    # Filter out empty DataFrames to avoid FutureWarning
                    dfs_to_concat = [df for df in [before_df, paste_df, after_df] if not df.empty]
                    if dfs_to_concat:
                        self.working_df = pd.concat(dfs_to_concat, ignore_index=True)
                    else:
                        self.working_df = paste_df.copy()
                    
                    messagebox.showinfo("Success", 
                                      f"✓ Inserted {len(paste_df)} rows at position {insert_idx + 1}",
                                      parent=self)
            
            # Refresh display
            self.populate_data()
            
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste:\n{e}", parent=self)
            if len(self.undo_stack) > 0:
                self.undo()
    
    def save_state(self):
        """Save current state for undo"""
        self.undo_stack.append(self.working_df.copy())
        self.redo_stack.clear()  # Clear redo stack on new action
        
        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
    
    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo", parent=self)
            return
        
        self.redo_stack.append(self.working_df.copy())
        self.working_df = self.undo_stack.pop()
        self.populate_data()
        self.update_status("Undo applied")
    
    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            messagebox.showinfo("Redo", "Nothing to redo", parent=self)
            return
        
        self.undo_stack.append(self.working_df.copy())
        self.working_df = self.redo_stack.pop()
        self.populate_data()
        self.update_status("Redo applied")
    
    def add_row(self):
        """Add new empty row at end"""
        self.save_state()
        new_row = pd.Series([None] * len(self.working_df.columns), index=self.working_df.columns)
        # Use loc to avoid FutureWarning
        self.working_df.loc[len(self.working_df)] = new_row
        self.working_df.reset_index(drop=True, inplace=True)
        self.populate_data()
        self.update_status("Added new row at end")
    
    def insert_row(self):
        """Insert new empty row at selected position"""
        selection = self.tree.selection()
        
        if not selection:
            # No selection - insert at beginning
            insert_idx = 0
            position_text = "beginning"
        else:
            # Insert before first selected row
            insert_idx = int(selection[0])
            position_text = f"position {insert_idx + 1}"
        
        self.save_state()
        
        # Create new row
        new_row = pd.Series([None] * len(self.working_df.columns), index=self.working_df.columns)
        
        # Split DataFrame and insert
        if insert_idx == 0:
            # Insert at beginning
            self.working_df = pd.concat([pd.DataFrame([new_row]), self.working_df], ignore_index=True)
        elif insert_idx >= len(self.working_df):
            # Insert at end
            self.working_df.loc[len(self.working_df)] = new_row
        else:
            # Insert in middle
            before_df = self.working_df.iloc[:insert_idx]
            after_df = self.working_df.iloc[insert_idx:]
            self.working_df = pd.concat([before_df, pd.DataFrame([new_row]), after_df], ignore_index=True)
        
        self.working_df.reset_index(drop=True, inplace=True)
        self.populate_data()
        self.update_status(f"Inserted row at {position_text}")
        
        # Select the newly inserted row
        self.tree.selection_set(str(insert_idx))
        self.tree.see(str(insert_idx))
    
    def delete_selected_rows(self):
        """Delete selected rows"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select rows to delete", parent=self)
            return
        
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(selection)} selected row(s)?",
                                   parent=self):
            return
        
        self.save_state()
        indices_to_delete = [int(item) for item in selection]
        self.working_df = self.working_df.drop(indices_to_delete).reset_index(drop=True)
        self.populate_data()
        self.update_status(f"Deleted {len(selection)} rows")
    
    def duplicate_selected_rows(self):
        """Duplicate selected rows"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select rows to duplicate", parent=self)
            return
        
        self.save_state()
        indices = [int(item) for item in selection]
        rows_to_duplicate = self.working_df.iloc[indices].copy()
        if not rows_to_duplicate.empty:
            self.working_df = pd.concat([self.working_df, rows_to_duplicate], ignore_index=True)
        self.populate_data()
        self.update_status(f"Duplicated {len(selection)} rows")
    
    def add_column(self):
        """Add new column at end"""
        # Dialog for column name
        dialog = tk.Toplevel(self)
        dialog.title("Add Column")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter column name:", font=("Segoe UI", 11)).pack(pady=20)
        
        entry = tk.Entry(dialog, font=("Segoe UI", 10), width=30)
        entry.pack(pady=10)
        entry.focus()
        
        def add():
            col_name = entry.get().strip()
            if not col_name:
                messagebox.showwarning("Invalid Name", "Column name cannot be empty", parent=dialog)
                return
            
            if col_name in self.working_df.columns:
                messagebox.showwarning("Duplicate", f"Column '{col_name}' already exists", parent=dialog)
                return
            
            self.save_state()
            self.working_df[col_name] = None
            self.populate_data()
            self.update_status(f"Added column '{col_name}' at end")
            dialog.destroy()
        
        tk.Button(dialog, text="Add Column", command=add,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 padx=20, pady=8).pack(pady=10)
        
        entry.bind('<Return>', lambda e: add())
    
    def insert_column(self):
        """Insert new column at specific position"""
        # Dialog for column name and position
        dialog = tk.Toplevel(self)
        dialog.title("Insert Column")
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter column name:", font=("Segoe UI", 11)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=35)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        tk.Label(dialog, text="Insert before column:", font=("Segoe UI", 11)).pack(pady=10)
        
        position_var = tk.StringVar()
        position_combo = ttk.Combobox(dialog, textvariable=position_var,
                                     values=["Beginning"] + list(self.working_df.columns) + ["End"],
                                     font=("Segoe UI", 10), width=32, state='readonly')
        position_combo.pack(pady=5)
        position_combo.set("End")
        
        def insert():
            col_name = name_entry.get().strip()
            if not col_name:
                messagebox.showwarning("Invalid Name", "Column name cannot be empty", parent=dialog)
                return
            
            if col_name in self.working_df.columns:
                messagebox.showwarning("Duplicate", f"Column '{col_name}' already exists", parent=dialog)
                return
            
            position = position_var.get()
            
            self.save_state()
            
            # Create new column with None values
            new_col_data = pd.Series([None] * len(self.working_df), name=col_name)
            
            if position == "Beginning":
                # Insert at beginning
                self.working_df.insert(0, col_name, new_col_data)
                position_text = "beginning"
            elif position == "End" or not position:
                # Add at end
                self.working_df[col_name] = new_col_data
                position_text = "end"
            else:
                # Insert before selected column
                col_index = list(self.working_df.columns).index(position)
                self.working_df.insert(col_index, col_name, new_col_data)
                position_text = f"before '{position}'"
            
            self.populate_data()
            self.update_status(f"Inserted column '{col_name}' at {position_text}")
            dialog.destroy()
        
        tk.Button(dialog, text="Insert Column", command=insert,
                 font=("Segoe UI", 10, "bold"), bg="#9b59b6", fg="white",
                 padx=20, pady=8).pack(pady=15)
        
        name_entry.bind('<Return>', lambda e: insert())
    
    def rename_column(self):
        """Rename a column"""
        # Get selected column (simplified - asks for column name)
        dialog = tk.Toplevel(self)
        dialog.title("Rename Column")
        dialog.geometry("450x200")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select column to rename:", font=("Segoe UI", 11)).pack(pady=10)
        
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=list(self.working_df.columns),
                                font=("Segoe UI", 10), width=30, state='readonly')
        col_combo.pack(pady=5)
        
        tk.Label(dialog, text="New name:", font=("Segoe UI", 11)).pack(pady=10)
        
        new_name_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=30)
        new_name_entry.pack(pady=5)
        
        def rename():
            old_name = col_var.get()
            new_name = new_name_entry.get().strip()
            
            if not old_name or not new_name:
                messagebox.showwarning("Invalid", "Please select column and enter new name", parent=dialog)
                return
            
            if new_name in self.working_df.columns:
                messagebox.showwarning("Duplicate", f"Column '{new_name}' already exists", parent=dialog)
                return
            
            self.save_state()
            self.working_df.rename(columns={old_name: new_name}, inplace=True)
            self.populate_data()
            self.update_status(f"Renamed '{old_name}' to '{new_name}'")
            dialog.destroy()
        
        tk.Button(dialog, text="Rename", command=rename,
                 font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white",
                 padx=20, pady=8).pack(pady=10)
    
    def delete_column(self):
        """Delete a column"""
        dialog = tk.Toplevel(self)
        dialog.title("Delete Column")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select column to delete:", font=("Segoe UI", 11)).pack(pady=20)
        
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=list(self.working_df.columns),
                                font=("Segoe UI", 10), width=30, state='readonly')
        col_combo.pack(pady=5)
        
        def delete():
            col_name = col_var.get()
            if not col_name:
                messagebox.showwarning("No Selection", "Please select a column", parent=dialog)
                return
            
            if not messagebox.askyesno("Confirm", f"Delete column '{col_name}'?", parent=dialog):
                return
            
            self.save_state()
            self.working_df.drop(columns=[col_name], inplace=True)
            self.populate_data()
            self.update_status(f"Deleted column '{col_name}'")
            dialog.destroy()
        
        tk.Button(dialog, text="Delete", command=delete,
                 font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                 padx=20, pady=8).pack(pady=10)
    
    def show_filter_dialog(self):
        """Show comprehensive filter dialog"""
        FilterDialog(self, self.working_df, self.apply_filter)
    
    def show_sort_dialog(self):
        """Show comprehensive sort dialog"""
        SortDialog(self, self.working_df, self.apply_sort)
    
    def show_find_replace(self):
        """Show find and replace dialog"""
        FindReplaceDialog(self, self.working_df, self.apply_find_replace)
    
    def select_all(self):
        """Select all rows"""
        self.tree.selection_set(*self.tree.get_children())
        self.update_selection_count()
    
    def clear_selection(self):
        """Clear selection"""
        self.tree.selection_remove(*self.tree.selection())
        self.update_selection_count()
    
    def on_cell_double_click(self, event):
        """Handle cell double-click for editing"""
        # Simplified - show edit dialog
        selection = self.tree.selection()
        if not selection:
            return
        
        row_id = selection[0]
        # Get column clicked
        col_id = self.tree.identify_column(event.x)
        if col_id == '#1':  # Row number column
            return
        
        col_idx = int(col_id.replace('#', '')) - 2  # Adjust for row number column
        if col_idx < 0 or col_idx >= len(self.working_df.columns):
            return
        
        col_name = self.working_df.columns[col_idx]
        row_idx = int(row_id)
        current_value = self.working_df.at[row_idx, col_name]
        
        # Show edit dialog
        self.edit_cell(row_idx, col_name, current_value)
    
    def edit_cell(self, row_idx, col_name, current_value):
        """Edit a single cell"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Cell")
        dialog.geometry("500x200")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Row: {row_idx + 1} | Column: {col_name}",
                font=("Segoe UI", 11, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="Current value:", font=("Segoe UI", 10)).pack(pady=5)
        
        entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
        entry.insert(0, str(current_value) if pd.notna(current_value) else "")
        entry.pack(pady=5)
        entry.focus()
        entry.selection_range(0, tk.END)
        
        def save():
            new_value = entry.get()
            
            # Try to convert to appropriate type
            try:
                if new_value == "":
                    new_value = None
                elif '.' in new_value or ',' in new_value:
                    new_value = float(new_value.replace(',', ''))
                else:
                    try:
                        new_value = int(new_value)
                    except:
                        pass  # Keep as string
            except:
                pass  # Keep as string
            
            self.save_state()
            self.working_df.at[row_idx, col_name] = new_value
            self.populate_data()
            self.update_status(f"Updated cell ({row_idx + 1}, {col_name})")
            dialog.destroy()
        
        tk.Button(dialog, text="Save", command=save,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 padx=20, pady=8).pack(pady=15)
        
        entry.bind('<Return>', lambda e: save())
    
    def on_selection_change(self, event):
        """Update selection count"""
        self.update_selection_count()
    
    def update_selection_count(self):
        """Update selection count label"""
        count = len(self.tree.selection())
        self.selection_label.config(text=f"{count} rows selected")
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy", command=self.copy_selected)
        menu.add_command(label="Paste", command=self.paste_from_clipboard)
        menu.add_separator()
        menu.add_command(label="Duplicate Rows", command=self.duplicate_selected_rows)
        menu.add_command(label="Delete Rows", command=self.delete_selected_rows)
        menu.post(event.x_root, event.y_root)
    
    def copy_selected(self):
        """Copy selected rows to clipboard"""
        selection = self.tree.selection()
        if not selection:
            return
        
        indices = [int(item) for item in selection]
        selected_data = self.working_df.iloc[indices]
        
        # Convert to tab-separated for Excel compatibility
        clipboard_text = selected_data.to_csv(sep='\t', index=False)
        self.clipboard_clear()
        self.clipboard_append(clipboard_text)
        self.update_status(f"Copied {len(selection)} rows to clipboard")
    
    def save_changes(self):
        """Save changes back to parent with amount validation"""
        # Check for potential amount column issues
        amount_warnings = []
        amount_keywords = ['amount', 'debit', 'credit', 'balance', 'total', 'value', 'amt']
        
        for col in self.working_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in amount_keywords):
                # Check if column has excessive zeros
                zero_count = (self.working_df[col] == 0).sum()
                total_rows = len(self.working_df)
                
                if zero_count > total_rows * 0.5 and total_rows > 5:  # More than 50% zeros
                    amount_warnings.append(f"• '{col}' has {zero_count}/{total_rows} zero values")
        
        # Show warning if amount issues detected
        if amount_warnings:
            warning_msg = (
                "⚠️ AMOUNT VALIDATION WARNING ⚠️\n\n"
                "The following amount columns have many zero values:\n\n" +
                "\n".join(amount_warnings) +
                "\n\nThis often happens when:\n"
                "• Data was pasted incorrectly from Excel\n"
                "• Amount formatting was lost during copy/paste\n"
                "• Text values weren't converted to numbers\n\n"
                "⚡ TIP: Try pasting the data again or check the source Excel file.\n\n"
                "Do you still want to save?"
            )
            if not messagebox.askyesno("Amount Validation Warning", warning_msg, parent=self):
                return
        
        # Proceed with save confirmation
        if messagebox.askyesno("Confirm Save",
                              f"Save changes to {self.data_type}?\n\n"
                              f"Rows: {len(self.working_df)}\n"
                              f"Columns: {len(self.working_df.columns)}",
                              parent=self):
            
            if self.callback:
                self.callback(self.working_df)
            
            messagebox.showinfo("Saved", "Changes saved successfully!\n\n"
                              "✅ Data is now ready for reconciliation.", parent=self)
            self.original_df = self.working_df.copy()
            self.update_status("Changes saved")
    
    def export_to_excel(self):
        """Export to Excel"""
        file_path = filedialog.asksaveasfilename(
            title="Export to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            parent=self
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                self.working_df.to_csv(file_path, index=False)
            else:
                self.working_df.to_excel(file_path, index=False)
            
            messagebox.showinfo("Success", f"Exported to:\n{file_path}", parent=self)
            self.update_status("Exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{e}", parent=self)
    
    def close_editor(self):
        """Close the editor"""
        if not self.working_df.equals(self.original_df):
            response = messagebox.askyesnocancel("Unsaved Changes",
                                                "You have unsaved changes.\n\n"
                                                "Save before closing?",
                                                parent=self)
            if response is None:  # Cancel
                return
            elif response:  # Yes - save
                self.save_changes()
        
        self.destroy()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def apply_filter(self, filtered_df):
        """Apply filter result to working DataFrame"""
        self.save_state()
        self.working_df = filtered_df.reset_index(drop=True)
        self.populate_data()
        self.update_status(f"Filter applied - {len(filtered_df)} rows")
    
    def apply_sort(self, sorted_df):
        """Apply sort result to working DataFrame"""
        self.save_state()
        self.working_df = sorted_df.reset_index(drop=True)
        self.populate_data()
        self.update_status(f"Data sorted - {len(sorted_df)} rows")
    
    def apply_find_replace(self, modified_df):
        """Apply find/replace result to working DataFrame"""
        self.save_state()
        self.working_df = modified_df.copy()
        self.populate_data()
        self.update_status("Find/Replace applied")
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        self.bind('<Control-c>', lambda e: self.copy_selected())
        self.bind('<Control-s>', lambda e: self.save_changes())
        self.bind('<Control-z>', lambda e: self.undo())
        self.bind('<Control-y>', lambda e: self.redo())
        self.bind('<Control-a>', lambda e: self.select_all())
        self.bind('<Delete>', lambda e: self.delete_selected_rows())
        self.bind('<F5>', lambda e: self.populate_data())
        self.bind('<Escape>', lambda e: self.close_editor())
