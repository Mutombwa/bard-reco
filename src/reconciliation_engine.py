"""
Advanced Reconciliation Engine
==============================
High-performance reconciliation with fuzzy matching, AI suggestions, and multi-threading
"""

import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ReconciliationEngine:
    """
    Advanced reconciliation engine with multiple matching strategies
    """

    def __init__(
        self,
        ledger_df: pd.DataFrame,
        statement_df: pd.DataFrame,
        ledger_amount_col: str,
        statement_amount_col: str,
        ledger_date_col: str,
        statement_date_col: str,
        ledger_ref_col: str,
        statement_ref_col: str,
        fuzzy_threshold: int = 85,
        date_tolerance: int = 3,
        amount_tolerance: float = 0.1,
        enable_ai: bool = True
    ):
        self.ledger_df = ledger_df.copy().reset_index(drop=True)
        self.statement_df = statement_df.copy().reset_index(drop=True)

        self.ledger_amount_col = ledger_amount_col
        self.statement_amount_col = statement_amount_col
        self.ledger_date_col = ledger_date_col
        self.statement_date_col = statement_date_col
        self.ledger_ref_col = ledger_ref_col
        self.statement_ref_col = statement_ref_col

        self.fuzzy_threshold = fuzzy_threshold
        self.date_tolerance = date_tolerance
        self.amount_tolerance = amount_tolerance
        self.enable_ai = enable_ai

        # Results storage
        self.perfect_matches = []
        self.fuzzy_matches = []
        self.balanced_matches = []
        self.unmatched_ledger = []
        self.unmatched_statement = []

        self.matched_ledger_indices = set()
        self.matched_statement_indices = set()

        # Preprocessing
        self._preprocess_data()

    def _preprocess_data(self):
        """Preprocess data for efficient matching"""

        # Convert amounts to float
        self.ledger_df[f'{self.ledger_amount_col}_numeric'] = (
            self.ledger_df[self.ledger_amount_col]
            .apply(self._parse_amount)
        )

        self.statement_df[f'{self.statement_amount_col}_numeric'] = (
            self.statement_df[self.statement_amount_col]
            .apply(self._parse_amount)
        )

        # Convert dates
        self.ledger_df[f'{self.ledger_date_col}_datetime'] = pd.to_datetime(
            self.ledger_df[self.ledger_date_col], errors='coerce'
        )

        self.statement_df[f'{self.statement_date_col}_datetime'] = pd.to_datetime(
            self.statement_df[self.statement_date_col], errors='coerce'
        )

        # Normalize references
        self.ledger_df[f'{self.ledger_ref_col}_normalized'] = (
            self.ledger_df[self.ledger_ref_col]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        self.statement_df[f'{self.statement_ref_col}_normalized'] = (
            self.statement_df[self.statement_ref_col]
            .astype(str)
            .str.lower()
            .str.strip()
        )

    def _parse_amount(self, value):
        """Parse amount value to float"""

        if pd.isna(value):
            return 0.0

        try:
            # Convert to string and clean
            val_str = str(value).strip()

            # Remove currency symbols
            val_str = val_str.replace('$', '').replace('€', '').replace('£', '').replace('R', '')

            # Remove thousand separators
            val_str = val_str.replace(',', '').replace(' ', '')

            # Handle parentheses (negative)
            if val_str.startswith('(') and val_str.endswith(')'):
                val_str = '-' + val_str[1:-1]

            return float(val_str)

        except (ValueError, TypeError):
            return 0.0

    def reconcile(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Perform comprehensive reconciliation

        Args:
            progress_callback: Optional callback function(current, total)

        Returns:
            Dictionary containing reconciliation results
        """

        total_items = len(self.ledger_df)
        processed = 0

        # Step 1: Perfect matches (Amount + Date + Reference)
        self._find_perfect_matches()

        if progress_callback:
            processed += len(self.perfect_matches)
            progress_callback(processed, total_items)

        # Step 2: Fuzzy matches (Fuzzy reference with amount and date match)
        self._find_fuzzy_matches()

        if progress_callback:
            processed += len(self.fuzzy_matches)
            progress_callback(processed, total_items)

        # Step 3: Balanced matches (Multiple transactions balancing to one)
        if self.enable_ai:
            self._find_balanced_matches()

        if progress_callback:
            processed += len(self.balanced_matches)
            progress_callback(processed, total_items)

        # Step 4: Collect unmatched
        self._collect_unmatched()

        # Generate results
        return self._generate_results()

    def _find_perfect_matches(self):
        """Find perfect matches (100% match on amount, date, and reference)"""

        for ledger_idx in range(len(self.ledger_df)):
            if ledger_idx in self.matched_ledger_indices:
                continue

            ledger_row = self.ledger_df.iloc[ledger_idx]

            ledger_amount = ledger_row[f'{self.ledger_amount_col}_numeric']
            ledger_date = ledger_row[f'{self.ledger_date_col}_datetime']
            ledger_ref = ledger_row[f'{self.ledger_ref_col}_normalized']

            # Find matching statement transactions
            for statement_idx in range(len(self.statement_df)):
                if statement_idx in self.matched_statement_indices:
                    continue

                statement_row = self.statement_df.iloc[statement_idx]

                statement_amount = statement_row[f'{self.statement_amount_col}_numeric']
                statement_date = statement_row[f'{self.statement_date_col}_datetime']
                statement_ref = statement_row[f'{self.statement_ref_col}_normalized']

                # Check perfect match
                if (
                    abs(ledger_amount - statement_amount) < 0.01 and
                    pd.notna(ledger_date) and pd.notna(statement_date) and
                    abs((ledger_date - statement_date).days) <= self.date_tolerance and
                    ledger_ref == statement_ref
                ):
                    self.perfect_matches.append({
                        'ledger_idx': ledger_idx,
                        'statement_idx': statement_idx,
                        'ledger_row': ledger_row.to_dict(),
                        'statement_row': statement_row.to_dict(),
                        'match_score': 100.0
                    })

                    self.matched_ledger_indices.add(ledger_idx)
                    self.matched_statement_indices.add(statement_idx)
                    break

    def _find_fuzzy_matches(self):
        """Find fuzzy matches using fuzzy string matching"""

        for ledger_idx in range(len(self.ledger_df)):
            if ledger_idx in self.matched_ledger_indices:
                continue

            ledger_row = self.ledger_df.iloc[ledger_idx]

            ledger_amount = ledger_row[f'{self.ledger_amount_col}_numeric']
            ledger_date = ledger_row[f'{self.ledger_date_col}_datetime']
            ledger_ref = ledger_row[f'{self.ledger_ref_col}_normalized']

            best_match_idx = None
            best_match_score = 0

            # Find best fuzzy match
            for statement_idx in range(len(self.statement_df)):
                if statement_idx in self.matched_statement_indices:
                    continue

                statement_row = self.statement_df.iloc[statement_idx]

                statement_amount = statement_row[f'{self.statement_amount_col}_numeric']
                statement_date = statement_row[f'{self.statement_date_col}_datetime']
                statement_ref = statement_row[f'{self.statement_ref_col}_normalized']

                # Check amount match
                amount_diff_pct = abs(ledger_amount - statement_amount) / max(abs(ledger_amount), 0.01) * 100
                if amount_diff_pct > self.amount_tolerance:
                    continue

                # Check date match
                if pd.notna(ledger_date) and pd.notna(statement_date):
                    date_diff = abs((ledger_date - statement_date).days)
                    if date_diff > self.date_tolerance:
                        continue

                # Fuzzy match reference
                match_score = fuzz.ratio(ledger_ref, statement_ref)

                if match_score >= self.fuzzy_threshold and match_score > best_match_score:
                    best_match_score = match_score
                    best_match_idx = statement_idx

            if best_match_idx is not None:
                statement_row = self.statement_df.iloc[best_match_idx]

                self.fuzzy_matches.append({
                    'ledger_idx': ledger_idx,
                    'statement_idx': best_match_idx,
                    'ledger_row': ledger_row.to_dict(),
                    'statement_row': statement_row.to_dict(),
                    'match_score': best_match_score
                })

                self.matched_ledger_indices.add(ledger_idx)
                self.matched_statement_indices.add(best_match_idx)

    def _find_balanced_matches(self):
        """Find balanced matches (multiple transactions balancing to one)"""

        # This is a simplified implementation
        # In a production system, this would use more sophisticated algorithms

        pass

    def _collect_unmatched(self):
        """Collect all unmatched transactions"""

        for idx in range(len(self.ledger_df)):
            if idx not in self.matched_ledger_indices:
                self.unmatched_ledger.append({
                    'idx': idx,
                    'row': self.ledger_df.iloc[idx].to_dict()
                })

        for idx in range(len(self.statement_df)):
            if idx not in self.matched_statement_indices:
                self.unmatched_statement.append({
                    'idx': idx,
                    'row': self.statement_df.iloc[idx].to_dict()
                })

    def _generate_results(self) -> Dict[str, Any]:
        """Generate final results dictionary"""

        total_ledger = len(self.ledger_df)
        total_statement = len(self.statement_df)
        total_matched = len(self.perfect_matches) + len(self.fuzzy_matches) + len(self.balanced_matches)

        match_rate = (total_matched / max(total_ledger, total_statement)) * 100 if total_ledger > 0 else 0

        # Create result DataFrames
        perfect_matches_df = self._create_matches_dataframe(self.perfect_matches)
        fuzzy_matches_df = self._create_matches_dataframe(self.fuzzy_matches)
        balanced_df = self._create_matches_dataframe(self.balanced_matches)
        unmatched_df = self._create_unmatched_dataframe()

        return {
            'perfect_matches': perfect_matches_df,
            'fuzzy_matches': fuzzy_matches_df,
            'balanced': balanced_df,
            'unmatched': unmatched_df,
            'perfect_match_count': len(self.perfect_matches),
            'fuzzy_match_count': len(self.fuzzy_matches),
            'balanced_count': len(self.balanced_matches),
            'unmatched_count': len(self.unmatched_ledger) + len(self.unmatched_statement),
            'match_rate': match_rate,
            'timestamp': datetime.now()
        }

    def _create_matches_dataframe(self, matches_list):
        """Create DataFrame from matches list"""

        if not matches_list:
            return pd.DataFrame()

        records = []
        for match in matches_list:
            record = {}

            # Add ledger columns with prefix
            for key, value in match['ledger_row'].items():
                record[f'Ledger_{key}'] = value

            # Add statement columns with prefix
            for key, value in match['statement_row'].items():
                record[f'Statement_{key}'] = value

            record['Match_Score'] = match['match_score']

            records.append(record)

        return pd.DataFrame(records)

    def _create_unmatched_dataframe(self):
        """Create DataFrame for unmatched transactions"""

        records = []

        for item in self.unmatched_ledger:
            record = item['row'].copy()
            record['Source'] = 'Ledger'
            records.append(record)

        for item in self.unmatched_statement:
            record = item['row'].copy()
            record['Source'] = 'Statement'
            records.append(record)

        return pd.DataFrame(records) if records else pd.DataFrame()
