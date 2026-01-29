"""
Kazang Workflow Component - Similar to FNB but with Kazang-specific Reference Extraction
=========================================================================================
Advanced reconciliation engine with weighted scoring matching
Date (30%) + Reference (40%) + Amount (30%) = Total Score

Key Differences from FNB:
- No statement reference extraction needed
- Payment Ref extracted from Comment column only
- Format: "Ref #RJ58822828410. - Gugu 6408370691" → Payment Ref = "Gugu"
- Format: "Ref #RJ58953541109. - Lucy6410281493" → Payment Ref = "Lucy"
- Format: "In: CSH666722052: Thandi 6456043502" → Payment Ref = "Thandi"
- Format: "Reversal: ECO117918890: Eco 6456318627" → Payment Ref = "Eco"
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
import sys
import os
import re

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_cleaner import clean_amount_column  # type: ignore
from column_selector import ColumnSelector  # type: ignore
from file_loader import load_uploaded_file, get_dataframe_info  # type: ignore
from extraction import ReferenceExtractor  # type: ignore


class KazangWorkflow:
    """Kazang Bank Reconciliation Workflow - Similar to FNB with Kazang-specific Reference Extraction"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'kazang_ledger' not in st.session_state:
            st.session_state.kazang_ledger = None
        if 'kazang_statement' not in st.session_state:
            st.session_state.kazang_statement = None
        if 'kazang_results' not in st.session_state:
            st.session_state.kazang_results = None
        if 'kazang_column_mapping' not in st.session_state:
            st.session_state.kazang_column_mapping = {}
        if 'kazang_match_settings' not in st.session_state:
            st.session_state.kazang_match_settings = {
                'ledger_date_col': 'Date',
                'ledger_ref_col': 'Payment Ref',
                'ledger_debit_col': 'Debit',
                'ledger_credit_col': 'Credit',
                'statement_date_col': 'Date',
                'statement_ref_col': 'Reference',
                'statement_amt_col': 'Amount',
                'fuzzy_ref': True,
                'similarity_ref': 85,
                'match_dates': True,
                'match_references': True,
                'match_amounts': True,
                'use_debits_only': False,
                'use_credits_only': False,
                'use_both_debit_credit': True
            }

    def render(self):
        """Render Kazang workflow page"""

        # Header
        st.markdown("""
        <style>
        .gradient-header {
            background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .gradient-header h1 {
            color: white;
            margin: 0;
        }
        .gradient-header p {
            color: #fef3c7;
            margin: 0.5rem 0 0 0;
        }
        .success-box {
            background-color: #d1fae5;
            border-left: 4px solid #059669;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #dbeafe;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>

        <div class="gradient-header">
            <h1>💳 Kazang Workflow</h1>
            <p>Advanced Kazang Reconciliation • Weighted Scoring Algorithm • 30% Date + 40% Reference + 30% Amount</p>
        </div>
        """, unsafe_allow_html=True)

        # Step 1: File Upload
        self.render_file_upload()

        # Step 2-5: Show configuration sections (if files uploaded)
        if st.session_state.kazang_ledger is not None and st.session_state.kazang_statement is not None:
            # Quick status summary at top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📗 Ledger Rows", f"{len(st.session_state.kazang_ledger):,}")
            with col2:
                st.metric("📘 Statement Rows", f"{len(st.session_state.kazang_statement):,}")
            with col3:
                st.metric("✅ Status", "Ready to Configure")
            self.render_data_tools()

            # Step 3: Column Mapping
            self.render_column_mapping()

            # Step 4: Matching Settings
            self.render_matching_settings()

            # Step 5: Run Reconciliation
            self.render_reconciliation_controls()

        # Step 5: Display Results
        if st.session_state.kazang_results is not None:
            self.render_results()

    def render_file_upload(self):
        """Render file upload section - Cloud deployment compatible"""
        
        st.subheader("📁 Step 1: Import Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger File**")

            # Show existing data status FIRST
            if st.session_state.kazang_ledger is not None:
                st.success(f"📊 **Ledger:** {len(st.session_state.kazang_ledger)} rows × {len(st.session_state.kazang_ledger.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.kazang_ledger.columns))

            ledger_file = st.file_uploader("Upload NEW Ledger File", type=['xlsx', 'xls', 'csv'], key='kazang_ledger_upload', help="Upload a new file to replace current data")

            if ledger_file is not None:
                # Use optimized loader with caching and progress indicator
                ledger_df, is_new = load_uploaded_file(
                    ledger_file,
                    session_key='kazang_ledger',
                    hash_key='kazang_ledger_hash',
                    show_progress=True
                )

                if is_new:
                    # New file loaded - update metadata
                    st.session_state.kazang_ledger_original_cols = list(ledger_df.columns)

                    # Reset saved selections for new file
                    if 'kazang_saved_selections' in st.session_state:
                        del st.session_state.kazang_saved_selections

                    st.success(f"✅ New ledger loaded: {get_dataframe_info(ledger_df)}")

        with col2:
            st.markdown("**Bank Statement File**")

            # Show existing data status FIRST
            if st.session_state.kazang_statement is not None:
                st.success(f"📊 **Statement:** {len(st.session_state.kazang_statement)} rows × {len(st.session_state.kazang_statement.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.kazang_statement.columns))

            statement_file = st.file_uploader("Upload NEW Statement File", type=['xlsx', 'xls', 'csv'], key='kazang_statement_upload', help="Upload a new file to replace current data")

            if statement_file is not None:
                # Use optimized loader with caching and progress indicator
                statement_df, is_new = load_uploaded_file(
                    statement_file,
                    session_key='kazang_statement',
                    hash_key='kazang_statement_hash',
                    show_progress=True
                )

                if is_new:
                    # New file loaded - update metadata
                    st.session_state.kazang_statement_original_cols = list(statement_df.columns)

                    # Reset saved selections for new file
                    if 'kazang_saved_selections' in st.session_state:
                        del st.session_state.kazang_saved_selections

                    st.success(f"✅ New statement loaded: {get_dataframe_info(statement_df)}")
        
        # Add View & Edit Data section
        if st.session_state.kazang_ledger is not None or st.session_state.kazang_statement is not None:
            st.markdown("---")
            st.subheader("👁️ Step 1.5: View & Edit Data")
            st.info("💡 **Edit your data before reconciliation:** View, add rows, delete rows, copy/paste from Excel, and more!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.kazang_ledger is not None:
                    if st.button("📊 View & Edit Ledger", key='kazang_view_edit_ledger_btn', use_container_width=True, type="secondary"):
                        st.session_state.kazang_show_ledger_editor = True
            
            with col2:
                if st.session_state.kazang_statement is not None:
                    if st.button("📊 View & Edit Statement", key='kazang_view_edit_statement_btn', use_container_width=True, type="secondary"):
                        st.session_state.kazang_show_statement_editor = True
            
            # Show Ledger Editor
            if st.session_state.get('kazang_show_ledger_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.kazang_ledger, "📗 Ledger Editor", "kazang_ledger")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.kazang_ledger = saved_data
                    st.session_state.kazang_show_ledger_editor = False
                    st.success("✅ Ledger data saved successfully!")

                if st.button("❌ Close Editor", key='kazang_close_ledger_editor'):
                    st.session_state.kazang_show_ledger_editor = False

            # Show Statement Editor
            if st.session_state.get('kazang_show_statement_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.kazang_statement, "📘 Statement Editor", "kazang_statement")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.kazang_statement = saved_data
                    st.session_state.kazang_show_statement_editor = False
                    st.success("✅ Statement data saved successfully!")

                if st.button("❌ Close Editor", key='kazang_close_statement_editor'):
                    st.session_state.kazang_show_statement_editor = False

    def render_data_tools(self):
        """Render data processing tools - Kazang specific: Extract Payment Ref from Comment"""
        st.markdown("---")
        st.subheader("🛠️ Step 2: Data Processing Tools")

        # Cache column lists to avoid repeated DataFrame column access
        if 'kazang_ledger_cols_cache' not in st.session_state or st.session_state.get('kazang_ledger_cols_dirty', True):
            st.session_state.kazang_ledger_cols_cache = [str(col) for col in st.session_state.kazang_ledger.columns] if st.session_state.kazang_ledger is not None else []
            st.session_state.kazang_ledger_cols_dirty = False

        if 'kazang_statement_cols_cache' not in st.session_state or st.session_state.get('kazang_statement_cols_dirty', True):
            st.session_state.kazang_statement_cols_cache = [str(col) for col in st.session_state.kazang_statement.columns] if st.session_state.kazang_statement is not None else []
            st.session_state.kazang_statement_cols_dirty = False

        ledger_cols = st.session_state.kazang_ledger_cols_cache
        statement_cols = st.session_state.kazang_statement_cols_cache

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔢 Extract Kazang Payment Ref**")
            st.caption("Extract Payment Ref from Ledger Comment column")
            st.caption("Format: 'Ref #RJ58822828410. - Gugu 6408370691' → 'Gugu'")
            if 'Payment Ref' in ledger_cols:
                st.success("✅ Payment Ref column added to Ledger")
            if st.button("🚀 Extract Payment Ref", key='kazang_extract_payment_ref_btn', use_container_width=True):
                self.extract_kazang_payment_ref()

        with col2:
            st.markdown("**🔢 RJ Number Extraction**")
            st.caption("Extract RJ numbers from Comment column")
            if 'RJ-Number' in ledger_cols:
                st.success("✅ RJ-Number column added")
            if st.button("🚀 Extract RJ Number", key='kazang_rj_number_btn', use_container_width=True):
                self.extract_rj_number()

    def extract_kazang_payment_ref(self):
        """
        Extract Payment Ref from Kazang Ledger Comment column using unified ReferenceExtractor.

        Supports all formats including:
        - "Ref CSH667941330 - (6503065718)" → Payment Ref = "6503065718" (phone number)
        - "Reversal: CSH564980448: 6505166670" → Payment Ref = "6505166670" (phone number)
        - "Ref #RJ58822828410. - Gugu 6408370691" → Payment Ref = "Gugu" (name)
        - "Ref CSH764074250 - (Phuthani mabhena)" → Payment Ref = "Phuthani mabhena" (name)
        """
        try:
            if st.session_state.kazang_ledger is None:
                st.error("❌ Please import a ledger first!")
                return

            ledger = st.session_state.kazang_ledger.copy()

            # Find Comment column (case-insensitive)
            comment_col = None
            for col in ledger.columns:
                col_str = str(col).strip().lower()
                if col_str in ['comment', 'comments', 'description', 'narration', 'particulars']:
                    comment_col = col
                    break

            if comment_col is None:
                # Try to find column B (index 1) as fallback - common for ledger files
                if len(ledger.columns) > 1:
                    comment_col = ledger.columns[1]
                    st.info(f"ℹ️ Using column '{comment_col}' for Payment Ref extraction")
                else:
                    st.error("❌ No suitable comment column found in ledger")
                    return

            # Check if Payment Ref column already exists
            if 'Payment Ref' in ledger.columns:
                st.info("ℹ️ Payment Ref column already exists in ledger")
                return

            # Apply extraction using unified ReferenceExtractor
            payment_refs = []
            rj_numbers = []

            for val in ledger[comment_col]:
                # Use unified extractor for both RJ number and Payment Ref
                rj, payref = ReferenceExtractor.extract_rj_and_ref(str(val) if pd.notna(val) else '')
                payment_refs.append(payref)
                rj_numbers.append(rj)

            # Find position to insert columns (after Comment column)
            comment_idx = list(ledger.columns).index(comment_col)
            
            # Insert Payment Ref column
            ledger.insert(comment_idx + 1, 'Payment Ref', payment_refs)
            
            # Also insert RJ-Number if not exists
            if 'RJ-Number' not in ledger.columns:
                ledger.insert(comment_idx + 2, 'RJ-Number', rj_numbers)

            st.session_state.kazang_ledger = ledger

            # Mark column cache as dirty
            st.session_state.kazang_ledger_cols_dirty = True

            # Reset saved selections to trigger reconfiguration
            if 'kazang_saved_selections' in st.session_state:
                del st.session_state.kazang_saved_selections

            # Show success with sample results
            st.success(f"✅ Payment Ref and RJ-Number columns added to Ledger!")
            st.info(f"📊 Processed {len(payment_refs)} transactions\n\n"
                   f"💾 **Columns persisted!** They will appear in the dropdown below.")

            # Show sample extractions
            with st.expander("📋 Sample Extractions (First 10)"):
                sample_data = []
                for i in range(min(10, len(payment_refs))):
                    sample_data.append({
                        'Original Comment': ledger.iloc[i][comment_col] if i < len(ledger) else '',
                        'Payment Ref': payment_refs[i],
                        'RJ-Number': rj_numbers[i]
                    })
                st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error extracting Payment Ref: {str(e)}")

    def extract_rj_number(self):
        """Extract RJ numbers from Comment column"""
        try:
            if st.session_state.kazang_ledger is None:
                st.error("❌ Please import a ledger first!")
                return

            ledger = st.session_state.kazang_ledger.copy()

            if 'RJ-Number' in ledger.columns:
                st.info("ℹ️ RJ-Number column already exists")
                return

            # Find Comment column
            comment_col = None
            for col in ledger.columns:
                col_str = str(col).strip().lower()
                if col_str in ['comment', 'comments', 'description', 'narration', 'particulars']:
                    comment_col = col
                    break

            if comment_col is None and len(ledger.columns) > 1:
                comment_col = ledger.columns[1]

            if comment_col is None:
                st.error("❌ No comment column found")
                return

            def extract_rj(comment):
                if not isinstance(comment, str):
                    return ''
                # Patterns: RJ123456, CSH764074250, TX123456, ZVC128809565, ECO904183634, INN757797206
                rj_match = re.search(r'#?(RJ|CSH|TX|ZVC|ECO|INN)[-]?(\d{6,})', comment, re.IGNORECASE)
                return rj_match.group(0).replace('#', '').replace('-', '').upper() if rj_match else ''

            rj_numbers = [extract_rj(val) for val in ledger[comment_col]]

            comment_idx = list(ledger.columns).index(comment_col)
            ledger.insert(comment_idx + 1, 'RJ-Number', rj_numbers)

            st.session_state.kazang_ledger = ledger
            st.session_state.kazang_ledger_cols_dirty = True

            if 'kazang_saved_selections' in st.session_state:
                del st.session_state.kazang_saved_selections

            st.success("✅ RJ-Number column added to Ledger!")

            with st.expander("📋 Sample Extractions (First 10)"):
                sample_data = []
                for i in range(min(10, len(rj_numbers))):
                    sample_data.append({
                        'Original Comment': ledger.iloc[i][comment_col],
                        'RJ-Number': rj_numbers[i]
                    })
                st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error extracting RJ numbers: {str(e)}")

    def render_column_mapping(self):
        """Render column mapping configuration"""
        st.markdown("---")
        st.subheader("⚙️ Step 3: Configure Column Mapping")

        # Use cached column lists for better performance
        ledger_cols = st.session_state.kazang_ledger_cols_cache
        statement_cols = st.session_state.kazang_statement_cols_cache

        # Show available columns with detailed info
        with st.expander("ℹ️ View Available Columns", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Ledger Columns ({len(ledger_cols)} total):**")
                st.code(", ".join(ledger_cols))
                added_cols = [col for col in ['Payment Ref', 'RJ-Number'] if col in ledger_cols]
                if added_cols:
                    st.info(f"✨ Added columns: {', '.join(added_cols)}")
            with col_b:
                st.markdown(f"**Statement Columns ({len(statement_cols)} total):**")
                st.code(", ".join(statement_cols))

        # Initialize saved selections if not present
        if 'kazang_saved_selections' not in st.session_state:
            st.session_state.kazang_saved_selections = {}

        def get_safe_index(col_list, saved_key, default_name):
            if saved_key in st.session_state.kazang_saved_selections:
                saved_idx = st.session_state.kazang_saved_selections[saved_key]
                if 0 <= saved_idx < len(col_list):
                    return saved_idx
            if default_name in col_list:
                return col_list.index(default_name)
            return 0

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger Columns**")

            ledger_date_selection = st.selectbox(
                "Date Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_date_idx', 'Date'),
                key='kazang_ledger_date_selector'
            )
            st.session_state.kazang_saved_selections['ledger_date_idx'] = ledger_cols.index(ledger_date_selection)
            st.session_state.kazang_match_settings['ledger_date_col'] = ledger_date_selection

            ledger_ref_selection = st.selectbox(
                "Reference Column (Payment Ref)",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_ref_idx', 'Payment Ref'),
                key='kazang_ledger_ref_selector'
            )
            st.session_state.kazang_saved_selections['ledger_ref_idx'] = ledger_cols.index(ledger_ref_selection)
            st.session_state.kazang_match_settings['ledger_ref_col'] = ledger_ref_selection

            ledger_debit_selection = st.selectbox(
                "Debit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_debit_idx', 'Debit'),
                key='kazang_ledger_debit_selector'
            )
            st.session_state.kazang_saved_selections['ledger_debit_idx'] = ledger_cols.index(ledger_debit_selection)
            st.session_state.kazang_match_settings['ledger_debit_col'] = ledger_debit_selection

            ledger_credit_selection = st.selectbox(
                "Credit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_credit_idx', 'Credit'),
                key='kazang_ledger_credit_selector'
            )
            st.session_state.kazang_saved_selections['ledger_credit_idx'] = ledger_cols.index(ledger_credit_selection)
            st.session_state.kazang_match_settings['ledger_credit_col'] = ledger_credit_selection

        with col2:
            st.markdown("**Statement Columns**")

            statement_date_selection = st.selectbox(
                "Date Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_date_idx', 'Date'),
                key='kazang_statement_date_selector'
            )
            st.session_state.kazang_saved_selections['statement_date_idx'] = statement_cols.index(statement_date_selection)
            st.session_state.kazang_match_settings['statement_date_col'] = statement_date_selection

            statement_ref_selection = st.selectbox(
                "Reference Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_ref_idx', 'Reference'),
                key='kazang_statement_ref_selector'
            )
            st.session_state.kazang_saved_selections['statement_ref_idx'] = statement_cols.index(statement_ref_selection)
            st.session_state.kazang_match_settings['statement_ref_col'] = statement_ref_selection

            statement_amt_selection = st.selectbox(
                "Amount Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_amt_idx', 'Amount'),
                key='kazang_statement_amt_selector'
            )
            st.session_state.kazang_saved_selections['statement_amt_idx'] = statement_cols.index(statement_amt_selection)
            st.session_state.kazang_match_settings['statement_amt_col'] = statement_amt_selection

    def render_matching_settings(self):
        """Render matching settings configuration"""
        st.markdown("---")
        st.subheader("🎯 Step 4: Matching Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Matching Criteria**")
            st.session_state.kazang_match_settings['match_dates'] = st.checkbox(
                "Match by Dates", value=True, key='kazang_match_dates'
            )
            if st.session_state.kazang_match_settings['match_dates']:
                st.session_state.kazang_match_settings['date_tolerance'] = st.checkbox(
                    "  ↳ Allow ±1 Day Tolerance", value=False, key='kazang_date_tolerance',
                    help="When enabled, dates within 1 day difference will be considered matching"
                )
            else:
                st.session_state.kazang_match_settings['date_tolerance'] = False

            st.session_state.kazang_match_settings['match_references'] = st.checkbox(
                "Match by References", value=True, key='kazang_match_refs'
            )
            st.session_state.kazang_match_settings['match_amounts'] = st.checkbox(
                "Match by Amounts", value=True, key='kazang_match_amts'
            )

        with col2:
            st.markdown("**Fuzzy Matching**")
            st.session_state.kazang_match_settings['fuzzy_ref'] = st.checkbox(
                "Enable Fuzzy Reference Matching", value=True, key='kazang_fuzzy'
            )
            st.session_state.kazang_match_settings['similarity_ref'] = st.slider(
                "Similarity Threshold (%)", 50, 100, 85, key='kazang_similarity'
            )

        with col3:
            st.markdown("**Amount Matching Mode**")
            amount_mode = st.radio(
                "Select Mode:",
                ["Use Both Debits and Credits", "Use Debits Only", "Use Credits Only"],
                key='kazang_amount_mode'
            )

            st.session_state.kazang_match_settings['use_debits_only'] = (amount_mode == "Use Debits Only")
            st.session_state.kazang_match_settings['use_credits_only'] = (amount_mode == "Use Credits Only")
            st.session_state.kazang_match_settings['use_both_debit_credit'] = (amount_mode == "Use Both Debits and Credits")

        # Show algorithm explanation
        with st.expander("ℹ️ How the Kazang Matching Algorithm Works"):
            st.markdown("""
            **💳 Kazang Multi-Phase Reconciliation:**

            **Key Difference from FNB:**
            - Payment Ref is extracted from Comment column only
            - Format: `Ref #RJ58822828410. - Gugu 6408370691` → Payment Ref = `Gugu`
            - No statement reference extraction needed

            **Phase 1: Perfect Match (100% Exact)**
            - ✅ **Date**: Exact same day (or ±1 day if tolerance enabled)
            - ✅ **Reference**: Case-insensitive exact match (100% similar)
            - ✅ **Amount**: Exact match (to 2 decimal places)

            **Phase 2: Fuzzy Matching**
            - ✅ **Date**: Exact same day (or ±1 day if tolerance enabled)
            - 🔍 **Reference**: Fuzzy match using fuzzywuzzy (≥ your threshold %)
            - ✅ **Amount**: Exact match

            **Phase 3: Foreign Credits (>10,000)**
            - 💰 **Amount**: ALWAYS required (exact match)
            - 📅 **Date**: Optional (only if enabled)
            - ❌ **Reference**: IGNORED

            **Phase 4: Split Transactions**
            - 🔀 Dynamic Programming algorithm
            - Finds combinations of 2-6 transactions that sum to target
            """)

    def render_reconciliation_controls(self):
        """Render reconciliation execution controls"""
        st.markdown("---")
        st.subheader("⚡ Step 5: Execute Reconciliation")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("🚀 Start Reconciliation", type="primary", use_container_width=True, key="kazang_start_recon"):
                self.run_reconciliation()

        with col2:
            if st.button("🔄 Reset", use_container_width=True, key="kazang_reset"):
                st.session_state.kazang_results = None
                st.rerun()

        with col3:
            if st.button("❌ Clear All", use_container_width=True, key="kazang_clear_all"):
                st.session_state.kazang_ledger = None
                st.session_state.kazang_statement = None
                st.session_state.kazang_results = None
                st.rerun()

    def run_reconciliation(self):
        """Execute the reconciliation using GUI engine"""
        try:
            import sys
            import importlib

            # Use FNB's reconciliation engine (same algorithm)
            try:
                if 'components.fnb_workflow_gui_engine' in sys.modules:
                    importlib.reload(sys.modules['components.fnb_workflow_gui_engine'])
                from components.fnb_workflow_gui_engine import GUIReconciliationEngine
            except ImportError:
                if 'fnb_workflow_gui_engine' in sys.modules:
                    importlib.reload(sys.modules['fnb_workflow_gui_engine'])
                from fnb_workflow_gui_engine import GUIReconciliationEngine

            settings = st.session_state.kazang_match_settings
            
            st.info("🚀 **Kazang Reconciliation Mode** - Using GUI reconciliation engine with:\n"
                   "- ⚡ Pre-built Indexes (O(1) lookups)\n"
                   "- 🔍 Fuzzy Match Caching (100x speedup)\n"
                   "- 💰 Foreign Credits (>10,000 amounts)\n"
                   "- 🔀 Split Transaction Detection (DP algorithm)")

            # Create reconciler instance
            reconciler = GUIReconciliationEngine()

            # Create progress placeholders
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Run reconciliation
            results = reconciler.reconcile(
                st.session_state.kazang_ledger,
                st.session_state.kazang_statement,
                st.session_state.kazang_match_settings,
                progress_bar,
                status_text
            )

            st.session_state.kazang_results = results
            st.session_state.kazang_results_saved = False

            # Get statistics
            perfect_count = results.get('perfect_match_count', 0)
            fuzzy_count = results.get('fuzzy_match_count', 0)
            foreign_count = results.get('foreign_credits_count', 0)
            split_count = results.get('split_count', 0)
            total_matched = results.get('total_matched', 0)
            unmatched_ledger_count = results.get('unmatched_ledger_count', 0)
            unmatched_statement_count = results.get('unmatched_statement_count', 0)

            # Log audit trail
            self.log_audit_trail("RUN_RECONCILIATION", {
                'perfect_matches': perfect_count,
                'fuzzy_matches': fuzzy_count,
                'foreign_credits': foreign_count,
                'split_transactions': split_count,
                'total_matched': total_matched,
                'unmatched': unmatched_ledger_count + unmatched_statement_count
            })

            st.success(f"""
            ✅ **Reconciliation Complete!**

            **Regular Matches:**
            - Perfect Matches (100%): {perfect_count}
            - Fuzzy Matches: {fuzzy_count}
            - Foreign Credits (>10K): {foreign_count}
            - **Total Matched**: {total_matched}

            **Split Transactions:** {split_count}

            **Unmatched:**
            - Ledger: {unmatched_ledger_count}
            - Statement: {unmatched_statement_count}
            """)

        except Exception as e:
            st.error(f"❌ Reconciliation failed: {str(e)}")

    def render_results(self):
        """Render reconciliation results"""
        st.markdown("---")
        st.subheader("📊 Reconciliation Results")

        results = st.session_state.kazang_results

        # Summary cards
        total_matched = (results.get('perfect_match_count', 0) +
                        results.get('fuzzy_match_count', 0) +
                        results.get('foreign_credits_count', 0))
        split_count = len(results.get('split_matches', []))
        unmatched_ledger_count = len(results.get('unmatched_ledger', []))
        unmatched_statement_count = len(results.get('unmatched_statement', []))

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("✅ Perfect Match", f"{results.get('perfect_match_count', 0):,}")
        with col2:
            st.metric("🔍 Fuzzy Match", f"{results.get('fuzzy_match_count', 0):,}")
        with col3:
            st.metric("💰 Foreign Credits", f"{results.get('foreign_credits_count', 0):,}")
        with col4:
            st.metric("🔀 Split Transactions", f"{split_count:,}")
        with col5:
            st.metric("📊 Total Matched", f"{total_matched:,}")

        col6, col7 = st.columns(2)
        with col6:
            st.metric("📋 Unmatched Ledger", f"{unmatched_ledger_count:,}")
        with col7:
            st.metric("🏦 Unmatched Statement", f"{unmatched_statement_count:,}")

        # Charts
        st.markdown("---")
        st.markdown("### 📈 Analytics & Insights")
        
        import plotly.graph_objects as go
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Match Distribution")
            
            labels = []
            values = []
            colors = []
            
            if results.get('perfect_match_count', 0) > 0:
                labels.append('Perfect Match')
                values.append(results.get('perfect_match_count', 0))
                colors.append('#10b981')
            
            if results.get('fuzzy_match_count', 0) > 0:
                labels.append('Fuzzy Match')
                values.append(results.get('fuzzy_match_count', 0))
                colors.append('#3b82f6')
            
            if results.get('foreign_credits_count', 0) > 0:
                labels.append('Foreign Credits')
                values.append(results.get('foreign_credits_count', 0))
                colors.append('#8b5cf6')
            
            if split_count > 0:
                labels.append('Split Transactions')
                values.append(split_count)
                colors.append('#f59e0b')
            
            if unmatched_ledger_count > 0:
                labels.append('Unmatched Ledger')
                values.append(unmatched_ledger_count)
                colors.append('#ef4444')
            
            if unmatched_statement_count > 0:
                labels.append('Unmatched Statement')
                values.append(unmatched_statement_count)
                colors.append('#f97316')
            
            if labels:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    textinfo='label+value+percent'
                )])
                fig_pie.update_layout(height=400, showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### Key Metrics")
            
            metrics_labels = ['Matched', 'Unmatched Items', 'Split Txns']
            metrics_values = [
                total_matched,
                unmatched_ledger_count + unmatched_statement_count,
                split_count
            ]
            metrics_colors = ['#10b981', '#ef4444', '#f59e0b']
            
            fig_bar = go.Figure(data=[go.Bar(
                x=metrics_labels,
                y=metrics_values,
                marker=dict(color=metrics_colors),
                text=metrics_values,
                textposition='auto'
            )])
            fig_bar.update_layout(height=400, yaxis_title="Count", showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)

        # Category navigation
        st.markdown("---")
        st.markdown("### 📊 Transaction Categories")

        if 'kazang_selected_category' not in st.session_state:
            st.session_state.kazang_selected_category = 'all'

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✅ Matched", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'matched' else "secondary",
                        key='kazang_btn_matched'):
                st.session_state.kazang_selected_category = 'matched'
            if st.button("🔀 Split Transactions", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'split' else "secondary",
                        key='kazang_btn_split'):
                st.session_state.kazang_selected_category = 'split'

        with col2:
            if st.button("📊 All Transactions", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'all' else "secondary",
                        key='kazang_btn_all'):
                st.session_state.kazang_selected_category = 'all'
            if st.button("💜 Balanced By Fuzzy", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'fuzzy' else "secondary",
                        key='kazang_btn_fuzzy'):
                st.session_state.kazang_selected_category = 'fuzzy'

        with col3:
            if st.button("❌ Unmatched Ledger", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'unmatched_ledger' else "secondary",
                        key='kazang_btn_unmatched_ledger'):
                st.session_state.kazang_selected_category = 'unmatched_ledger'
            if st.button("💎 Foreign Credits", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'foreign' else "secondary",
                        key='kazang_btn_foreign'):
                st.session_state.kazang_selected_category = 'foreign'

        with col4:
            if st.button("⚠️ Unmatched Statement", use_container_width=True,
                        type="primary" if st.session_state.kazang_selected_category == 'unmatched_statement' else "secondary",
                        key='kazang_btn_unmatched_stmt'):
                st.session_state.kazang_selected_category = 'unmatched_statement'

        st.markdown("---")
        self.display_category(results, st.session_state.kazang_selected_category)

        # Export buttons
        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("💾 Save Results to Database", type="primary", use_container_width=True, key="kazang_save_db"):
                self.save_results_to_db(results)

        with col_b:
            if 'kazang_export_mode' not in st.session_state:
                st.session_state.kazang_export_mode = False
            
            if not st.session_state.kazang_export_mode:
                if st.button("📊 Export All to Excel", type="primary", use_container_width=True, key="kazang_export_excel"):
                    st.session_state.kazang_export_mode = True
        
        if st.session_state.get('kazang_export_mode', False):
            self.export_to_excel(results)

    def display_category(self, results, category):
        """Display transactions for selected category"""

        if category == 'all':
            st.info("👆 Select a category above to view specific transaction details")
            return

        category_data = None
        category_title = ""
        download_filename = ""

        if category == 'matched':
            if 'matched' in results and not results['matched'].empty:
                category_data = results['matched']
                category_title = "✅ All Matched Transactions"
                download_filename = "kazang_all_matched.csv"

        elif category == 'split':
            split_matches = results.get('split_matches', [])
            if split_matches:
                st.markdown(f"### 🔀 Split Transactions ({len(split_matches)} splits)")
                st.info(f"📊 Found {len(split_matches)} split transaction(s)")
                
                ledger = st.session_state.get('kazang_ledger')
                statement = st.session_state.get('kazang_statement')
                
                for i, split in enumerate(split_matches):
                    split_type = split.get('split_type', 'Unknown')
                    with st.expander(f"🔀 Split #{i+1} - {split_type.replace('_', ' ').title()}", expanded=(i==0)):
                        st.write(f"Total Amount: {split.get('total_amount', 0):,.2f}")
                return
            else:
                st.success("✅ No split transactions found")
                return

        elif category == 'fuzzy':
            if 'matched' in results and not results['matched'].empty:
                fuzzy_df = results['matched'][results['matched']['Match_Type'] == 'Fuzzy']
                if not fuzzy_df.empty:
                    category_data = fuzzy_df
                    category_title = "💜 Fuzzy Matched Transactions"
                    download_filename = "kazang_fuzzy_matched.csv"

        elif category == 'foreign':
            if 'matched' in results and not results['matched'].empty:
                foreign_df = results['matched'][results['matched']['Match_Type'] == 'Foreign_Credit']
                if not foreign_df.empty:
                    category_data = foreign_df
                    category_title = "💎 Foreign Credits"
                    download_filename = "kazang_foreign_credits.csv"

        elif category == 'unmatched_ledger':
            if 'unmatched_ledger' in results and not results['unmatched_ledger'].empty:
                category_data = results['unmatched_ledger']
                category_title = "❌ Unmatched Ledger Items"
                download_filename = "kazang_unmatched_ledger.csv"

        elif category == 'unmatched_statement':
            if 'unmatched_statement' in results and not results['unmatched_statement'].empty:
                category_data = results['unmatched_statement']
                category_title = "⚠️ Unmatched Statement Items"
                download_filename = "kazang_unmatched_statement.csv"

        if category_data is not None and not category_data.empty:
            st.markdown(f"### {category_title}")
            st.info(f"📊 Found {len(category_data)} transaction(s)")
            st.dataframe(category_data, use_container_width=True, height=400)
            st.download_button(
                f"📥 Download {category_title}",
                category_data.to_csv(index=False),
                download_filename,
                "text/csv",
                key=f'kazang_download_{category}'
            )
        else:
            st.info(f"No data found for this category")

    def export_to_excel(self, results):
        """Export all results to CSV"""
        try:
            ledger = st.session_state.get('kazang_ledger')
            statement = st.session_state.get('kazang_statement')
            
            ledger_cols = [col for col in ledger.columns if not col.startswith('_')] if ledger is not None else []
            stmt_cols = [col for col in statement.columns if not col.startswith('_')] if statement is not None else []
            
            st.markdown("---")
            st.markdown("### 🎯 Customize Your Report")
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Cancel", key="kazang_cancel_export"):
                    st.session_state.kazang_export_mode = False
            
            with st.expander("📋 Select Columns to Include in Export", expanded=True):
                selected_ledger, selected_statement = ColumnSelector.render_column_selector(
                    ledger_cols=ledger_cols,
                    statement_cols=stmt_cols,
                    workflow_name="kazang"
                )
                
                if not selected_ledger and not selected_statement:
                    st.error("❌ Please select at least one column to export")
                    return
                
                st.success(f"✅ Ready to export: **{len(selected_ledger)}** ledger columns + **{len(selected_statement)}** statement columns")
            
            # Build CSV
            master_columns = ['Match_Score', 'Match_Type']
            for col in selected_ledger:
                master_columns.append(f'Ledger_{col}')
            master_columns.extend(['', ' '])
            for col in selected_statement:
                master_columns.append(f'Statement_{col}')
            
            def align_to_master(row_dict):
                aligned_row = []
                for col in master_columns:
                    value = row_dict.get(col, '')
                    if pd.notna(value) and ('Date' in col or 'date' in col):
                        try:
                            value = pd.to_datetime(value, errors='ignore')
                            if isinstance(value, pd.Timestamp):
                                value = value.strftime('%Y-%m-%d')
                        except:
                            pass
                    if pd.isna(value):
                        value = ''
                    aligned_row.append(value)
                return aligned_row
            
            csv_rows = []
            csv_rows.append(['KAZANG RECONCILIATION RESULTS'])
            csv_rows.append(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            csv_rows.append([])
            
            # Add matched data
            if 'matched' in results and not results['matched'].empty:
                csv_rows.append(['MATCHED TRANSACTIONS'])
                csv_rows.append(master_columns)
                for _, row in results['matched'].iterrows():
                    csv_rows.append(align_to_master(row.to_dict()))
                csv_rows.append([])
            
            # UNMATCHED ITEMS - Ledger and Statement SIDE BY SIDE (like FNB)
            unmatched_ledger = results.get('unmatched_ledger', pd.DataFrame())
            unmatched_statement = results.get('unmatched_statement', pd.DataFrame())
            
            if not unmatched_ledger.empty or not unmatched_statement.empty:
                csv_rows.append(['UNMATCHED ITEMS'])
                csv_rows.append([f'Unmatched Ledger: {len(unmatched_ledger)} | Unmatched Statement: {len(unmatched_statement)}'])
                csv_rows.append([])
                csv_rows.append(master_columns)
                
                # Determine how many rows we need (max of ledger or statement)
                max_rows = max(len(unmatched_ledger), len(unmatched_statement))
                
                # Add data rows - side by side, aligned to master columns
                for i in range(max_rows):
                    row_dict = {
                        'Match_Score': '',
                        'Match_Type': 'Unmatched'
                    }
                    
                    # Add ledger data if available at this index (left side)
                    if i < len(unmatched_ledger):
                        ledger_row = unmatched_ledger.iloc[i]
                        for col in selected_ledger:
                            if col in ledger_row.index:
                                val = ledger_row.get(col, '')
                                row_dict[f'Ledger_{col}'] = val if pd.notna(val) else ''
                    
                    # Add statement data if available at this index (right side)
                    if i < len(unmatched_statement):
                        stmt_row = unmatched_statement.iloc[i]
                        for col in selected_statement:
                            if col in stmt_row.index:
                                val = stmt_row.get(col, '')
                                row_dict[f'Statement_{col}'] = val if pd.notna(val) else ''
                    
                    csv_rows.append(align_to_master(row_dict))
                
                csv_rows.append([])
            
            # Summary
            csv_rows.append(['SUMMARY'])
            csv_rows.append(['Perfect Matches:', results.get('perfect_match_count', 0)])
            csv_rows.append(['Fuzzy Matches:', results.get('fuzzy_match_count', 0)])
            csv_rows.append(['Total Matched:', results.get('total_matched', 0)])
            csv_rows.append(['Unmatched Ledger:', results.get('unmatched_ledger_count', 0)])
            csv_rows.append(['Unmatched Statement:', results.get('unmatched_statement_count', 0)])
            
            max_cols = max(len(row) for row in csv_rows)
            for row in csv_rows:
                while len(row) < max_cols:
                    row.append('')
            
            export_df = pd.DataFrame(csv_rows)
            csv_string = export_df.to_csv(index=False, header=False)

            st.markdown("---")
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                st.download_button(
                    label="📥 Download Kazang Report",
                    data=csv_string,
                    file_name=f"Kazang_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.success("✅ Report ready for download!")

        except Exception as e:
            st.error(f"❌ Failed to create report: {str(e)}")

    def save_results_to_db(self, results):
        """Save reconciliation results to database"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
            from database import get_db

            result_name = st.text_input(
                "Enter a name for these results:",
                value=f"Kazang_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                key='kazang_save_result_name'
            )

            if st.button("✅ Confirm Save", key='kazang_confirm_save'):
                db = get_db()

                metadata = {
                    'ledger_columns': list(st.session_state.kazang_ledger.columns),
                    'statement_columns': list(st.session_state.kazang_statement.columns),
                    'match_settings': st.session_state.kazang_match_settings,
                    'saved_timestamp': datetime.now().isoformat()
                }

                result_id = db.save_result(
                    name=result_name,
                    workflow_type='Kazang',
                    results=results,
                    metadata=metadata
                )

                st.session_state.kazang_results = results
                st.session_state.kazang_results_saved = True

                st.success(f"✅ Results saved successfully! (ID: {result_id})")
                
                self.log_audit_trail("SAVE_RESULTS", {
                    'result_id': result_id,
                    'name': result_name
                })

        except Exception as e:
            st.error(f"❌ Failed to save results: {str(e)}")

    def log_audit_trail(self, action, details):
        """Log actions to audit trail"""
        if 'audit_trail' not in st.session_state:
            st.session_state.audit_trail = []
        
        st.session_state.audit_trail.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'workflow': 'Kazang',
            'action': action,
            'details': details,
            'user': st.session_state.get('username', 'admin')
        })
