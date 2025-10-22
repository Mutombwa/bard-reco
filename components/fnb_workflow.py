"""
FNB Workflow Component - Exact Replica of GUI Logic
=================================================
Advanced reconciliation engine with weighted scoring matching
Date (30%) + Reference (40%) + Amount (30%) = Total Score
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_cleaner import clean_amount_column  # type: ignore
from column_selector import ColumnSelector  # type: ignore
from file_loader import load_uploaded_file, get_dataframe_info  # type: ignore

class FNBWorkflow:
    """FNB Bank Reconciliation Workflow with Exact GUI Logic"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'fnb_ledger' not in st.session_state:
            st.session_state.fnb_ledger = None
        if 'fnb_statement' not in st.session_state:
            st.session_state.fnb_statement = None
        if 'fnb_results' not in st.session_state:
            st.session_state.fnb_results = None
        if 'fnb_column_mapping' not in st.session_state:
            st.session_state.fnb_column_mapping = {}
        if 'fnb_match_settings' not in st.session_state:
            st.session_state.fnb_match_settings = {
                'ledger_date_col': 'Date',
                'ledger_ref_col': 'Reference',
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
        """Render FNB workflow page"""

        # Header
        st.markdown("""
        <style>
        .gradient-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
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
            color: #cbd5e1;
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
            <h1>🏦 FNB Workflow</h1>
            <p>Advanced Bank Reconciliation • Weighted Scoring Algorithm • 30% Date + 40% Reference + 30% Amount</p>
        </div>
        """, unsafe_allow_html=True)

        # Removed back button - workflows are now shown in tabs

        # Step 1: File Upload
        self.render_file_upload()

        # Step 2-5: Show configuration sections (if files uploaded)
        if st.session_state.fnb_ledger is not None and st.session_state.fnb_statement is not None:
            # Quick status summary at top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📗 Ledger Rows", f"{len(st.session_state.fnb_ledger):,}")
            with col2:
                st.metric("📘 Statement Rows", f"{len(st.session_state.fnb_statement):,}")
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
        if st.session_state.fnb_results is not None:
            self.render_results()

    def render_file_upload(self):
        """Render file upload section - Cloud deployment compatible"""
        st.subheader("📁 Step 1: Import Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger File**")

            # Show existing data status FIRST
            if st.session_state.fnb_ledger is not None:
                st.success(f"📊 **Ledger:** {len(st.session_state.fnb_ledger)} rows × {len(st.session_state.fnb_ledger.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.fnb_ledger.columns))

            ledger_file = st.file_uploader("Upload NEW Ledger File", type=['xlsx', 'xls', 'csv'], key='fnb_ledger_upload', help="Upload a new file to replace current data")

            if ledger_file is not None:
                # Use optimized loader with caching and progress indicator
                ledger_df, is_new = load_uploaded_file(
                    ledger_file,
                    session_key='fnb_ledger',
                    hash_key='fnb_ledger_hash',
                    show_progress=True
                )

                if is_new:
                    # New file loaded - update metadata
                    st.session_state.fnb_ledger_original_cols = list(ledger_df.columns)

                    # Reset saved selections for new file
                    if 'fnb_saved_selections' in st.session_state:
                        del st.session_state.fnb_saved_selections

                    st.success(f"✅ New ledger loaded: {get_dataframe_info(ledger_df)}")
                    # Removed st.rerun() - happens automatically on session state change

        with col2:
            st.markdown("**Bank Statement File**")

            # Show existing data status FIRST
            if st.session_state.fnb_statement is not None:
                st.success(f"📊 **Statement:** {len(st.session_state.fnb_statement)} rows × {len(st.session_state.fnb_statement.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.fnb_statement.columns))

            statement_file = st.file_uploader("Upload NEW Statement File", type=['xlsx', 'xls', 'csv'], key='fnb_statement_upload', help="Upload a new file to replace current data")

            if statement_file is not None:
                # Use optimized loader with caching and progress indicator
                statement_df, is_new = load_uploaded_file(
                    statement_file,
                    session_key='fnb_statement',
                    hash_key='fnb_statement_hash',
                    show_progress=True
                )

                if is_new:
                    # New file loaded - update metadata
                    st.session_state.fnb_statement_original_cols = list(statement_df.columns)

                    # Reset saved selections for new file
                    if 'fnb_saved_selections' in st.session_state:
                        del st.session_state.fnb_saved_selections

                    st.success(f"✅ New statement loaded: {get_dataframe_info(statement_df)}")
                    # Removed st.rerun() - happens automatically on session state change
        
        # Add View & Edit Data section
        if st.session_state.fnb_ledger is not None or st.session_state.fnb_statement is not None:
            st.markdown("---")
            st.subheader("👁️ Step 1.5: View & Edit Data")
            st.info("💡 **Edit your data before reconciliation:** View, add rows, delete rows, copy/paste from Excel, and more!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.fnb_ledger is not None:
                    if st.button("📊 View & Edit Ledger", key='view_edit_ledger_btn', use_container_width=True, type="secondary"):
                        st.session_state.fnb_show_ledger_editor = True
            
            with col2:
                if st.session_state.fnb_statement is not None:
                    if st.button("📊 View & Edit Statement", key='view_edit_statement_btn', use_container_width=True, type="secondary"):
                        st.session_state.fnb_show_statement_editor = True
            
            # Show Ledger Editor
            if st.session_state.get('fnb_show_ledger_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.fnb_ledger, "📗 Ledger Editor", "fnb_ledger")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.fnb_ledger = saved_data
                    st.session_state.fnb_show_ledger_editor = False
                    st.success("✅ Ledger data saved successfully!")
                    # Removed st.rerun() - happens automatically

                if st.button("❌ Close Editor", key='close_ledger_editor'):
                    st.session_state.fnb_show_ledger_editor = False
                    # Removed st.rerun() - happens automatically

            # Show Statement Editor
            if st.session_state.get('fnb_show_statement_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.fnb_statement, "📘 Statement Editor", "fnb_statement")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.fnb_statement = saved_data
                    st.session_state.fnb_show_statement_editor = False
                    st.success("✅ Statement data saved successfully!")
                    # Removed st.rerun() - happens automatically

                if st.button("❌ Close Editor", key='close_statement_editor'):
                    st.session_state.fnb_show_statement_editor = False
                    # Removed st.rerun() - happens automatically

    def render_data_tools(self):
        """Render data processing tools like Add Reference, Nedbank Ref, RJ & Payment Ref"""
        st.markdown("---")
        st.subheader("🛠️ Step 2: Data Processing Tools")

        # Cache column lists to avoid repeated DataFrame column access
        if 'fnb_ledger_cols_cache' not in st.session_state or st.session_state.get('fnb_ledger_cols_dirty', True):
            st.session_state.fnb_ledger_cols_cache = list(st.session_state.fnb_ledger.columns) if st.session_state.fnb_ledger is not None else []
            st.session_state.fnb_ledger_cols_dirty = False

        if 'fnb_statement_cols_cache' not in st.session_state or st.session_state.get('fnb_statement_cols_dirty', True):
            st.session_state.fnb_statement_cols_cache = list(st.session_state.fnb_statement.columns) if st.session_state.fnb_statement is not None else []
            st.session_state.fnb_statement_cols_dirty = False

        ledger_cols = st.session_state.fnb_ledger_cols_cache
        statement_cols = st.session_state.fnb_statement_cols_cache

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📝 Add Reference**")
            st.caption("Extract names from Statement Description")
            if 'Reference' in statement_cols:
                st.success("✅ Reference added to Statement")
            if st.button("🚀 Launch", key='add_reference_btn', use_container_width=True):
                self.add_reference_tool()

        with col2:
            st.markdown("**🏦 Nedbank Processing**")
            st.caption("Process Nedbank statement")
            if 'Processed_Ref' in statement_cols:
                st.success("✅ Processed_Ref added")
            if st.button("🚀 Launch", key='nedbank_ref_btn', use_container_width=True):
                self.nedbank_processing_tool()

        with col3:
            st.markdown("**🔢 RJ & Payment Ref**")
            st.caption("Generate RJ numbers")
            if 'RJ-Number' in ledger_cols and 'Payment Ref' in ledger_cols:
                st.success("✅ RJ-Number & Payment Ref added")
            if st.button("🚀 Launch", key='rj_payment_ref_btn', use_container_width=True):
                self.rj_payment_ref_tool()

    def add_reference_tool(self):
        """Extract reference names from Statement Description column (exact GUI logic)"""
        try:
            import re

            # Check if statement exists
            if st.session_state.fnb_statement is None:
                st.error("❌ Please import a statement first!")
                return

            statement = st.session_state.fnb_statement.copy()

            # Find Description column (case-insensitive)
            desc_col = None
            for col in statement.columns:
                if str(col).strip().lower() == 'description':
                    desc_col = col
                    break

            if desc_col is None:
                st.error("❌ No 'Description' column found in statement")
                return

            # Check if Reference column already exists
            if 'Reference' in statement.columns:
                st.info("ℹ️ Reference column already exists in statement")
                return

            def extract_reference_name(description):
                """Extract reference names from banking transaction descriptions"""
                desc = str(description).strip()

                # Pattern-based extraction for common transaction types
                patterns = [
                    # FNB APP PAYMENT FROM [NAME]
                    (r'FNB APP PAYMENT FROM\s+(.+)', lambda m: m.group(1).strip()),

                    # ADT CASH DEPO variations
                    (r'ADT CASH DEPO00882112\s+(.+)', lambda m: m.group(1).strip()),
                    (r'ADT CASH DEPOSIT\s+(.+)', lambda m: m.group(1).strip()),
                    (r'ADT CASH DEPO([A-Z]+)\s+(.+)', lambda m: m.group(2).strip()),
                    (r'ADT CASH DEPO\w*\s+(.+)', lambda m: m.group(1).strip()),

                    # CAPITEC [NAME]
                    (r'CAPITEC\s+(.+)', lambda m: m.group(1).strip()),

                    # ABSA BANK [NAME]
                    (r'ABSA BANK\s+(.+)', lambda m: m.group(1).strip()),

                    # NEDBANK [NAME]
                    (r'NEDBANK\s+(.+)', lambda m: m.group(1).strip()),

                    # Standard Bank [NAME]
                    (r'STANDARD BANK\s+(.+)', lambda m: m.group(1).strip()),

                    # Direct names (capitalized words)
                    (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[a-z]+)$', lambda m: m.group(1).strip()),
                ]

                # Try each pattern
                for pattern, extractor in patterns:
                    match = re.search(pattern, desc, re.IGNORECASE)
                    if match:
                        try:
                            result = extractor(match)
                            if result:
                                # Clean up the reference name
                                result = result.strip()
                                # Remove common banking codes/numbers at end
                                result = re.sub(r'\s*\d{10,}$', '', result)
                                return result
                        except Exception:
                            continue

                # Fallback: extract capitalized words that look like names
                words = desc.split()
                name_words = []
                for word in words:
                    # Look for capitalized words that could be names
                    if re.match(r'^[A-Z][a-z]+$', word) or re.match(r'^[A-Z]+$', word):
                        name_words.append(word)

                if name_words:
                    return ' '.join(name_words[-2:]) if len(name_words) >= 2 else name_words[-1]

                return "UNKNOWN"

            # Apply reference extraction to all descriptions
            references = []
            for desc in statement[desc_col]:
                ref = extract_reference_name(desc)
                references.append(ref)

            # Insert Reference column after Description column
            desc_idx = list(statement.columns).index(desc_col)
            statement.insert(desc_idx + 1, 'Reference', references)

            # Update session state
            st.session_state.fnb_statement = statement

            # Mark column cache as dirty
            st.session_state.fnb_statement_cols_dirty = True

            # Reset saved selections to trigger reconfiguration
            if 'fnb_saved_selections' in st.session_state:
                del st.session_state.fnb_saved_selections

            # Show success with sample results
            st.success(f"✅ Reference column added to Statement after Description column!")
            st.info(f"📊 Processed {len(references)} transactions\n\n"
                   f"💾 **Column persisted!** It will appear in the dropdown below.")

            # Show sample extractions
            with st.expander("📋 Sample Extractions (First 10)"):
                sample_data = []
                for i in range(min(10, len(references))):
                    sample_data.append({
                        'Description': statement.iloc[i][desc_col],
                        'Extracted Reference': references[i]
                    })
                st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

            # Only one rerun needed after modifying session state

        except Exception as e:
            st.error(f"❌ Error adding reference: {str(e)}")

    def nedbank_processing_tool(self):
        """Process Nedbank-specific statement formatting"""
        try:
            statement = st.session_state.fnb_statement.copy()

            # Nedbank-specific processing (customize as needed)
            if 'Description' in statement.columns:
                statement['Processed_Ref'] = statement['Description'].astype(str).str.strip()
                st.session_state.fnb_statement = statement

                # Mark column cache as dirty
                st.session_state.fnb_statement_cols_dirty = True

                # Reset saved selections to trigger reconfiguration
                if 'fnb_saved_selections' in st.session_state:
                    del st.session_state.fnb_saved_selections

                st.success("✅ Nedbank processing complete - Added Processed_Ref column")
                st.rerun()
            else:
                st.info("Statement format not recognized for Nedbank processing")

        except Exception as e:
            st.error(f"❌ Error processing Nedbank data: {str(e)}")

    def rj_payment_ref_tool(self):
        """Generate RJ-Number and Payment Ref columns"""
        try:
            import re
            ledger = st.session_state.fnb_ledger.copy()

            if len(ledger.columns) < 2:
                st.error("Ledger must have at least 2 columns")
                return

            # Check if already exists
            if 'RJ-Number' in ledger.columns or 'Payment Ref' in ledger.columns:
                st.info("RJ-Number and Payment Ref columns already exist")
                return

            def extract_rj_and_ref(comment):
                if not isinstance(comment, str):
                    return '', ''

                # RJ-Number: look for RJ or TX followed by digits
                rj_match = re.search(r'(RJ|TX)[-]?(\d{6,})', comment, re.IGNORECASE)
                rj = rj_match.group(0).replace('-', '') if rj_match else ''

                payref = ''
                payref_match = re.search(r'Payment Ref[#:]?\s*([\w\s\-\.,&]+)', comment, re.IGNORECASE)
                if payref_match:
                    payref = payref_match.group(1).strip()
                elif rj_match:
                    after = comment[rj_match.end():]
                    after = after.lstrip(' .:-#')
                    payref = re.split(r'[.,\n\r]', after)[0].strip()
                else:
                    # No RJ-Number found, use the whole comment as Payment Ref
                    payref = comment.strip()

                return rj, payref

            rj_numbers = []
            pay_refs = []

            for val in ledger.iloc[:, 1]:
                rj, ref = extract_rj_and_ref(val)
                rj_numbers.append(rj)
                pay_refs.append(ref)

            # Insert columns after column B (index 1)
            ledger.insert(2, 'RJ-Number', rj_numbers)
            ledger.insert(3, 'Payment Ref', pay_refs)

            st.session_state.fnb_ledger = ledger

            # Mark column cache as dirty
            st.session_state.fnb_ledger_cols_dirty = True

            # Reset saved selections to trigger reconfiguration
            if 'fnb_saved_selections' in st.session_state:
                del st.session_state.fnb_saved_selections

            st.success("✅ Added RJ-Number and Payment Ref columns to ledger")
            st.dataframe(ledger[['RJ-Number', 'Payment Ref']].head(10), use_container_width=True)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating RJ & Payment Ref: {str(e)}")

    def render_column_mapping(self):
        """Render column mapping configuration"""
        st.markdown("---")
        st.subheader("⚙️ Step 3: Configure Column Mapping")

        # Use cached column lists for better performance
        ledger_cols = st.session_state.fnb_ledger_cols_cache
        statement_cols = st.session_state.fnb_statement_cols_cache

        # Show available columns with detailed info (collapsed by default for faster rendering)
        with st.expander("ℹ️ View Available Columns", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Ledger Columns ({len(ledger_cols)} total):**")
                st.code(", ".join(ledger_cols))
                # Highlight added columns
                added_cols = [col for col in ['Reference', 'RJ-Number', 'Payment Ref'] if col in ledger_cols]
                if added_cols:
                    st.info(f"✨ Added columns: {', '.join(added_cols)}")
            with col_b:
                st.markdown(f"**Statement Columns ({len(statement_cols)} total):**")
                st.code(", ".join(statement_cols))
                # Highlight added columns
                added_cols = [col for col in ['Reference', 'Processed_Ref'] if col in statement_cols]
                if added_cols:
                    st.info(f"✨ Added columns: {', '.join(added_cols)}")

        # Initialize saved selections if not present or validate existing ones
        if 'fnb_saved_selections' not in st.session_state:
            st.session_state.fnb_saved_selections = {}

        # Validate and set safe indices
        def get_safe_index(col_list, saved_key, default_name):
            if saved_key in st.session_state.fnb_saved_selections:
                saved_idx = st.session_state.fnb_saved_selections[saved_key]
                # Validate index is within range
                if 0 <= saved_idx < len(col_list):
                    return saved_idx
            # Try to find default column
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
                key='fnb_ledger_date_selector'
            )
            st.session_state.fnb_saved_selections['ledger_date_idx'] = ledger_cols.index(ledger_date_selection)
            st.session_state.fnb_match_settings['ledger_date_col'] = ledger_date_selection

            ledger_ref_selection = st.selectbox(
                "Reference Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_ref_idx', 'Reference'),
                key='fnb_ledger_ref_selector'
            )
            st.session_state.fnb_saved_selections['ledger_ref_idx'] = ledger_cols.index(ledger_ref_selection)
            st.session_state.fnb_match_settings['ledger_ref_col'] = ledger_ref_selection

            ledger_debit_selection = st.selectbox(
                "Debit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_debit_idx', 'Debit'),
                key='fnb_ledger_debit_selector'
            )
            st.session_state.fnb_saved_selections['ledger_debit_idx'] = ledger_cols.index(ledger_debit_selection)
            st.session_state.fnb_match_settings['ledger_debit_col'] = ledger_debit_selection

            ledger_credit_selection = st.selectbox(
                "Credit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_credit_idx', 'Credit'),
                key='fnb_ledger_credit_selector'
            )
            st.session_state.fnb_saved_selections['ledger_credit_idx'] = ledger_cols.index(ledger_credit_selection)
            st.session_state.fnb_match_settings['ledger_credit_col'] = ledger_credit_selection

        with col2:
            st.markdown("**Statement Columns**")

            statement_date_selection = st.selectbox(
                "Date Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_date_idx', 'Date'),
                key='fnb_statement_date_selector'
            )
            st.session_state.fnb_saved_selections['statement_date_idx'] = statement_cols.index(statement_date_selection)
            st.session_state.fnb_match_settings['statement_date_col'] = statement_date_selection

            statement_ref_selection = st.selectbox(
                "Reference Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_ref_idx', 'Reference'),
                key='fnb_statement_ref_selector'
            )
            st.session_state.fnb_saved_selections['statement_ref_idx'] = statement_cols.index(statement_ref_selection)
            st.session_state.fnb_match_settings['statement_ref_col'] = statement_ref_selection

            statement_amt_selection = st.selectbox(
                "Amount Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_amt_idx', 'Amount'),
                key='fnb_statement_amt_selector'
            )
            st.session_state.fnb_saved_selections['statement_amt_idx'] = statement_cols.index(statement_amt_selection)
            st.session_state.fnb_match_settings['statement_amt_col'] = statement_amt_selection

    def render_matching_settings(self):
        """Render matching settings configuration"""
        st.markdown("---")
        st.subheader("🎯 Step 4: Matching Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Matching Criteria**")
            st.session_state.fnb_match_settings['match_dates'] = st.checkbox(
                "Match by Dates", value=True, key='fnb_match_dates'
            )
            # Add date tolerance option
            if st.session_state.fnb_match_settings['match_dates']:
                st.session_state.fnb_match_settings['date_tolerance'] = st.checkbox(
                    "  ↳ Allow ±1 Day Tolerance", value=False, key='fnb_date_tolerance',
                    help="When enabled, dates within 1 day difference will be considered matching"
                )
            else:
                st.session_state.fnb_match_settings['date_tolerance'] = False

            st.session_state.fnb_match_settings['match_references'] = st.checkbox(
                "Match by References", value=True, key='fnb_match_refs'
            )
            st.session_state.fnb_match_settings['match_amounts'] = st.checkbox(
                "Match by Amounts", value=True, key='fnb_match_amts'
            )

        with col2:
            st.markdown("**Fuzzy Matching**")
            st.session_state.fnb_match_settings['fuzzy_ref'] = st.checkbox(
                "Enable Fuzzy Reference Matching", value=True, key='fnb_fuzzy'
            )
            st.session_state.fnb_match_settings['similarity_ref'] = st.slider(
                "Similarity Threshold (%)", 50, 100, 85, key='fnb_similarity'
            )

        with col3:
            st.markdown("**Amount Matching Mode**")
            amount_mode = st.radio(
                "Select Mode:",
                ["Use Both Debits and Credits", "Use Debits Only", "Use Credits Only"],
                key='fnb_amount_mode'
            )

            st.session_state.fnb_match_settings['use_debits_only'] = (amount_mode == "Use Debits Only")
            st.session_state.fnb_match_settings['use_credits_only'] = (amount_mode == "Use Credits Only")
            st.session_state.fnb_match_settings['use_both_debit_credit'] = (amount_mode == "Use Both Debits and Credits")

        # Show algorithm explanation
        with st.expander("ℹ️ How the Ultra-Fast Matching Algorithm Works"):
            st.markdown("""
            **🚀 ULTRA FAST Multi-Phase Reconciliation:**

            **Phase 1: Perfect Match (100% Exact)**
            - ✅ **Date**: Exact same day (or ±1 day if tolerance enabled)
            - ✅ **Reference**: Case-insensitive exact match (100% similar)
            - ✅ **Amount**: Exact match (to 2 decimal places)
            - **Result**: Highest priority, no ambiguity

            **Phase 2: Fuzzy Matching**
            - ✅ **Date**: Exact same day (or ±1 day if tolerance enabled)
            - 🔍 **Reference**: Fuzzy match using fuzzywuzzy (≥ your threshold %)
            - ✅ **Amount**: Exact match
            - **Result**: Matches similar references within threshold

            **Phase 3: Foreign Credits (>10,000)**
            - 💰 **Amount**: ALWAYS required (exact match), regardless of settings
            - 📅 **Date**: Optional (only if "Match by Dates" enabled)
            - ❌ **Reference**: IGNORED (not checked)
            - **Purpose**: High-value transactions often have inconsistent references

            **Phase 4: Split Transactions**
            - 🔀 Uses Dynamic Programming (DP) algorithm
            - Finds combinations of 2-6 transactions that sum to target (±2% tolerance)
            - **Two types**:
              - Many Ledger → One Statement
              - One Ledger → Many Statement
            - Ultra-fast indexing by date and amount range

            **Performance Optimizations:**
            - ⚡ Amount-based indexing (instant lookup)
            - 🔍 Fuzzy score caching (no re-computation)
            - 📊 Date and reference pre-filtering
            - 🎯 Early exit conditions in DP algorithm

            **Flexible Matching:**
            - You can match by any combination: Dates only, References only, Amounts only, or all three
            - When a criterion is unchecked, it's ignored in matching
            """)


    def render_reconciliation_controls(self):
        """Render reconciliation execution controls"""
        st.markdown("---")
        st.subheader("⚡ Step 5: Execute Reconciliation")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("🚀 Start Reconciliation", type="primary", use_container_width=True, key="fnb_start_recon"):
                self.run_reconciliation()

        with col2:
            if st.button("🔄 Reset", use_container_width=True, key="fnb_reset"):
                st.session_state.fnb_results = None
                st.rerun()

        with col3:
            if st.button("❌ Clear All", use_container_width=True, key="fnb_clear_all"):
                st.session_state.fnb_ledger = None
                st.session_state.fnb_statement = None
                st.session_state.fnb_results = None
                st.rerun()

    def run_reconciliation(self):
        """Execute the ULTRA-FAST reconciliation with all matching modes"""
        try:
            # Import GUI-based engine (handle both local and deployed paths)
            # Force reload to pick up code changes
            import sys
            import importlib

            try:
                if 'components.fnb_workflow_gui_engine' in sys.modules:
                    importlib.reload(sys.modules['components.fnb_workflow_gui_engine'])
                from components.fnb_workflow_gui_engine import GUIReconciliationEngine
            except ImportError:
                if 'fnb_workflow_gui_engine' in sys.modules:
                    importlib.reload(sys.modules['fnb_workflow_gui_engine'])
                from fnb_workflow_gui_engine import GUIReconciliationEngine

            # Check if reference-only mode (ULTRA FAST PATH)
            settings = st.session_state.fnb_match_settings
            is_reference_only = (
                settings.get('match_references', False) and
                not settings.get('match_dates', False) and
                not settings.get('match_amounts', False)
            )

            if is_reference_only:
                st.success("⚡ **ULTRA-FAST MODE ACTIVATED** - Reference-Only Matching:\n"
                          "- 🚀 Hash-based O(1) exact lookups\n"
                          "- 🔍 Cached fuzzy matching (100x speedup)\n"
                          "- ⏱️ **10-100x faster** than standard matching\n"
                          "- 💡 Perfect for matching by reference only!")
            else:
                st.info("🚀 **GUI ALGORITHM Mode Enabled** - Using proven GUI reconciliation engine with:\n"
                       "- ⚡ Pre-built Indexes (O(1) lookups)\n"
                       "- 🔍 Fuzzy Match Caching (100x speedup)\n"
                       "- 💰 Foreign Credits (>10,000 amounts)\n"
                       "- 🔀 Split Transaction Detection (DP algorithm)\n"
                       "- ✅ Flexible Debit/Credit Matching")

            # Create reconciler instance
            reconciler = GUIReconciliationEngine()

            # Create progress placeholders
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Run reconciliation
            results = reconciler.reconcile(
                st.session_state.fnb_ledger,
                st.session_state.fnb_statement,
                st.session_state.fnb_match_settings,
                progress_bar,
                status_text
            )

            st.session_state.fnb_results = results
            st.session_state.fnb_results_saved = False  # Mark as not saved yet

            # Get statistics from results (now included in results dict)
            perfect_count = results.get('perfect_match_count', 0)
            fuzzy_count = results.get('fuzzy_match_count', 0)
            foreign_count = results.get('foreign_credits_count', 0)
            split_count = results.get('split_count', 0)
            total_matched = results.get('total_matched', 0)
            unmatched_ledger_count = results.get('unmatched_ledger_count', 0)
            unmatched_statement_count = results.get('unmatched_statement_count', 0)

            # Update session state for sidebar Quick Stats
            if 'session' in st.session_state:
                st.session_state.session.set_stat('total_reconciliations',
                                                 st.session_state.session.get_stat('total_reconciliations', 0) + 1)
                st.session_state.session.set_stat('matched_transactions', total_matched + split_count)
                if (total_matched + split_count) > 0:
                    success_rate = ((total_matched + split_count) / 
                                  (total_matched + split_count + unmatched_ledger_count + unmatched_statement_count)) * 100
                    st.session_state.session.set_stat('success_rate', int(success_rate))
            
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

    def prepare_ledger_data(self, df, settings):
        """Prepare ledger data for matching (exact GUI logic)"""
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

        # Prepare amount columns using enhanced clean_amount_column
        if settings.get('match_amounts', True):
            debit_col = settings.get('ledger_debit_col', 'Debit')
            credit_col = settings.get('ledger_credit_col', 'Credit')

            # Use robust cleaning from data_cleaner
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

    def prepare_statement_data(self, df, settings):
        """Prepare statement data for matching (exact GUI logic)"""
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

        # Prepare amount column using robust cleaning
        if settings.get('match_amounts', True):
            amt_col = settings.get('statement_amt_col', 'Amount')
            statement['amount_for_matching'] = clean_amount_column(statement[amt_col], column_name=amt_col)

        return statement

    def find_matches(self, ledger, statement, settings):
        """Find matches between ledger and statement (exact GUI algorithm)"""
        matches = []
        used_statement_indices = set()

        total_ledger = len(ledger)
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, ledger_row in ledger.iterrows():
            # Update progress
            if i % 50 == 0:
                progress = i / total_ledger
                progress_bar.progress(progress)
                status_text.text(f"Matching row {i+1} of {total_ledger}...")

            best_match = None
            best_score = 0

            for j, stmt_row in statement.iterrows():
                if j in used_statement_indices:
                    continue

                score = self.calculate_match_score(ledger_row, stmt_row, settings)

                if score > best_score and score >= 0.7:  # Minimum threshold
                    best_score = score
                    best_match = j

            if best_match is not None:
                matches.append((i, best_match, best_score))
                used_statement_indices.add(best_match)

        progress_bar.progress(1.0)
        status_text.text(f"✅ Matched {len(matches)} pairs")

        return matches

    def calculate_match_score(self, ledger_row, stmt_row, settings):
        """Calculate match score (exact GUI weighted algorithm)"""
        scores = []
        weights = []

        # Date matching (30% weight)
        if settings.get('match_dates', True):
            date_score = self.calculate_date_score(ledger_row, stmt_row)
            if date_score is not None:
                scores.append(date_score)
                weights.append(0.3)

        # Reference matching (40% weight)
        if settings.get('match_references', True):
            ref_score = self.calculate_reference_score(ledger_row, stmt_row, settings)
            if ref_score is not None:
                scores.append(ref_score)
                weights.append(0.4)

        # Amount matching (30% weight)
        if settings.get('match_amounts', True):
            amt_score = self.calculate_amount_score(ledger_row, stmt_row)
            if amt_score is not None:
                scores.append(amt_score)
                weights.append(0.3)

        if not scores:
            return 0.0

        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def calculate_date_score(self, ledger_row, stmt_row):
        """Calculate date matching score (exact GUI logic)"""
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

    def calculate_reference_score(self, ledger_row, stmt_row, settings):
        """Calculate reference matching score (exact GUI logic with fuzzywuzzy)"""
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

    def calculate_amount_score(self, ledger_row, stmt_row):
        """Calculate amount matching score (exact GUI logic)"""
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

    def process_results(self, ledger, statement, matches, settings):
        """Process reconciliation results (exact GUI logic)"""
        results = {}

        # Get all original columns (excluding helper columns)
        ledger_display_cols = [col for col in ledger.columns if not col in ['ledger_index', 'date_normalized', 'reference_clean', 'amount_for_matching']]
        statement_display_cols = [col for col in statement.columns if not col in ['statement_index', 'date_normalized', 'reference_clean', 'amount_for_matching']]

        # Create matched pairs DataFrame with ALL columns
        if matches:
            matched_data = []
            matched_ledger_indices = set()
            matched_stmt_indices = set()

            for ledger_idx, stmt_idx, score in matches:
                ledger_row = ledger.iloc[ledger_idx]
                stmt_row = statement.iloc[stmt_idx]

                # Build row with Match Score first
                row_data = {'Match_Score': round(score, 3)}

                # Add ALL ledger columns (prefixed with Ledger_)
                for col in ledger_display_cols:
                    row_data[f'Ledger_{col}'] = ledger_row[col]

                # Add ALL statement columns (prefixed with Statement_)
                for col in statement_display_cols:
                    row_data[f'Statement_{col}'] = stmt_row[col]

                matched_data.append(row_data)
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

    def render_results(self):
        """Render reconciliation results"""
        st.markdown("---")
        st.subheader("📊 Reconciliation Results")

        results = st.session_state.fnb_results

        # Summary cards with new structure
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

        # ADD VISUAL CHARTS
        st.markdown("---")
        st.markdown("### 📈 Analytics & Insights")
        
        # Create charts
        import plotly.graph_objects as go
        import plotly.express as px
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Match Distribution Pie Chart
            st.markdown("#### Match Distribution")
            
            labels = []
            values = []
            colors = []
            
            if results.get('perfect_match_count', 0) > 0:
                labels.append(f'Perfect Match')
                values.append(results.get('perfect_match_count', 0))
                colors.append('#10b981')  # Green
            
            if results.get('fuzzy_match_count', 0) > 0:
                labels.append(f'Fuzzy Match')
                values.append(results.get('fuzzy_match_count', 0))
                colors.append('#3b82f6')  # Blue
            
            if results.get('foreign_credits_count', 0) > 0:
                labels.append(f'Foreign Credits')
                values.append(results.get('foreign_credits_count', 0))
                colors.append('#8b5cf6')  # Purple
            
            if split_count > 0:
                labels.append(f'Split Transactions')
                values.append(split_count)
                colors.append('#f59e0b')  # Orange
            
            if unmatched_ledger_count > 0:
                labels.append(f'Unmatched Ledger')
                values.append(unmatched_ledger_count)
                colors.append('#ef4444')  # Red
            
            if unmatched_statement_count > 0:
                labels.append(f'Unmatched Statement')
                values.append(unmatched_statement_count)
                colors.append('#f97316')  # Orange-Red
            
            if labels:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    textinfo='label+value+percent',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig_pie.update_layout(
                    height=400,
                    showlegend=True,
                    margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No reconciliation data yet. Run a reconciliation to see match distribution.")
        
        with col2:
            # Key Metrics Bar Chart
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
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )])
            fig_bar.update_layout(
                height=400,
                yaxis_title="Count",
                showlegend=False,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Success Rate Gauge
        total_items = total_matched + split_count + unmatched_ledger_count + unmatched_statement_count
        if total_items > 0:
            success_rate = ((total_matched + split_count) / total_items) * 100
            
            st.markdown("#### 🎯 Success Rate")
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Match Accuracy", 'font': {'size': 20}},
                delta={'reference': 80, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#10b981" if success_rate >= 80 else "#f59e0b" if success_rate >= 60 else "#ef4444"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 60], 'color': '#fee2e2'},
                        {'range': [60, 80], 'color': '#fef3c7'},
                        {'range': [80, 100], 'color': '#d1fae5'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # CATEGORY NAVIGATION BUTTONS (Like localhost dashboard)
        st.markdown("---")
        st.markdown("### 📊 Transaction Categories")

        # Initialize selected category
        if 'fnb_selected_category' not in st.session_state:
            st.session_state.fnb_selected_category = 'all'

        # Create navigation buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✅ Matched", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'matched' else "secondary",
                        key='btn_matched'):
                st.session_state.fnb_selected_category = 'matched'
                st.rerun()
            if st.button("🔀 Split Transactions", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'split' else "secondary",
                        key='btn_split'):
                st.session_state.fnb_selected_category = 'split'
                st.rerun()

        with col2:
            if st.button("📊 All Transactions", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'all' else "secondary",
                        key='btn_all'):
                st.session_state.fnb_selected_category = 'all'
                st.rerun()
            if st.button("💜 Balanced By Fuzzy", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'fuzzy' else "secondary",
                        key='btn_fuzzy'):
                st.session_state.fnb_selected_category = 'fuzzy'
                st.rerun()

        with col3:
            if st.button("❌ Unmatched Ledger", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'unmatched_ledger' else "secondary",
                        key='btn_unmatched_ledger'):
                st.session_state.fnb_selected_category = 'unmatched_ledger'
                st.rerun()
            if st.button("💎 Foreign Credits", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'foreign' else "secondary",
                        key='btn_foreign'):
                st.session_state.fnb_selected_category = 'foreign'
                st.rerun()

        with col4:
            if st.button("⚠️ Unmatched Statement", use_container_width=True,
                        type="primary" if st.session_state.fnb_selected_category == 'unmatched_statement' else "secondary",
                        key='btn_unmatched_stmt'):
                st.session_state.fnb_selected_category = 'unmatched_statement'
                st.rerun()

        # Display selected category
        st.markdown("---")
        
        # Data Manipulation Controls
        st.markdown("### 🛠️ Data Tools")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔍 Filter Results", use_container_width=True, key='filter_results_btn'):
                st.session_state.show_filter = not st.session_state.get('show_filter', False)
        with col2:
            if st.button("✏️ Edit Mode", use_container_width=True, key='edit_mode_btn'):
                st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
                if st.session_state.edit_mode:
                    st.info("✏️ Edit mode enabled - Click on transactions to modify")
        with col3:
            if st.button("↻ Refresh", use_container_width=True, key='refresh_btn'):
                self.log_audit_trail("REFRESH_DATA", {})
                st.rerun()
        with col4:
            if st.button("📋 Audit Log", use_container_width=True, key='audit_btn'):
                st.session_state.show_audit = not st.session_state.get('show_audit', False)
        
        # Show audit log if requested
        if st.session_state.get('show_audit', False):
            with st.expander("📋 Audit Trail", expanded=True):
                audit_trail = st.session_state.get('audit_trail', [])
                if audit_trail:
                    audit_df = pd.DataFrame(audit_trail)
                    st.dataframe(audit_df, use_container_width=True, height=200)
                else:
                    st.info("No audit entries yet")
        
        st.markdown("---")
        
        self.display_fnb_category(results, st.session_state.fnb_selected_category)

        # Alternative: Tabs (collapsed by default)
        with st.expander("📑 View All Categories (Tab View)", expanded=False):
            tabs = st.tabs([
                "✅ Perfect Match",
                "🔍 Fuzzy Match",
                "💰 Foreign Credits",
                "🔀 Split Transactions",
                "❌ Unmatched Ledger",
                "⚠️ Unmatched Statement",
                "📊 All Matched"
            ])

            # Tab 0: Perfect Match
            with tabs[0]:
                if 'matched' in results and not results['matched'].empty:
                    perfect = results['matched'][results['matched']['Match_Type'] == 'Perfect']
                    if not perfect.empty:
                        st.dataframe(perfect, use_container_width=True)
                        st.download_button(
                            "📥 Download Perfect Matches",
                            perfect.to_csv(index=False),
                            "fnb_perfect_matches.csv",
                            "text/csv",
                            key='download_perfect_tab_view'
                        )
                    else:
                        st.info("No perfect matches found")
                else:
                    st.info("No perfect matches found")

            # Tab 1: Fuzzy Match
            with tabs[1]:
                if 'matched' in results and not results['matched'].empty:
                    fuzzy = results['matched'][results['matched']['Match_Type'] == 'Fuzzy']
                    if not fuzzy.empty:
                        st.dataframe(fuzzy, use_container_width=True)
                        st.download_button(
                            "📥 Download Fuzzy Matches",
                            fuzzy.to_csv(index=False),
                            "fnb_fuzzy_matches.csv",
                            "text/csv",
                            key='download_fuzzy_tab_view'
                        )
                    else:
                        st.info("No fuzzy matches found")
                else:
                    st.info("No fuzzy matches found")

            # Tab 2: Foreign Credits
            with tabs[2]:
                if 'matched' in results and not results['matched'].empty:
                    foreign = results['matched'][results['matched']['Match_Type'] == 'Foreign_Credit']
                    if not foreign.empty:
                        st.dataframe(foreign, use_container_width=True)
                        st.download_button(
                            "📥 Download Foreign Credits",
                            foreign.to_csv(index=False),
                            "fnb_foreign_credits.csv",
                            "text/csv",
                            key='download_foreign_tab_view'
                        )
                    else:
                        st.info("No foreign credits found")
                else:
                    st.info("No foreign credits found")

            # Tab 3: Split Transactions
            with tabs[3]:
                split_matches = results.get('split_matches', [])
                if split_matches and len(split_matches) > 0:
                    st.info(f"📊 Found {len(split_matches)} split transaction(s)")
                    
                    # Get original dataframes from session state
                    ledger = st.session_state.get('fnb_ledger')
                    statement = st.session_state.get('fnb_statement')
                    
                    for i, split in enumerate(split_matches):
                        split_type = split.get('split_type', 'Unknown')
                        with st.expander(f"🔀 Split #{i+1} - {split_type.replace('_', ' ').title()}", expanded=(i==0)):
                            # Summary info
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown("**📋 Type:**")
                                if split_type == 'many_to_one':
                                    st.write("Multiple Ledger → One Statement")
                                elif split_type == 'one_to_many':
                                    st.write("One Ledger → Multiple Statements")
                                else:
                                    st.write(split_type.replace('_', ' ').title())
                            
                            with col2:
                                st.markdown("**💰 Total Amount:**")
                                st.write(f"`{split.get('total_amount', 0):,.2f}`")
                            
                            st.divider()
                            
                            # Show actual transaction data
                            if split_type == 'many_to_one':
                                # Statement transaction (target)
                                stmt_idx = split.get('statement_idx')
                                if statement is not None and stmt_idx in statement.index:
                                    st.markdown("**� Statement Transaction (Target):**")
                                    stmt_row = statement.loc[[stmt_idx]].copy()
                                    # Remove normalized columns
                                    display_cols = [col for col in stmt_row.columns if not col.startswith('_')]
                                    st.dataframe(stmt_row[display_cols], use_container_width=True, hide_index=True)
                                    st.markdown("")
                                
                                # Ledger transactions (components)
                                ledger_indices = split.get('ledger_indices', [])
                                if ledger is not None and ledger_indices:
                                    st.markdown(f"**📊 Ledger Transactions (Components - {len(ledger_indices)} items):**")
                                    ledger_rows = ledger.loc[ledger_indices].copy()
                                    # Remove normalized columns
                                    display_cols = [col for col in ledger_rows.columns if not col.startswith('_')]
                                    st.dataframe(ledger_rows[display_cols], use_container_width=True, hide_index=True)
                            
                            elif split_type == 'one_to_many':
                                # Ledger transaction (target)
                                ledger_idx = split.get('ledger_idx')
                                if ledger is not None and ledger_idx in ledger.index:
                                    st.markdown("**📊 Ledger Transaction (Target):**")
                                    ledger_row = ledger.loc[[ledger_idx]].copy()
                                    # Remove normalized columns
                                    display_cols = [col for col in ledger_row.columns if not col.startswith('_')]
                                    st.dataframe(ledger_row[display_cols], use_container_width=True, hide_index=True)
                                    st.markdown("")
                                
                                # Statement transactions (components)
                                stmt_indices = split.get('statement_indices', [])
                                if statement is not None and stmt_indices:
                                    st.markdown(f"**📄 Statement Transactions (Components - {len(stmt_indices)} items):**")
                                    stmt_rows = statement.loc[stmt_indices].copy()
                                    # Remove normalized columns
                                    display_cols = [col for col in stmt_rows.columns if not col.startswith('_')]
                                    st.dataframe(stmt_rows[display_cols], use_container_width=True, hide_index=True)
                else:
                    st.success("✅ No split transactions found - All transactions matched individually")

            # Tab 4: Unmatched Ledger
            with tabs[4]:
                if 'unmatched_ledger' in results and isinstance(results['unmatched_ledger'], pd.DataFrame) and not results['unmatched_ledger'].empty:
                    unmatched_ledger = results['unmatched_ledger'].copy()
                    # Remove any None values
                    unmatched_ledger = unmatched_ledger.fillna('')
                    
                    st.warning(f"⚠️ Found {len(unmatched_ledger)} unmatched ledger item(s)")
                    st.dataframe(unmatched_ledger, use_container_width=True, height=400)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download Unmatched Ledger",
                            unmatched_ledger.to_csv(index=False),
                            "fnb_unmatched_ledger.csv",
                            "text/csv",
                            key='download_unmatched_ledger_tab_view'
                        )
                    with col2:
                        if st.button("🔍 Investigate", key='investigate_ledger'):
                            st.info("💡 Review these items manually or adjust matching settings")
                else:
                    st.success("✅ All ledger items matched!")

            # Tab 5: Unmatched Statement
            with tabs[5]:
                if 'unmatched_statement' in results and isinstance(results['unmatched_statement'], pd.DataFrame) and not results['unmatched_statement'].empty:
                    unmatched_statement = results['unmatched_statement'].copy()
                    # Remove any None values
                    unmatched_statement = unmatched_statement.fillna('')
                    
                    st.warning(f"⚠️ Found {len(unmatched_statement)} unmatched statement item(s)")
                    st.dataframe(unmatched_statement, use_container_width=True, height=400)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download Unmatched Statement",
                            unmatched_statement.to_csv(index=False),
                            "fnb_unmatched_statement.csv",
                            "text/csv",
                            key='download_unmatched_stmt_tab_view'
                        )
                    with col2:
                        if st.button("🔍 Investigate", key='investigate_statement'):
                            st.info("💡 Review these items manually or adjust matching settings")
                else:
                    st.success("✅ All statement items matched!")

            # Tab 6: All Matched (Combined view)
            with tabs[6]:
                if 'matched' in results and not results['matched'].empty:
                    st.dataframe(results['matched'], use_container_width=True)
                    st.download_button(
                        "📥 Download All Matched",
                        results['matched'].to_csv(index=False),
                        "fnb_all_matched.csv",
                        "text/csv",
                        key='download_all_matched'
                    )
                else:
                    st.info("No matched transactions found")

        # Export and Save buttons
        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("💾 Save Results to Database", type="primary", use_container_width=True, key="fnb_save_db"):
                self.save_results_to_db(results)

        with col_b:
            # Initialize export mode in session state
            if 'fnb_export_mode' not in st.session_state:
                st.session_state.fnb_export_mode = False
            
            # Button to enter export mode
            if not st.session_state.fnb_export_mode:
                if st.button("📊 Export All to Excel", type="primary", use_container_width=True, key="fnb_export_excel"):
                    st.session_state.fnb_export_mode = True
                    st.rerun()
        
        # Show export UI when in export mode (outside columns)
        if st.session_state.get('fnb_export_mode', False):
            self.export_to_excel(results)

    def export_to_excel(self, results):
        """Export all results to Excel with proper batch grouping (GUI style)"""
        try:
            from io import BytesIO
            import pandas as pd

            # Get original dataframes to determine master column structure
            ledger = st.session_state.get('fnb_ledger')
            statement = st.session_state.get('fnb_statement')
            
            # Get all original columns (excluding normalized columns)
            ledger_cols = [col for col in ledger.columns if not col.startswith('_')] if ledger is not None else []
            stmt_cols = [col for col in statement.columns if not col.startswith('_')] if statement is not None else []
            
            # ========== COLUMN SELECTION UI ==========
            st.markdown("---")
            st.markdown("### 🎯 Customize Your Report")
            
            # Add Cancel button at the top
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Cancel", key="fnb_cancel_export"):
                    st.session_state.fnb_export_mode = False
                    st.rerun()
            
            with st.expander("📋 Select Columns to Include in Export", expanded=True):
                selected_ledger, selected_statement = ColumnSelector.render_column_selector(
                    ledger_cols=ledger_cols,
                    statement_cols=stmt_cols,
                    workflow_name="fnb"
                )
                
                # Validate - at least one column must be selected
                if not selected_ledger and not selected_statement:
                    st.error("❌ Please select at least one column to export")
                    st.info("💡 Click **Cancel** above to go back")
                    return
                
                st.success(f"✅ Ready to export: **{len(selected_ledger)}** ledger columns + **{len(selected_statement)}** statement columns")
            
            # Define MASTER COLUMN STRUCTURE using SELECTED columns only
            # Format: [Match_Score, Match_Type] + Selected_Ledger_cols + [EMPTY, EMPTY] + Selected_Statement_cols
            master_columns = ['Match_Score', 'Match_Type']
            for col in selected_ledger:
                master_columns.append(f'Ledger_{col}')
            master_columns.extend(['', ' '])  # 2 empty separator columns
            for col in selected_statement:
                master_columns.append(f'Statement_{col}')
            
            # Helper function to align row data to master columns
            def align_to_master(row_dict):
                """Align a row dictionary to master column structure"""
                aligned_row = []
                for col in master_columns:
                    aligned_row.append(row_dict.get(col, ''))
                return aligned_row
            
            # Create organized CSV with batch headers and separators (like GUI)
            csv_rows = []
            
            # Add header information
            csv_rows.append(['FNB RECONCILIATION RESULTS'])
            csv_rows.append(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            csv_rows.append([])  # Blank line
            
            # BATCH 1: PERFECT MATCHES (100% Score)
            if 'matched' in results and not results['matched'].empty:
                perfect_matches = results['matched'][results['matched']['Match_Type'] == 'Perfect']
                if not perfect_matches.empty:
                    csv_rows.append(['=' * 100])
                    csv_rows.append(['BATCH 1: PERFECT MATCHES (100% Score)'])
                    csv_rows.append([f'Count: {len(perfect_matches)}'])
                    csv_rows.append(['=' * 100])
                    csv_rows.append([])
                    
                    # Add master column headers
                    csv_rows.append(master_columns)
                    
                    # Add data rows aligned to master columns
                    for _, row in perfect_matches.iterrows():
                        row_dict = row.to_dict()
                        csv_rows.append(align_to_master(row_dict))
                    
                    csv_rows.append([])
                    csv_rows.append([])  # Double blank line separator
            
            # BATCH 2: FUZZY MATCHES
            if 'matched' in results and not results['matched'].empty:
                fuzzy_matches = results['matched'][results['matched']['Match_Type'] == 'Fuzzy']
                if not fuzzy_matches.empty:
                    csv_rows.append(['=' * 100])
                    csv_rows.append(['BATCH 2: FUZZY MATCHES (85-99% Similarity)'])
                    csv_rows.append([f'Count: {len(fuzzy_matches)}'])
                    csv_rows.append(['=' * 100])
                    csv_rows.append([])
                    
                    # Add master column headers
                    csv_rows.append(master_columns)
                    
                    # Add data rows aligned to master columns
                    for _, row in fuzzy_matches.iterrows():
                        row_dict = row.to_dict()
                        csv_rows.append(align_to_master(row_dict))
                    
                    csv_rows.append([])
                    csv_rows.append([])
            
            # BATCH 3: FOREIGN CREDITS (>10,000)
            if 'matched' in results and not results['matched'].empty:
                foreign_credits = results['matched'][results['matched']['Match_Type'] == 'Foreign_Credit']
                if not foreign_credits.empty:
                    csv_rows.append(['=' * 100])
                    csv_rows.append(['BATCH 3: FOREIGN CREDITS (Amount > 10,000)'])
                    csv_rows.append([f'Count: {len(foreign_credits)}'])
                    csv_rows.append(['=' * 100])
                    csv_rows.append([])
                    
                    # Add master column headers
                    csv_rows.append(master_columns)
                    
                    # Add data rows aligned to master columns
                    for _, row in foreign_credits.iterrows():
                        row_dict = row.to_dict()
                        csv_rows.append(align_to_master(row_dict))
                    
                    csv_rows.append([])
                    csv_rows.append([])
            
            # BATCH 4: SPLIT TRANSACTIONS - GUI Style with actual transaction rows
            split_matches = results.get('split_matches', [])
            if split_matches:
                csv_rows.append(['=' * 100])
                csv_rows.append(['BATCH 4: SPLIT TRANSACTIONS'])
                csv_rows.append([f'Count: {len(split_matches)}'])
                csv_rows.append(['=' * 100])
                csv_rows.append([])
                
                # Get original dataframes from session state
                ledger = st.session_state.get('fnb_ledger')
                statement = st.session_state.get('fnb_statement')
                
                # Get column settings
                settings = st.session_state.get('fnb_match_settings', {})
                ledger_date_col = settings.get('ledger_date_col', 'Date')
                ledger_ref_col = settings.get('ledger_ref_col', 'Reference')
                ledger_debit_col = settings.get('ledger_debit_col', 'Debit')
                ledger_credit_col = settings.get('ledger_credit_col', 'Credit')
                stmt_date_col = settings.get('statement_date_col', 'Date')
                stmt_ref_col = settings.get('statement_ref_col', 'Reference')
                stmt_amt_col = settings.get('statement_amt_col', 'Amount')
                
                # Use master column headers with selected columns (same as other batches)
                csv_rows.append(master_columns)
                
                # Process each split match
                for split in split_matches:
                    split_type = split.get('split_type', 'Unknown')
                    
                    if split_type == 'many_to_one':
                        # Multiple ledger entries to one statement
                        stmt_idx = split.get('statement_idx')
                        ledger_indices = split.get('ledger_indices', [])
                        
                        if statement is not None and stmt_idx in statement.index:
                            stmt_row = statement.loc[stmt_idx]
                            
                            # First row: First ledger with statement data
                            if ledger_indices and ledger is not None:
                                for idx_num, ledger_idx in enumerate(ledger_indices):
                                    if ledger_idx in ledger.index:
                                        ledger_row_data = ledger.loc[ledger_idx]
                                        row_data = []
                                        
                                        # Build row dict aligned to master columns
                                        row_dict = {
                                            'Match_Score': '',
                                            'Match_Type': 'Split'
                                        }
                                        
                                        # Add ONLY selected ledger columns
                                        for col in selected_ledger:
                                            val = ledger_row_data.get(col, '')
                                            row_dict[f'Ledger_{col}'] = val if pd.notna(val) else ''
                                        
                                        # Add ONLY selected statement columns (only on first row)
                                        if idx_num == 0:
                                            for col in selected_statement:
                                                val = stmt_row.get(col, '')
                                                row_dict[f'Statement_{col}'] = val if pd.notna(val) else ''
                                        else:
                                            # Empty statement columns for subsequent rows
                                            for col in selected_statement:
                                                row_dict[f'Statement_{col}'] = ''
                                        
                                        csv_rows.append(align_to_master(row_dict))
                    
                    elif split_type == 'one_to_many':
                        # One ledger entry to multiple statements
                        ledger_idx = split.get('ledger_idx')
                        stmt_indices = split.get('statement_indices', [])
                        
                        if ledger is not None and ledger_idx in ledger.index:
                            ledger_row_data = ledger.loc[ledger_idx]
                            
                            # Process each statement
                            if stmt_indices and statement is not None:
                                for idx_num, stmt_idx in enumerate(stmt_indices):
                                    if stmt_idx in statement.index:
                                        stmt_row = statement.loc[stmt_idx]
                                        row_data = []
                                        
                                        # Build row dict aligned to master columns
                                        row_dict = {
                                            'Match_Score': '',
                                            'Match_Type': 'Split'
                                        }
                                        
                                        # Add ONLY selected ledger columns (only on first row)
                                        if idx_num == 0:
                                            for col in selected_ledger:
                                                val = ledger_row_data.get(col, '')
                                                row_dict[f'Ledger_{col}'] = val if pd.notna(val) else ''
                                        else:
                                            # Empty ledger columns for subsequent rows
                                            for col in selected_ledger:
                                                row_dict[f'Ledger_{col}'] = ''
                                        
                                        # Add ONLY selected statement columns
                                        for col in selected_statement:
                                            val = stmt_row.get(col, '')
                                            row_dict[f'Statement_{col}'] = val if pd.notna(val) else ''
                                        
                                        csv_rows.append(align_to_master(row_dict))
                
                csv_rows.append([])
                csv_rows.append([])
            
            # BATCH 5: UNMATCHED ITEMS (Ledger and Statement side-by-side)
            unmatched_ledger = results.get('unmatched_ledger', pd.DataFrame())
            unmatched_statement = results.get('unmatched_statement', pd.DataFrame())
            
            if not unmatched_ledger.empty or not unmatched_statement.empty:
                csv_rows.append(['=' * 100])
                csv_rows.append(['BATCH 5: UNMATCHED ITEMS'])
                csv_rows.append([f'Unmatched Ledger: {len(unmatched_ledger)} | Unmatched Statement: {len(unmatched_statement)}'])
                csv_rows.append(['=' * 100])
                csv_rows.append([])
                
                # Use master column headers (same as other batches)
                unmatched_ledger_cols = unmatched_ledger.columns.tolist() if not unmatched_ledger.empty else []
                unmatched_stmt_cols = unmatched_statement.columns.tolist() if not unmatched_statement.empty else []
                
                csv_rows.append(master_columns)
                
                # Determine how many rows we need (max of ledger or statement)
                max_rows = max(len(unmatched_ledger), len(unmatched_statement))
                
                # Add data rows - side by side, aligned to master columns
                for i in range(max_rows):
                    row_dict = {
                        'Match_Score': '',
                        'Match_Type': 'Unmatched'
                    }
                    
                    # Add ONLY selected ledger data if available at this index
                    if i < len(unmatched_ledger):
                        ledger_row = unmatched_ledger.iloc[i]
                        for col in selected_ledger:
                            if col in ledger_row.index:
                                val = ledger_row.get(col, '')
                                row_dict[f'Ledger_{col}'] = val if pd.notna(val) else ''
                    else:
                        # Empty ledger columns if no more ledger items
                        for col in selected_ledger:
                            row_dict[f'Ledger_{col}'] = ''
                    
                    # Add ONLY selected statement data if available at this index
                    if i < len(unmatched_statement):
                        stmt_row = unmatched_statement.iloc[i]
                        for col in selected_statement:
                            if col in stmt_row.index:
                                val = stmt_row.get(col, '')
                                row_dict[f'Statement_{col}'] = val if pd.notna(val) else ''
                    else:
                        # Empty statement columns if no more statement items
                        for col in selected_statement:
                            row_dict[f'Statement_{col}'] = ''
                    
                    csv_rows.append(align_to_master(row_dict))
                
                csv_rows.append([])
                csv_rows.append([])
            
            # SUMMARY SECTION
            csv_rows.append(['=' * 100])
            csv_rows.append(['RECONCILIATION SUMMARY'])
            csv_rows.append(['=' * 100])
            csv_rows.append([])
            csv_rows.append(['Perfect Matches:', results.get('perfect_match_count', 0)])
            csv_rows.append(['Fuzzy Matches:', results.get('fuzzy_match_count', 0)])
            csv_rows.append(['Foreign Credits:', results.get('foreign_credits_count', 0)])
            csv_rows.append(['Split Transactions:', results.get('split_count', 0)])
            csv_rows.append(['Total Matched:', results.get('total_matched', 0)])
            csv_rows.append([])
            csv_rows.append(['Unmatched Ledger:', results.get('unmatched_ledger_count', 0)])
            csv_rows.append(['Unmatched Statement:', results.get('unmatched_statement_count', 0)])
            
            # Convert to DataFrame for CSV export
            max_cols = max(len(row) for row in csv_rows)
            for row in csv_rows:
                while len(row) < max_cols:
                    row.append('')
            
            export_df = pd.DataFrame(csv_rows)
            
            # Create CSV string
            csv_string = export_df.to_csv(index=False, header=False)

            st.markdown("---")
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                st.download_button(
                    label="📥 Download Batched CSV Report (GUI Style)",
                    data=csv_string,
                    file_name=f"FNB_Reconciliation_Batched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.success("✅ Batched CSV report ready for download! Organized like GUI export with separators.")
            st.info("💡 After downloading, click **Cancel** above to return to results")

        except Exception as e:
            st.error(f"❌ Failed to create CSV report: {str(e)}")

    def save_results_to_db(self, results):
        """Save reconciliation results to database with proper persistence"""
        try:
            import sys
            import os
            import pickle
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
            from database import get_db  # type: ignore

            # Show input dialog for result name
            result_name = st.text_input(
                "Enter a name for these results:",
                value=f"FNB_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                key='fnb_save_result_name'
            )

            if st.button("✅ Confirm Save", key='fnb_confirm_save'):
                # Get database instance
                db = get_db()

                # Prepare metadata with timestamp
                metadata = {
                    'ledger_columns': list(st.session_state.fnb_ledger.columns),
                    'statement_columns': list(st.session_state.fnb_statement.columns),
                    'match_settings': st.session_state.fnb_match_settings,
                    'saved_timestamp': datetime.now().isoformat()
                }

                # Save to database
                result_id = db.save_result(
                    name=result_name,
                    workflow_type='FNB',
                    results=results,
                    metadata=metadata
                )

                # PERSIST TO SESSION STATE (so data survives refresh)
                st.session_state.fnb_results = results
                st.session_state.fnb_results_saved = True
                st.session_state.fnb_last_save_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Add to reconciliation history
                if 'reconciliation_history' not in st.session_state:
                    st.session_state.reconciliation_history = []
                
                st.session_state.reconciliation_history.append({
                    'date': datetime.now(),
                    'workflow': 'FNB',
                    'matched': results.get('total_matched', 0),
                    'unmatched': results.get('unmatched_ledger_count', 0) + results.get('unmatched_statement_count', 0),
                    'result_id': result_id
                })

                st.success(f"✅ Results saved successfully! (ID: {result_id})")
                st.info("💡 Data persisted to session. View from Dashboard or Data Management page")
                
                # Log audit trail
                self.log_audit_trail("SAVE_RESULTS", {
                    'result_id': result_id,
                    'name': result_name,
                    'matched_count': results.get('total_matched', 0),
                    'unmatched_count': results.get('unmatched_ledger_count', 0) + results.get('unmatched_statement_count', 0)
                })

        except Exception as e:
            st.error(f"❌ Failed to save results: {str(e)}")
            
    def log_audit_trail(self, action, details):
        """Log actions to audit trail"""
        if 'audit_trail' not in st.session_state:
            st.session_state.audit_trail = []
        
        st.session_state.audit_trail.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'workflow': 'FNB',
            'action': action,
            'details': details,
            'user': st.session_state.get('username', 'admin')
        })

    def display_fnb_category(self, results, category):
        """Display transactions for selected category"""

        if category == 'all':
            st.info("👆 Select a category above to view specific transaction details")
            return

        # Map category to results data
        category_data = None
        category_title = ""
        download_filename = ""

        if category == 'matched':
            if 'matched' in results and not results['matched'].empty:
                # Show all matched (perfect + fuzzy + foreign)
                category_data = results['matched']
                category_title = "✅ All Matched Transactions"
                download_filename = "fnb_all_matched.csv"

        elif category == 'split':
            split_matches = results.get('split_matches', [])
            if split_matches and len(split_matches) > 0:
                st.markdown(f"### 🔀 Split Transactions ({len(split_matches)} splits)")
                st.info(f"📊 Found {len(split_matches)} split transaction(s)")
                
                # Get original dataframes from session state
                ledger = st.session_state.get('fnb_ledger')
                statement = st.session_state.get('fnb_statement')
                
                if ledger is None or statement is None:
                    st.error("❌ Original data not found in session state")
                    return
                
                # Get column names (excluding normalized columns)
                ledger_display_cols = [col for col in ledger.columns if not col.startswith('_')]
                statement_display_cols = [col for col in statement.columns if not col.startswith('_')]
                
                # Build flat Excel-style table like matched transactions
                all_split_rows = []
                
                for split_idx, split in enumerate(split_matches, start=1):
                    split_type = split.get('split_type', 'Unknown')
                    
                    if split_type == 'many_to_one':
                        # Many Ledger → One Statement
                        # Show: Multiple ledger rows + ONE statement row at the end
                        stmt_idx = split.get('statement_idx')
                        ledger_indices = split.get('ledger_indices', [])
                        
                        if stmt_idx not in statement.index:
                            continue
                        
                        stmt_row = statement.loc[stmt_idx]
                        
                        # Add each ledger row with the statement in the FIRST row only
                        for idx, ledger_idx in enumerate(ledger_indices):
                            if ledger_idx in ledger.index:
                                row_dict = {}
                                
                                # Add all ledger columns with Ledger_ prefix
                                ledger_row = ledger.loc[ledger_idx]
                                for col in ledger_display_cols:
                                    row_dict[f'Ledger_{col}'] = ledger_row[col]
                                
                                # Add statement columns ONLY in the first row
                                if idx == 0:
                                    for col in statement_display_cols:
                                        row_dict[f'Statement_{col}'] = stmt_row[col]
                                else:
                                    # Empty statement columns for subsequent rows
                                    for col in statement_display_cols:
                                        row_dict[f'Statement_{col}'] = ''
                                
                                all_split_rows.append(row_dict)
                    
                    elif split_type == 'one_to_many':
                        # One Ledger → Many Statement
                        # Show: ONE ledger row + Multiple statement rows
                        ledger_idx = split.get('ledger_idx')
                        stmt_indices = split.get('statement_indices', [])
                        
                        if ledger_idx not in ledger.index:
                            continue
                        
                        ledger_row = ledger.loc[ledger_idx]
                        
                        # Add each statement row with the ledger in the FIRST row only
                        for idx, stmt_idx in enumerate(stmt_indices):
                            if stmt_idx in statement.index:
                                row_dict = {}
                                
                                # Add ledger columns ONLY in the first row
                                if idx == 0:
                                    for col in ledger_display_cols:
                                        row_dict[f'Ledger_{col}'] = ledger_row[col]
                                else:
                                    # Empty ledger columns for subsequent rows
                                    for col in ledger_display_cols:
                                        row_dict[f'Ledger_{col}'] = ''
                                
                                # Add all statement columns with Statement_ prefix
                                stmt_row = statement.loc[stmt_idx]
                                for col in statement_display_cols:
                                    row_dict[f'Statement_{col}'] = stmt_row[col]
                                
                                all_split_rows.append(row_dict)
                
                # Create DataFrame
                if all_split_rows:
                    split_df = pd.DataFrame(all_split_rows)
                    
                    # Display in Excel-like format (same as matched transactions)
                    st.dataframe(split_df, use_container_width=True, height=600)
                    
                    # Download button
                    st.download_button(
                        "📥 Download Split Transactions",
                        split_df.to_csv(index=False),
                        "fnb_split_transactions.csv",
                        "text/csv",
                        key='download_split'
                    )
                else:
                    st.warning("⚠️ Could not build split transactions table")
                
                return
            else:
                st.success("✅ No split transactions found - All transactions matched individually")
                return

        elif category == 'fuzzy':
            if 'matched' in results and not results['matched'].empty:
                fuzzy_df = results['matched'][results['matched']['Match_Type'] == 'Fuzzy']
                if not fuzzy_df.empty:
                    category_data = fuzzy_df
                    category_title = "💜 Fuzzy Matched Transactions"
                    download_filename = "fnb_fuzzy_matched.csv"

        elif category == 'foreign':
            if 'matched' in results and not results['matched'].empty:
                foreign_df = results['matched'][results['matched']['Match_Type'] == 'Foreign_Credit']
                if not foreign_df.empty:
                    category_data = foreign_df
                    category_title = "💎 Foreign Credits"
                    download_filename = "fnb_foreign_credits.csv"

        elif category == 'unmatched_ledger':
            if 'unmatched_ledger' in results and not results['unmatched_ledger'].empty:
                category_data = results['unmatched_ledger']
                category_title = "❌ Unmatched Ledger Items"
                download_filename = "fnb_unmatched_ledger.csv"

        elif category == 'unmatched_statement':
            if 'unmatched_statement' in results and not results['unmatched_statement'].empty:
                category_data = results['unmatched_statement']
                category_title = "⚠️ Unmatched Statement Items"
                download_filename = "fnb_unmatched_statement.csv"

        # Display the data
        if category_data is not None and not category_data.empty:
            st.markdown(f"### {category_title}")
            st.info(f"📊 Found {len(category_data)} transaction(s)")

            st.dataframe(category_data, use_container_width=True, height=400)

            # Download button
            st.download_button(
                f"📥 Download {category_title}",
                category_data.to_csv(index=False),
                download_filename,
                "text/csv",
                key=f'download_{category}'
            )
        else:
            st.info(f"No data found for this category")
