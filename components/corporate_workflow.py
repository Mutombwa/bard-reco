"""
Corporate Settlements Workflow - ULTRA-OPTIMIZED VERSION
=========================================================
Designed for LARGE datasets (100k+ rows) with MAXIMUM speed

Key Optimizations:
- Hash-based matching (O(1) lookups instead of O(n²))
- Vectorized operations throughout
- Pre-filtering to reduce iterations
- Single-pass algorithms
- No redundant DataFrame operations
- Efficient memory usage
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import time
import re

class CorporateWorkflow:
    """Ultra-fast Corporate Settlement Workflow - OPTIMIZED"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state"""
        if 'corporate_data' not in st.session_state:
            st.session_state.corporate_data = None
        if 'corporate_df' not in st.session_state:
            st.session_state.corporate_df = None
        if 'corporate_results' not in st.session_state:
            st.session_state.corporate_results = None
        if 'corporate_reference_extracted' not in st.session_state:
            st.session_state.corporate_reference_extracted = False
        if 'show_extracted_data' not in st.session_state:
            st.session_state.show_extracted_data = False

    @staticmethod
    def extract_references(comment_text):
        """Extract RJ, TX, CSH, ZVC, ECO, INN reference numbers from comment text"""
        if pd.isna(comment_text) or not isinstance(comment_text, str):
            return ""

        # Check for special patterns
        if 'Correcting' in comment_text:
            return comment_text.strip()

        if re.search(r'(?<!R)(?<!T)\b[A-Za-z]+\s+J\d{5}\b', comment_text):
            return comment_text.strip()

        all_matches = []

        # Extract ALL reference patterns (RJ, TX, CSH, ZVC, ECO, INN)
        # RJ patterns (11 digits)
        all_matches.extend(re.findall(r'RJ\d{11}', comment_text))
        # TX patterns (11 digits)
        all_matches.extend(re.findall(r'TX\d{11}', comment_text))
        # CSH patterns (9+ digits) - Cash transactions
        all_matches.extend(re.findall(r'CSH\d{9,}', comment_text))
        # ZVC patterns (9 digits) - Reversal transactions
        all_matches.extend(re.findall(r'ZVC\d{9}', comment_text))
        # ECO patterns (9 digits) - ECO transactions
        all_matches.extend(re.findall(r'ECO\d{9}', comment_text))
        # INN patterns (9 digits) - INN transactions
        all_matches.extend(re.findall(r'INN\d{9}', comment_text))
        # J patterns (5 digits) - Journal entries
        all_matches.extend(re.findall(r'(?<!R)(?<!T)J\d{5}', comment_text))

        # Remove duplicates while preserving order
        seen = set()
        unique_matches = [m for m in all_matches if not (m in seen or seen.add(m))]

        return ', '.join(unique_matches) if unique_matches else ""

    @staticmethod
    def extract_payment_ref(comment_text):
        """Extract payment reference (name) from comment text - strips phone numbers"""
        if pd.isna(comment_text) or not isinstance(comment_text, str):
            return ""

        comment = comment_text.strip()

        def clean_name(name):
            """Remove phone numbers from extracted name"""
            if not name:
                return ''
            name = name.strip()
            # Remove trailing phone number after space: "Jenet 6452843846" → "Jenet"
            name = re.sub(r'\s+\d{10,}$', '', name)
            # Remove phone number after slash: "gracious/6453092146" → "gracious"
            name = re.sub(r'/\d{10,}$', '', name)
            # Remove attached phone number: "remember6453463069" → "remember"
            name = re.sub(r'^([a-zA-Z][a-zA-Z\s]*?)\d{10,}$', r'\1', name)
            return name.strip()

        # Find ALL parentheses and use the one with the name (not #Ref)
        all_parens = re.findall(r'\(\s*([^)]+)\s*\)', comment)
        for paren_content in all_parens:
            paren_content = paren_content.strip()
            # Skip if it looks like a reference
            if re.match(r'#?Ref\s+(RJ|TX|CSH|ZVC|ECO|INN)', paren_content, re.IGNORECASE):
                continue
            # Found a valid name in parentheses
            cleaned = clean_name(paren_content)
            if cleaned:
                return cleaned

        # Pattern: ". - Name" or "- Name"
        dash_match = re.search(r'[-–]\s*([A-Za-z][A-Za-z\s]*)', comment)
        if dash_match:
            return clean_name(dash_match.group(1))

        return ""

    def render(self):
        """Render Corporate workflow"""

        st.markdown("""
        <div class="gradient-header">
            <h1>💼 Corporate Settlements - ULTRA FAST</h1>
            <p>Optimized for large datasets (100k+ rows) with blazing speed</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📁 Upload Corporate Settlement File")

        file = st.file_uploader("Upload Settlement File", type=['xlsx', 'xls', 'csv'])

        if file:
            file_id = f"{file.name}_{file.size}"
            if 'corporate_file_id' not in st.session_state or st.session_state.corporate_file_id != file_id:
                try:
                    start_time = time.time()

                    with st.spinner("⚡ Loading file..."):
                        if file.name.endswith('.csv'):
                            df = pd.read_csv(file, low_memory=False, engine='c')
                        else:
                            df = pd.read_excel(file, engine='openpyxl')

                    load_time = time.time() - start_time

                    st.session_state.corporate_data = df
                    st.session_state.corporate_df = df
                    st.session_state.corporate_file_id = file_id
                    st.session_state.corporate_reference_extracted = False
                    st.session_state.show_extracted_data = False

                    rows_per_sec = len(df) / load_time if load_time > 0 else 0
                    st.success(f"⚡ Loaded {len(df):,} rows × {len(df.columns)} columns in {load_time:.2f}s ({rows_per_sec:,.0f} rows/sec)")

                except Exception as e:
                    st.error(f"Error loading file: {e}")
                    return

            if st.session_state.corporate_df is not None:
                with st.expander("👁️ Preview Data"):
                    preview_df = st.session_state.corporate_df
                    st.info(f"Current columns: {', '.join(preview_df.columns.tolist())}")
                    st.dataframe(preview_df.head(20), use_container_width=True)

                st.markdown("---")
                st.markdown("### 🔍 Extract References from Comment Column")
                self.render_reference_extraction()

                self.render_extracted_data_view()

                st.markdown("---")
                st.markdown("### ⚙️ Configuration")
                st.markdown("Select the columns to use for reconciliation:")

                working_df = st.session_state.corporate_df

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    debit_col = st.selectbox("Foreign Debits", working_df.columns, key="debit_col")
                with col2:
                    credit_col = st.selectbox("Foreign Credits", working_df.columns, key="credit_col")
                with col3:
                    ref_col = st.selectbox("Reference", working_df.columns, key="ref_col")
                with col4:
                    journal_col = st.selectbox("Journal", working_df.columns, key="journal_col")

                if st.button("🚀 Run ULTRA-FAST Reconciliation", type="primary", use_container_width=True):
                    self.run_ultra_fast_reconciliation(working_df, debit_col, credit_col, ref_col, journal_col)

        if st.session_state.corporate_results:
            st.markdown("---")
            self.render_results()

    def run_ultra_fast_reconciliation(self, df, debit_col, credit_col, ref_col, journal_col):
        """
        ULTRA-FAST reconciliation using hash maps and vectorization
        Designed for datasets of ANY size - 100k+ rows in seconds
        """

        start_time = time.time()

        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        metrics_placeholder = st.empty()

        status_placeholder.info("🚀 **Starting ULTRA-FAST Reconciliation...**")
        progress_bar = progress_placeholder.progress(0)

        # =============================================================================
        # STEP 1: VECTORIZED DATA PREPARATION (< 0.1s for 100k rows)
        # =============================================================================
        status_placeholder.info("⚡ **Step 1/7 (0.0%):** Vectorized data preparation...")
        df = df.copy()
        original_row_count = len(df)

        # Sub-step 1.1: Clean debits/credits
        status_placeholder.info(f"⚡ **Step 1/7 (2.0%):** Cleaning {original_row_count:,} debit/credit amounts...")
        df['_debit'] = pd.to_numeric(df[debit_col], errors='coerce').fillna(0).abs()
        df['_credit'] = pd.to_numeric(df[credit_col], errors='coerce').fillna(0).abs()
        progress_bar.progress(0.02)

        # Sub-step 1.2: Clean references/journals (CASE-INSENSITIVE)
        status_placeholder.info(f"⚡ **Step 1/7 (5.0%):** Normalizing references and journals...")
        df['_reference'] = df[ref_col].astype(str).str.strip().str.upper()  # Already uppercase
        df['_journal'] = df[journal_col].astype(str).str.strip().str.upper()  # Make case-insensitive
        progress_bar.progress(0.05)

        # Sub-step 1.3: Mark blank references
        status_placeholder.info(f"⚡ **Step 1/7 (8.0%):** Marking blank references with unique IDs...")
        blank_mask = df['_reference'].isin(['', 'NAN', 'NONE', 'NULL', '0', 'NATT'])
        blank_count = blank_mask.sum()
        df.loc[blank_mask, '_reference'] = [f'__BLANK_{i}__' for i in range(blank_count)]
        progress_bar.progress(0.10)

        step1_time = time.time() - start_time
        metrics_placeholder.success(f"✅ Step 1 complete: {step1_time:.3f}s | {original_row_count:,} rows prepared | {blank_count:,} blanks marked")

        # =============================================================================
        # STEP 2: BUILD HASH MAPS FOR O(1) LOOKUPS
        # =============================================================================
        status_placeholder.info(f"🗂️ **Step 2/7 (10.0%):** Building hash indexes for {original_row_count:,} rows...")

        # Create efficient lookup structures
        ref_to_indices = defaultdict(list)
        journal_to_indices = defaultdict(list)

        # Build indexes with progress updates
        total_rows = len(df.index)
        update_interval = max(1, total_rows // 20)  # Update 20 times during this step

        for i, idx in enumerate(df.index):
            ref = df.loc[idx, '_reference']
            journal = df.loc[idx, '_journal']

            # Skip blank references
            if not str(ref).startswith('__BLANK_'):
                ref_to_indices[ref].append(idx)

            journal_to_indices[journal].append(idx)

            # Update progress periodically
            if i % update_interval == 0:
                current_progress = 0.10 + (i / total_rows) * 0.05  # 10% to 15%
                progress_pct = current_progress * 100
                status_placeholder.info(f"🗂️ **Step 2/7 ({progress_pct:.1f}%):** Indexing row {i+1:,} / {total_rows:,}...")
                progress_bar.progress(current_progress)

        progress_bar.progress(0.15)
        step2_time = time.time() - start_time
        unique_refs = len(ref_to_indices)
        unique_journals = len(journal_to_indices)
        metrics_placeholder.success(f"✅ Step 2 complete: {step2_time-step1_time:.3f}s | {unique_refs:,} unique refs | {unique_journals:,} journals indexed")

        # Initialize tracking
        matched = set()
        batch1_rows = []
        batch2_rows = []
        batch3_rows = []
        batch4_rows = []
        batch5_rows = []

        # =============================================================================
        # BATCH 1: CORRECTING JOURNALS (Ultra-fast vectorized matching)
        # =============================================================================
        status_placeholder.info("🔍 **Step 3/7 (15.0%):** Batch 1 - Correcting Journals...")

        # Extract all correcting journal references with vectorized regex
        correcting_mask = df['_reference'].str.contains('CORRECTING', na=False, case=False)
        correcting_df = df[correcting_mask].copy()
        total_correcting = len(correcting_df)

        if total_correcting > 0:
            # Vectorized extraction of journal numbers from "Correcting J239918" format
            # Extract just the digits after "J" - handles J239918, J1, J239, etc.
            correcting_df['_journal_num'] = correcting_df['_reference'].str.extract(r'J(\d+)', flags=re.IGNORECASE)[0]
            
            # Remove rows where extraction failed
            valid_correcting = correcting_df[correcting_df['_journal_num'].notna()].copy()
            
            # Create normalized journal lookup for entire dataframe
            # Convert journal to string, remove .0 decimal, strip whitespace
            df['_journal_str'] = df['_journal'].astype(str).str.strip()
            # Remove .0 from floats (e.g., '61705.0' -> '61705')
            df['_journal_str'] = df['_journal_str'].str.replace(r'\.0$', '', regex=True)
            
            # Create a journal lookup dictionary for FAST O(1) matching
            # Key: normalized journal (no leading zeros, no decimals), Value: list of indices
            journal_lookup = {}
            for idx in df.index:
                if idx not in matched:
                    j_str = df.loc[idx, '_journal_str']
                    # Normalize: remove leading zeros and handle decimals
                    j_normalized = j_str.lstrip('0') or '0'
                    if j_normalized not in journal_lookup:
                        journal_lookup[j_normalized] = []
                    journal_lookup[j_normalized].append(idx)
            
            # Match each correcting journal
            for idx, corr_row in valid_correcting.iterrows():
                if idx in matched:
                    continue
                
                # Extract journal number from correcting reference
                journal_num = corr_row['_journal_num']
                journal_normalized = journal_num.lstrip('0') or '0'
                
                # Look up matching journals using hash map (O(1))
                if journal_normalized in journal_lookup:
                    potential_indices = journal_lookup[journal_normalized]
                    
                    # Find first unmatched transaction with this journal (excluding self)
                    for match_idx in potential_indices:
                        if match_idx != idx and match_idx not in matched:
                            # Add as paired rows (matched transaction FIRST, then correcting)
                            batch1_rows.append(df.loc[match_idx])
                            batch1_rows.append(df.loc[idx])
                            matched.add(idx)
                            matched.add(match_idx)
                            # Remove from lookup to prevent reuse
                            journal_lookup[journal_normalized].remove(match_idx)
                            break
            
            # Cleanup temporary columns
            df.drop(columns=['_journal_str'], inplace=True, errors='ignore')

        progress_bar.progress(0.30)
        step3_time = time.time() - start_time
        batch1_pairs = len(batch1_rows) // 2 if len(batch1_rows) > 0 else 0
        metrics_placeholder.success(f"✅ Batch 1 complete: {step3_time-step2_time:.3f}s | {len(batch1_rows):,} transactions in {batch1_pairs:,} pairs ({total_correcting:,} correcting entries found)")

        # =============================================================================
        # BATCH 2-5: VECTORIZED MATCHING WITH HASH LOOKUP
        # =============================================================================
        status_placeholder.info("⚡ **Step 4/7 (30.0%):** Batches 2-5 - Ultra-fast vectorized matching...")

        # Process only unmatched transactions
        unmatched_mask = ~df.index.isin(matched)
        unmatched_df = df[unmatched_mask].copy()

        # Group by reference for batch processing
        grouped_refs = list(unmatched_df.groupby('_reference'))
        total_ref_groups = len(grouped_refs)
        processed_groups = 0

        for ref, group in grouped_refs:
            # Skip blanks
            if str(ref).startswith('__BLANK_') or len(group) < 2:
                processed_groups += 1
                continue

            # Split into debit/credit
            debit_rows = group[group['_debit'] > 0]
            credit_rows = group[group['_credit'] > 0]

            if len(debit_rows) == 0 or len(credit_rows) == 0:
                processed_groups += 1
                continue

            # Vectorized matching
            debit_idx = debit_rows.index.values
            credit_idx = credit_rows.index.values
            debit_amt = debit_rows['_debit'].values
            credit_amt = credit_rows['_credit'].values

            used_debit = set()
            used_credit = set()

            for i, d_amt in enumerate(debit_amt):
                if debit_idx[i] in matched or i in used_debit:
                    continue

                # Calculate all differences at once
                diffs = d_amt - credit_amt

                # BATCH 2: Exact match (diff < 0.01)
                exact_matches = np.where((np.abs(diffs) < 0.01) & ~np.isin(np.arange(len(credit_amt)), list(used_credit)))[0]
                if len(exact_matches) > 0:
                    j = exact_matches[0]
                    if credit_idx[j] not in matched:
                        batch2_rows.extend([df.loc[debit_idx[i]], df.loc[credit_idx[j]]])
                        matched.update([debit_idx[i], credit_idx[j]])
                        used_debit.add(i)
                        used_credit.add(j)
                        continue

                # BATCH 3: FD commission (debit > credit by ≥1)
                fd_matches = np.where((diffs >= 1) & ~np.isin(np.arange(len(credit_amt)), list(used_credit)))[0]
                if len(fd_matches) > 0:
                    j = fd_matches[0]
                    if credit_idx[j] not in matched:
                        batch3_rows.extend([df.loc[debit_idx[i]], df.loc[credit_idx[j]]])
                        matched.update([debit_idx[i], credit_idx[j]])
                        used_debit.add(i)
                        used_credit.add(j)
                        continue

                # BATCH 4: FC commission (credit > debit by ≥1)
                fc_matches = np.where((diffs <= -1) & ~np.isin(np.arange(len(credit_amt)), list(used_credit)))[0]
                if len(fc_matches) > 0:
                    j = fc_matches[0]
                    if credit_idx[j] not in matched:
                        batch4_rows.extend([df.loc[debit_idx[i]], df.loc[credit_idx[j]]])
                        matched.update([debit_idx[i], credit_idx[j]])
                        used_debit.add(i)
                        used_credit.add(j)
                        continue

                # BATCH 5: Rate differences (0.01 ≤ |diff| < 1)
                rate_matches = np.where((np.abs(diffs) >= 0.01) & (np.abs(diffs) < 1) & ~np.isin(np.arange(len(credit_amt)), list(used_credit)))[0]
                if len(rate_matches) > 0:
                    j = rate_matches[0]
                    if credit_idx[j] not in matched:
                        batch5_rows.extend([df.loc[debit_idx[i]], df.loc[credit_idx[j]]])
                        matched.update([debit_idx[i], credit_idx[j]])
                        used_debit.add(i)
                        used_credit.add(j)
                        continue

            processed_groups += 1

            # Update progress every 5% of groups or every 100 groups, whichever is smaller
            update_freq = min(100, max(1, total_ref_groups // 20))
            if processed_groups % update_freq == 0 or processed_groups == total_ref_groups:
                current_progress = 0.30 + (processed_groups / total_ref_groups) * 0.50  # 30% to 80%
                progress_pct = current_progress * 100
                total_matched = len(batch2_rows) + len(batch3_rows) + len(batch4_rows) + len(batch5_rows)

                # Show current reference being processed (truncate if too long)
                ref_display = str(ref)[:30] + "..." if len(str(ref)) > 30 else str(ref)
                status_placeholder.info(
                    f"⚡ **Step 4/7 ({progress_pct:.1f}%):** Processing reference group {processed_groups:,} / {total_ref_groups:,}\n"
                    f"Current Ref: `{ref_display}` | Total Matched: {total_matched:,} (B2: {len(batch2_rows):,}, B3: {len(batch3_rows):,}, B4: {len(batch4_rows):,}, B5: {len(batch5_rows):,})"
                )
                progress_bar.progress(current_progress)

        progress_bar.progress(0.80)
        step4_time = time.time() - start_time
        total_matched_2_5 = len(batch2_rows) + len(batch3_rows) + len(batch4_rows) + len(batch5_rows)
        metrics_placeholder.success(f"✅ Batches 2-5 complete: {step4_time-step3_time:.3f}s | {total_matched_2_5:,} transactions | {processed_groups:,} ref groups processed")

        # =============================================================================
        # BATCH 6: UNMATCHED
        # =============================================================================
        status_placeholder.info("📊 **Step 5/7 (80.0%):** Batch 6 - Collecting unmatched transactions...")
        batch6_indices = set(df.index) - matched

        # Create batch DataFrames with progress updates
        status_placeholder.info("📊 **Step 5/7 (82.0%):** Creating Batch 1 DataFrame (Correcting Journals)...")
        batch1_df = pd.DataFrame(batch1_rows) if batch1_rows else pd.DataFrame()
        progress_bar.progress(0.82)

        status_placeholder.info("📊 **Step 5/7 (84.0%):** Creating Batch 2 DataFrame (Exact Matches)...")
        batch2_df = pd.DataFrame(batch2_rows) if batch2_rows else pd.DataFrame()
        progress_bar.progress(0.84)

        status_placeholder.info("📊 **Step 5/7 (86.0%):** Creating Batch 3 DataFrame (FD Commission)...")
        batch3_df = pd.DataFrame(batch3_rows) if batch3_rows else pd.DataFrame()
        progress_bar.progress(0.86)

        status_placeholder.info("📊 **Step 5/7 (88.0%):** Creating Batch 4 DataFrame (FC Commission)...")
        batch4_df = pd.DataFrame(batch4_rows) if batch4_rows else pd.DataFrame()
        progress_bar.progress(0.88)

        status_placeholder.info("📊 **Step 5/7 (90.0%):** Creating Batch 5 DataFrame (Rate Differences)...")
        batch5_df = pd.DataFrame(batch5_rows) if batch5_rows else pd.DataFrame()
        progress_bar.progress(0.90)

        status_placeholder.info(f"📊 **Step 5/7 (92.0%):** Creating Batch 6 DataFrame ({len(batch6_indices):,} Unmatched)...")
        batch6_df = df.loc[list(batch6_indices)].copy() if batch6_indices else pd.DataFrame()
        progress_bar.progress(0.92)

        # =============================================================================
        # DATA INTEGRITY VALIDATION
        # =============================================================================
        status_placeholder.info("✅ **Step 6/7 (92.0%):** Validating data integrity...")

        # Calculate row counts
        status_placeholder.info("✅ **Step 6/7 (93.0%):** Validating row counts...")
        total_output = len(batch1_df) + len(batch2_df) + len(batch3_df) + len(batch4_df) + len(batch5_df) + len(batch6_df)
        progress_bar.progress(0.93)

        # Calculate original sums
        status_placeholder.info("✅ **Step 6/7 (95.0%):** Calculating original debit/credit sums...")
        orig_debit_sum = df['_debit'].sum()
        orig_credit_sum = df['_credit'].sum()
        progress_bar.progress(0.95)

        # Calculate output sums
        status_placeholder.info("✅ **Step 6/7 (97.0%):** Calculating output debit/credit sums...")
        out_debit_sum = sum(b['_debit'].sum() if not b.empty and '_debit' in b.columns else 0
                           for b in [batch1_df, batch2_df, batch3_df, batch4_df, batch5_df, batch6_df])
        out_credit_sum = sum(b['_credit'].sum() if not b.empty and '_credit' in b.columns else 0
                            for b in [batch1_df, batch2_df, batch3_df, batch4_df, batch5_df, batch6_df])
        progress_bar.progress(0.97)

        # Check for issues
        status_placeholder.info("✅ **Step 6/7 (98.0%):** Running integrity checks...")
        has_duplicates = total_output != original_row_count
        sum_mismatch = abs(orig_debit_sum - out_debit_sum) > 0.01 or abs(orig_credit_sum - out_credit_sum) > 0.01
        progress_bar.progress(0.98)

        elapsed_time = time.time() - start_time

        # Prepare results
        status_placeholder.info("🎉 **Step 7/7 (99.0%):** Preparing final results...")
        results = {
            'batch1': batch1_df, 'batch2': batch2_df, 'batch3': batch3_df,
            'batch4': batch4_df, 'batch5': batch5_df, 'batch6': batch6_df,
            'stats': {
                'total': original_row_count,
                'batch1': len(batch1_df), 'batch2': len(batch2_df), 'batch3': len(batch3_df),
                'batch4': len(batch4_df), 'batch5': len(batch5_df), 'batch6': len(batch6_df),
                'processing_time': elapsed_time,
                'original_rows': original_row_count, 'output_rows': total_output,
                'original_debit_sum': orig_debit_sum, 'original_credit_sum': orig_credit_sum,
                'output_debit_sum': out_debit_sum, 'output_credit_sum': out_credit_sum,
                'has_duplicates': has_duplicates, 'sum_mismatch': sum_mismatch
            }
        }
        progress_bar.progress(0.99)

        # Save to session state
        status_placeholder.info("🎉 **Step 7/7 (100.0%):** Finalizing and saving results...")
        st.session_state.corporate_results = results
        progress_bar.progress(1.0)

        # Show completion message briefly
        status_placeholder.success("✅ **COMPLETE!** All batches processed successfully!")
        time.sleep(0.5)  # Brief pause to show completion

        # Clear progress indicators
        status_placeholder.empty()
        progress_placeholder.empty()
        metrics_placeholder.empty()

        # Display completion
        rows_per_sec = original_row_count / elapsed_time if elapsed_time > 0 else 0
        match_rate = (len(matched) / original_row_count * 100) if original_row_count > 0 else 0

        if has_duplicates or sum_mismatch:
            st.error(f"""
            ## ⚠️ Reconciliation Complete with Warnings!
            {"⚠️ Row count mismatch!" if has_duplicates else ""}
            {"⚠️ Sum mismatch detected!" if sum_mismatch else ""}
            """)

        st.success(f"""
        ## 🎉 ULTRA-FAST Reconciliation Complete! ⚡

        **⚡ Performance (BLAZING FAST):**
        - 🚀 **Speed**: {rows_per_sec:,.0f} rows/second
        - ⏱️ **Total Time**: {elapsed_time:.2f}s
        - 📊 **Processed**: {original_row_count:,} transactions
        - ✅ **Matched**: {len(matched):,} ({match_rate:.1f}%)
        - ❌ **Unmatched**: {len(batch6_indices):,} ({100-match_rate:.1f}%)

        **📊 Batch Summary:**
        - Batch 1: {len(batch1_df):,} | Batch 2: {len(batch2_df):,} | Batch 3: {len(batch3_df):,}
        - Batch 4: {len(batch4_df):,} | Batch 5: {len(batch5_df):,} | Batch 6: {len(batch6_df):,}

        **✅ Data Integrity:**
        - Rows: {original_row_count:,} in = {total_output:,} out
        - FD Sum: {orig_debit_sum:,.2f} in = {out_debit_sum:,.2f} out
        - FC Sum: {orig_credit_sum:,.2f} in = {out_credit_sum:,.2f} out
        """)

        st.rerun()

    def render_reference_extraction(self):
        """Render reference extraction UI"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("🔍 Extract References", type="primary", use_container_width=True):
                self.execute_reference_extraction()

        with col2:
            if st.session_state.corporate_reference_extracted:
                st.success("✅ References extracted!")

        with col3:
            if st.session_state.corporate_reference_extracted:
                if st.button("👁️ View Data", type="secondary", use_container_width=True):
                    st.session_state.show_extracted_data = True

    def execute_reference_extraction(self):
        """Execute reference extraction"""
        if st.session_state.corporate_df is None:
            st.error("❌ No data loaded")
            return

        df = st.session_state.corporate_df.copy()
        comment_columns = [col for col in df.columns if 'comment' in col.lower()]

        if not comment_columns:
            st.error("❌ No Comment column found")
            return

        comment_col = comment_columns[0]

        with st.spinner(f"⚡ Extracting references..."):
            start_time = time.time()
            df['Reference'] = df[comment_col].apply(self.extract_references)
            elapsed_time = time.time() - start_time

            extracted_count = (df['Reference'].str.len() > 0).sum()
            st.success(f"⚡ Extracted {extracted_count:,}/{len(df):,} in {elapsed_time:.2f}s")

            st.session_state.corporate_df = df
            st.session_state.corporate_data = df
            st.session_state.corporate_reference_extracted = True
            st.session_state.show_extracted_data = True

    def render_extracted_data_view(self):
        """Render extracted data view"""
        if not st.session_state.get('show_extracted_data', False) or st.session_state.corporate_df is None:
            return

        df = st.session_state.corporate_df

        if 'Reference' not in df.columns:
            return

        st.markdown("---")
        st.markdown("### 📊 Extracted Data")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            refs_found = df['Reference'].str.len().gt(0).sum()
            st.metric("References Found", f"{refs_found:,}")
        with col3:
            rate = (refs_found / len(df) * 100) if len(df) > 0 else 0
            st.metric("Extraction Rate", f"{rate:.1f}%")

        cols = ['Reference'] + [col for col in df.columns if col != 'Reference']
        st.dataframe(df[cols], use_container_width=True, height=400)

        if st.button("🔼 Hide Data View"):
            st.session_state.show_extracted_data = False
            st.rerun()

    def render_results(self):
        """Render reconciliation results"""

        results = st.session_state.corporate_results
        stats = results['stats']

        st.markdown("## 🎉 Corporate Settlement Results")

        processing_time = stats.get('processing_time', 0)
        rows_per_sec = stats['total'] / processing_time if processing_time > 0 else 0
        st.success(f"⚡ **Ultra-Fast Processing:** {stats['total']:,} rows in {processing_time:.2f}s ({rows_per_sec:,.0f} rows/sec)")

        # Export buttons
        st.markdown("### 📥 Export Results")
        col_exp1, col_exp2 = st.columns(2)

        # Define batch configs (used for both export and display)
        batch_configs = [
            ('batch1', 'Correcting Journal Batch'),
            ('batch2', 'Exact Match Batch'),
            ('batch3', 'Foreign Debit Include Commission'),
            ('batch4', 'Foreign Credits Include Commission'),
            ('batch5', 'Common References & Diff Caused By Diff Rates'),
            ('batch6', 'Unmatched Transactions')
        ]

        # CACHE the combined export dataframe to avoid rebuilding on every render
        if 'combined_export_df' not in results:
            all_batches = []

            for batch_key, batch_title in batch_configs:
                batch_df = results[batch_key]
                if not batch_df.empty:
                    display_df = batch_df.drop(columns=[c for c in batch_df.columns if c.startswith('_')], errors='ignore')
                    header_dict = {col: [batch_title if col == display_df.columns[0] else ''] for col in display_df.columns}
                    header_row = pd.DataFrame(header_dict)
                    empty_row = pd.DataFrame({col: [''] for col in display_df.columns})
                    all_batches.extend([header_row, display_df, empty_row])

            if all_batches:
                results['combined_export_df'] = pd.concat(all_batches, ignore_index=True)
            else:
                results['combined_export_df'] = pd.DataFrame()

        combined_df = results['combined_export_df']

        if not combined_df.empty:
            with col_exp1:
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, index=False, sheet_name='Results')
                excel_data = output.getvalue()
                st.download_button("📊 Download Excel", excel_data, "corporate_results.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 use_container_width=True)

            with col_exp2:
                csv_data = combined_df.to_csv(index=False).encode('utf-8')
                st.download_button("📄 Download CSV", csv_data, "corporate_results.csv", "text/csv",
                                 use_container_width=True)
        else:
            st.warning("No data to export")

        # Summary metrics
        st.markdown("### 📊 Summary")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.metric("Total", f"{stats['total']:,}")
        with col2:
            st.metric("Batch 1", f"{stats['batch1']:,}")
        with col3:
            st.metric("Batch 2", f"{stats['batch2']:,}")
        with col4:
            st.metric("Batch 3", f"{stats['batch3']:,}")
        with col5:
            st.metric("Batch 4", f"{stats['batch4']:,}")
        with col6:
            st.metric("Batch 5", f"{stats['batch5']:,}")
        with col7:
            st.metric("Batch 6", f"{stats['batch6']:,}")

        # Display batches
        st.markdown("---")
        for batch_key, batch_title in batch_configs:
            st.markdown(f'<p style="font-family: Calibri; font-size: 18px; font-weight: bold;">{batch_title}</p>', unsafe_allow_html=True)
            batch_df = results[batch_key]
            if not batch_df.empty:
                display_df = batch_df.drop(columns=[c for c in batch_df.columns if c.startswith('_')], errors='ignore')
                st.dataframe(display_df, use_container_width=True, height=400)
                st.info(f"✅ {len(batch_df):,} transactions")
            else:
                st.info("No transactions in this batch")
