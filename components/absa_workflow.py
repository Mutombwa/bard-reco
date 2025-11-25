"""
ABSA Workflow Component - Based on FNB Logic with ABSA Statement Processing
===========================================================================
Advanced reconciliation engine with weighted scoring matching
Date (30%) + Reference (40%) + Amount (30%) = Total Score

Special ABSA Features:
- Extracts Reference and Fee from Description column
- Format: "CARDLESS CASH DEP HILLBROW 1( 5,49 ) DEPOSIT NO : linda CONTACT : 0744811776"
  * Reference: "linda" (extracted from "DEPOSIT NO : linda")
  * Fee: 5.49 (extracted from "( 5,49 )" where comma is decimal separator)
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

class ABSAWorkflow:
    """ABSA Bank Reconciliation Workflow with ABSA-Specific Statement Processing"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'absa_ledger' not in st.session_state:
            st.session_state.absa_ledger = None
        if 'absa_statement' not in st.session_state:
            st.session_state.absa_statement = None
        if 'absa_results' not in st.session_state:
            st.session_state.absa_results = None
        if 'absa_column_mapping' not in st.session_state:
            st.session_state.absa_column_mapping = {}
        if 'absa_match_settings' not in st.session_state:
            st.session_state.absa_match_settings = {
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
        """Render ABSA workflow page"""

        # Header
        st.markdown("""
        <style>
        .gradient-header {
            background: linear-gradient(135deg, #c41e3a 0%, #e63946 100%);
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
            color: #ffc8d0;
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
            <h1>🏦 ABSA Workflow</h1>
            <p>Advanced Bank Reconciliation • ABSA Statement Processing • Auto Reference & Fee Extraction</p>
        </div>
        """, unsafe_allow_html=True)

        # Step 1: File Upload
        self.render_file_upload()

        # Step 2-5: Show configuration sections (if files uploaded)
        if st.session_state.absa_ledger is not None and st.session_state.absa_statement is not None:
            # Quick status summary at top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📗 Ledger Rows", f"{len(st.session_state.absa_ledger):,}")
            with col2:
                st.metric("📘 Statement Rows", f"{len(st.session_state.absa_statement):,}")
            with col3:
                st.metric("✅ Status", "Ready to Configure")
            
            self.render_data_tools()

            # Step 3: Column Mapping
            self.render_column_mapping()

            # Step 4: Matching Settings
            self.render_matching_settings()

            # Step 5: Run Reconciliation
            self.render_reconciliation_controls()

        # Step 6: Display Results
        if st.session_state.absa_results is not None:
            self.render_results()

    def render_file_upload(self):
        """Render file upload section"""
        
        st.subheader("📁 Step 1: Import Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger File**")

            # Show existing data status FIRST
            if st.session_state.absa_ledger is not None:
                st.success(f"📊 **Ledger:** {len(st.session_state.absa_ledger)} rows × {len(st.session_state.absa_ledger.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.absa_ledger.columns))

            ledger_file = st.file_uploader("Upload NEW Ledger File", type=['xlsx', 'xls', 'csv'], key='absa_ledger_upload', help="Upload a new file to replace current data")

            if ledger_file is not None:
                ledger_df, is_new = load_uploaded_file(
                    ledger_file,
                    session_key='absa_ledger',
                    hash_key='absa_ledger_hash',
                    show_progress=True
                )

                if is_new:
                    st.session_state.absa_ledger_original_cols = list(ledger_df.columns)
                    if 'absa_saved_selections' in st.session_state:
                        del st.session_state.absa_saved_selections
                    st.success(f"✅ New ledger loaded: {get_dataframe_info(ledger_df)}")

        with col2:
            st.markdown("**ABSA Bank Statement File**")

            # Show existing data status FIRST
            if st.session_state.absa_statement is not None:
                st.success(f"📊 **Statement:** {len(st.session_state.absa_statement)} rows × {len(st.session_state.absa_statement.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.absa_statement.columns))

            statement_file = st.file_uploader("Upload NEW ABSA Statement File", type=['xlsx', 'xls', 'csv'], key='absa_statement_upload', help="Upload ABSA statement - Reference and Fee will be auto-extracted")

            if statement_file is not None:
                statement_df, is_new = load_uploaded_file(
                    statement_file,
                    session_key='absa_statement',
                    hash_key='absa_statement_hash',
                    show_progress=True
                )

                if is_new:
                    st.session_state.absa_statement_original_cols = list(statement_df.columns)
                    if 'absa_saved_selections' in st.session_state:
                        del st.session_state.absa_saved_selections
                    st.success(f"✅ New statement loaded: {get_dataframe_info(statement_df)}")
        
        # Add View & Edit Data section
        if st.session_state.absa_ledger is not None or st.session_state.absa_statement is not None:
            st.markdown("---")
            st.subheader("👁️ Step 1.5: View & Edit Data")
            st.info("💡 **Edit your data before reconciliation:** View, add rows, delete rows, copy/paste from Excel, and more!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.absa_ledger is not None:
                    if st.button("📊 View & Edit Ledger", key='absa_view_edit_ledger_btn', use_container_width=True, type="secondary"):
                        st.session_state.absa_show_ledger_editor = True
            
            with col2:
                if st.session_state.absa_statement is not None:
                    if st.button("📊 View & Edit Statement", key='absa_view_edit_statement_btn', use_container_width=True, type="secondary"):
                        st.session_state.absa_show_statement_editor = True
            
            # Show Ledger Editor
            if st.session_state.get('absa_show_ledger_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.absa_ledger, "📗 Ledger Editor", "absa_ledger")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.absa_ledger = saved_data
                    st.session_state.absa_show_ledger_editor = False
                    st.success("✅ Ledger data saved successfully!")

                if st.button("❌ Close Editor", key='absa_close_ledger_editor'):
                    st.session_state.absa_show_ledger_editor = False

            # Show Statement Editor
            if st.session_state.get('absa_show_statement_editor', False):
                st.markdown("---")
                from utils.excel_editor import ExcelEditor
                editor = ExcelEditor(st.session_state.absa_statement, "📘 Statement Editor", "absa_statement")
                saved_data = editor.render()

                if saved_data is not None:
                    st.session_state.absa_statement = saved_data
                    st.session_state.absa_show_statement_editor = False
                    st.success("✅ Statement data saved successfully!")

                if st.button("❌ Close Editor", key='absa_close_statement_editor'):
                    st.session_state.absa_show_statement_editor = False

    def render_data_tools(self):
        """Render ABSA-specific data processing tools"""
        st.markdown("---")
        st.subheader("🛠️ Step 2: ABSA Data Processing Tools")

        # Cache column lists
        if 'absa_ledger_cols_cache' not in st.session_state or st.session_state.get('absa_ledger_cols_dirty', True):
            st.session_state.absa_ledger_cols_cache = list(st.session_state.absa_ledger.columns) if st.session_state.absa_ledger is not None else []
            st.session_state.absa_ledger_cols_dirty = False

        if 'absa_statement_cols_cache' not in st.session_state or st.session_state.get('absa_statement_cols_dirty', True):
            st.session_state.absa_statement_cols_cache = list(st.session_state.absa_statement.columns) if st.session_state.absa_statement is not None else []
            st.session_state.absa_statement_cols_dirty = False

        ledger_cols = st.session_state.absa_ledger_cols_cache
        statement_cols = st.session_state.absa_statement_cols_cache

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🔍 Extract Reference & Fee (ABSA)**")
            st.caption("Extract Reference and Fee from Description")
            if 'Reference' in statement_cols and 'Fee' in statement_cols:
                st.success("✅ Reference and Fee extracted")
            if st.button("🚀 Launch", key='absa_extract_absa_ref_fee', use_container_width=True):
                self.extract_absa_reference_and_fee()

        with col2:
            st.markdown("**📝 Add Reference (Ledger)**")
            st.caption("Extract names from Ledger Description")
            if 'Reference' in ledger_cols:
                st.success("✅ Reference added to Ledger")
            if st.button("🚀 Launch", key='absa_add_ledger_reference_btn', use_container_width=True):
                self.add_ledger_reference()

        with col3:
            st.markdown("**🔢 RJ & Payment Ref**")
            st.caption("Generate RJ numbers")
            if 'RJ-Number' in ledger_cols and 'Payment Ref' in ledger_cols:
                st.success("✅ RJ-Number & Payment Ref added")
            if st.button("🚀 Launch", key='absa_rj_payment_ref_btn', use_container_width=True):
                self.rj_payment_ref_tool()

    def extract_absa_reference_and_fee(self):
        """
        Extract Reference and Fee from ABSA statement Description column
        
        Example: "CARDLESS CASH DEP HILLBROW 1( 5,49 ) DEPOSIT NO : linda CONTACT : 0744811776"
        - Fee: 5.49 (from "( 5,49 )" where comma is decimal separator, so 5 RAND 49 CENTS)
        - Reference: "linda" (from "DEPOSIT NO : linda")
        """
        try:
            if st.session_state.absa_statement is None:
                st.error("❌ Please import an ABSA statement first!")
                return

            statement = st.session_state.absa_statement.copy()

            # Find Description column (case-insensitive)
            desc_col = None
            for col in statement.columns:
                if str(col).strip().lower() == 'description':
                    desc_col = col
                    break

            if desc_col is None:
                st.error("❌ No 'Description' column found in statement")
                return

            def extract_absa_data(description):
                """
                Extract Reference and Fee from ABSA description
                
                Returns: (reference, fee)
                """
                desc = str(description).strip()
                
                # Extract Fee - Format: ( 5,49 ) where comma is decimal separator
                # Pattern: ( followed by digits, comma, digits, close paren
                fee_pattern = r'\(\s*(\d+),(\d+)\s*\)'
                fee_match = re.search(fee_pattern, desc)
                
                if fee_match:
                    # fee_match.group(1) = rand (e.g., "5")
                    # fee_match.group(2) = cents (e.g., "49")
                    rand = fee_match.group(1)
                    cents = fee_match.group(2)
                    # Convert to decimal: 5,49 = 5.49
                    fee = float(f"{rand}.{cents}")
                else:
                    fee = 0.0
                
                # Extract Reference - Multiple ABSA patterns:
                # Examples:
                # - "ACB CREDIT CAPITEC K KWIYO" -> "K KWIYO"
                # - "PayShap Ext Credit P NCUBE" -> "P NCUBE"
                # - "PayShap Ext Credit S MOYO" -> "S MOYO"
                # - "DIGITAL PAYMENT CR ABSA BANK Dumi" -> "Dumi"
                # - "DEPOSIT NO : linda" -> "linda"
                # - "STAMPED STATEMENT ( 13,00 )" -> "" (no reference)
                
                reference = "UNKNOWN"
                
                # Check if it's STAMPED STATEMENT (no reference, only fee)
                if 'STAMPED STATEMENT' in desc.upper():
                    reference = ""
                else:
                    # Try pattern 1: PayShap Ext Credit followed by name
                    # Matches: "PayShap Ext Credit K KWIYO", "PayShap Ext Credit P NCUBE", "PayShap Ext Credit S MOYO"
                    # Pattern: Captures first letter + space + word (e.g., "K KWIYO")
                    payshap_pattern = r'PayShap\s+Ext\s+Credit\s+([A-Z]\s+[A-Za-z]+)'
                    payshap_match = re.search(payshap_pattern, desc, re.IGNORECASE)
                    
                    if payshap_match:
                        reference = payshap_match.group(1).strip().upper()
                    else:
                        # Try pattern 2: ACB CREDIT CAPITEC followed by name
                        # Matches: "ACB CREDIT CAPITEC K KWIYO"
                        # Pattern: Captures first letter + space + word (e.g., "K KWIYO")
                        acb_pattern = r'ACB\s+CREDIT\s+(?:CAPITEC?|CAPITE[C]?)\s+([A-Z]\s+[A-Za-z]+)'
                        acb_match = re.search(acb_pattern, desc, re.IGNORECASE)
                        
                        if acb_match:
                            reference = acb_match.group(1).strip().upper()
                        else:
                            # Try pattern 3: DIGITAL PAYMENT CR ABSA BANK followed by name
                            # Matches: "DIGITAL PAYMENT CR ABSA BANK Dumi"
                            digital_pattern = r'DIGITAL\s+PAYMENT\s+CR\s+ABSA\s+BANK\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)'
                            digital_match = re.search(digital_pattern, desc, re.IGNORECASE)
                            
                            if digital_match:
                                reference = digital_match.group(1).strip()
                            else:
                                # Try pattern 4: DEPOSIT NO
                                # Matches: "DEPOSIT NO : linda" or "DEPOSIT NO : nama twin"
                                # Pattern captures multiple words until CONTACT or end
                                ref_pattern = r'DEPOSIT\s+NO\s*:\s*([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*?)(?:\s+CONTACT\s*:|$)'
                                ref_match = re.search(ref_pattern, desc, re.IGNORECASE)
                                
                                if ref_match:
                                    reference = ref_match.group(1).strip()
                                else:
                                    # Try pattern 5: ABSA BANK followed by name
                                    absa_pattern = r'ABSA\s+BANK\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)'
                                    absa_match = re.search(absa_pattern, desc, re.IGNORECASE)
                                    
                                    if absa_match:
                                        reference = absa_match.group(1).strip()
                                    else:
                                        # Fallback: try CONTACT pattern
                                        contact_pattern = r'CONTACT\s*:\s*(\d+)'
                                        contact_match = re.search(contact_pattern, desc, re.IGNORECASE)
                                        if contact_match:
                                            reference = contact_match.group(1).strip()
                
                return reference, fee

            # Apply extraction to all descriptions
            references = []
            fees = []
            
            for desc in statement[desc_col]:
                ref, fee = extract_absa_data(desc)
                references.append(ref)
                fees.append(fee)

            # Check if columns already exist
            if 'Reference' in statement.columns:
                # Update existing
                statement['Reference'] = references
            else:
                # Insert after Description column
                desc_idx = statement.columns.get_loc(desc_col)
                statement.insert(desc_idx + 1, 'Reference', references)
            
            if 'Fee' in statement.columns:
                # Update existing
                statement['Fee'] = fees
            else:
                # Insert after Reference column
                ref_idx = statement.columns.get_loc('Reference')
                statement.insert(ref_idx + 1, 'Fee', fees)

            st.session_state.absa_statement = statement
            st.session_state.absa_statement_cols_dirty = True

            # Reset saved selections
            if 'absa_saved_selections' in st.session_state:
                del st.session_state.absa_saved_selections

            st.success("✅ Reference and Fee extracted from ABSA statement!")
            
            # Show preview
            with st.expander("📊 Preview Extracted Data (first 10 rows)"):
                preview_cols = [desc_col, 'Reference', 'Fee']
                st.dataframe(statement[preview_cols].head(10), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error extracting ABSA data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    def add_ledger_reference(self):
        """Extract reference names from Ledger Description/Comment column"""
        try:
            import re

            if st.session_state.absa_ledger is None:
                st.error("❌ Please import a ledger first!")
                return

            ledger = st.session_state.absa_ledger.copy()

            # Find Description/Comment column
            desc_col = None
            for col in ledger.columns:
                col_lower = str(col).strip().lower()
                if col_lower in ['description', 'comment', 'narration', 'details']:
                    desc_col = col
                    break

            if desc_col is None:
                st.error("❌ No Description/Comment column found in ledger")
                return

            if 'Reference' in ledger.columns:
                st.info("ℹ️ Reference column already exists in ledger")
                return

            def extract_reference_name(description):
                """Extract reference names from descriptions
                Example: 'Ref #RJ55909152420. - K.kwiyo' -> 'K.kwiyo'
                Example: 'Ref #RJ55909152420. - Ref #RJ55909152420. - K.kwiyo' -> 'K.kwiyo'
                """
                desc = str(description).strip()

                # Pattern 1: RJ number followed by dash and name (handles repeated RJ patterns)
                # Match: "Ref #RJxxxxxxx" followed by "- Name" (capture everything after the last dash)
                # Use greedy match .+ to capture everything including dots
                rj_pattern = r'Ref\s+#RJ\d+\.?\s*-\s*(?:Ref\s+#RJ\d+\.?\s*-\s*)?(.+)'
                rj_match = re.search(rj_pattern, desc, re.IGNORECASE)
                
                if rj_match:
                    reference = rj_match.group(1).strip()
                    # Clean up: remove trailing dots or spaces
                    reference = reference.rstrip('. ')
                    return reference

                # Pattern 2: Other patterns
                patterns = [
                    (r'^\d{10}$', lambda m: m.group(0)),
                    (r'DEPOSIT\s+NO\s*:\s*([a-zA-Z0-9]+)', lambda m: m.group(1).strip()),
                    (r'CONTACT\s*:\s*(\d{10})', lambda m: m.group(1)),
                    (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[a-z]+)$', lambda m: m.group(1).strip()),
                ]

                for pattern, extractor in patterns:
                    match = re.search(pattern, desc, re.IGNORECASE)
                    if match:
                        try:
                            result = extractor(match)
                            if result:
                                return result.strip()
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

            references = []
            for val in ledger[desc_col]:
                ref = extract_reference_name(val)
                references.append(ref)

            desc_idx = ledger.columns.get_loc(desc_col)
            ledger.insert(desc_idx + 1, 'Reference', references)

            st.session_state.absa_ledger = ledger
            st.session_state.absa_ledger_cols_dirty = True

            if 'absa_saved_selections' in st.session_state:
                del st.session_state.absa_saved_selections

            st.success("✅ Reference extracted from ledger!")
            with st.expander("📊 Preview (first 10 rows)"):
                st.dataframe(ledger[[desc_col, 'Reference']].head(10), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error adding reference: {str(e)}")

    def rj_payment_ref_tool(self):
        """Generate RJ-Number and Payment Ref columns"""
        try:
            import re
            ledger = st.session_state.absa_ledger.copy()

            if len(ledger.columns) < 2:
                st.error("Ledger must have at least 2 columns")
                return

            if 'RJ-Number' in ledger.columns or 'Payment Ref' in ledger.columns:
                st.info("RJ-Number and Payment Ref columns already exist")
                return

            def extract_rj_and_ref(comment):
                if not isinstance(comment, str):
                    return '', ''

                rj_match = re.search(r'(RJ|TX)[-]?(\d{6,})', comment, re.IGNORECASE)
                rj = rj_match.group(0).replace('-', '') if rj_match else ''

                payref = ''
                payref_match = re.search(r'Payment Ref[#:]?\s*([\w\s\-\.,&]+)', comment, re.IGNORECASE)
                if payref_match:
                    payref = payref_match.group(1).strip()
                elif rj_match:
                    after = comment[rj_match.end():]
                    after = after.lstrip(' .:-#')
                    # Don't split on dots to preserve names like "K.kwiyo"
                    payref = re.split(r'[,\n\r]', after)[0].strip()
                    # Clean up trailing dots/spaces
                    payref = payref.rstrip('. ')
                else:
                    payref = comment.strip()

                return rj, payref

            rj_numbers = []
            pay_refs = []

            for val in ledger.iloc[:, 1]:
                rj, ref = extract_rj_and_ref(val)
                rj_numbers.append(rj)
                pay_refs.append(ref)

            ledger.insert(2, 'RJ-Number', rj_numbers)
            ledger.insert(3, 'Payment Ref', pay_refs)

            st.session_state.absa_ledger = ledger
            st.session_state.absa_ledger_cols_dirty = True

            if 'absa_saved_selections' in st.session_state:
                del st.session_state.absa_saved_selections

            st.success("✅ Added RJ-Number and Payment Ref columns to ledger")
            st.dataframe(ledger[['RJ-Number', 'Payment Ref']].head(10), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error generating RJ & Payment Ref: {str(e)}")

    def render_column_mapping(self):
        """Render column mapping configuration - Same as FNB"""
        st.markdown("---")
        st.subheader("⚙️ Step 3: Configure Column Mapping")

        ledger_cols = st.session_state.absa_ledger_cols_cache
        statement_cols = st.session_state.absa_statement_cols_cache

        with st.expander("ℹ️ View Available Columns", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Ledger Columns ({len(ledger_cols)} total):**")
                st.code(", ".join(ledger_cols))
            with col_b:
                st.markdown(f"**Statement Columns ({len(statement_cols)} total):**")
                st.code(", ".join(statement_cols))

        if 'absa_saved_selections' not in st.session_state:
            st.session_state.absa_saved_selections = {}

        def get_safe_index(col_list, saved_key, default_name):
            if saved_key in st.session_state.absa_saved_selections:
                saved_idx = st.session_state.absa_saved_selections[saved_key]
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
                key='absa_ledger_date_selector'
            )
            st.session_state.absa_saved_selections['ledger_date_idx'] = ledger_cols.index(ledger_date_selection)
            st.session_state.absa_match_settings['ledger_date_col'] = ledger_date_selection

            ledger_ref_selection = st.selectbox(
                "Reference Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_ref_idx', 'Reference'),
                key='absa_ledger_ref_selector'
            )
            st.session_state.absa_saved_selections['ledger_ref_idx'] = ledger_cols.index(ledger_ref_selection)
            st.session_state.absa_match_settings['ledger_ref_col'] = ledger_ref_selection

            ledger_debit_selection = st.selectbox(
                "Debit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_debit_idx', 'Debit'),
                key='absa_ledger_debit_selector'
            )
            st.session_state.absa_saved_selections['ledger_debit_idx'] = ledger_cols.index(ledger_debit_selection)
            st.session_state.absa_match_settings['ledger_debit_col'] = ledger_debit_selection

            ledger_credit_selection = st.selectbox(
                "Credit Column",
                ledger_cols,
                index=get_safe_index(ledger_cols, 'ledger_credit_idx', 'Credit'),
                key='absa_ledger_credit_selector'
            )
            st.session_state.absa_saved_selections['ledger_credit_idx'] = ledger_cols.index(ledger_credit_selection)
            st.session_state.absa_match_settings['ledger_credit_col'] = ledger_credit_selection

        with col2:
            st.markdown("**Statement Columns**")

            statement_date_selection = st.selectbox(
                "Date Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_date_idx', 'Date'),
                key='absa_statement_date_selector'
            )
            st.session_state.absa_saved_selections['statement_date_idx'] = statement_cols.index(statement_date_selection)
            st.session_state.absa_match_settings['statement_date_col'] = statement_date_selection

            statement_ref_selection = st.selectbox(
                "Reference Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_ref_idx', 'Reference'),
                key='absa_statement_ref_selector'
            )
            st.session_state.absa_saved_selections['statement_ref_idx'] = statement_cols.index(statement_ref_selection)
            st.session_state.absa_match_settings['statement_ref_col'] = statement_ref_selection

            statement_amt_selection = st.selectbox(
                "Amount Column",
                statement_cols,
                index=get_safe_index(statement_cols, 'statement_amt_idx', 'Amount'),
                key='absa_statement_amt_selector'
            )
            st.session_state.absa_saved_selections['statement_amt_idx'] = statement_cols.index(statement_amt_selection)
            st.session_state.absa_match_settings['statement_amt_col'] = statement_amt_selection

    def render_matching_settings(self):
        """Render matching settings - Same as FNB"""
        st.markdown("---")
        st.subheader("🎯 Step 4: Matching Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Matching Criteria**")
            st.session_state.absa_match_settings['match_dates'] = st.checkbox(
                "Match by Dates", value=True, key='absa_match_dates'
            )
            if st.session_state.absa_match_settings['match_dates']:
                st.session_state.absa_match_settings['date_tolerance'] = st.checkbox(
                    "  ↳ Allow ±1 Day Tolerance", value=False, key='absa_date_tolerance',
                    help="When enabled, dates within 1 day difference will be considered matching"
                )
            else:
                st.session_state.absa_match_settings['date_tolerance'] = False

            st.session_state.absa_match_settings['match_references'] = st.checkbox(
                "Match by References", value=True, key='absa_match_refs'
            )
            st.session_state.absa_match_settings['match_amounts'] = st.checkbox(
                "Match by Amounts", value=True, key='absa_match_amts'
            )

        with col2:
            st.markdown("**Fuzzy Matching**")
            st.session_state.absa_match_settings['fuzzy_ref'] = st.checkbox(
                "Enable Fuzzy Reference Matching", value=True, key='absa_fuzzy'
            )
            st.session_state.absa_match_settings['similarity_ref'] = st.slider(
                "Similarity Threshold (%)", 50, 100, 85, key='absa_similarity'
            )

        with col3:
            st.markdown("**Amount Matching Mode**")
            amount_mode = st.radio(
                "Select Mode:",
                ["Use Both Debits and Credits", "Use Debits Only", "Use Credits Only"],
                key='absa_amount_mode'
            )

            st.session_state.absa_match_settings['use_debits_only'] = (amount_mode == "Use Debits Only")
            st.session_state.absa_match_settings['use_credits_only'] = (amount_mode == "Use Credits Only")
            st.session_state.absa_match_settings['use_both_debit_credit'] = (amount_mode == "Use Both Debits and Credits")

    def render_reconciliation_controls(self):
        """Render reconciliation execution controls"""
        st.markdown("---")
        st.subheader("⚡ Step 5: Execute Reconciliation")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("🚀 Start Reconciliation", type="primary", use_container_width=True, key="absa_start_recon"):
                self.run_reconciliation()

        with col2:
            if st.button("🔄 Reset", use_container_width=True, key="absa_reset"):
                st.session_state.absa_results = None
                st.rerun()

        with col3:
            if st.button("❌ Clear All", use_container_width=True, key="absa_clear_all"):
                st.session_state.absa_ledger = None
                st.session_state.absa_statement = None
                st.session_state.absa_results = None
                st.rerun()

    def run_reconciliation(self):
        """Execute reconciliation using FNB engine with ABSA data"""
        try:
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

            st.info("🚀 **ABSA Reconciliation Mode** - Using proven reconciliation engine")

            reconciler = GUIReconciliationEngine()

            progress_bar = st.progress(0)
            status_text = st.empty()

            results = reconciler.reconcile(
                st.session_state.absa_ledger,
                st.session_state.absa_statement,
                st.session_state.absa_match_settings,
                progress_bar,
                status_text
            )

            progress_bar.progress(100)
            status_text.success("✅ Reconciliation complete!")

            st.session_state.absa_results = results

            st.success(f"✅ **Reconciliation Complete!**\n\n"
                      f"- Perfect Matches: {results.get('perfect_match_count', 0)}\n"
                      f"- Fuzzy Matches: {results.get('fuzzy_match_count', 0)}\n"
                      f"- Total Matched: {results.get('total_matched', 0)}")

            st.balloons()

        except Exception as e:
            st.error(f"❌ Reconciliation failed: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())

    def render_results(self):
        """Render reconciliation results with ABSA-specific export"""
        st.markdown("---")
        st.subheader("📊 Reconciliation Results")

        results = st.session_state.absa_results

        total_matched = (results.get('perfect_match_count', 0) +
                        results.get('fuzzy_match_count', 0) +
                        results.get('foreign_credits_count', 0))
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("✅ Perfect Match", f"{results.get('perfect_match_count', 0):,}")
        with col2:
            st.metric("🔍 Fuzzy Match", f"{results.get('fuzzy_match_count', 0):,}")
        with col3:
            st.metric("📊 Total Matched", f"{total_matched:,}")
        with col4:
            st.metric("📋 Unmatched", f"{len(results.get('unmatched_ledger', [])) + len(results.get('unmatched_statement', [])):,}")

        st.markdown("---")
        
        # Export button section
        if 'absa_export_mode' not in st.session_state:
            st.session_state.absa_export_mode = False
        
        # Make export button prominent and always visible
        if not st.session_state.absa_export_mode:
            st.markdown("### 📥 Export Options")
            if st.button("📊 Export All to Excel", type="primary", use_container_width=True, key="absa_export_excel"):
                st.session_state.absa_export_mode = True
            st.markdown("---")
        
        # Show export UI when in export mode
        if st.session_state.get('absa_export_mode', False):
            self.export_to_excel(results)
            return  # Don't show tabs when in export mode
        
        # Simple tabs for results (only shown when not in export mode)
        tabs = st.tabs(["All Matched", "Unmatched Ledger", "Unmatched Statement"])
        
        with tabs[0]:
            if 'matched' in results and not results['matched'].empty:
                st.dataframe(results['matched'], use_container_width=True)
        
        with tabs[1]:
            if 'unmatched_ledger' in results and not results['unmatched_ledger'].empty:
                st.dataframe(results['unmatched_ledger'], use_container_width=True)
        
        with tabs[2]:
            if 'unmatched_statement' in results and not results['unmatched_statement'].empty:
                st.dataframe(results['unmatched_statement'], use_container_width=True)
    
    def export_to_excel(self, results):
        """Export all results to Excel with proper batch grouping (ABSA style)"""
        try:
            from io import BytesIO
            import pandas as pd
            from utils.column_selector import ColumnSelector
            from datetime import datetime

            # Get original dataframes to determine master column structure
            ledger = st.session_state.get('absa_ledger')
            statement = st.session_state.get('absa_statement')
            
            # Get all original columns (excluding normalized columns)
            ledger_cols = [col for col in ledger.columns if not col.startswith('_')] if ledger is not None else []
            stmt_cols = [col for col in statement.columns if not col.startswith('_')] if statement is not None else []
            
            # ========== COLUMN SELECTION UI ==========
            st.markdown("---")
            st.markdown("### 🎯 Customize Your Report")
            
            # Add Cancel button at the top
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Cancel", key="absa_cancel_export"):
                    st.session_state.absa_export_mode = False
            
            with st.expander("📋 Select Columns to Include in Export", expanded=True):
                selected_ledger, selected_statement = ColumnSelector.render_column_selector(
                    ledger_cols=ledger_cols,
                    statement_cols=stmt_cols,
                    workflow_name="absa"
                )
                
                # DEBUG: Show selection order
                if selected_ledger:
                    st.info(f"🔍 Ledger export order: {' → '.join(selected_ledger)}")
                if selected_statement:
                    st.info(f"🔍 Statement export order: {' → '.join(selected_statement)}")
                
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
            
            # Helper function to align row data to master columns preserving original dates
            def align_to_master(row_dict):
                """Align a row dictionary to master column structure preserving original date format"""
                aligned_row = []
                for col in master_columns:
                    value = row_dict.get(col, '')
                    
                    # Check if this is a date column and preserve original format
                    if 'Date' in col or 'date' in col:
                        # Try to get original date value (stored before conversion)
                        original_col = col.replace('Ledger_', '').replace('Statement_', '')
                        original_key = f'_original_{original_col}'
                        
                        # Check if original value exists in row_dict
                        if original_key in row_dict and pd.notna(row_dict[original_key]):
                            value = row_dict[original_key]
                        # If not in row_dict, keep the value as-is without conversion
                    
                    # Convert pandas NA/NaN to empty string
                    if pd.isna(value):
                        value = ''
                    aligned_row.append(value)
                return aligned_row
            
            # Create organized CSV with batch headers and separators (like GUI)
            csv_rows = []
            
            # Add header information
            csv_rows.append(['ABSA RECONCILIATION RESULTS'])
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
                ledger = st.session_state.get('absa_ledger')
                statement = st.session_state.get('absa_statement')
                
                # Get column settings
                settings = st.session_state.get('absa_match_settings', {})
                
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
                    file_name=f"ABSA_Reconciliation_Batched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.success("✅ Batched CSV report ready for download! Organized like GUI export with separators.")
            st.info("💡 After downloading, click **Cancel** above to return to results")

        except Exception as e:
            st.error(f"❌ Failed to create CSV report: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
