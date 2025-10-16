"""
FNB Reconciliation Engine and Configuration Dialog
================================================
Advanced reconciliation algorithms and configuration interface for FNB workflow
"""

import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Optional, Any, Tuple
import threading
import sys
import os

# Add utils to path for data cleaner
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from data_cleaner import clean_amount_column

# Multi-user components removed for simplified version

class FNBReconciliationEngine:
    """Advanced reconciliation engine for FNB workflow"""
    
    def __init__(self, workflow_instance):
        self.workflow = workflow_instance
        self.progress_callback = None
        self.cancel_flag = False
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def cancel_reconciliation(self):
        """Cancel ongoing reconciliation"""
        self.cancel_flag = True
    
    def reconcile(self, ledger_df: pd.DataFrame, statement_df: pd.DataFrame, 
                  settings: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Perform reconciliation with given settings"""
        self.cancel_flag = False
        
        if self.progress_callback:
            self.progress_callback("Initializing reconciliation...", 0)
        
        try:
            # Prepare data
            ledger_clean = self._prepare_ledger_data(ledger_df, settings)
            statement_clean = self._prepare_statement_data(statement_df, settings)
            
            if self.progress_callback:
                self.progress_callback("Finding matches...", 20)
            
            # Find matches
            matches = self._find_matches(ledger_clean, statement_clean, settings)
            
            if self.cancel_flag:
                return None
            
            if self.progress_callback:
                self.progress_callback("Processing results...", 80)
            
            # Process results
            results = self._process_results(ledger_clean, statement_clean, matches, settings)
            
            if self.progress_callback:
                self.progress_callback("Reconciliation complete!", 100)
            
            # Activity logging removed for simplified version
            
            return results
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error: {str(e)}", -1)
            raise e
    
    def _prepare_ledger_data(self, df: pd.DataFrame, settings: Dict[str, Any]) -> pd.DataFrame:
        """Prepare ledger data for matching"""
        ledger = df.copy()
        ledger.reset_index(drop=True, inplace=True)
        ledger['ledger_index'] = ledger.index
        
        # Standardize date column
        date_col = settings.get('ledger_date_col', 'Date')
        if date_col in ledger.columns:
            ledger['date_normalized'] = pd.to_datetime(ledger[date_col], errors='coerce')
        
        # Standardize reference column
        ref_col = settings.get('ledger_ref_col', 'Reference')
        if ref_col in ledger.columns:
            ledger['reference_clean'] = ledger[ref_col].astype(str).str.strip().str.upper()
        
        # Prepare amount columns
        if settings.get('match_amounts', True):
            debit_col = settings.get('ledger_debit_col', 'Debit')
            credit_col = settings.get('ledger_credit_col', 'Credit')
            
            # Create unified amount column with robust cleaning
            # Use the enhanced clean_amount_column to handle Excel paste issues
            debits = clean_amount_column(ledger[debit_col], column_name=debit_col)
            credits = clean_amount_column(ledger[credit_col], column_name=credit_col)
            
            # Determine amount based on mode
            if settings.get('use_debits_only', False):
                ledger['amount_for_matching'] = debits
            elif settings.get('use_credits_only', False):
                ledger['amount_for_matching'] = credits
            else:
                # Use both - positive for credits, negative for debits
                ledger['amount_for_matching'] = credits - debits
        
        return ledger
    
    def _prepare_statement_data(self, df: pd.DataFrame, settings: Dict[str, Any]) -> pd.DataFrame:
        """Prepare statement data for matching"""
        statement = df.copy()
        statement.reset_index(drop=True, inplace=True)
        statement['statement_index'] = statement.index
        
        # Standardize date column
        date_col = settings.get('statement_date_col', 'Date')
        if date_col in statement.columns:
            statement['date_normalized'] = pd.to_datetime(statement[date_col], errors='coerce')
        
        # Standardize reference column
        ref_col = settings.get('statement_ref_col', 'Reference')
        if ref_col in statement.columns:
            statement['reference_clean'] = statement[ref_col].astype(str).str.strip().str.upper()
        
        # Prepare amount column with robust cleaning
        if settings.get('match_amounts', True):
            amt_col = settings.get('statement_amt_col', 'Amount')
            # Use the enhanced clean_amount_column to handle Excel paste issues
            statement['amount_for_matching'] = clean_amount_column(statement[amt_col], column_name=amt_col)
        
        return statement
    
    def _find_matches(self, ledger: pd.DataFrame, statement: pd.DataFrame, 
                     settings: Dict[str, Any]) -> List[Tuple[int, int, float]]:
        """Find matches between ledger and statement"""
        matches = []
        used_statement_indices = set()
        
        total_ledger = len(ledger)
        
        for i, ledger_row in ledger.iterrows():
            if self.cancel_flag:
                break
            
            if self.progress_callback and i % 50 == 0:
                progress = 20 + (60 * i / total_ledger)  # 20-80% range
                self.progress_callback(f"Matching row {i+1} of {total_ledger}...", progress)
            
            best_match = None
            best_score = 0
            
            for j, stmt_row in statement.iterrows():
                if j in used_statement_indices:
                    continue
                
                score = self._calculate_match_score(ledger_row, stmt_row, settings)
                
                if score > best_score and score >= 0.7:  # Minimum threshold
                    best_score = score
                    best_match = j
            
            if best_match is not None:
                matches.append((i, best_match, best_score))
                used_statement_indices.add(best_match)
        
        return matches
    
    def _calculate_match_score(self, ledger_row: pd.Series, stmt_row: pd.Series, 
                              settings: Dict[str, Any]) -> float:
        """Calculate match score between ledger and statement rows"""
        scores = []
        weights = []
        
        # Date matching
        if settings.get('match_dates', True):
            date_score = self._calculate_date_score(ledger_row, stmt_row)
            if date_score is not None:
                scores.append(date_score)
                weights.append(0.3)
        
        # Reference matching
        if settings.get('match_references', True):
            ref_score = self._calculate_reference_score(ledger_row, stmt_row, settings)
            if ref_score is not None:
                scores.append(ref_score)
                weights.append(0.4)
        
        # Amount matching
        if settings.get('match_amounts', True):
            amt_score = self._calculate_amount_score(ledger_row, stmt_row)
            if amt_score is not None:
                scores.append(amt_score)
                weights.append(0.3)
        
        if not scores:
            return 0.0
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_date_score(self, ledger_row: pd.Series, stmt_row: pd.Series) -> Optional[float]:
        """Calculate date matching score"""
        try:
            ledger_date = ledger_row.get('date_normalized')
            stmt_date = stmt_row.get('date_normalized')
            
            if pd.isna(ledger_date) or pd.isna(stmt_date):
                return None
            
            # Calculate date difference in days
            diff_days = abs((ledger_date - stmt_date).days)
            
            if diff_days == 0:
                return 1.0
            elif diff_days <= 1:
                return 0.9
            elif diff_days <= 3:
                return 0.7
            elif diff_days <= 7:
                return 0.5
            else:
                return 0.0
                
        except Exception:
            return None
    
    def _calculate_reference_score(self, ledger_row: pd.Series, stmt_row: pd.Series, 
                                  settings: Dict[str, Any]) -> Optional[float]:
        """Calculate reference matching score"""
        try:
            ledger_ref = ledger_row.get('reference_clean', '')
            stmt_ref = stmt_row.get('reference_clean', '')
            
            if not ledger_ref or not stmt_ref or ledger_ref == 'NAN' or stmt_ref == 'NAN':
                return None
            
            # Use fuzzy matching if enabled
            if settings.get('fuzzy_ref', True):
                similarity = fuzz.ratio(ledger_ref, stmt_ref)
                min_similarity = settings.get('similarity_ref', 85)
                
                if similarity >= min_similarity:
                    return similarity / 100.0
                else:
                    return 0.0
            else:
                # Exact match only
                return 1.0 if ledger_ref == stmt_ref else 0.0
                
        except Exception:
            return None
    
    def _calculate_amount_score(self, ledger_row: pd.Series, stmt_row: pd.Series) -> Optional[float]:
        """Calculate amount matching score"""
        try:
            ledger_amt = ledger_row.get('amount_for_matching')
            stmt_amt = stmt_row.get('amount_for_matching')
            
            if pd.isna(ledger_amt) or pd.isna(stmt_amt):
                return None
            
            # Handle zero amounts
            if ledger_amt == 0 and stmt_amt == 0:
                return 1.0
            
            if ledger_amt == 0 or stmt_amt == 0:
                return 0.0
            
            # Calculate percentage difference
            diff = abs(ledger_amt - stmt_amt)
            avg_amt = (abs(ledger_amt) + abs(stmt_amt)) / 2
            
            if avg_amt == 0:
                return 1.0 if diff == 0 else 0.0
            
            percentage_diff = diff / avg_amt
            
            if percentage_diff == 0:
                return 1.0
            elif percentage_diff <= 0.01:  # 1% tolerance
                return 0.95
            elif percentage_diff <= 0.05:  # 5% tolerance
                return 0.8
            else:
                return 0.0
                
        except Exception:
            return None
    
    def _process_results(self, ledger: pd.DataFrame, statement: pd.DataFrame, 
                        matches: List[Tuple[int, int, float]], 
                        settings: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Process reconciliation results"""
        results = {}
        
        # Create matched pairs DataFrame
        if matches:
            matched_data = []
            matched_ledger_indices = set()
            matched_stmt_indices = set()
            
            for ledger_idx, stmt_idx, score in matches:
                ledger_row = ledger.iloc[ledger_idx]
                stmt_row = statement.iloc[stmt_idx]
                
                matched_data.append({
                    'Ledger_Index': ledger_idx,
                    'Statement_Index': stmt_idx,
                    'Match_Score': round(score, 3),
                    'Ledger_Date': ledger_row.get(settings.get('ledger_date_col', 'Date')),
                    'Statement_Date': stmt_row.get(settings.get('statement_date_col', 'Date')),
                    'Ledger_Reference': ledger_row.get(settings.get('ledger_ref_col', 'Reference')),
                    'Statement_Reference': stmt_row.get(settings.get('statement_ref_col', 'Reference')),
                    'Ledger_Amount': ledger_row.get('amount_for_matching'),
                    'Statement_Amount': stmt_row.get('amount_for_matching')
                })
                
                matched_ledger_indices.add(ledger_idx)
                matched_stmt_indices.add(stmt_idx)
            
            results['matched'] = pd.DataFrame(matched_data)
        else:
            results['matched'] = pd.DataFrame()
        
        # Create unmatched ledger DataFrame
        if matches:
            matched_ledger_indices = {match[0] for match in matches}
            unmatched_ledger = ledger[~ledger.index.isin(matched_ledger_indices)].copy()
        else:
            unmatched_ledger = ledger.copy()
        
        # Remove helper columns
        cols_to_remove = ['ledger_index', 'date_normalized', 'reference_clean', 'amount_for_matching']
        for col in cols_to_remove:
            if col in unmatched_ledger.columns:
                unmatched_ledger = unmatched_ledger.drop(columns=[col])
        
        results['unmatched_ledger'] = unmatched_ledger
        
        # Create unmatched statement DataFrame
        if matches:
            matched_stmt_indices = {match[1] for match in matches}
            unmatched_statement = statement[~statement.index.isin(matched_stmt_indices)].copy()
        else:
            unmatched_statement = statement.copy()
        
        # Remove helper columns
        cols_to_remove = ['statement_index', 'date_normalized', 'reference_clean', 'amount_for_matching']
        for col in cols_to_remove:
            if col in unmatched_statement.columns:
                unmatched_statement = unmatched_statement.drop(columns=[col])
        
        results['unmatched_statement'] = unmatched_statement
        
        # Add summary
        results['summary'] = pd.DataFrame([{
            'Total_Ledger_Rows': len(ledger),
            'Total_Statement_Rows': len(statement),
            'Matched_Pairs': len(matches),
            'Unmatched_Ledger': len(results['unmatched_ledger']),
            'Unmatched_Statement': len(results['unmatched_statement']),
            'Match_Rate': round(len(matches) / max(len(ledger), len(statement)) * 100, 2),
            'Reconciliation_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        return results

class MatchingConfigDialog:
    """Configuration dialog for matching settings"""
    
    def __init__(self, parent, current_settings: Dict[str, Any], 
                 ledger_df: pd.DataFrame, statement_df: pd.DataFrame):
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.ledger_df = ledger_df
        self.statement_df = statement_df
        self.result = None
        self.dialog = None
    
    def show_config(self) -> Optional[Dict[str, Any]]:
        """Show configuration dialog and return new settings"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("BARD-RECO - Configure Column Matching")
        self.dialog.geometry("900x700")
        self.dialog.configure(bg="#f8fafc")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"900x700+{x}+{y}")
        
        self._create_interface()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_interface(self):
        """Create the configuration interface"""
        # Header
        header = tk.Frame(self.dialog, bg="#1e40af", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Configure Column Matching", 
                font=("Segoe UI", 16, "bold"), fg="white", bg="#1e40af").pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.dialog, bg="#f8fafc")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create sections
        self._create_date_section(main_frame)
        self._create_reference_section(main_frame)
        self._create_amount_section(main_frame)
        self._create_matching_options_section(main_frame)
        self._create_buttons_section(main_frame)
    
    def _create_date_section(self, parent):
        """Create date matching section"""
        section = tk.LabelFrame(parent, text="📅 Date Column Matching", 
                               font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#1e40af")
        section.pack(fill="x", pady=(0, 15))
        
        content = tk.Frame(section, bg="#ffffff")
        content.pack(fill="x", padx=15, pady=10)
        
        # Get column options
        ledger_cols = list(self.ledger_df.columns) if self.ledger_df is not None else []
        stmt_cols = list(self.statement_df.columns) if self.statement_df is not None else []
        
        # Ledger date column
        tk.Label(content, text="Ledger Date Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
        
        self.ledger_date_var = tk.StringVar(value=self.current_settings.get('ledger_date_col', ''))
        ledger_date_combo = ttk.Combobox(content, textvariable=self.ledger_date_var, 
                                        values=ledger_cols, state="readonly", width=30)
        ledger_date_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Statement date column
        tk.Label(content, text="Statement Date Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
        
        self.stmt_date_var = tk.StringVar(value=self.current_settings.get('statement_date_col', ''))
        stmt_date_combo = ttk.Combobox(content, textvariable=self.stmt_date_var, 
                                      values=stmt_cols, state="readonly", width=30)
        stmt_date_combo.grid(row=1, column=1, padx=10, pady=5)
    
    def _create_reference_section(self, parent):
        """Create reference matching section"""
        section = tk.LabelFrame(parent, text="🏷️ Reference Column Matching", 
                               font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#7c3aed")
        section.pack(fill="x", pady=(0, 15))
        
        content = tk.Frame(section, bg="#ffffff")
        content.pack(fill="x", padx=15, pady=10)
        
        # Get column options
        ledger_cols = list(self.ledger_df.columns) if self.ledger_df is not None else []
        stmt_cols = list(self.statement_df.columns) if self.statement_df is not None else []
        
        # Ledger reference column
        tk.Label(content, text="Ledger Reference Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
        
        self.ledger_ref_var = tk.StringVar(value=self.current_settings.get('ledger_ref_col', ''))
        ledger_ref_combo = ttk.Combobox(content, textvariable=self.ledger_ref_var, 
                                       values=ledger_cols, state="readonly", width=30)
        ledger_ref_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Statement reference column
        tk.Label(content, text="Statement Reference Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
        
        self.stmt_ref_var = tk.StringVar(value=self.current_settings.get('statement_ref_col', ''))
        stmt_ref_combo = ttk.Combobox(content, textvariable=self.stmt_ref_var, 
                                     values=stmt_cols, state="readonly", width=30)
        stmt_ref_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Fuzzy matching options
        fuzzy_frame = tk.Frame(content, bg="#f3e8ff", relief="solid", bd=1)
        fuzzy_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Label(fuzzy_frame, text="🤖 Fuzzy Matching Settings", 
                font=("Segoe UI", 11, "bold"), bg="#f3e8ff", fg="#7c3aed").pack(pady=5)
        
        fuzzy_content = tk.Frame(fuzzy_frame, bg="#f3e8ff")
        fuzzy_content.pack(fill="x", padx=10, pady=5)
        
        # Enable fuzzy matching
        self.fuzzy_ref_var = tk.BooleanVar(value=self.current_settings.get('fuzzy_ref', True))
        fuzzy_check = tk.Checkbutton(fuzzy_content, text="Enable Fuzzy Reference Matching", 
                                    variable=self.fuzzy_ref_var, font=("Segoe UI", 10), 
                                    bg="#f3e8ff")
        fuzzy_check.pack(anchor="w")
        
        # Similarity threshold
        threshold_frame = tk.Frame(fuzzy_content, bg="#f3e8ff")
        threshold_frame.pack(fill="x", pady=5)
        
        tk.Label(threshold_frame, text="Similarity Threshold:", 
                font=("Segoe UI", 10), bg="#f3e8ff").pack(side="left")
        
        self.similarity_var = tk.IntVar(value=self.current_settings.get('similarity_ref', 85))
        similarity_spinbox = tk.Spinbox(threshold_frame, from_=50, to=100, 
                                       textvariable=self.similarity_var, width=10)
        similarity_spinbox.pack(side="left", padx=10)
        
        tk.Label(threshold_frame, text="%", font=("Segoe UI", 10), 
                bg="#f3e8ff").pack(side="left")
    
    def _create_amount_section(self, parent):
        """Create amount matching section"""
        section = tk.LabelFrame(parent, text="💰 Amount Column Matching", 
                               font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#059669")
        section.pack(fill="x", pady=(0, 15))
        
        content = tk.Frame(section, bg="#ffffff")
        content.pack(fill="x", padx=15, pady=10)
        
        # Get column options
        ledger_cols = list(self.ledger_df.columns) if self.ledger_df is not None else []
        stmt_cols = list(self.statement_df.columns) if self.statement_df is not None else []
        
        # Ledger debit column
        tk.Label(content, text="Ledger Debit Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
        
        self.ledger_debit_var = tk.StringVar(value=self.current_settings.get('ledger_debit_col', ''))
        ledger_debit_combo = ttk.Combobox(content, textvariable=self.ledger_debit_var, 
                                         values=ledger_cols, state="readonly", width=30)
        ledger_debit_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Ledger credit column
        tk.Label(content, text="Ledger Credit Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
        
        self.ledger_credit_var = tk.StringVar(value=self.current_settings.get('ledger_credit_col', ''))
        ledger_credit_combo = ttk.Combobox(content, textvariable=self.ledger_credit_var, 
                                          values=ledger_cols, state="readonly", width=30)
        ledger_credit_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Statement amount column
        tk.Label(content, text="Statement Amount Column:", font=("Segoe UI", 10, "bold"), 
                bg="#ffffff").grid(row=2, column=0, sticky="w", pady=5)
        
        self.stmt_amt_var = tk.StringVar(value=self.current_settings.get('statement_amt_col', ''))
        stmt_amt_combo = ttk.Combobox(content, textvariable=self.stmt_amt_var, 
                                     values=stmt_cols, state="readonly", width=30)
        stmt_amt_combo.grid(row=2, column=1, padx=10, pady=5)
    
    def _create_matching_options_section(self, parent):
        """Create matching options section"""
        section = tk.LabelFrame(parent, text="🎯 Matching Options", 
                               font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#dc2626")
        section.pack(fill="x", pady=(0, 15))
        
        content = tk.Frame(section, bg="#ffffff")
        content.pack(fill="x", padx=15, pady=10)
        
        # Matching criteria
        self.match_dates_var = tk.BooleanVar(value=self.current_settings.get('match_dates', True))
        self.match_refs_var = tk.BooleanVar(value=self.current_settings.get('match_references', True))
        self.match_amts_var = tk.BooleanVar(value=self.current_settings.get('match_amounts', True))
        
        tk.Checkbutton(content, text="Match by Dates", variable=self.match_dates_var, 
                      font=("Segoe UI", 10), bg="#ffffff").pack(anchor="w", pady=2)
        
        tk.Checkbutton(content, text="Match by References", variable=self.match_refs_var, 
                      font=("Segoe UI", 10), bg="#ffffff").pack(anchor="w", pady=2)
        
        tk.Checkbutton(content, text="Match by Amounts", variable=self.match_amts_var, 
                      font=("Segoe UI", 10), bg="#ffffff").pack(anchor="w", pady=2)
        
        # Amount matching mode
        mode_frame = tk.Frame(content, bg="#fef3c7", relief="solid", bd=1)
        mode_frame.pack(fill="x", pady=10)
        
        tk.Label(mode_frame, text="💰 Amount Matching Mode", 
                font=("Segoe UI", 11, "bold"), bg="#fef3c7", fg="#f59e0b").pack(pady=5)
        
        mode_content = tk.Frame(mode_frame, bg="#fef3c7")
        mode_content.pack(fill="x", padx=10, pady=5)
        
        self.amount_mode_var = tk.StringVar(value="both")
        if self.current_settings.get('use_debits_only', False):
            self.amount_mode_var.set("debits_only")
        elif self.current_settings.get('use_credits_only', False):
            self.amount_mode_var.set("credits_only")
        
        tk.Radiobutton(mode_content, text="Use Both Debits and Credits", 
                      variable=self.amount_mode_var, value="both", 
                      font=("Segoe UI", 10), bg="#fef3c7").pack(anchor="w")
        
        tk.Radiobutton(mode_content, text="Use Debits Only", 
                      variable=self.amount_mode_var, value="debits_only", 
                      font=("Segoe UI", 10), bg="#fef3c7").pack(anchor="w")
        
        tk.Radiobutton(mode_content, text="Use Credits Only", 
                      variable=self.amount_mode_var, value="credits_only", 
                      font=("Segoe UI", 10), bg="#fef3c7").pack(anchor="w")
    
    def _create_buttons_section(self, parent):
        """Create dialog buttons"""
        button_frame = tk.Frame(parent, bg="#f8fafc")
        button_frame.pack(fill="x", pady=20)
        
        # Save button
        save_btn = tk.Button(button_frame, text="✅ Save Configuration", 
                           font=("Segoe UI", 12, "bold"), bg="#059669", fg="white",
                           relief="flat", padx=30, pady=10, command=self._save_config, cursor="hand2")
        save_btn.pack(side="left")
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                             font=("Segoe UI", 11), bg="#6b7280", fg="white",
                             relief="flat", padx=20, pady=8, command=self._cancel_config, cursor="hand2")
        cancel_btn.pack(side="right")
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="🔄 Reset to Defaults", 
                            font=("Segoe UI", 11), bg="#f59e0b", fg="white",
                            relief="flat", padx=20, pady=8, command=self._reset_config, cursor="hand2")
        reset_btn.pack(side="right", padx=(0, 15))
    
    def _save_config(self):
        """Save configuration"""
        try:
            # Build new settings
            new_settings = {
                'ledger_date_col': self.ledger_date_var.get(),
                'statement_date_col': self.stmt_date_var.get(),
                'ledger_ref_col': self.ledger_ref_var.get(),
                'statement_ref_col': self.stmt_ref_var.get(),
                'ledger_debit_col': self.ledger_debit_var.get(),
                'ledger_credit_col': self.ledger_credit_var.get(),
                'statement_amt_col': self.stmt_amt_var.get(),
                'fuzzy_ref': self.fuzzy_ref_var.get(),
                'similarity_ref': self.similarity_var.get(),
                'match_dates': self.match_dates_var.get(),
                'match_references': self.match_refs_var.get(),
                'match_amounts': self.match_amts_var.get(),
                'use_debits_only': self.amount_mode_var.get() == 'debits_only',
                'use_credits_only': self.amount_mode_var.get() == 'credits_only',
                'use_both_debit_credit': self.amount_mode_var.get() == 'both'
            }
            
            self.result = new_settings
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to save configuration: {str(e)}")
    
    def _cancel_config(self):
        """Cancel configuration"""
        self.result = None
        self.dialog.destroy()
    
    def _reset_config(self):
        """Reset to default configuration"""
        defaults = {
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
            'match_amounts': True
        }
        
        # Update UI with defaults
        self.ledger_date_var.set(defaults['ledger_date_col'])
        self.stmt_date_var.set(defaults['statement_date_col'])
        self.ledger_ref_var.set(defaults['ledger_ref_col'])
        self.stmt_ref_var.set(defaults['statement_ref_col'])
        self.ledger_debit_var.set(defaults['ledger_debit_col'])
        self.ledger_credit_var.set(defaults['ledger_credit_col'])
        self.stmt_amt_var.set(defaults['statement_amt_col'])
        self.fuzzy_ref_var.set(defaults['fuzzy_ref'])
        self.similarity_var.set(defaults['similarity_ref'])
        self.match_dates_var.set(defaults['match_dates'])
        self.match_refs_var.set(defaults['match_references'])
        self.match_amts_var.set(defaults['match_amounts'])
        self.amount_mode_var.set('both')
        
        messagebox.showinfo("Reset Complete", "Configuration has been reset to default values")

# Continue with the reconciliation execution and results display in the next stage...
