"""
Bidvest Workflow Component - Exact Replica of GUI Logic
======================================================
Bidvest settlement reconciliation with two match types:
1. 100% Exact Matches: Date+1 rule with exact amount
2. Grouped Matches: Same date, same amount
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os
import re

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_cleaner import clean_amount_column  # type: ignore
from column_selector import ColumnSelector  # type: ignore

class BidvestWorkflow:
    """Bidvest Settlement Reconciliation Workflow with Exact GUI Logic"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'bidvest_ledger' not in st.session_state:
            st.session_state.bidvest_ledger = None
        if 'bidvest_statement' not in st.session_state:
            st.session_state.bidvest_statement = None
        if 'bidvest_results' not in st.session_state:
            st.session_state.bidvest_results = None
        if 'bidvest_match_config' not in st.session_state:
            st.session_state.bidvest_match_config = {
                'ledger_date': 'Date',
                'statement_date': 'Date',
                'ledger_debit': 'Debit',
                'ledger_credit': 'Credit',
                'statement_amt': 'Amount'
            }
        if 'bidvest_reference_extracted' not in st.session_state:
            st.session_state.bidvest_reference_extracted = False

    @staticmethod
    def extract_references(comment_text):
        """
        Extract RJ reference numbers from comment text.
        
        Examples:
        - "Ref #RJ49465028731. - 000089828" → "RJ49465028731"
        - "Ref RJ34570058702" → "RJ34570058702"
        - "RJ42325355002 cancelled" → "RJ42325355002"
        - Multiple refs: "Ref RJ48033113323  Payment ref 010348419,Ref RJ47777997623" 
          → "RJ48033113323, RJ47777997623"
        
        Returns: Comma-separated string of all RJ references found
        """
        if pd.isna(comment_text) or not isinstance(comment_text, str):
            return ""
        
        # Pattern to match RJ followed by 11 digits
        pattern = r'RJ\d{11}'
        
        # Find all matches
        matches = re.findall(pattern, comment_text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)
        
        # Return comma-separated string
        return ', '.join(unique_matches) if unique_matches else ""

    def render(self):
        """Render Bidvest workflow page"""

        # Header
        st.markdown("""
        <style>
        .gradient-header {
            background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
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
            color: #e9d5ff;
            margin: 0.5rem 0 0 0;
        }
        </style>

        <div class="gradient-header">
            <h1>💼 Bidvest Workflow</h1>
            <p>Settlement Reconciliation • Date+1 Exact Matches • Grouped Matches</p>
        </div>
        """, unsafe_allow_html=True)

        # Removed back button - workflows are now shown in tabs

        # Step 1: File Upload
        self.render_file_upload()

        # Step 2: Column Configuration (if files uploaded)
        if st.session_state.bidvest_ledger is not None and st.session_state.bidvest_statement is not None:
            self.render_column_configuration()

            # Step 3: Run Reconciliation
            self.render_reconciliation_controls()

        # Step 4: Display Results
        if st.session_state.bidvest_results is not None:
            self.render_results()

    def render_file_upload(self):
        """Render file upload section"""
        st.subheader("📁 Step 1: Import Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger File**")
            ledger_file = st.file_uploader("Upload Ledger (Excel/CSV)", type=['xlsx', 'xls', 'csv'], key='bidvest_ledger_upload')

            if ledger_file is not None:
                try:
                    if ledger_file.name.endswith('.csv'):
                        st.session_state.bidvest_ledger = pd.read_csv(ledger_file)
                    else:
                        st.session_state.bidvest_ledger = pd.read_excel(ledger_file)

                    st.success(f"✅ Loaded {len(st.session_state.bidvest_ledger)} ledger rows")
                    # Reset reference extraction flag when new file uploaded
                    st.session_state.bidvest_reference_extracted = False
                except Exception as e:
                    st.error(f"❌ Error loading ledger: {str(e)}")

        with col2:
            st.markdown("**Bank Statement File**")
            statement_file = st.file_uploader("Upload Statement (Excel/CSV)", type=['xlsx', 'xls', 'csv'], key='bidvest_statement_upload')

            if statement_file is not None:
                try:
                    if statement_file.name.endswith('.csv'):
                        st.session_state.bidvest_statement = pd.read_csv(statement_file)
                    else:
                        st.session_state.bidvest_statement = pd.read_excel(statement_file)

                    st.success(f"✅ Loaded {len(st.session_state.bidvest_statement)} statement rows")
                except Exception as e:
                    st.error(f"❌ Error loading statement: {str(e)}")

        # Reference Extraction Feature
        if st.session_state.bidvest_ledger is not None:
            self.render_reference_extraction()

    def render_reference_extraction(self):
        """Render reference extraction feature"""
        st.markdown("---")
        st.subheader("🔍 Extract References from Comments")
        
        ledger_cols = list(st.session_state.bidvest_ledger.columns)
        
        # Check if Comment column exists
        comment_col = None
        for col in ledger_cols:
            if col.strip().upper() == 'COMMENT' or col.strip().upper() == 'B':
                comment_col = col
                break
        
        if comment_col:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"📝 Found column: **{comment_col}** - This will be used to extract RJ references")
                
                # Show example of what will be extracted
                with st.expander("ℹ️ How Reference Extraction Works"):
                    st.markdown("""
                    **The system will extract RJ reference numbers from your Comment column:**
                    
                    **Examples:**
                    - `Ref #RJ49465028731. - 000089828` → **RJ49465028731**
                    - `Ref #RJ49475326175. - Senzpack logistics` → **RJ49475326175**
                    - `Cash  ZAR 100 paid out. Ref RJ34570058702` → **RJ34570058702**
                    - `RJ42325355002 cancelled` → **RJ42325355002**
                    - Multiple: `Ref RJ48033113323  Payment ref 010348419,Ref RJ47777997623` → **RJ48033113323, RJ47777997623**
                    
                    **A new column named "Reference" will be created with the extracted RJ numbers.**
                    """)
            
            with col2:
                if not st.session_state.bidvest_reference_extracted:
                    if st.button("✨ Extract References", type="primary", use_container_width=True, key="bidvest_extract_ref"):
                        self.execute_reference_extraction(comment_col)
                else:
                    st.success("✅ References extracted!")
                    if st.button("🔄 Re-extract", use_container_width=True, key="bidvest_reextract_ref"):
                        self.execute_reference_extraction(comment_col)
        else:
            st.warning("⚠️ No 'Comment' column found. Please ensure your ledger has a column named 'Comment' or 'B'.")
    
    def execute_reference_extraction(self, comment_col):
        """Execute reference extraction from comment column"""
        try:
            with st.spinner("🔄 Extracting RJ references..."):
                ledger = st.session_state.bidvest_ledger
                
                # Apply extraction to all rows
                ledger['Reference'] = ledger[comment_col].apply(self.extract_references)
                
                # Count how many references were extracted
                non_empty_refs = ledger['Reference'].apply(lambda x: len(x) > 0 if isinstance(x, str) else False).sum()
                
                st.session_state.bidvest_ledger = ledger
                st.session_state.bidvest_reference_extracted = True
                
                st.success(f"✅ Extracted references from {non_empty_refs:,} out of {len(ledger):,} rows!")
                
                # Show preview
                st.markdown("**Preview of extracted references:**")
                preview_df = ledger[[comment_col, 'Reference']].head(10)
                st.dataframe(preview_df, use_container_width=True)
                
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error extracting references: {str(e)}")

    def render_column_configuration(self):
        """Render column configuration"""
        st.markdown("---")
        st.subheader("⚙️ Step 2: Configure Columns")

        ledger_cols = list(st.session_state.bidvest_ledger.columns)
        statement_cols = list(st.session_state.bidvest_statement.columns)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Ledger Columns**")
            st.session_state.bidvest_match_config['ledger_date'] = st.selectbox(
                "Date Column", ledger_cols,
                index=ledger_cols.index('Date') if 'Date' in ledger_cols else 0,
                key='bidvest_ledger_date'
            )
            st.session_state.bidvest_match_config['ledger_debit'] = st.selectbox(
                "Debit Column", ledger_cols,
                index=ledger_cols.index('Debit') if 'Debit' in ledger_cols else 0,
                key='bidvest_ledger_debit'
            )
            st.session_state.bidvest_match_config['ledger_credit'] = st.selectbox(
                "Credit Column", ledger_cols,
                index=ledger_cols.index('Credit') if 'Credit' in ledger_cols else 0,
                key='bidvest_ledger_credit'
            )

        with col2:
            st.markdown("**Statement Columns**")
            st.session_state.bidvest_match_config['statement_date'] = st.selectbox(
                "Date Column", statement_cols,
                index=statement_cols.index('Date') if 'Date' in statement_cols else 0,
                key='bidvest_statement_date'
            )
            st.session_state.bidvest_match_config['statement_amt'] = st.selectbox(
                "Amount Column", statement_cols,
                index=statement_cols.index('Amount') if 'Amount' in statement_cols else 0,
                key='bidvest_statement_amt'
            )

        # Show matching rules
        with st.expander("ℹ️ How Bidvest Matching Works"):
            st.markdown("""
            **Bidvest uses a two-tier matching system:**

            **1. 100% Exact Matches (Date+1 Rule):**
            - Ledger Date + 1 day = Statement Date
            - Exact amount match
            - Debits match positive statement amounts
            - Credits match negative statement amounts

            **2. Grouped Matches (Same Date, Same Amount):**
            - For unmatched transactions only
            - Same date on both sides
            - Same amount (absolute value)
            - Does not require Date+1 rule

            **Example:**
            - Ledger: Date=2024-01-15, Debit=1000
            - Statement: Date=2024-01-16, Amount=1000
            - Result: **100% Exact Match** ✅
            """)

    def render_reconciliation_controls(self):
        """Render reconciliation execution controls"""
        st.markdown("---")
        st.subheader("⚡ Step 3: Execute Reconciliation")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("🚀 Start Reconciliation", type="primary", use_container_width=True, key="bidvest_start_recon"):
                self.run_reconciliation()

        with col2:
            if st.button("🔄 Reset", use_container_width=True, key="bidvest_reset"):
                st.session_state.bidvest_results = None
                st.rerun()

        with col3:
            if st.button("❌ Clear All", use_container_width=True, key="bidvest_clear_all"):
                st.session_state.bidvest_ledger = None
                st.session_state.bidvest_statement = None
                st.session_state.bidvest_results = None
                st.rerun()

    def run_reconciliation(self):
        """Execute Bidvest reconciliation with exact GUI algorithm"""
        try:
            with st.spinner("🔄 Running Bidvest reconciliation..."):
                import time
                start_time = time.time()

                cfg = st.session_state.bidvest_match_config
                ledger = st.session_state.bidvest_ledger.copy()
                statement = st.session_state.bidvest_statement.copy()

                # Get column names
                l_date_col = cfg['ledger_date']
                s_date_col = cfg['statement_date']
                l_debit_col = cfg['ledger_debit']
                l_credit_col = cfg['ledger_credit']
                s_amt_col = cfg['statement_amt']

                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Parse dates (20%)
                status_text.text("📅 Parsing dates...")
                progress_bar.progress(0.2)

                ledger['__date'] = pd.to_datetime(ledger[l_date_col], errors='coerce')
                statement['__date'] = pd.to_datetime(statement[s_date_col], errors='coerce')

                # Step 2: Parse amounts (30%)
                status_text.text("💰 Parsing amounts...")
                progress_bar.progress(0.3)

                ledger['__debit'] = clean_amount_column(ledger[l_debit_col], l_debit_col)
                ledger['__credit'] = clean_amount_column(ledger[l_credit_col], l_credit_col)
                statement['__amt'] = clean_amount_column(statement[s_amt_col], s_amt_col)

                # Step 3: Build fast indexes (40%)
                status_text.text("📇 Building lookup indexes...")
                progress_bar.progress(0.4)

                stmt_debit_idx = defaultdict(list)  # For positive amounts (matching debits)
                stmt_credit_idx = defaultdict(list)  # For negative amounts (matching credits)

                for si, srow in statement.iterrows():
                    stmt_amt = srow['__amt']
                    stmt_date = srow['__date']

                    if pd.isnull(stmt_date) or pd.isnull(stmt_amt):
                        continue

                    key = (stmt_date.date(), round(abs(stmt_amt), 2))

                    if stmt_amt > 0:
                        stmt_debit_idx[key].append(si)
                    else:
                        stmt_credit_idx[key].append(si)

                # Step 4: Match debits (60%)
                status_text.text("🔍 Matching debit transactions...")
                progress_bar.progress(0.6)

                matched_pairs = []
                matched_statement = set()

                # Match debits (Date+1 rule)
                for i, lrow in ledger.iterrows():
                    ldate = lrow['__date']
                    ldebit = lrow['__debit']

                    if pd.isnull(ldate) or pd.isnull(ldebit) or ldebit <= 0:
                        continue

                    # Expected statement date (ledger date + 1 day)
                    sdate = ldate + timedelta(days=1)
                    key = (sdate.date(), round(ldebit, 2))

                    if key in stmt_debit_idx:
                        for si in stmt_debit_idx[key]:
                            if si in matched_statement:
                                continue

                            stmt_amt = statement.at[si, '__amt']
                            stmt_date = statement.at[si, '__date']

                            # Match if statement date is 1 day after ledger and amounts match exactly
                            if (not pd.isnull(stmt_date) and
                                (stmt_date.date() - ldate.date()).days == 1 and
                                round(ldebit, 2) == round(stmt_amt, 2) and stmt_amt > 0):

                                matched_pairs.append((i, si, 'debit'))
                                matched_statement.add(si)
                                break

                # Step 5: Match credits (70%)
                status_text.text("🔍 Matching credit transactions...")
                progress_bar.progress(0.7)

                # Match credits (Date+1 rule)
                for i, lrow in ledger.iterrows():
                    ldate = lrow['__date']
                    lcredit = lrow['__credit']

                    if pd.isnull(ldate) or pd.isnull(lcredit) or lcredit <= 0:
                        continue

                    # Expected statement date (ledger date + 1 day)
                    sdate = ldate + timedelta(days=1)
                    key = (sdate.date(), round(lcredit, 2))

                    if key in stmt_credit_idx:
                        for si in stmt_credit_idx[key]:
                            if si in matched_statement:
                                continue

                            stmt_amt = statement.at[si, '__amt']
                            stmt_date = statement.at[si, '__date']

                            # Match if statement date is 1 day after ledger and amounts match (credit = negative)
                            if (not pd.isnull(stmt_date) and
                                (stmt_date.date() - ldate.date()).days == 1 and
                                round(lcredit, 2) == round(abs(stmt_amt), 2) and stmt_amt < 0):

                                matched_pairs.append((i, si, 'credit'))
                                matched_statement.add(si)
                                break

                # Step 6: Group unmatched transactions (80%)
                status_text.text("📦 Grouping unmatched transactions...")
                progress_bar.progress(0.8)

                matched_ledger_idx = {pair[0] for pair in matched_pairs}
                matched_stmt_idx = {pair[1] for pair in matched_pairs}

                unmatched_ledger = ledger[~ledger.index.isin(matched_ledger_idx)]
                unmatched_statement = statement[~statement.index.isin(matched_stmt_idx)]

                # Group by date and amount
                ledger_groups = defaultdict(list)
                stmt_groups = defaultdict(list)

                # Group unmatched ledger entries
                for idx, row in unmatched_ledger.iterrows():
                    if pd.isnull(row['__date']):
                        continue

                    # Group debits
                    if not pd.isnull(row['__debit']) and row['__debit'] > 0:
                        date_key = row['__date'].date()
                        key = (date_key, round(row['__debit'], 2), 'debit')
                        ledger_groups[key].append(idx)

                    # Group credits
                    if not pd.isnull(row['__credit']) and row['__credit'] > 0:
                        date_key = row['__date'].date()
                        key = (date_key, round(row['__credit'], 2), 'credit')
                        ledger_groups[key].append(idx)

                # Group unmatched statement entries
                for idx, row in unmatched_statement.iterrows():
                    if pd.isnull(row['__date']) or pd.isnull(row['__amt']):
                        continue

                    date_key = row['__date'].date()
                    amt_type = 'debit' if row['__amt'] > 0 else 'credit'
                    key = (date_key, round(abs(row['__amt']), 2), amt_type)
                    stmt_groups[key].append(idx)

                # Find grouped matches (same date, same amount)
                grouped_matches = []
                for key in ledger_groups:
                    if key in stmt_groups and len(ledger_groups[key]) > 0 and len(stmt_groups[key]) > 0:
                        # Match groups (one-to-one within groups)
                        for l_idx in ledger_groups[key]:
                            for s_idx in stmt_groups[key]:
                                if s_idx not in matched_statement:
                                    grouped_matches.append((l_idx, s_idx, f'group_{key[2]}'))
                                    matched_statement.add(s_idx)
                                    break

                # Step 7: Finalize results (100%)
                status_text.text("✅ Finalizing results...")
                progress_bar.progress(1.0)

                total_time = time.time() - start_time

                # Store results
                results = {
                    'exact_matches': [(pair[0], pair[1]) for pair in matched_pairs],
                    'grouped_matches': [(pair[0], pair[1]) for pair in grouped_matches],
                    'ledger': ledger,
                    'statement': statement,
                    'summary': {
                        'total_ledger': len(ledger),
                        'total_statement': len(statement),
                        'exact_matches': len(matched_pairs),
                        'grouped_matches': len(grouped_matches),
                        'unmatched_ledger': len(ledger) - len(matched_pairs) - len(grouped_matches),
                        'unmatched_statement': len(statement) - len(matched_pairs) - len(grouped_matches),
                        'processing_time': total_time
                    }
                }

                st.session_state.bidvest_results = results

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                # Show success message
                st.success(f"""
                ✅ **Reconciliation Complete!**

                - 100% Exact Matches: {results['summary']['exact_matches']}
                - Grouped Matches: {results['summary']['grouped_matches']}
                - Unmatched Ledger: {results['summary']['unmatched_ledger']}
                - Unmatched Statement: {results['summary']['unmatched_statement']}
                - Processing Time: {total_time:.2f}s
                """)

        except Exception as e:
            st.error(f"❌ Reconciliation failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    def render_results(self):
        """Render reconciliation results"""
        st.markdown("---")
        st.subheader("📊 Reconciliation Results")

        results = st.session_state.bidvest_results
        summary = results['summary']

        # Summary cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("100% Exact Matches", f"{summary['exact_matches']:,}")
        with col2:
            st.metric("Grouped Matches", f"{summary['grouped_matches']:,}")
        with col3:
            st.metric("Unmatched Ledger", f"{summary['unmatched_ledger']:,}")
        with col4:
            st.metric("Unmatched Statement", f"{summary['unmatched_statement']:,}")

        # Tabbed results view
        tab1, tab2, tab3, tab4 = st.tabs([
            "✅ 100% Exact Matches",
            "🔄 Grouped Matches",
            "📋 Unmatched Ledger",
            "🏦 Unmatched Statement"
        ])

        with tab1:
            if results['exact_matches']:
                exact_data = self.build_matched_dataframe(
                    results['exact_matches'],
                    results['ledger'],
                    results['statement'],
                    st.session_state.bidvest_match_config
                )
                st.dataframe(exact_data, use_container_width=True)
                st.download_button(
                    "📥 Download 100% Exact Matches",
                    exact_data.to_csv(index=False),
                    "bidvest_exact_matches.csv",
                    "text/csv",
                    key='download_exact'
                )
            else:
                st.info("No 100% exact matches found")

        with tab2:
            if results['grouped_matches']:
                grouped_data = self.build_matched_dataframe(
                    results['grouped_matches'],
                    results['ledger'],
                    results['statement'],
                    st.session_state.bidvest_match_config
                )
                st.dataframe(grouped_data, use_container_width=True)
                st.download_button(
                    "📥 Download Grouped Matches",
                    grouped_data.to_csv(index=False),
                    "bidvest_grouped_matches.csv",
                    "text/csv",
                    key='download_grouped'
                )
            else:
                st.info("No grouped matches found")

        with tab3:
            matched_ledger_idx = set([p[0] for p in results['exact_matches']] + [p[0] for p in results['grouped_matches']])
            unmatched_ledger = results['ledger'][~results['ledger'].index.isin(matched_ledger_idx)].copy()
            # Remove helper columns
            unmatched_ledger = unmatched_ledger.drop(columns=['__date', '__debit', '__credit'], errors='ignore')

            if not unmatched_ledger.empty:
                st.dataframe(unmatched_ledger, use_container_width=True)
                st.download_button(
                    "📥 Download Unmatched Ledger",
                    unmatched_ledger.to_csv(index=False),
                    "bidvest_unmatched_ledger.csv",
                    "text/csv",
                    key='download_unmatched_ledger'
                )
            else:
                st.info("No unmatched ledger items")

        with tab4:
            matched_stmt_idx = set([p[1] for p in results['exact_matches']] + [p[1] for p in results['grouped_matches']])
            unmatched_statement = results['statement'][~results['statement'].index.isin(matched_stmt_idx)].copy()
            # Remove helper columns
            unmatched_statement = unmatched_statement.drop(columns=['__date', '__amt'], errors='ignore')

            if not unmatched_statement.empty:
                st.dataframe(unmatched_statement, use_container_width=True)
                st.download_button(
                    "📥 Download Unmatched Statement",
                    unmatched_statement.to_csv(index=False),
                    "bidvest_unmatched_statement.csv",
                    "text/csv",
                    key='download_unmatched_stmt'
                )
            else:
                st.info("No unmatched statement items")

        # Export all button
        st.markdown("---")
        
        # Initialize export mode in session state
        if 'bidvest_export_mode' not in st.session_state:
            st.session_state.bidvest_export_mode = False
        
        # Button to enter export mode
        if not st.session_state.bidvest_export_mode:
            if st.button("📊 Export All Results to Excel", type="primary", use_container_width=True, key="bidvest_export_excel"):
                st.session_state.bidvest_export_mode = True
                st.rerun()
        
        # Show export UI when in export mode
        if st.session_state.bidvest_export_mode:
            self.export_to_excel(results)

    def build_matched_dataframe(self, matches, ledger, statement, config):
        """Build a dataframe from matched pairs with ALL columns side-by-side"""
        matched_data = []

        # Get all original columns (excluding helper columns)
        ledger_display_cols = [col for col in ledger.columns if not col.startswith('__')]
        statement_display_cols = [col for col in statement.columns if not col.startswith('__')]

        for l_idx, s_idx in matches:
            ledger_row = ledger.loc[l_idx]
            stmt_row = statement.loc[s_idx]

            # Build row with ALL ledger columns first (prefixed with Ledger_)
            row_data = {}
            for col in ledger_display_cols:
                row_data[f'Ledger_{col}'] = ledger_row[col]

            # Add 2 empty separator columns
            row_data[''] = ''
            row_data[' '] = ''

            # Then add ALL statement columns (prefixed with Statement_)
            for col in statement_display_cols:
                row_data[f'Statement_{col}'] = stmt_row[col]

            matched_data.append(row_data)

        return pd.DataFrame(matched_data)
    
    def _align_to_master_columns(self, df, master_columns):
        """Align dataframe columns to master column structure"""
        # Create a new dataframe with master columns
        aligned_data = []
        for _, row in df.iterrows():
            aligned_row = {}
            for col in master_columns:
                aligned_row[col] = row.get(col, '')
            aligned_data.append(aligned_row)
        return pd.DataFrame(aligned_data)
    
    def _build_filtered_matched_dataframe(self, matches, ledger, statement, selected_ledger_cols, selected_statement_cols, master_columns):
        """Build dataframe with ONLY selected columns"""
        matched_data = []

        for l_idx, s_idx in matches:
            ledger_row = ledger.loc[l_idx]
            stmt_row = statement.loc[s_idx]

            # Build row with ONLY selected columns
            row_data = {}
            
            # Initialize all master columns as empty
            for col in master_columns:
                row_data[col] = ''
            
            # Add ONLY selected ledger columns
            for col in selected_ledger_cols:
                if col in ledger_row.index:
                    row_data[f'Ledger_{col}'] = ledger_row[col]
            
            # Separator columns are already in master_columns
            
            # Add ONLY selected statement columns
            for col in selected_statement_cols:
                if col in stmt_row.index:
                    row_data[f'Statement_{col}'] = stmt_row[col]
            
            matched_data.append(row_data)

        return pd.DataFrame(matched_data, columns=master_columns)

    def export_to_excel(self, results):
        """Export all results to Excel with consistent column alignment"""
        try:
            from io import BytesIO

            # Get original dataframes to determine master column structure
            ledger = results['ledger']
            statement = results['statement']
            
            # Get all original columns (excluding helper columns)
            ledger_cols = [col for col in ledger.columns if not col.startswith('__')]
            stmt_cols = [col for col in statement.columns if not col.startswith('__')]
            
            # ========== COLUMN SELECTION UI ==========
            st.markdown("---")
            st.markdown("### 🎯 Customize Your Report")
            
            # Add Cancel button at the top
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Cancel", key="bidvest_cancel_export"):
                    st.session_state.bidvest_export_mode = False
                    st.rerun()
            
            with st.expander("📋 Select Columns to Include in Export", expanded=True):
                selected_ledger, selected_statement = ColumnSelector.render_column_selector(
                    ledger_cols=ledger_cols,
                    statement_cols=stmt_cols,
                    workflow_name="bidvest"
                )
                
                # Validate - at least one column must be selected
                if not selected_ledger and not selected_statement:
                    st.error("❌ Please select at least one column to export")
                    st.info("💡 Click **Cancel** above to go back")
                    return
                
                st.success(f"✅ Ready to export: **{len(selected_ledger)}** ledger columns + **{len(selected_statement)}** statement columns")
            
            # Define MASTER COLUMN STRUCTURE using SELECTED columns only
            # Format: Selected_Ledger_cols + [EMPTY, EMPTY] + Selected_Statement_cols
            master_columns = ColumnSelector.build_master_columns(
                selected_ledger,
                selected_statement
            )

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([results['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # 100% Exact Matches - with ONLY selected columns
                if results['exact_matches']:
                    exact_data = self._build_filtered_matched_dataframe(
                        results['exact_matches'],
                        results['ledger'],
                        results['statement'],
                        selected_ledger,
                        selected_statement,
                        master_columns
                    )
                    exact_data.to_excel(writer, sheet_name='100% Exact Matches', index=False)

                # Grouped Matches - with ONLY selected columns
                if results['grouped_matches']:
                    grouped_data = self._build_filtered_matched_dataframe(
                        results['grouped_matches'],
                        results['ledger'],
                        results['statement'],
                        selected_ledger,
                        selected_statement,
                        master_columns
                    )
                    grouped_data.to_excel(writer, sheet_name='Grouped Matches', index=False)

                # Unmatched Items (Ledger and Statement side-by-side) - with ONLY selected columns
                matched_ledger_idx = set([p[0] for p in results['exact_matches']] + [p[0] for p in results['grouped_matches']])
                unmatched_ledger = results['ledger'][~results['ledger'].index.isin(matched_ledger_idx)].copy()
                unmatched_ledger = unmatched_ledger.drop(columns=['__date', '__debit', '__credit'], errors='ignore')
                
                matched_stmt_idx = set([p[1] for p in results['exact_matches']] + [p[1] for p in results['grouped_matches']])
                unmatched_statement = results['statement'][~results['statement'].index.isin(matched_stmt_idx)].copy()
                unmatched_statement = unmatched_statement.drop(columns=['__date', '__amt'], errors='ignore')
                
                # Build side-by-side unmatched sheet with ONLY selected columns
                if not unmatched_ledger.empty or not unmatched_statement.empty:
                    max_rows = max(len(unmatched_ledger), len(unmatched_statement))
                    unmatched_data = []
                    
                    for i in range(max_rows):
                        row_data = {}
                        
                        # Initialize with all master columns as empty
                        for col in master_columns:
                            row_data[col] = ''
                        
                        # Add ONLY selected ledger columns
                        if i < len(unmatched_ledger):
                            ledger_row = unmatched_ledger.iloc[i]
                            for col in selected_ledger:
                                if col in ledger_row.index:
                                    row_data[f'Ledger_{col}'] = ledger_row[col]
                        
                        # Add ONLY selected statement columns
                        if i < len(unmatched_statement):
                            stmt_row = unmatched_statement.iloc[i]
                            for col in selected_statement:
                                if col in stmt_row.index:
                                    row_data[f'Statement_{col}'] = stmt_row[col]
                        
                        unmatched_data.append(row_data)
                    
                    unmatched_df = pd.DataFrame(unmatched_data, columns=master_columns)
                    unmatched_df.to_excel(writer, sheet_name='Unmatched Items', index=False)

            output.seek(0)

            st.markdown("---")
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                download_clicked = st.download_button(
                    label="📥 Download Complete Excel Report",
                    data=output,
                    file_name=f"Bidvest_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            st.success("✅ Excel report ready for download!")
            st.info("💡 After downloading, click **Cancel** above to return to results")

        except Exception as e:
            st.error(f"❌ Failed to create Excel report: {str(e)}")
