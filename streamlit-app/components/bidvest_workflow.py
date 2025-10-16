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

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_cleaner import clean_amount_column

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
            if st.button("🚀 Start Reconciliation", type="primary", use_container_width=True):
                self.run_reconciliation()

        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.bidvest_results = None
                st.rerun()

        with col3:
            if st.button("❌ Clear All", use_container_width=True):
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
        if st.button("📊 Export All Results to Excel", type="primary", use_container_width=True):
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

            # Then add ALL statement columns (prefixed with Statement_)
            for col in statement_display_cols:
                row_data[f'Statement_{col}'] = stmt_row[col]

            matched_data.append(row_data)

        return pd.DataFrame(matched_data)

    def export_to_excel(self, results):
        """Export all results to Excel"""
        try:
            from io import BytesIO

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([results['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # 100% Exact Matches
                if results['exact_matches']:
                    exact_data = self.build_matched_dataframe(
                        results['exact_matches'],
                        results['ledger'],
                        results['statement'],
                        st.session_state.bidvest_match_config
                    )
                    exact_data.to_excel(writer, sheet_name='100% Exact Matches', index=False)

                # Grouped Matches
                if results['grouped_matches']:
                    grouped_data = self.build_matched_dataframe(
                        results['grouped_matches'],
                        results['ledger'],
                        results['statement'],
                        st.session_state.bidvest_match_config
                    )
                    grouped_data.to_excel(writer, sheet_name='Grouped Matches', index=False)

                # Unmatched Ledger
                matched_ledger_idx = set([p[0] for p in results['exact_matches']] + [p[0] for p in results['grouped_matches']])
                unmatched_ledger = results['ledger'][~results['ledger'].index.isin(matched_ledger_idx)].copy()
                unmatched_ledger = unmatched_ledger.drop(columns=['__date', '__debit', '__credit'], errors='ignore')
                if not unmatched_ledger.empty:
                    unmatched_ledger.to_excel(writer, sheet_name='Unmatched Ledger', index=False)

                # Unmatched Statement
                matched_stmt_idx = set([p[1] for p in results['exact_matches']] + [p[1] for p in results['grouped_matches']])
                unmatched_statement = results['statement'][~results['statement'].index.isin(matched_stmt_idx)].copy()
                unmatched_statement = unmatched_statement.drop(columns=['__date', '__amt'], errors='ignore')
                if not unmatched_statement.empty:
                    unmatched_statement.to_excel(writer, sheet_name='Unmatched Statement', index=False)

            output.seek(0)

            st.download_button(
                label="📥 Download Complete Excel Report",
                data=output,
                file_name=f"Bidvest_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Excel report ready for download!")

        except Exception as e:
            st.error(f"❌ Failed to create Excel report: {str(e)}")
