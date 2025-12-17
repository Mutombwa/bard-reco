"""
Fix Ledger Workflow Component - Enrich Palladium Ledger with TX Report References
==================================================================================
Fast exact-match workflow to add Source Payment Reference from TX Report to Palladium Ledger.

Process:
1. Upload Palladium Ledger (with Comment column containing CSH references)
2. Upload TX Report (with Trans Ref and Source Payment Reference)
3. Extract TX_REF from Comment column (e.g., "Ref CSH850038838" -> "CSH850038838")
4. Match TX_REF with Trans Ref from TX Report (exact match - ultra fast)
5. Add Source Payment Reference to matched rows
6. Download enriched Palladium Ledger
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import re
import io

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from file_loader import load_uploaded_file, get_dataframe_info  # type: ignore


class FixLedgerWorkflow:
    """Fix Ledger Workflow - Enrich Palladium Ledger with TX Report Source Payment Reference"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'fix_ledger_palladium' not in st.session_state:
            st.session_state.fix_ledger_palladium = None
        if 'fix_ledger_tx_report' not in st.session_state:
            st.session_state.fix_ledger_tx_report = None
        if 'fix_ledger_results' not in st.session_state:
            st.session_state.fix_ledger_results = None
        if 'fix_ledger_enriched' not in st.session_state:
            st.session_state.fix_ledger_enriched = None
        if 'fix_ledger_settings' not in st.session_state:
            st.session_state.fix_ledger_settings = {
                'comment_col': 'Comment',
                'trans_ref_col': 'Trans Ref',
                'source_payment_ref_col': 'Source Payment Reference'
            }

    def render(self):
        """Render Fix Ledger workflow page"""

        # Header
        st.markdown("""
        <style>
        .fix-ledger-header {
            background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .fix-ledger-header h1 {
            color: white;
            margin: 0;
        }
        .fix-ledger-header p {
            color: #ede9fe;
            margin: 0.5rem 0 0 0;
        }
        .match-stats {
            background: linear-gradient(135deg, #059669 0%, #34d399 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        }
        .unmatch-stats {
            background: linear-gradient(135deg, #dc2626 0%, #f87171 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        }
        </style>

        <div class="fix-ledger-header">
            <h1>🔧 Fix Ledger Workflow</h1>
            <p>Enrich Palladium Ledger with Source Payment Reference from TX Report • Fast Exact Matching</p>
        </div>
        """, unsafe_allow_html=True)

        # Step 1: File Upload
        self.render_file_upload()

        # Step 2: Column Configuration (if files uploaded)
        if st.session_state.fix_ledger_palladium is not None and st.session_state.fix_ledger_tx_report is not None:
            self.render_column_config()

            # Step 3: Preview extracted references
            self.render_reference_preview()

            # Step 4: Run matching
            self.render_matching_controls()

        # Step 5: Display Results
        if st.session_state.fix_ledger_results is not None:
            self.render_results()

    def render_file_upload(self):
        """Render file upload section"""

        st.subheader("📁 Step 1: Upload Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📗 Palladium Ledger**")
            st.caption("Contains Comment column with CSH references")

            # Show existing data status
            if st.session_state.fix_ledger_palladium is not None:
                st.success(f"✅ **Loaded:** {len(st.session_state.fix_ledger_palladium):,} rows × {len(st.session_state.fix_ledger_palladium.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.fix_ledger_palladium.columns))
                with st.expander("👁️ Preview Data (first 5 rows)"):
                    st.dataframe(st.session_state.fix_ledger_palladium.head(), use_container_width=True)

            palladium_file = st.file_uploader(
                "Upload Palladium Ledger",
                type=['xlsx', 'xls', 'csv'],
                key='fix_ledger_palladium_upload',
                help="Excel or CSV file with Comment column"
            )

            if palladium_file is not None:
                palladium_df, is_new = load_uploaded_file(
                    palladium_file,
                    session_key='fix_ledger_palladium',
                    hash_key='fix_ledger_palladium_hash',
                    show_progress=True
                )

                if is_new:
                    # Reset results when new file is loaded
                    st.session_state.fix_ledger_results = None
                    st.session_state.fix_ledger_enriched = None
                    st.success(f"✅ Palladium Ledger loaded: {get_dataframe_info(palladium_df)}")
                    st.rerun()

        with col2:
            st.markdown("**📘 TX Report**")
            st.caption("Contains Trans Ref and Source Payment Reference columns")

            # Show existing data status
            if st.session_state.fix_ledger_tx_report is not None:
                st.success(f"✅ **Loaded:** {len(st.session_state.fix_ledger_tx_report):,} rows × {len(st.session_state.fix_ledger_tx_report.columns)} columns")
                with st.expander("📋 View Columns"):
                    st.code(", ".join(st.session_state.fix_ledger_tx_report.columns))
                with st.expander("👁️ Preview Data (first 5 rows)"):
                    st.dataframe(st.session_state.fix_ledger_tx_report.head(), use_container_width=True)

            tx_file = st.file_uploader(
                "Upload TX Report",
                type=['xlsx', 'xls', 'csv'],
                key='fix_ledger_tx_upload',
                help="Excel or CSV file with Trans Ref and Source Payment Reference"
            )

            if tx_file is not None:
                tx_df, is_new = load_uploaded_file(
                    tx_file,
                    session_key='fix_ledger_tx_report',
                    hash_key='fix_ledger_tx_hash',
                    show_progress=True
                )

                if is_new:
                    # Reset results when new file is loaded
                    st.session_state.fix_ledger_results = None
                    st.session_state.fix_ledger_enriched = None
                    st.success(f"✅ TX Report loaded: {get_dataframe_info(tx_df)}")
                    st.rerun()

        # Clear data buttons
        if st.session_state.fix_ledger_palladium is not None or st.session_state.fix_ledger_tx_report is not None:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🗑️ Clear Palladium", use_container_width=True):
                    st.session_state.fix_ledger_palladium = None
                    st.session_state.fix_ledger_results = None
                    st.session_state.fix_ledger_enriched = None
                    if 'fix_ledger_palladium_hash' in st.session_state:
                        del st.session_state.fix_ledger_palladium_hash
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear TX Report", use_container_width=True):
                    st.session_state.fix_ledger_tx_report = None
                    st.session_state.fix_ledger_results = None
                    st.session_state.fix_ledger_enriched = None
                    if 'fix_ledger_tx_hash' in st.session_state:
                        del st.session_state.fix_ledger_tx_hash
                    st.rerun()

    def render_column_config(self):
        """Render column configuration section"""

        st.markdown("---")
        st.subheader("⚙️ Step 2: Configure Columns")

        palladium_df = st.session_state.fix_ledger_palladium
        tx_df = st.session_state.fix_ledger_tx_report
        settings = st.session_state.fix_ledger_settings

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Palladium Ledger Columns**")

            # Auto-detect Comment column
            comment_cols = [c for c in palladium_df.columns if 'comment' in c.lower()]
            default_comment = comment_cols[0] if comment_cols else palladium_df.columns[0]

            comment_col = st.selectbox(
                "Comment Column (contains references)",
                options=palladium_df.columns.tolist(),
                index=palladium_df.columns.tolist().index(default_comment) if default_comment in palladium_df.columns else 0,
                key='fix_ledger_comment_col',
                help="Column containing CSH references like 'Ref CSH850038838'"
            )
            settings['comment_col'] = comment_col

        with col2:
            st.markdown("**TX Report Columns**")

            # Auto-detect Trans Ref column
            trans_ref_cols = [c for c in tx_df.columns if 'trans' in c.lower() and 'ref' in c.lower()]
            default_trans_ref = trans_ref_cols[0] if trans_ref_cols else tx_df.columns[0]

            trans_ref_col = st.selectbox(
                "Trans Ref Column",
                options=tx_df.columns.tolist(),
                index=tx_df.columns.tolist().index(default_trans_ref) if default_trans_ref in tx_df.columns else 0,
                key='fix_ledger_trans_ref_col',
                help="Column containing transaction references like 'CSH850038838'"
            )
            settings['trans_ref_col'] = trans_ref_col

            # Auto-detect Source Payment Reference column
            payment_ref_cols = [c for c in tx_df.columns if 'source' in c.lower() or 'payment' in c.lower()]
            default_payment_ref = payment_ref_cols[0] if payment_ref_cols else (tx_df.columns[2] if len(tx_df.columns) > 2 else tx_df.columns[-1])

            source_payment_col = st.selectbox(
                "Source Payment Reference Column",
                options=tx_df.columns.tolist(),
                index=tx_df.columns.tolist().index(default_payment_ref) if default_payment_ref in tx_df.columns else 0,
                key='fix_ledger_source_payment_col',
                help="Column containing source payment reference to add to Palladium Ledger"
            )
            settings['source_payment_ref_col'] = source_payment_col

    def extract_reference(self, comment: str) -> str:
        """
        Extract CSH/ECO/INN reference from Comment column.

        Examples:
        - "Ref CSH850038838" -> "CSH850038838"
        - "Reversal: (#Ref CSH294940644)" -> "CSH294940644"
        - "12/15/2025 Ref CSH172860609" -> "CSH172860609"

        Returns empty string if no reference found.
        """
        if pd.isna(comment) or not isinstance(comment, str):
            return ''

        # Pattern to match CSH, ECO, or INN followed by digits
        # Handles various formats: "Ref CSH...", "#Ref CSH...", "CSH..."
        pattern = r'(CSH\d+|ECO\d+|INN\d+)'

        match = re.search(pattern, comment, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        return ''

    def render_reference_preview(self):
        """Preview extracted references before matching"""

        st.markdown("---")
        st.subheader("👁️ Step 3: Preview Extracted References")

        palladium_df = st.session_state.fix_ledger_palladium.copy()
        settings = st.session_state.fix_ledger_settings
        comment_col = settings['comment_col']

        # Extract references
        palladium_df['TX_REF'] = palladium_df[comment_col].apply(self.extract_reference)

        # Show extraction statistics
        total_rows = len(palladium_df)
        extracted_count = (palladium_df['TX_REF'] != '').sum()
        not_extracted = total_rows - extracted_count

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Rows", f"{total_rows:,}")
        with col2:
            st.metric("✅ References Extracted", f"{extracted_count:,}", delta=f"{extracted_count/total_rows*100:.1f}%")
        with col3:
            st.metric("❌ No Reference Found", f"{not_extracted:,}")

        # Show sample extractions
        with st.expander("🔍 View Sample Extractions (first 20 rows)", expanded=True):
            preview_df = palladium_df[[comment_col, 'TX_REF']].head(20).copy()
            preview_df.columns = ['Original Comment', 'Extracted TX_REF']
            st.dataframe(preview_df, use_container_width=True)

        # Show rows without references
        if not_extracted > 0:
            with st.expander(f"⚠️ Rows Without References ({not_extracted} rows)"):
                no_ref_df = palladium_df[palladium_df['TX_REF'] == ''][[comment_col]].head(20)
                st.dataframe(no_ref_df, use_container_width=True)
                if not_extracted > 20:
                    st.caption(f"Showing first 20 of {not_extracted} rows without references")

    def run_matching(self) -> dict:
        """
        Run the matching process - Ultra fast using dictionary lookup.

        Returns dict with:
        - enriched_df: Palladium Ledger with TX_REF and Source Payment Reference added
        - matched_count: Number of matched rows
        - unmatched_count: Number of unmatched rows
        - matched_df: DataFrame of matched rows
        - unmatched_df: DataFrame of unmatched rows
        """
        palladium_df = st.session_state.fix_ledger_palladium.copy()
        tx_df = st.session_state.fix_ledger_tx_report.copy()
        settings = st.session_state.fix_ledger_settings

        comment_col = settings['comment_col']
        trans_ref_col = settings['trans_ref_col']
        source_payment_col = settings['source_payment_ref_col']

        # Step 1: Extract TX_REF from Comment column (vectorized)
        palladium_df['TX_REF'] = palladium_df[comment_col].apply(self.extract_reference)

        # Step 2: Create lookup dictionary from TX Report (O(1) lookups)
        # Handle potential duplicates by keeping first occurrence
        tx_lookup = {}
        for _, row in tx_df.iterrows():
            ref = str(row[trans_ref_col]).strip().upper() if pd.notna(row[trans_ref_col]) else ''
            if ref and ref not in tx_lookup:
                tx_lookup[ref] = row[source_payment_col] if pd.notna(row[source_payment_col]) else ''

        # Step 3: Map Source Payment Reference using lookup (vectorized)
        palladium_df['Source Payment Reference'] = palladium_df['TX_REF'].apply(
            lambda x: tx_lookup.get(x.upper(), '') if x else ''
        )

        # Step 4: Calculate statistics
        has_ref = palladium_df['TX_REF'] != ''
        has_match = palladium_df['Source Payment Reference'] != ''

        matched_df = palladium_df[has_ref & has_match].copy()
        unmatched_df = palladium_df[has_ref & ~has_match].copy()
        no_ref_df = palladium_df[~has_ref].copy()

        results = {
            'enriched_df': palladium_df,
            'matched_count': len(matched_df),
            'unmatched_count': len(unmatched_df),
            'no_ref_count': len(no_ref_df),
            'total_count': len(palladium_df),
            'matched_df': matched_df,
            'unmatched_df': unmatched_df,
            'no_ref_df': no_ref_df,
            'tx_lookup_size': len(tx_lookup)
        }

        return results

    def render_matching_controls(self):
        """Render matching controls and run button"""

        st.markdown("---")
        st.subheader("🚀 Step 4: Run Matching")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔗 Match & Enrich Ledger", use_container_width=True, type="primary"):
                with st.spinner("⚡ Matching transactions..."):
                    start_time = datetime.now()
                    results = self.run_matching()
                    end_time = datetime.now()

                    processing_time = (end_time - start_time).total_seconds()
                    results['processing_time'] = processing_time

                    st.session_state.fix_ledger_results = results
                    st.session_state.fix_ledger_enriched = results['enriched_df']

                st.success(f"✅ Matching complete in {processing_time:.2f} seconds!")
                st.rerun()

    def render_results(self):
        """Render matching results and download options"""

        st.markdown("---")
        st.subheader("📊 Step 5: Results & Download")

        results = st.session_state.fix_ledger_results

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="match-stats">
                <h2>{results['matched_count']:,}</h2>
                <p>Matched</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="unmatch-stats">
                <h2>{results['unmatched_count']:,}</h2>
                <p>Unmatched (with ref)</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            match_rate = (results['matched_count'] / max(results['matched_count'] + results['unmatched_count'], 1)) * 100
            st.metric("📈 Match Rate", f"{match_rate:.1f}%")

        with col4:
            st.metric("⚡ Processing Time", f"{results['processing_time']:.2f}s")

        # Additional stats
        st.info(f"📊 TX Report had **{results['tx_lookup_size']:,}** unique references | "
                f"**{results['no_ref_count']:,}** rows had no extractable reference")

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            f"✅ Matched ({results['matched_count']:,})",
            f"❌ Unmatched ({results['unmatched_count']:,})",
            "📗 Full Enriched Ledger",
            "📥 Download"
        ])

        settings = st.session_state.fix_ledger_settings
        comment_col = settings['comment_col']

        with tab1:
            if results['matched_count'] > 0:
                st.markdown("**Matched Transactions** - TX_REF found in TX Report")
                display_cols = [comment_col, 'TX_REF', 'Source Payment Reference']
                # Add other columns from original data
                other_cols = [c for c in results['matched_df'].columns if c not in display_cols]
                display_df = results['matched_df'][display_cols + other_cols[:5]]  # Limit extra cols for display
                st.dataframe(display_df, use_container_width=True, height=400)
            else:
                st.warning("No matches found")

        with tab2:
            if results['unmatched_count'] > 0:
                st.markdown("**Unmatched Transactions** - TX_REF NOT found in TX Report")
                display_cols = [comment_col, 'TX_REF']
                other_cols = [c for c in results['unmatched_df'].columns if c not in display_cols + ['Source Payment Reference']]
                display_df = results['unmatched_df'][display_cols + other_cols[:5]]
                st.dataframe(display_df, use_container_width=True, height=400)
            else:
                st.success("✅ All transactions with references were matched!")

        with tab3:
            st.markdown("**Complete Enriched Palladium Ledger** - All original columns + TX_REF + Source Payment Reference")
            st.dataframe(results['enriched_df'], use_container_width=True, height=400)

        with tab4:
            self.render_download_section(results)

    def render_download_section(self, results):
        """Render download options"""

        st.markdown("### 📥 Download Options")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📗 Enriched Palladium Ledger**")
            st.caption("Full ledger with TX_REF and Source Payment Reference columns added")

            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                results['enriched_df'].to_excel(writer, sheet_name='Enriched Ledger', index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets['Enriched Ledger']
                for i, col in enumerate(results['enriched_df'].columns):
                    max_len = max(
                        results['enriched_df'][col].astype(str).str.len().max(),
                        len(str(col))
                    ) + 2
                    worksheet.set_column(i, i, min(max_len, 50))

            output.seek(0)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="⬇️ Download Enriched Ledger (Excel)",
                data=output,
                file_name=f"enriched_palladium_ledger_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            st.markdown("**📊 Matching Report**")
            st.caption("Summary with matched and unmatched transactions")

            # Create multi-sheet Excel report
            report_output = io.BytesIO()
            with pd.ExcelWriter(report_output, engine='xlsxwriter') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Rows', 'Matched', 'Unmatched (with ref)', 'No Reference', 'Match Rate', 'Processing Time'],
                    'Value': [
                        results['total_count'],
                        results['matched_count'],
                        results['unmatched_count'],
                        results['no_ref_count'],
                        f"{(results['matched_count'] / max(results['matched_count'] + results['unmatched_count'], 1)) * 100:.1f}%",
                        f"{results['processing_time']:.2f}s"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

                # Matched sheet
                if not results['matched_df'].empty:
                    results['matched_df'].to_excel(writer, sheet_name='Matched', index=False)

                # Unmatched sheet
                if not results['unmatched_df'].empty:
                    results['unmatched_df'].to_excel(writer, sheet_name='Unmatched', index=False)

                # Format worksheets
                workbook = writer.book
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column('A:Z', 15)

            report_output.seek(0)

            st.download_button(
                label="⬇️ Download Matching Report (Excel)",
                data=report_output,
                file_name=f"matching_report_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # CSV options
        st.markdown("---")
        st.markdown("**CSV Downloads**")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv_enriched = results['enriched_df'].to_csv(index=False)
            st.download_button(
                label="📄 Enriched Ledger (CSV)",
                data=csv_enriched,
                file_name=f"enriched_ledger_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            if not results['matched_df'].empty:
                csv_matched = results['matched_df'].to_csv(index=False)
                st.download_button(
                    label="✅ Matched Only (CSV)",
                    data=csv_matched,
                    file_name=f"matched_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col3:
            if not results['unmatched_df'].empty:
                csv_unmatched = results['unmatched_df'].to_csv(index=False)
                st.download_button(
                    label="❌ Unmatched Only (CSV)",
                    data=csv_unmatched,
                    file_name=f"unmatched_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )


# For standalone testing
if __name__ == "__main__":
    st.set_page_config(page_title="Fix Ledger Workflow", layout="wide")
    workflow = FixLedgerWorkflow()
    workflow.render()
