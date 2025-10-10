"""
Enhanced FNB Workflow Implementation (Part 2)
===========================================
Data processing, reconciliation, and collaborative features for FNB workflow
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pandas as pd
import numpy as np
from datetime import datetime
import re
import threading
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Optional, Any, Tuple

# Multi-user components removed for simplified version
from fnb_reconciliation_engine import MatchingConfigDialog

# Continuation of enhanced_fnb_workflow.py

class EnhancedFNBWorkflowContinued:
    """Continuation methods for Enhanced FNB Workflow"""
    
    # Data processing methods
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
            
            # Extract references
            references = []
            for description in df[desc_col]:
                ref = self._extract_reference_name(str(description))
                references.append(ref)
            
            # Add Reference column
            desc_idx = list(df.columns).index(desc_col)
            df.insert(desc_idx + 1, 'Reference', references)
            
            self.statement_df = df
            
            # Auto-save changes
            self.mark_unsaved_changes()
            
            # Activity logging removed for simplified version
            
            messagebox.showinfo("Success", 
                              f"Reference column added successfully!\n"
                              f"Processed {len(references)} descriptions.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add reference column: {str(e)}")
    
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
            
            # Add columns to dataframe
            df['RJ-Number'] = rj_numbers
            df['Payment Ref'] = payment_refs
            
            self.ledger_df = df
            
            # Auto-save changes
            self.mark_unsaved_changes()
            
            # Activity logging removed for simplified version
            
            messagebox.showinfo("Columns Added", 
                              f"RJ-Number and Payment Ref columns added!\n\n"
                              f"📊 Extraction Summary:\n"
                              f"• RJ-Numbers found: {rj_count}\n"
                              f"• Payment References found: {payref_count}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add RJ columns: {str(e)}")
    
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
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names (case-insensitive)"""
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        for name in possible_names:
            name_lower = name.lower().strip()
            if name_lower in df_columns_lower:
                return df.columns[df_columns_lower.index(name_lower)]
        
        return None
    
    def _view_data(self):
        """Show data viewer dialog"""
        if self.ledger_df is None and self.statement_df is None:
            messagebox.showwarning("No Data", "Please import ledger and/or statement files first")
            return
        
        # Create data viewer window
        viewer = tk.Toplevel(self.parent)
        viewer.title("BARD-RECO - Data Viewer")
        viewer.geometry("1200x800")
        viewer.configure(bg="#f8fafc")
        
        # Center window
        viewer.update_idletasks()
        x = (viewer.winfo_screenwidth() // 2) - (1200 // 2)
        y = (viewer.winfo_screenheight() // 2) - (800 // 2)
        viewer.geometry(f"1200x800+{x}+{y}")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(viewer)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs for each dataset
        if self.ledger_df is not None:
            self._create_data_tab(notebook, "📊 Ledger", self.ledger_df)
        
        if self.statement_df is not None:
            self._create_data_tab(notebook, "🏦 Statement", self.statement_df)
        
        if self.reconciliation_results is not None:
            self._create_results_tabs(notebook, self.reconciliation_results)
    
    def _create_data_tab(self, notebook: ttk.Notebook, title: str, df: pd.DataFrame):
        """Create a tab showing DataFrame data"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        
        # Info section
        info_frame = tk.Frame(frame, bg="#f1f5f9", height=60)
        info_frame.pack(fill="x", padx=5, pady=5)
        info_frame.pack_propagate(False)
        
        tk.Label(info_frame, text=f"📊 {len(df)} rows × {len(df.columns)} columns", 
                font=("Segoe UI", 12, "bold"), bg="#f1f5f9", fg="#1e293b").pack(pady=20)
        
        # Create treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Treeview with scrollbars
        tree = ttk.Treeview(tree_frame, columns=list(df.columns), show="headings")
        
        # Configure columns
        for col in df.columns:
            tree.heading(col, text=str(col))
            tree.column(col, width=120, minwidth=80)
        
        # Add data (limit to first 1000 rows for performance)
        display_df = df.head(1000)
        for idx, row in display_df.iterrows():
            values = [str(val)[:50] + "..." if len(str(val)) > 50 else str(val) for val in row]
            tree.insert("", "end", values=values)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Show warning if data was truncated
        if len(df) > 1000:
            warning_label = tk.Label(frame, 
                                   text=f"⚠️ Showing first 1000 rows of {len(df)} total rows",
                                   font=("Segoe UI", 10), fg="#f59e0b", bg="#fef3c7")
            warning_label.pack(fill="x", padx=5, pady=2)
    
    def _create_results_tabs(self, notebook: ttk.Notebook, results: Dict[str, Any]):
        """Create tabs for reconciliation results"""
        for key, data in results.items():
            if isinstance(data, pd.DataFrame) and not data.empty:
                title = f"📋 {key.title().replace('_', ' ')}"
                self._create_data_tab(notebook, title, data)
    
    # Mode setting methods
    def _set_references_only_mode(self):
        """Set matching to references only mode"""
        self.match_dates.set(False)
        self.match_references.set(True)
        self.match_amounts.set(False)
        
        messagebox.showinfo("⚡ References Only Mode", 
                           "🚀 SUPER FAST MATCHING ENABLED!\n\n"
                           "✅ References: ON\n"
                           "❌ Dates: OFF\n" 
                           "❌ Amounts: OFF\n\n"
                           "This mode matches ONLY by reference fields\n"
                           "for maximum speed and performance.")
    
    def _set_all_fields_mode(self):
        """Set matching to use all fields"""
        self.match_dates.set(True)
        self.match_references.set(True)
        self.match_amounts.set(True)
        
        messagebox.showinfo("🎯 All Fields Mode", 
                           "🔍 COMPREHENSIVE MATCHING ENABLED!\n\n"
                           "✅ References: ON\n"
                           "✅ Dates: ON\n" 
                           "✅ Amounts: ON\n\n"
                           "This mode uses all fields for thorough\n"
                           "and accurate matching.")
    
    def _set_dates_amounts_mode(self):
        """Set matching to dates and amounts only"""
        self.match_dates.set(True)
        self.match_references.set(False)
        self.match_amounts.set(True)
        
        messagebox.showinfo("📅💰 Dates & Amounts Mode", 
                           "📊 DATES & AMOUNTS MATCHING ENABLED!\n\n"
                           "✅ Dates: ON\n"
                           "❌ References: OFF\n" 
                           "✅ Amounts: ON\n\n"
                           "This mode matches by dates and amounts only,\n"
                           "useful when references are unreliable.")
    
    def _configure_matching(self):
        """Show matching configuration dialog"""
        config_dialog = MatchingConfigDialog(self.parent, self.match_settings, 
                                           self.ledger_df, self.statement_df)
        new_settings = config_dialog.show_config()
        
        if new_settings:
            self.match_settings.update(new_settings)
            
            # Auto-save settings
            self.mark_unsaved_changes()
            
            messagebox.showinfo("Configuration Updated", 
                              "Matching configuration has been updated successfully!")

# Continue with reconciliation engine in next stage...
