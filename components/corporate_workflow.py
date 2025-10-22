"""
Corporate Settlements Workflow Component
========================================
Ultra-fast settlement matching with 5-tier batch processing
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

class CorporateWorkflow:
    """Corporate Settlement Workflow with 5-Tier Matching"""

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
        """
        Extract RJ, TX reference numbers, or return the entire comment text if it contains special patterns.
        
        Supported patterns:
        1. RJ + 11 digits (e.g., RJ49465028731)
        2. TX + 11 digits (e.g., TX32749881276)
        3. If text contains "Correcting" or "J" followed by digits, return entire text
        
        Examples:
        - "Ref #RJ49465028731. - 000089828" → "RJ49465028731"
        - "Ref #TX32749881276. Payment Ref #708164596" → "TX32749881276"
        - "Correcting J62970" → "Correcting J62970"
        - "Cash  ZAR 100 paid out. Ref RJ34570058702" → "RJ34570058702"
        - "RJ42325355002 cancelled, TX12345678901" → "RJ42325355002, TX12345678901"
        
        Returns: Comma-separated string of all references found, or entire text if special pattern
        """
        if pd.isna(comment_text) or not isinstance(comment_text, str):
            return ""
        
        # Check if this is a special case (contains "Correcting")
        # Need to be specific - NOT RJ or TX patterns
        # Only match if it's something like "Correcting J62970" or "Adjusting J12345"
        if 'Correcting' in comment_text:
            return comment_text.strip()
        
        # Check for other text patterns before J (but NOT RJ or TX)
        # Match patterns like "word J12345" but NOT "RJ12345" or "TX12345"
        if re.search(r'(?<!R)(?<!T)\b[A-Za-z]+\s+J\d{5}\b', comment_text):
            return comment_text.strip()
        
        all_matches = []
        
        # Pattern 1: RJ followed by 11 digits
        pattern_rj = r'RJ\d{11}'
        matches_rj = re.findall(pattern_rj, comment_text)
        all_matches.extend(matches_rj)
        
        # Pattern 2: TX followed by 11 digits
        pattern_tx = r'TX\d{11}'
        matches_tx = re.findall(pattern_tx, comment_text)
        all_matches.extend(matches_tx)
        
        # Pattern 3: J followed by 5 digits (standalone, not part of RJ or TX)
        pattern_j = r'(?<!R)(?<!T)J\d{5}'
        matches_j = re.findall(pattern_j, comment_text)
        all_matches.extend(matches_j)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in all_matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)
        
        # Return comma-separated string
        return ', '.join(unique_matches) if unique_matches else ""

    def render(self):
        """Render Corporate workflow"""

        st.markdown("""
        <div class="gradient-header">
            <h1>💼 Corporate Settlements</h1>
            <p>Ultra-fast settlement matching with 5-tier batch processing</p>
        </div>
        """, unsafe_allow_html=True)

        # Removed back button - workflows are now shown in tabs
        st.markdown("### 📁 Upload Corporate Settlement File")

        file = st.file_uploader("Upload Settlement File", type=['xlsx', 'xls', 'csv'])

        if file:
            # Check if this is a new file (prevent reloading and losing Reference column)
            file_id = f"{file.name}_{file.size}"
            if 'corporate_file_id' not in st.session_state or st.session_state.corporate_file_id != file_id:
                try:
                    # Ultra-fast file loading with performance timer
                    import time
                    start_time = time.time()
                    
                    with st.spinner("⚡ Loading file..."):
                        if file.name.endswith('.csv'):
                            # Ultra-fast CSV loading with optimized settings
                            df = pd.read_csv(
                                file, 
                                low_memory=False, 
                                engine='c',  # Fastest C engine
                                dtype_backend='numpy_nullable'  # Fast dtype inference
                            )
                        else:
                            # Ultra-fast Excel loading with optimized settings
                            df = pd.read_excel(
                                file, 
                                engine='openpyxl',
                                dtype_backend='numpy_nullable'  # Fast dtype inference
                            )
                    
                    load_time = time.time() - start_time

                    st.session_state.corporate_data = df
                    st.session_state.corporate_df = df  # Initialize for reference extraction
                    st.session_state.corporate_file_id = file_id  # Track loaded file
                    st.session_state.corporate_reference_extracted = False  # Reset on new file
                    st.session_state.show_extracted_data = False  # Reset data view on new file
                    
                    rows_per_sec = len(df) / load_time if load_time > 0 else 0
                    st.success(f"⚡ Loaded {len(df):,} rows × {len(df.columns)} columns in {load_time:.2f}s ({rows_per_sec:,.0f} rows/sec)")
                
                except Exception as e:
                    st.error(f"Error loading file: {e}")
                    return
            
            # Show preview (use session state df which may have Reference column)
            if st.session_state.corporate_df is not None:
                with st.expander("👁️ Preview Data"):
                    preview_df = st.session_state.corporate_df
                    st.info(f"Current columns: {', '.join(preview_df.columns.tolist())}")
                    st.dataframe(preview_df.head(20), use_container_width=True)

                # Reference Extraction Feature
                st.markdown("---")
                st.markdown("### 🔍 Extract References from Comment Column")
                self.render_reference_extraction()
                
                # Show extracted data if available
                self.render_extracted_data_view()

                st.markdown("---")
                st.markdown("### ⚙️ Configuration")
                st.markdown("Select the columns to use for reconciliation:")
                
                # Use the dataframe from session state (which may have Reference column added)
                working_df = st.session_state.corporate_df

                # 4 column selectors as requested
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    debit_col = st.selectbox("Foreign Debits", working_df.columns, key="debit_col")
                with col2:
                    credit_col = st.selectbox("Foreign Credits", working_df.columns, key="credit_col")
                with col3:
                    ref_col = st.selectbox("Reference", working_df.columns, key="ref_col")
                with col4:
                    journal_col = st.selectbox("Journal", working_df.columns, key="journal_col")

                if st.button("🚀 Run Corporate Reconciliation", type="primary", use_container_width=True):
                    self.run_batch_reconciliation(working_df, debit_col, credit_col, ref_col, journal_col)

        if st.session_state.corporate_results:
            st.markdown("---")
            self.render_results()

    def run_batch_reconciliation(self, df, debit_col, credit_col, ref_col, journal_col):
        """Ultra-fast batch reconciliation matching the exact criteria from the image"""
        
        import time
        start_time = time.time()
        
        # Create placeholders for dynamic updates
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        metrics_placeholder = st.empty()
        
        status_placeholder.info("🚀 **Starting Reconciliation Process...**")
        progress_bar = progress_placeholder.progress(0)
        
        # Step 1: Clean and prepare data (vectorized - ULTRA FAST)
        status_placeholder.info("⚙️ **Step 1/7:** Preparing and cleaning data...")
        df = df.copy()

        # Store original row count for validation
        original_row_count = len(df)

        # Vectorized data cleaning - FAST
        df['_debit'] = pd.to_numeric(df[debit_col], errors='coerce').fillna(0).abs()
        df['_credit'] = pd.to_numeric(df[credit_col], errors='coerce').fillna(0).abs()

        # Clean references - replace blanks with a unique marker to prevent matching
        df['_reference'] = df[ref_col].astype(str).str.strip().str.upper()
        # Replace empty/null references with unique values to prevent blank matching
        blank_mask = df['_reference'].isin(['', 'NAN', 'NONE', 'NULL', '0'])
        df.loc[blank_mask, '_reference'] = ['__BLANK_' + str(i) + '__' for i in range(blank_mask.sum())]

        df['_journal'] = df[journal_col].astype(str).str.strip()
        df['_net_diff'] = df['_debit'] - df['_credit']  # Debit - Credit
        df['_abs_diff'] = np.abs(df['_net_diff'])
        
        progress_bar.progress(10)
        step1_time = time.time() - start_time
        metrics_placeholder.success(f"✅ Data prepared in {step1_time:.2f}s | {len(df):,} rows processed")

        # Initialize batches
        batch1_rows = []  # Correcting Journals (paired)
        batch2_indices = set()  # Exact Match
        batch3_indices = set()  # Foreign Debit Include Commission (Debit > Credit, small diff)
        batch4_indices = set()  # Foreign Credits Include Commission (Credit > Debit, small diff)
        batch5_indices = set()  # Common References & Diff <1 (not in batch 3 or 4)
        batch6_indices = set()  # Unmatched
        
        matched_indices = set()
        
        progress_bar.progress(15)

        # BATCH 1: Correcting Journal Transactions (Paired sequentially)
        status_placeholder.info("🔍 **Step 2/7:** Processing Batch 1 - Correcting Journal Transactions...")
        correcting_mask = df['_reference'].str.contains('CORRECTING', na=False, case=False)
        correcting_df = df[correcting_mask]
        
        for idx, row in correcting_df.iterrows():
            if idx in matched_indices:
                continue
                
            # Extract journal number from "Correcting J157158" format
            journal_match = re.search(r'J(\d+)', row['_reference'], re.IGNORECASE)
            if journal_match:
                journal_num = journal_match.group(1)
                
                # Find matching journal in journal column
                potential_matches = df[
                    (df['_journal'] == journal_num) & 
                    (~df.index.isin(matched_indices)) &
                    (df.index != idx)
                ]
                
                if not potential_matches.empty:
                    match_idx = potential_matches.index[0]
                    # Add as paired rows (matched transaction FIRST, then correcting)
                    batch1_rows.append(df.loc[match_idx])
                    batch1_rows.append(df.loc[idx])
                    matched_indices.add(idx)
                    matched_indices.add(match_idx)
        
        progress_bar.progress(30)
        batch1_count = len(batch1_rows)
        metrics_placeholder.success(f"✅ Batch 1 complete: {batch1_count:,} transactions in {batch1_count//2:,} pairs")

        # BATCH 2: Exact Match (Same Reference + Amounts match exactly) - OPTIMIZED
        status_placeholder.info("✅ **Step 3/7:** Processing Batch 2 - Exact Match Transactions...")
        unmatched_df = df[~df.index.isin(matched_indices)].copy()

        batch2_rows = []  # Store paired rows to maintain order

        # Group by reference for faster processing
        grouped = unmatched_df.groupby('_reference')

        for ref, group in grouped:
            # CRITICAL FIX: Do NOT match if reference is blank/empty OR has blank marker!
            if (len(group) < 2 or
                ref in ['', 'NAN', 'NONE', 'nan', '0', 'NULL'] or
                str(ref).strip() == '' or
                str(ref).startswith('__BLANK_')):  # Skip blank markers
                continue

            # Separate into debit and credit transactions
            debit_txns = group[group['_debit'] > 0].copy()
            credit_txns = group[group['_credit'] > 0].copy()
            
            if len(debit_txns) == 0 or len(credit_txns) == 0:
                continue
            
            # Use numpy for fast matching
            debit_amounts = debit_txns['_debit'].values
            credit_amounts = credit_txns['_credit'].values
            
            debit_indices = debit_txns.index.values
            credit_indices = credit_txns.index.values
            
            used_debits = set()
            used_credits = set()
            
            # Fast pairing algorithm - EXACT match only
            for i, debit_amt in enumerate(debit_amounts):
                if i in used_debits or debit_indices[i] in matched_indices:
                    continue
                    
                # Vectorized difference calculation
                diffs = np.abs(credit_amounts - debit_amt)
                
                # Find EXACT match (diff = 0) or very close (< 0.01 for rounding errors)
                valid_matches = np.where((diffs < 0.01) & ~np.isin(np.arange(len(credit_amounts)), list(used_credits)))[0]
                
                if len(valid_matches) > 0:
                    j = valid_matches[0]  # Take first valid match
                    
                    if credit_indices[j] not in matched_indices:
                        # Add paired rows
                        batch2_rows.append(df.loc[debit_indices[i]])
                        batch2_rows.append(df.loc[credit_indices[j]])
                        batch2_indices.add(debit_indices[i])
                        batch2_indices.add(credit_indices[j])
                        matched_indices.add(debit_indices[i])
                        matched_indices.add(credit_indices[j])
                        used_debits.add(i)
                        used_credits.add(j)
        
        progress_bar.progress(50)
        metrics_placeholder.success(f"✅ Batch 2 complete: {len(batch2_indices):,} exact match transactions")

        # BATCH 3: Foreign Debit Include Commission (Debit > Credit, diff >= 1) - OPTIMIZED
        status_placeholder.info("📊 **Step 4/7:** Processing Batch 3 - Foreign Debit Include Commission...")
        unmatched_df = df[~df.index.isin(matched_indices)].copy()
        batch3_rows = []

        grouped = unmatched_df.groupby('_reference')

        for ref, group in grouped:
            # CRITICAL FIX: Do NOT match if reference is blank/empty OR has blank marker!
            if (len(group) < 2 or
                ref in ['', 'NAN', 'NONE', 'nan', '0', 'NULL'] or
                str(ref).strip() == '' or
                str(ref).startswith('__BLANK_')):  # Skip blank markers
                continue

            # Separate debit and credit transactions
            debit_txns = group[group['_debit'] > 0].copy()
            credit_txns = group[group['_credit'] > 0].copy()
            
            if len(debit_txns) == 0 or len(credit_txns) == 0:
                continue
            
            debit_amounts = debit_txns['_debit'].values
            credit_amounts = credit_txns['_credit'].values
            debit_indices = debit_txns.index.values
            credit_indices = credit_txns.index.values
            
            used_debits = set()
            used_credits = set()
            
            # Fast vectorized matching - Debit > Credit by at least 1
            for i, debit_amt in enumerate(debit_amounts):
                if i in used_debits or debit_indices[i] in matched_indices:
                    continue
                
                # Calculate differences (Debit - Credit)
                diffs = debit_amt - credit_amounts
                
                # Find matches where Debit is higher by at least 1
                valid_matches = np.where((diffs >= 1) & ~np.isin(np.arange(len(credit_amounts)), list(used_credits)))[0]
                
                if len(valid_matches) > 0:
                    j = valid_matches[0]
                    
                    if credit_indices[j] not in matched_indices:
                        batch3_rows.append(df.loc[debit_indices[i]])
                        batch3_rows.append(df.loc[credit_indices[j]])
                        matched_indices.add(debit_indices[i])
                        matched_indices.add(credit_indices[j])
                        used_debits.add(i)
                        used_credits.add(j)
        
        progress_bar.progress(65)
        metrics_placeholder.success(f"✅ Batch 3 complete: {len(batch3_rows):,} transactions with debit commission")

        # BATCH 4: Foreign Credits Include Commission (Credit > Debit, diff >= 1) - OPTIMIZED
        status_placeholder.info("📊 **Step 5/7:** Processing Batch 4 - Foreign Credits Include Commission...")
        unmatched_df = df[~df.index.isin(matched_indices)].copy()
        batch4_rows = []

        grouped = unmatched_df.groupby('_reference')

        for ref, group in grouped:
            # CRITICAL FIX: Do NOT match if reference is blank/empty OR has blank marker!
            if (len(group) < 2 or
                ref in ['', 'NAN', 'NONE', 'nan', '0', 'NULL'] or
                str(ref).strip() == '' or
                str(ref).startswith('__BLANK_')):  # Skip blank markers
                continue

            # Separate debit and credit transactions
            debit_txns = group[group['_debit'] > 0].copy()
            credit_txns = group[group['_credit'] > 0].copy()
            
            if len(debit_txns) == 0 or len(credit_txns) == 0:
                continue
            
            debit_amounts = debit_txns['_debit'].values
            credit_amounts = credit_txns['_credit'].values
            debit_indices = debit_txns.index.values
            credit_indices = credit_txns.index.values
            
            used_debits = set()
            used_credits = set()
            
            # Fast vectorized matching - Credit > Debit by at least 1
            for i, debit_amt in enumerate(debit_amounts):
                if i in used_debits or debit_indices[i] in matched_indices:
                    continue
                
                # Calculate differences (Credit - Debit)
                diffs = credit_amounts - debit_amt
                
                # Find matches where Credit is higher by at least 1
                valid_matches = np.where((diffs >= 1) & ~np.isin(np.arange(len(credit_amounts)), list(used_credits)))[0]
                
                if len(valid_matches) > 0:
                    j = valid_matches[0]
                    
                    if credit_indices[j] not in matched_indices:
                        batch4_rows.append(df.loc[debit_indices[i]])
                        batch4_rows.append(df.loc[credit_indices[j]])
                        matched_indices.add(debit_indices[i])
                        matched_indices.add(credit_indices[j])
                        used_debits.add(i)
                        used_credits.add(j)
        
        progress_bar.progress(80)
        metrics_placeholder.success(f"✅ Batch 4 complete: {len(batch4_rows):,} transactions with credit commission")

        # BATCH 5: Common References & Diff Caused By Diff Rates (0.5 <= diff < 1) - OPTIMIZED
        status_placeholder.info("📊 **Step 6/7:** Processing Batch 5 - Common References & Rate Differences...")
        unmatched_df = df[~df.index.isin(matched_indices)].copy()
        batch5_rows = []

        grouped = unmatched_df.groupby('_reference')

        for ref, group in grouped:
            # CRITICAL FIX: Do NOT match if reference is blank/empty OR has blank marker!
            if (len(group) < 2 or
                ref in ['', 'NAN', 'NONE', 'nan', '0', 'NULL'] or
                str(ref).strip() == '' or
                str(ref).startswith('__BLANK_')):  # Skip blank markers
                continue

            # Separate debit and credit transactions
            debit_txns = group[group['_debit'] > 0].copy()
            credit_txns = group[group['_credit'] > 0].copy()
            
            if len(debit_txns) == 0 or len(credit_txns) == 0:
                continue
            
            debit_amounts = debit_txns['_debit'].values
            credit_amounts = credit_txns['_credit'].values
            debit_indices = debit_txns.index.values
            credit_indices = credit_txns.index.values
            
            used_debits = set()
            used_credits = set()
            
            # Fast vectorized matching - 0.01 <= diff < 1 (small differences due to rates)
            for i, debit_amt in enumerate(debit_amounts):
                if i in used_debits or debit_indices[i] in matched_indices:
                    continue
                
                # Calculate absolute differences
                diffs = np.abs(credit_amounts - debit_amt)
                
                # Find matches where 0.01 <= diff < 1 (captures all small rate differences)
                valid_matches = np.where((diffs >= 0.01) & (diffs < 1) & ~np.isin(np.arange(len(credit_amounts)), list(used_credits)))[0]
                
                if len(valid_matches) > 0:
                    j = valid_matches[0]
                    
                    if credit_indices[j] not in matched_indices:
                        batch5_rows.append(df.loc[debit_indices[i]])
                        batch5_rows.append(df.loc[credit_indices[j]])
                        matched_indices.add(debit_indices[i])
                        matched_indices.add(credit_indices[j])
                        used_debits.add(i)
                        used_credits.add(j)
        
        progress_bar.progress(90)
        metrics_placeholder.success(f"✅ Batch 5 complete: {len(batch5_rows):,} transactions with rate differences")

        # BATCH 6: Unmatched Transactions
        status_placeholder.info("❌ **Step 7/7:** Processing Batch 6 - Unmatched Transactions...")
        batch6_indices = set(df.index) - matched_indices
        
        # Create batch dataframes (all batches use paired rows now)
        batch1_df = pd.DataFrame(batch1_rows) if batch1_rows else pd.DataFrame()
        batch2_df = pd.DataFrame(batch2_rows) if batch2_rows else pd.DataFrame()
        batch3_df = pd.DataFrame(batch3_rows) if batch3_rows else pd.DataFrame()
        batch4_df = pd.DataFrame(batch4_rows) if batch4_rows else pd.DataFrame()
        batch5_df = pd.DataFrame(batch5_rows) if batch5_rows else pd.DataFrame()
        batch6_df = df.loc[list(batch6_indices)].copy() if batch6_indices else pd.DataFrame()
        
        progress_bar.progress(95)
        
        # Calculate processing time
        elapsed_time = time.time() - start_time

        # CRITICAL VALIDATION: Ensure no duplications or data loss
        total_output_rows = len(batch1_df) + len(batch2_df) + len(batch3_df) + len(batch4_df) + len(batch5_df) + len(batch6_df)

        # Calculate sums for validation
        original_debit_sum = df['_debit'].sum()
        original_credit_sum = df['_credit'].sum()

        output_debit_sum = 0
        output_credit_sum = 0

        for batch_df in [batch1_df, batch2_df, batch3_df, batch4_df, batch5_df, batch6_df]:
            if not batch_df.empty and '_debit' in batch_df.columns:
                output_debit_sum += batch_df['_debit'].sum()
                output_credit_sum += batch_df['_credit'].sum()

        # Validation checks
        has_duplicates = total_output_rows != len(df)
        sum_mismatch = abs(original_debit_sum - output_debit_sum) > 0.01 or abs(original_credit_sum - output_credit_sum) > 0.01

        results = {
            'batch1': batch1_df,
            'batch2': batch2_df,
            'batch3': batch3_df,
            'batch4': batch4_df,
            'batch5': batch5_df,
            'batch6': batch6_df,
            'stats': {
                'total': len(df),
                'batch1': len(batch1_df),
                'batch2': len(batch2_df),
                'batch3': len(batch3_df),
                'batch4': len(batch4_df),
                'batch5': len(batch5_df),
                'batch6': len(batch6_df),
                'processing_time': elapsed_time,
                # Validation metrics
                'original_rows': len(df),
                'output_rows': total_output_rows,
                'original_debit_sum': original_debit_sum,
                'original_credit_sum': original_credit_sum,
                'output_debit_sum': output_debit_sum,
                'output_credit_sum': output_credit_sum,
                'has_duplicates': has_duplicates,
                'sum_mismatch': sum_mismatch
            }
        }

        progress_bar.progress(100)
        
        st.session_state.corporate_results = results
        
        # Clear placeholders and show final completion message
        status_placeholder.empty()
        progress_placeholder.empty()
        metrics_placeholder.empty()
        
        # Show comprehensive completion message with speed emphasis
        rows_per_sec = len(df) / elapsed_time if elapsed_time > 0 else 0
        matched_count = len(matched_indices)
        match_rate = (matched_count / len(df) * 100) if len(df) > 0 else 0
        
        # Show completion message with validation warnings if needed
        validation_msg = ""
        if has_duplicates:
            validation_msg += f"\n⚠️ **WARNING**: Row count mismatch! Input: {len(df):,} | Output: {total_output_rows:,}"
        if sum_mismatch:
            validation_msg += f"\n⚠️ **WARNING**: Sum mismatch detected!"
            validation_msg += f"\n   - Input FD: {original_debit_sum:,.2f} | Output FD: {output_debit_sum:,.2f}"
            validation_msg += f"\n   - Input FC: {original_credit_sum:,.2f} | Output FC: {output_credit_sum:,.2f}"

        if validation_msg:
            st.error(f"""
            ## ⚠️ Reconciliation Complete with Warnings!
            {validation_msg}

            Please review the results carefully!
            """)

        st.success(f"""
        ## 🎉 Reconciliation Complete! ⚡ ULTRA FAST

        **⚡ Performance Metrics:**
        - 🚀 **Lightning Speed**: {rows_per_sec:,.0f} rows/second
        - ⏱️ **Total Time**: {elapsed_time:.2f} seconds
        - 📊 **Processed**: {len(df):,} total transactions
        - ✅ **Matched**: {matched_count:,} transactions ({match_rate:.1f}%)
        - ❌ **Unmatched**: {len(batch6_indices):,} transactions ({100-match_rate:.1f}%)

        **Batch Summary:**
        - 📋 Batch 1 (Correcting Journals): {len(batch1_df):,} transactions
        - ✅ Batch 2 (Exact Match): {len(batch2_df):,} transactions
        - 💰 Batch 3 (FD + Commission): {len(batch3_df):,} transactions
        - 💳 Batch 4 (FC + Commission): {len(batch4_df):,} transactions
        - 📊 Batch 5 (Rate Differences): {len(batch5_df):,} transactions
        - ❌ Batch 6 (Unmatched): {len(batch6_df):,} transactions

        **✅ Data Integrity:**
        - Input Rows: {len(df):,} | Output Rows: {total_output_rows:,}
        - Input FD Sum: {original_debit_sum:,.2f} | Output FD Sum: {output_debit_sum:,.2f}
        - Input FC Sum: {original_credit_sum:,.2f} | Output FC Sum: {output_credit_sum:,.2f}

        🎯 **Results are ready for viewing and export below!**
        """)
        
        st.rerun()

    def render_reference_extraction(self):
        """Render reference extraction UI"""
        st.markdown("### 📝 Extract References from Comment Column")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("🔍 Extract References", type="primary", use_container_width=True):
                self.execute_reference_extraction()
        
        with col2:
            if st.session_state.corporate_reference_extracted:
                st.success("✅ References extracted! Check the 'Reference' column.")
        
        with col3:
            if st.session_state.corporate_reference_extracted:
                if st.button("👁️ View Data", type="secondary", use_container_width=True):
                    st.session_state.show_extracted_data = True
    
    def execute_reference_extraction(self):
        """Execute reference extraction from Comment column"""
        if st.session_state.corporate_df is None:
            st.error("❌ No data loaded. Upload a file first.")
            return
        
        df = st.session_state.corporate_df.copy()
        
        # Check if Comment column exists (Column B)
        comment_columns = [col for col in df.columns if 'comment' in col.lower() or col == 'B' or col == 'Column B']
        
        if not comment_columns:
            st.error("❌ No Comment column found. Looking for 'Comment', 'B', or 'Column B'.")
            st.info(f"Available columns: {', '.join(df.columns.tolist())}")
            return
        
        comment_col = comment_columns[0]
        st.info(f"📌 Using column: **{comment_col}** for extraction")
        
        # Extract references with optimized processing
        total_rows = len(df)
        with st.spinner(f"⚡ Extracting references from {total_rows:,} rows..."):
            import time
            start_time = time.time()
            
            # Use the extract_references function (correct logic!)
            df['Reference'] = df[comment_col].apply(self.extract_references)
            
            elapsed_time = time.time() - start_time
            
            # Show preview
            extracted_count = (df['Reference'].str.len() > 0).sum()
            rows_per_sec = total_rows / elapsed_time if elapsed_time > 0 else 0
            
            st.success(f"⚡ Extracted {extracted_count:,}/{total_rows:,} references in {elapsed_time:.2f}s ({rows_per_sec:,.0f} rows/sec)")
            
            # Show sample
            sample = df[df['Reference'].str.len() > 0][['Reference', comment_col]].head(10)
            if not sample.empty:
                st.markdown("**Sample Extractions:**")
                st.dataframe(sample, use_container_width=True)
            
            # Update session state - Update both df and data to keep them in sync
            st.session_state.corporate_df = df
            st.session_state.corporate_data = df  # Keep corporate_data in sync
            st.session_state.corporate_reference_extracted = True
            st.session_state.show_extracted_data = True  # Auto-show data after extraction
            
            # Debug: Confirm column was added
            st.info(f"✅ Reference column successfully added! Total columns now: {len(df.columns)}")
            st.info(f"📋 All columns: {', '.join(df.columns.tolist())}")
    
    def render_extracted_data_view(self):
        """Render the extracted data with Reference column"""
        if not st.session_state.get('show_extracted_data', False):
            return
        
        if st.session_state.corporate_df is None:
            return
        
        df = st.session_state.corporate_df
        
        # Debug: Show current columns
        st.info(f"🔍 Debug - Columns in dataframe: {', '.join(df.columns.tolist())}")
        
        # Check if Reference column exists
        if 'Reference' not in df.columns:
            st.warning("⚠️ No Reference column found. Please extract references first.")
            st.error(f"Available columns: {', '.join(df.columns.tolist())}")
            return
        
        st.markdown("---")
        st.markdown("### 📊 Extracted Data with Reference Column")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            references_extracted = df['Reference'].str.len().gt(0).sum()
            st.metric("References Found", f"{references_extracted:,}")
        with col3:
            blank_refs = df['Reference'].str.len().eq(0).sum()
            st.metric("Blank References", f"{blank_refs:,}")
        with col4:
            extraction_rate = (references_extracted / len(df) * 100) if len(df) > 0 else 0
            st.metric("Extraction Rate", f"{extraction_rate:.1f}%")
        
        # Show dataframe with Reference column highlighted
        st.markdown("**Full Data Preview:**")
        
        # Move Reference column to front for visibility
        cols = ['Reference'] + [col for col in df.columns if col != 'Reference']
        df_display = df[cols]
        
        st.dataframe(df_display, use_container_width=True, height=600)
        
        # Option to hide the view
        if st.button("🔼 Hide Data View"):
            st.session_state.show_extracted_data = False
            st.rerun()

    def render_results(self):
        """Render batch reconciliation results matching exact format from image"""

        results = st.session_state.corporate_results
        stats = results['stats']

        st.markdown("## 🎉 Corporate Settlement Results")
        
        # Performance banner
        processing_time = stats.get('processing_time', 0)
        rows_per_sec = stats['total'] / processing_time if processing_time > 0 else 0
        st.success(f"⚡ **Ultra-Fast Processing:** {stats['total']:,} rows in {processing_time:.2f}s ({rows_per_sec:,.0f} rows/sec)")

        # Export all results
        st.markdown("### 📥 Export Complete Results")
        col_exp1, col_exp2 = st.columns(2)
        
        # Combine all batches for export
        all_batches = []
        batch_configs = [
            ('batch1', 'Correcting Journal Batch'),
            ('batch2', 'Exact Match Batch'),
            ('batch3', 'Foreign Debit Include Commission'),
            ('batch4', 'Foreign Credits Include Commission'),
            ('batch5', 'Common References & Diff Caused By Diff Rates'),
            ('batch6', 'Unmatched Transactions')
        ]
        
        for batch_key, batch_title in batch_configs:
            batch_df = results[batch_key].copy()
            if not batch_df.empty:
                # Remove internal columns first
                display_df = batch_df.drop(columns=[c for c in batch_df.columns if c.startswith('_')], errors='ignore')
                
                # Add section header row - title ONLY in first column
                header_dict = {col: [batch_title if col == display_df.columns[0] else ''] for col in display_df.columns}
                header_row = pd.DataFrame(header_dict)
                empty_row = pd.DataFrame({col: [''] for col in display_df.columns})
                
                all_batches.append(header_row)
                all_batches.append(display_df)
                all_batches.append(empty_row)
        
        if all_batches:
            combined_df = pd.concat(all_batches, ignore_index=True)
            
            with col_exp1:
                # Excel export
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, index=False, sheet_name='Reconciliation Results')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name="corporate_reconciliation_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col_exp2:
                # CSV export
                csv_data = combined_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name="corporate_reconciliation_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # Summary Metrics
        st.markdown("### 📊 Summary Metrics")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.metric("**Total**", f"{stats['total']:,}")
        with col2:
            pct = (stats['batch1'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("Correcting", f"{stats['batch1']:,}", f"{pct:.1f}%")
        with col3:
            pct = (stats['batch2'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("Exact", f"{stats['batch2']:,}", f"{pct:.1f}%")
        with col4:
            pct = (stats['batch3'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("FD + Comm", f"{stats['batch3']:,}", f"{pct:.1f}%")
        with col5:
            pct = (stats['batch4'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("FC + Comm", f"{stats['batch4']:,}", f"{pct:.1f}%")
        with col6:
            pct = (stats['batch5'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("Diff < 1", f"{stats['batch5']:,}", f"{pct:.1f}%")
        with col7:
            pct = (stats['batch6'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.metric("Unmatched", f"{stats['batch6']:,}", f"{pct:.1f}%")

        # Display each batch with proper formatting
        st.markdown("---")
        
        # Batch 1: Correcting Journal Batch
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Correcting Journal Batch</p>', unsafe_allow_html=True)
        batch1_df = results['batch1']
        if not batch1_df.empty:
            display_df = batch1_df.drop(columns=[c for c in batch1_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info(f"✅ {len(batch1_df):,} transactions in {len(batch1_df)//2:,} pairs")
        else:
            st.info("No correcting journal transactions found")
        
        # Batch 2: Exact Match Batch
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Exact Match Batch</p>', unsafe_allow_html=True)
        batch2_df = results['batch2']
        if not batch2_df.empty:
            display_df = batch2_df.drop(columns=[c for c in batch2_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info(f"✅ {len(batch2_df):,} transactions in {len(batch2_df)//2:,} pairs")
        else:
            st.info("No exact match transactions found")
        
        # Batch 3: Foreign Debit Include Commission
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Foreign Debit Include Commission</p>', unsafe_allow_html=True)
        batch3_df = results['batch3']
        if not batch3_df.empty:
            display_df = batch3_df.drop(columns=[c for c in batch3_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info(f"✅ {len(batch3_df):,} transactions (Debit includes commission)")
        else:
            st.info("No foreign debit commission transactions found")
        
        # Batch 4: Foreign Credits Include Commission
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Foreign Credits Include Commission</p>', unsafe_allow_html=True)
        batch4_df = results['batch4']
        if not batch4_df.empty:
            display_df = batch4_df.drop(columns=[c for c in batch4_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info(f"✅ {len(batch4_df):,} transactions (Credit includes commission)")
        else:
            st.info("No foreign credit commission transactions found")
        
        # Batch 5: Common References & Diff < 1
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Common References & Diff Caused By Diff Rates</p>', unsafe_allow_html=True)
        st.caption("Note: The difference between FD amount and FC amount is less than 1 but Reference Column is the same")
        batch5_df = results['batch5']
        if not batch5_df.empty:
            display_df = batch5_df.drop(columns=[c for c in batch5_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info(f"✅ {len(batch5_df):,} transactions with small differences")
        else:
            st.info("No transactions with small rate differences found")
        
        # Batch 6: Unmatched Transactions
        st.markdown('<p style="font-family: Calibri, sans-serif; font-size: 18px; font-weight: bold;">Unmatched Transactions</p>', unsafe_allow_html=True)
        batch6_df = results['batch6']
        if not batch6_df.empty:
            display_df = batch6_df.drop(columns=[c for c in batch6_df.columns if c.startswith('_')], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=400)
            st.warning(f"⚠️ {len(batch6_df):,} transactions remain unmatched")
        else:
            st.success("✅ All transactions matched!")
