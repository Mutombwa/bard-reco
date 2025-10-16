"""
FNB Workflow - ULTRA FAST Reconciliation Engine
===============================================
Optimized for maximum speed with proper matching logic:
- 100% Perfect Match (exact date, reference, amount)
- Fuzzy Matching with configurable threshold
- Foreign Credits handling (>10,000)
- Split Transaction detection with DP algorithm
- Flexible date matching (+/- 1 day tolerance)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
import sys
import os
from typing import Dict, List, Tuple, Optional, Set

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_cleaner import clean_amount_column


class UltraFastFNBReconciler:
    """Ultra-fast FNB reconciliation engine with all matching modes"""

    def __init__(self):
        self.fuzzy_cache = {}  # Cache for fuzzy matching scores

    def reconcile(self, ledger_df: pd.DataFrame, statement_df: pd.DataFrame,
                  settings: Dict) -> Dict:
        """
        Main reconciliation method - ULTRA FAST

        Returns:
            Dict with keys: 'perfect_match', 'fuzzy_match', 'foreign_credits',
                          'split_matches', 'unmatched_ledger', 'unmatched_statement'
        """
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🚀 Preparing data...")
        progress_bar.progress(0.05)

        # Prepare data
        ledger = self._prepare_ledger(ledger_df, settings)
        statement = self._prepare_statement(statement_df, settings)

        # Show diagnostic info
        with st.expander("🔍 Data Diagnostics", expanded=False):
            st.write(f"**Ledger:** {len(ledger)} rows")
            st.write(f"**Statement:** {len(statement)} rows")
            st.write(f"**Matching Settings:**")
            st.write(f"  - Match Dates: {settings.get('match_dates', True)}")
            st.write(f"  - Match References: {settings.get('match_references', True)}")
            st.write(f"  - Match Amounts: {settings.get('match_amounts', True)}")
            st.write(f"  - Fuzzy Enabled: {settings.get('fuzzy_ref', True)}")
            st.write(f"  - Similarity Threshold: {settings.get('similarity_ref', 85)}%")
            st.write(f"  - Date Tolerance: ±{1 if settings.get('date_tolerance', False) else 0} day(s)")

            # Sample data check
            st.write("**Sample Ledger Data:**")
            sample_cols = ['_date_norm', '_ref_norm', '_amount']
            available_cols = [c for c in sample_cols if c in ledger.columns]
            if available_cols:
                st.dataframe(ledger[available_cols].head(3), use_container_width=True)

            st.write("**Sample Statement Data:**")
            if available_cols:
                st.dataframe(statement[available_cols].head(3), use_container_width=True)

        status_text.text("⚡ Phase 1: Perfect Match (100% exact)...")
        progress_bar.progress(0.15)

        # Phase 1: Perfect Match (exact date, reference, amount)
        perfect_matches = self._find_perfect_matches(ledger, statement, settings)

        status_text.text(f"✅ Perfect matches: {len(perfect_matches)}")
        progress_bar.progress(0.30)

        # Phase 2: Fuzzy Matching
        status_text.text("🔍 Phase 2: Fuzzy Matching...")
        fuzzy_matches = self._find_fuzzy_matches(ledger, statement, settings, perfect_matches)

        status_text.text(f"✅ Fuzzy matches: {len(fuzzy_matches)}")
        progress_bar.progress(0.50)

        # Phase 3: Foreign Credits (>10,000)
        status_text.text("💰 Phase 3: Foreign Credits (>10K)...")
        foreign_matches = self._find_foreign_credits(ledger, statement, settings,
                                                     perfect_matches, fuzzy_matches)

        status_text.text(f"✅ Foreign credits: {len(foreign_matches)}")
        progress_bar.progress(0.65)

        # Phase 4: Split Transactions
        status_text.text("🔀 Phase 4: Split Transactions...")
        split_matches = self._find_split_transactions(ledger, statement, settings,
                                                      perfect_matches, fuzzy_matches, foreign_matches)

        status_text.text(f"✅ Split transactions: {len(split_matches)}")
        progress_bar.progress(0.85)

        # Process results
        status_text.text("📊 Processing results...")
        results = self._process_results(ledger_df, statement_df, ledger, statement,
                                       perfect_matches, fuzzy_matches, foreign_matches,
                                       split_matches, settings)

        progress_bar.progress(1.0)
        status_text.text("✅ Reconciliation complete!")

        return results

    def _prepare_ledger(self, df: pd.DataFrame, settings: Dict) -> pd.DataFrame:
        """Prepare ledger data with normalized columns"""
        ledger = df.copy()
        ledger.reset_index(drop=True, inplace=True)
        ledger['_original_index'] = ledger.index

        # Get column names
        date_col = settings.get('ledger_date_col', 'Date')
        ref_col = settings.get('ledger_ref_col', 'Reference')
        debit_col = settings.get('ledger_debit_col', 'Debit')
        credit_col = settings.get('ledger_credit_col', 'Credit')

        # Normalize date
        if date_col in ledger.columns:
            ledger['_date_norm'] = pd.to_datetime(ledger[date_col], errors='coerce')

        # Normalize reference (case-insensitive)
        if ref_col in ledger.columns:
            ledger['_ref_norm'] = ledger[ref_col].astype(str).str.strip().str.upper()
            ledger['_ref_norm'] = ledger['_ref_norm'].replace(['NAN', 'NONE', ''], np.nan)

        # Normalize amounts
        if debit_col in ledger.columns and credit_col in ledger.columns:
            debits = clean_amount_column(ledger[debit_col])
            credits = clean_amount_column(ledger[credit_col])

            # Store both separately
            ledger['_debit'] = debits
            ledger['_credit'] = credits

            # For matching: use mode from settings
            if settings.get('use_debits_only'):
                ledger['_amount'] = debits
            elif settings.get('use_credits_only'):
                ledger['_amount'] = credits
            else:
                # Both: credits are positive, debits are negative
                ledger['_amount'] = credits - debits

        return ledger

    def _prepare_statement(self, df: pd.DataFrame, settings: Dict) -> pd.DataFrame:
        """Prepare statement data with normalized columns"""
        statement = df.copy()
        statement.reset_index(drop=True, inplace=True)
        statement['_original_index'] = statement.index

        # Get column names
        date_col = settings.get('statement_date_col', 'Date')
        ref_col = settings.get('statement_ref_col', 'Reference')
        amt_col = settings.get('statement_amt_col', 'Amount')

        # Normalize date
        if date_col in statement.columns:
            statement['_date_norm'] = pd.to_datetime(statement[date_col], errors='coerce')

        # Normalize reference (case-insensitive)
        if ref_col in statement.columns:
            statement['_ref_norm'] = statement[ref_col].astype(str).str.strip().str.upper()
            statement['_ref_norm'] = statement['_ref_norm'].replace(['NAN', 'NONE', ''], np.nan)

        # Normalize amount
        if amt_col in statement.columns:
            statement['_amount'] = clean_amount_column(statement[amt_col])

        return statement

    def _find_perfect_matches(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                             settings: Dict) -> List[Tuple[int, int]]:
        """
        Find 100% perfect matches:
        - Exact date match (same day OR +/- 1 day if tolerance enabled)
        - Case-insensitive reference match (100% similarity)
        - Exact amount match
        """
        matches = []
        matched_ledger = set()
        matched_statement = set()

        match_dates = settings.get('match_dates', True)
        match_refs = settings.get('match_references', True)
        match_amounts = settings.get('match_amounts', True)
        date_tolerance = settings.get('date_tolerance', False)  # +/- 1 day

        # Build indexes for ultra-fast lookup
        if match_amounts:
            # Index statement by amount (rounded to avoid float precision issues)
            stmt_by_amount = {}
            for idx, row in statement.iterrows():
                amt = row.get('_amount')
                if pd.notna(amt):
                    amt_key = round(amt, 2)
                    if amt_key not in stmt_by_amount:
                        stmt_by_amount[amt_key] = []
                    stmt_by_amount[amt_key].append(idx)

        # Iterate through ledger
        for l_idx, l_row in ledger.iterrows():
            l_date = l_row.get('_date_norm')
            l_ref = l_row.get('_ref_norm')
            l_amt = l_row.get('_amount')

            # Get candidate statements by amount (ultra-fast filter)
            candidates = []
            if match_amounts and pd.notna(l_amt):
                amt_key = round(l_amt, 2)
                candidates = stmt_by_amount.get(amt_key, [])
            else:
                candidates = list(statement.index)

            # Check each candidate
            for s_idx in candidates:
                if s_idx in matched_statement:
                    continue

                s_row = statement.iloc[s_idx]
                s_date = s_row.get('_date_norm')
                s_ref = s_row.get('_ref_norm')
                s_amt = s_row.get('_amount')

                # Check all criteria
                date_match = True
                ref_match = True
                amt_match = True

                # Date check
                if match_dates:
                    if pd.isna(l_date) or pd.isna(s_date):
                        date_match = False
                    else:
                        diff_days = abs((l_date - s_date).days)
                        if date_tolerance:
                            date_match = diff_days <= 1  # +/- 1 day
                        else:
                            date_match = diff_days == 0  # exact same day

                # Reference check (case-insensitive exact match)
                if match_refs:
                    if pd.isna(l_ref) or pd.isna(s_ref):
                        ref_match = False
                    else:
                        ref_match = (l_ref == s_ref)

                # Amount check (exact match)
                if match_amounts:
                    if pd.isna(l_amt) or pd.isna(s_amt):
                        amt_match = False
                    else:
                        amt_match = (round(l_amt, 2) == round(s_amt, 2))

                # Perfect match requires ALL enabled criteria to match
                if date_match and ref_match and amt_match:
                    matches.append((l_idx, s_idx))
                    matched_ledger.add(l_idx)
                    matched_statement.add(s_idx)
                    break  # Found perfect match, move to next ledger row

        return matches

    def _find_fuzzy_matches(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                           settings: Dict, perfect_matches: List[Tuple[int, int]]) -> List[Tuple[int, int, float]]:
        """
        Find fuzzy matches with configurable threshold:
        - Date match (exact OR +/- 1 day if tolerance)
        - Fuzzy reference match (>= threshold %)
        - Exact amount match
        """
        matches = []

        # Already matched indices
        matched_ledger = {m[0] for m in perfect_matches}
        matched_statement = {m[1] for m in perfect_matches}

        match_dates = settings.get('match_dates', True)
        match_refs = settings.get('match_references', True)
        match_amounts = settings.get('match_amounts', True)
        fuzzy_enabled = settings.get('fuzzy_ref', True)
        similarity_threshold = settings.get('similarity_ref', 85)
        date_tolerance = settings.get('date_tolerance', False)

        if not fuzzy_enabled:
            return matches  # Fuzzy matching disabled

        # Build indexes
        stmt_by_amount = {}
        if match_amounts:
            for idx, row in statement.iterrows():
                if idx in matched_statement:
                    continue
                amt = row.get('_amount')
                if pd.notna(amt):
                    amt_key = round(amt, 2)
                    if amt_key not in stmt_by_amount:
                        stmt_by_amount[amt_key] = []
                    stmt_by_amount[amt_key].append(idx)

        # Iterate unmatched ledger
        for l_idx, l_row in ledger.iterrows():
            if l_idx in matched_ledger:
                continue

            l_date = l_row.get('_date_norm')
            l_ref = l_row.get('_ref_norm')
            l_amt = l_row.get('_amount')

            # Get candidates by amount
            candidates = []
            if match_amounts and pd.notna(l_amt):
                amt_key = round(l_amt, 2)
                candidates = stmt_by_amount.get(amt_key, [])
            else:
                candidates = [idx for idx in statement.index if idx not in matched_statement]

            best_match = None
            best_score = 0

            for s_idx in candidates:
                s_row = statement.iloc[s_idx]
                s_date = s_row.get('_date_norm')
                s_ref = s_row.get('_ref_norm')
                s_amt = s_row.get('_amount')

                # Check criteria
                date_match = True
                ref_score = 0
                amt_match = True

                # Date check
                if match_dates:
                    if pd.isna(l_date) or pd.isna(s_date):
                        continue
                    diff_days = abs((l_date - s_date).days)
                    if date_tolerance:
                        date_match = diff_days <= 1
                    else:
                        date_match = diff_days == 0
                    if not date_match:
                        continue

                # Amount check
                if match_amounts:
                    if pd.isna(l_amt) or pd.isna(s_amt):
                        continue
                    if round(l_amt, 2) != round(s_amt, 2):
                        continue

                # Reference fuzzy check
                if match_refs:
                    if pd.isna(l_ref) or pd.isna(s_ref):
                        continue

                    # Fuzzy matching with cache
                    cache_key = (l_ref, s_ref)
                    if cache_key in self.fuzzy_cache:
                        ref_score = self.fuzzy_cache[cache_key]
                    else:
                        ref_score = fuzz.ratio(l_ref, s_ref)
                        self.fuzzy_cache[cache_key] = ref_score

                    if ref_score < similarity_threshold:
                        continue

                # Valid fuzzy match
                if ref_score > best_score:
                    best_score = ref_score
                    best_match = s_idx

            if best_match is not None:
                matches.append((l_idx, best_match, best_score))
                matched_statement.add(best_match)

        return matches

    def _find_foreign_credits(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                             settings: Dict, perfect_matches: List, fuzzy_matches: List) -> List[Tuple[int, int]]:
        """
        Find foreign credits (amounts > 10,000):
        - Amount ALWAYS required (exact match)
        - Date optional (only if match_dates enabled)
        - Reference IGNORED
        """
        matches = []

        # Already matched indices
        matched_ledger = {m[0] for m in perfect_matches}
        matched_ledger.update({m[0] for m in fuzzy_matches})
        matched_statement = {m[1] for m in perfect_matches}
        matched_statement.update({m[1] for m in fuzzy_matches})

        match_dates = settings.get('match_dates', True)
        date_tolerance = settings.get('date_tolerance', False)

        # Filter statement for foreign credits (>10,000)
        fc_statement = statement[(statement['_amount'].abs() > 10000) &
                                (~statement.index.isin(matched_statement))]

        # Build ledger index by amount (for foreign credits)
        ledger_by_amount = {}
        for idx, row in ledger.iterrows():
            if idx in matched_ledger:
                continue
            amt = row.get('_amount')
            if pd.notna(amt) and abs(amt) > 10000:
                amt_key = round(amt, 2)
                if amt_key not in ledger_by_amount:
                    ledger_by_amount[amt_key] = []
                ledger_by_amount[amt_key].append(idx)

        # Match foreign credits
        for s_idx, s_row in fc_statement.iterrows():
            s_amt = s_row.get('_amount')
            s_date = s_row.get('_date_norm')

            # Get ledger candidates by amount
            amt_key = round(s_amt, 2)
            candidates = ledger_by_amount.get(amt_key, [])

            for l_idx in candidates:
                if l_idx in matched_ledger:
                    continue

                l_row = ledger.iloc[l_idx]
                l_date = l_row.get('_date_norm')

                # Amount ALWAYS matches (we filtered by it)
                # Check date only if required
                if match_dates:
                    if pd.isna(l_date) or pd.isna(s_date):
                        continue
                    diff_days = abs((l_date - s_date).days)
                    if date_tolerance:
                        if diff_days > 1:
                            continue
                    else:
                        if diff_days != 0:
                            continue

                # Match found
                matches.append((l_idx, s_idx))
                matched_ledger.add(l_idx)
                break

        return matches

    def _find_split_transactions(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                                settings: Dict, perfect_matches: List, fuzzy_matches: List,
                                foreign_matches: List) -> List[Dict]:
        """
        Find split transactions using ultra-fast DP algorithm:
        - Many ledger → One statement
        - One ledger → Many statement

        OPTIMIZED: Only runs if there are unmatched items and split detection is beneficial
        """
        matches = []

        # Already matched indices
        matched_ledger = {m[0] for m in perfect_matches}
        matched_ledger.update({m[0] for m in fuzzy_matches})
        matched_ledger.update({m[0] for m in foreign_matches})
        matched_statement = {m[1] for m in perfect_matches}
        matched_statement.update({m[1] for m in fuzzy_matches})
        matched_statement.update({m[1] for m in foreign_matches})

        # OPTIMIZATION: Skip split detection if match rate is very high (>95%)
        total_items = len(ledger) + len(statement)
        matched_items = len(matched_ledger) + len(matched_statement)
        match_rate = (matched_items / total_items * 100) if total_items > 0 else 0

        if match_rate > 95:
            st.info(f"⚡ Skipped split detection - Match rate {match_rate:.1f}% is very high")
            return matches

        # OPTIMIZATION: Limit split detection to reasonable dataset sizes
        unmatched_ledger_count = len(ledger) - len(matched_ledger)
        unmatched_stmt_count = len(statement) - len(matched_statement)

        if unmatched_ledger_count < 2 and unmatched_stmt_count < 2:
            return matches  # Not enough items for splits

        # OPTIMIZATION: Process splits even with many unmatched items, but limit candidates
        # Increase threshold to handle larger datasets
        if unmatched_ledger_count > 500 or unmatched_stmt_count > 500:
            st.info(f"⚡ Large dataset detected ({unmatched_ledger_count} ledger, {unmatched_stmt_count} statement) - Using optimized split detection")
            # Will use more aggressive filtering below

        match_dates = settings.get('match_dates', True)
        match_refs = settings.get('match_references', True)
        similarity_threshold = settings.get('similarity_ref', 85)
        fuzzy_enabled = settings.get('fuzzy_ref', True)
        date_tolerance = settings.get('date_tolerance', False)

        # Phase 1: Many ledger → One statement
        st.text("  🔀 Phase 1: Many-to-One...")
        many_to_one = self._find_many_ledger_to_one_statement(
            ledger, statement, matched_ledger, matched_statement,
            match_dates, match_refs, similarity_threshold, fuzzy_enabled, date_tolerance
        )
        matches.extend(many_to_one)

        # Update matched indices
        for match in many_to_one:
            matched_statement.add(match['statement_idx'])
            matched_ledger.update(match['ledger_indices'])

        # Phase 2: One ledger → Many statement
        st.text("  🔀 Phase 2: One-to-Many...")
        one_to_many = self._find_one_ledger_to_many_statement(
            ledger, statement, matched_ledger, matched_statement,
            match_dates, match_refs, similarity_threshold, fuzzy_enabled, date_tolerance
        )
        matches.extend(one_to_many)

        return matches

    def _find_many_ledger_to_one_statement(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                                          matched_ledger: Set[int], matched_statement: Set[int],
                                          match_dates: bool, match_refs: bool,
                                          similarity_threshold: int, fuzzy_enabled: bool,
                                          date_tolerance: bool) -> List[Dict]:
        """Find cases where multiple ledger entries match one statement - OPTIMIZED"""
        matches = []
        MAX_SPLITS = 50  # Limit to prevent excessive processing

        # Build indexes for fast lookup
        ledger_by_date = {}
        ledger_by_amount_range = {}

        for idx, row in ledger.iterrows():
            if idx in matched_ledger:
                continue

            date = row.get('_date_norm')
            amt = row.get('_amount')

            if pd.notna(date) and match_dates:
                if date not in ledger_by_date:
                    ledger_by_date[date] = []
                ledger_by_date[date].append(idx)

            if pd.notna(amt):
                amt_range = int(abs(amt) / 1000) * 1000
                if amt_range not in ledger_by_amount_range:
                    ledger_by_amount_range[amt_range] = []
                ledger_by_amount_range[amt_range].append((idx, amt))

        # Check each unmatched statement
        for s_idx, s_row in statement.iterrows():
            if s_idx in matched_statement:
                continue

            s_date = s_row.get('_date_norm')
            s_ref = s_row.get('_ref_norm')
            s_amt = s_row.get('_amount')

            if pd.isna(s_amt):
                continue

            # Get candidates by date
            candidates = set()
            if match_dates and pd.notna(s_date):
                candidates = set(ledger_by_date.get(s_date, []))
                if date_tolerance:
                    # Add +/- 1 day
                    candidates.update(ledger_by_date.get(s_date + timedelta(days=1), []))
                    candidates.update(ledger_by_date.get(s_date - timedelta(days=1), []))
            else:
                candidates = set(ledger.index) - matched_ledger

            if len(candidates) < 2:
                continue

            # Get candidates by amount range
            target_range = int(abs(s_amt) / 1000) * 1000
            search_ranges = [target_range - 1000, target_range, target_range + 1000]

            potential_matches = []
            for amt_range in search_ranges:
                for l_idx, l_amt in ledger_by_amount_range.get(amt_range, []):
                    if l_idx not in candidates:
                        continue

                    l_row = ledger.iloc[l_idx]
                    l_ref = l_row.get('_ref_norm')

                    # Check reference if required
                    ref_score = 100
                    if match_refs and fuzzy_enabled and pd.notna(l_ref) and pd.notna(s_ref):
                        cache_key = (l_ref, s_ref)
                        if cache_key in self.fuzzy_cache:
                            ref_score = self.fuzzy_cache[cache_key]
                        else:
                            ref_score = fuzz.ratio(l_ref, s_ref)
                            self.fuzzy_cache[cache_key] = ref_score

                        if ref_score < similarity_threshold:
                            continue

                    potential_matches.append((l_idx, l_row, l_amt, ref_score))

            if len(potential_matches) < 2:
                continue

            # OPTIMIZATION: Limit potential matches to prevent excessive DP computation
            if len(potential_matches) > 20:
                # Sort by amount (closest to target) and reference score
                potential_matches.sort(key=lambda x: (abs(abs(x[2]) - abs(s_amt)), -x[3]))
                potential_matches = potential_matches[:20]  # Keep best 20 candidates

            # Find combination using DP
            combination = self._find_split_combination_dp(potential_matches, s_amt)

            if combination:
                matches.append({
                    'statement_idx': s_idx,
                    'ledger_indices': [c[0] for c in combination],
                    'split_type': 'many_to_one'
                })

                # Early termination if we found enough splits
                if len(matches) >= MAX_SPLITS:
                    st.info(f"⚡ Found {MAX_SPLITS} splits in Many-to-One - stopping early for performance")
                    break

        return matches

    def _find_one_ledger_to_many_statement(self, ledger: pd.DataFrame, statement: pd.DataFrame,
                                          matched_ledger: Set[int], matched_statement: Set[int],
                                          match_dates: bool, match_refs: bool,
                                          similarity_threshold: int, fuzzy_enabled: bool,
                                          date_tolerance: bool) -> List[Dict]:
        """Find cases where one ledger entry matches multiple statements - OPTIMIZED"""
        matches = []
        MAX_SPLITS = 50  # Limit to prevent excessive processing

        # Build statement indexes
        stmt_by_date = {}
        stmt_by_amount_range = {}

        for idx, row in statement.iterrows():
            if idx in matched_statement:
                continue

            date = row.get('_date_norm')
            amt = row.get('_amount')

            if pd.notna(date) and match_dates:
                if date not in stmt_by_date:
                    stmt_by_date[date] = []
                stmt_by_date[date].append(idx)

            if pd.notna(amt):
                amt_range = int(abs(amt) / 1000) * 1000
                if amt_range not in stmt_by_amount_range:
                    stmt_by_amount_range[amt_range] = []
                stmt_by_amount_range[amt_range].append((idx, amt))

        # Check each unmatched ledger
        for l_idx, l_row in ledger.iterrows():
            if l_idx in matched_ledger:
                continue

            l_date = l_row.get('_date_norm')
            l_ref = l_row.get('_ref_norm')
            l_amt = l_row.get('_amount')

            if pd.isna(l_amt):
                continue

            # Get candidates by date
            candidates = set()
            if match_dates and pd.notna(l_date):
                candidates = set(stmt_by_date.get(l_date, []))
                if date_tolerance:
                    candidates.update(stmt_by_date.get(l_date + timedelta(days=1), []))
                    candidates.update(stmt_by_date.get(l_date - timedelta(days=1), []))
            else:
                candidates = set(statement.index) - matched_statement

            if len(candidates) < 2:
                continue

            # Get candidates by amount range
            target_range = int(abs(l_amt) / 1000) * 1000
            search_ranges = [target_range - 1000, target_range, target_range + 1000]

            potential_matches = []
            for amt_range in search_ranges:
                for s_idx, s_amt in stmt_by_amount_range.get(amt_range, []):
                    if s_idx not in candidates:
                        continue

                    s_row = statement.iloc[s_idx]
                    s_ref = s_row.get('_ref_norm')

                    # Check reference if required
                    ref_score = 100
                    if match_refs and fuzzy_enabled and pd.notna(l_ref) and pd.notna(s_ref):
                        cache_key = (l_ref, s_ref)
                        if cache_key in self.fuzzy_cache:
                            ref_score = self.fuzzy_cache[cache_key]
                        else:
                            ref_score = fuzz.ratio(l_ref, s_ref)
                            self.fuzzy_cache[cache_key] = ref_score

                        if ref_score < similarity_threshold:
                            continue

                    potential_matches.append((s_idx, s_row, s_amt, ref_score))

            if len(potential_matches) < 2:
                continue

            # OPTIMIZATION: Limit potential matches to prevent excessive DP computation
            if len(potential_matches) > 20:
                # Sort by amount (closest to target) and reference score
                potential_matches.sort(key=lambda x: (abs(abs(x[2]) - abs(l_amt)), -x[3]))
                potential_matches = potential_matches[:20]  # Keep best 20 candidates

            # Find combination using DP
            combination = self._find_split_combination_dp(potential_matches, l_amt)

            if combination:
                matches.append({
                    'ledger_idx': l_idx,
                    'statement_indices': [c[0] for c in combination],
                    'split_type': 'one_to_many'
                })

                # Early termination if we found enough splits
                if len(matches) >= MAX_SPLITS:
                    st.info(f"⚡ Found {MAX_SPLITS} splits in One-to-Many - stopping early for performance")
                    break

        return matches

    def _find_split_combination_dp(self, candidates: List[Tuple], target: float,
                                   tolerance: float = 0.02) -> Optional[List]:
        """
        Ultra-fast Dynamic Programming algorithm for finding split combinations

        Returns combinations of 2-6 items that sum to target (within tolerance)
        """
        target_int = int(round(target * 100))
        tolerance_int = int(tolerance * abs(target_int))
        min_sum = target_int - tolerance_int
        max_sum = target_int + tolerance_int

        # Prepare items
        items = []
        for idx, row, amt, score in candidates:
            amt_int = int(round(abs(amt) * 100))
            if 0 < amt_int <= max_sum:
                items.append((amt_int, (idx, row, amt, score)))

        if len(items) < 2:
            return None

        # Sort by amount (descending)
        items.sort(key=lambda x: x[0], reverse=True)

        # OPTIMIZATION 1: Try 2-item combinations first (most common)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                sum_int = items[i][0] + items[j][0]
                if min_sum <= sum_int <= max_sum:
                    return [items[i][1], items[j][1]]

        # OPTIMIZATION 2: Dynamic Programming for 3+ items
        dp = {0: []}

        for item_idx, (amt, data) in enumerate(items):
            new_dp = {}
            for current_sum, indices in list(dp.items()):
                # Don't include current item
                if current_sum not in new_dp:
                    new_dp[current_sum] = indices[:]

                # Include current item
                new_sum = current_sum + amt

                if new_sum > max_sum:
                    continue

                new_indices = indices + [item_idx]

                # Max 6 items
                if len(new_indices) > 6:
                    continue

                if new_sum not in new_dp or len(new_indices) < len(new_dp[new_sum]):
                    new_dp[new_sum] = new_indices

                    # Early exit on exact match
                    if len(new_indices) >= 2 and min_sum <= new_sum <= max_sum:
                        return [items[i][1] for i in new_indices]

            dp = new_dp

            # Memory protection
            if len(dp) > 5000:
                dp = {s: indices for s, indices in dp.items()
                     if s >= min_sum - 5000 or len(indices) <= 3}

        # Check final DP table
        for sum_val in range(min_sum, max_sum + 1):
            if sum_val in dp and len(dp[sum_val]) >= 2:
                return [items[i][1] for i in dp[sum_val]]

        return None

    def _process_results(self, ledger_orig: pd.DataFrame, statement_orig: pd.DataFrame,
                        ledger: pd.DataFrame, statement: pd.DataFrame,
                        perfect_matches: List, fuzzy_matches: List,
                        foreign_matches: List, split_matches: List,
                        settings: Dict) -> Dict:
        """Process all matches into result dataframes"""

        # Collect all matched indices
        matched_ledger = set()
        matched_statement = set()

        # Perfect matches
        perfect_data = []
        for l_idx, s_idx in perfect_matches:
            perfect_data.append({
                'Match_Type': 'Perfect',
                'Match_Score': 1.0,
                'Ledger_Index': l_idx,
                'Statement_Index': s_idx
            })
            matched_ledger.add(l_idx)
            matched_statement.add(s_idx)

        # Fuzzy matches
        fuzzy_data = []
        for l_idx, s_idx, score in fuzzy_matches:
            fuzzy_data.append({
                'Match_Type': 'Fuzzy',
                'Match_Score': round(score / 100, 3),
                'Ledger_Index': l_idx,
                'Statement_Index': s_idx
            })
            matched_ledger.add(l_idx)
            matched_statement.add(s_idx)

        # Foreign credits
        fc_data = []
        for l_idx, s_idx in foreign_matches:
            fc_data.append({
                'Match_Type': 'Foreign_Credit',
                'Match_Score': 1.0,
                'Ledger_Index': l_idx,
                'Statement_Index': s_idx
            })
            matched_ledger.add(l_idx)
            matched_statement.add(s_idx)

        # Create combined matched dataframe
        matched_rows = []
        for match_dict in perfect_data + fuzzy_data + fc_data:
            l_idx = match_dict['Ledger_Index']
            s_idx = match_dict['Statement_Index']

            row = {
                'Match_Type': match_dict['Match_Type'],
                'Match_Score': match_dict['Match_Score']
            }

            # Add ledger columns
            for col in ledger_orig.columns:
                row[f'Ledger_{col}'] = ledger_orig.iloc[l_idx][col]

            # Add statement columns
            for col in statement_orig.columns:
                row[f'Statement_{col}'] = statement_orig.iloc[s_idx][col]

            matched_rows.append(row)

        # Split transactions
        split_data = []
        for split_match in split_matches:
            if split_match['split_type'] == 'many_to_one':
                matched_statement.add(split_match['statement_idx'])
                matched_ledger.update(split_match['ledger_indices'])
                split_data.append(split_match)
            else:  # one_to_many
                matched_ledger.add(split_match['ledger_idx'])
                matched_statement.update(split_match['statement_indices'])
                split_data.append(split_match)

        # Unmatched
        unmatched_ledger_indices = set(ledger.index) - matched_ledger
        unmatched_statement_indices = set(statement.index) - matched_statement

        return {
            'matched': pd.DataFrame(matched_rows) if matched_rows else pd.DataFrame(),
            'split_matches': split_data,
            'foreign_credits_count': len(fc_data),
            'perfect_match_count': len(perfect_data),
            'fuzzy_match_count': len(fuzzy_data),
            'unmatched_ledger': ledger_orig.iloc[list(unmatched_ledger_indices)],
            'unmatched_statement': statement_orig.iloc[list(unmatched_statement_indices)]
        }
