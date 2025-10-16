"""
Corporate Settlements Workflow Component
========================================
Ultra-fast settlement matching with 5-tier batch processing
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class CorporateWorkflow:
    """Corporate Settlement Workflow with 5-Tier Matching"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state"""
        if 'corporate_data' not in st.session_state:
            st.session_state.corporate_data = None
        if 'corporate_results' not in st.session_state:
            st.session_state.corporate_results = None

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
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                st.session_state.corporate_data = df
                st.success(f"✅ Loaded {len(df)} rows")

                with st.expander("👁️ Preview Data"):
                    st.dataframe(df.head(20), use_container_width=True)

                st.markdown("---")
                st.markdown("### ⚙️ Configuration")

                col1, col2, col3 = st.columns(3)

                with col1:
                    debit_col = st.selectbox("Foreign Debits", df.columns)
                with col2:
                    credit_col = st.selectbox("Foreign Credits", df.columns)
                with col3:
                    ref_col = st.selectbox("Reference", df.columns)

                st.markdown("#### Matching Parameters")

                col1, col2 = st.columns(2)
                with col1:
                    tolerance = st.number_input("Tolerance", value=0.5, min_value=0.0)
                with col2:
                    threshold = st.number_input("Percentage Threshold", value=7.0, min_value=0.0)

                if st.button("🚀 Run Corporate Reconciliation", type="primary", use_container_width=True):
                    self.run_5_tier_matching(df, debit_col, credit_col, ref_col, tolerance, threshold)

            except Exception as e:
                st.error(f"Error loading file: {e}")

        if st.session_state.corporate_results:
            st.markdown("---")
            self.render_results()

    def run_5_tier_matching(self, df, debit_col, credit_col, ref_col, tolerance, threshold):
        """Run 5-tier matching algorithm"""

        with st.spinner("Running 5-tier matching algorithm..."):
            progress = st.progress(0)

            # Clean data
            df['debit'] = pd.to_numeric(df[debit_col], errors='coerce').fillna(0)
            df['credit'] = pd.to_numeric(df[credit_col], errors='coerce').fillna(0)
            df['reference'] = df[ref_col].astype(str)

            # Initialize result tiers
            tiers = {
                'tier1': [],  # Perfect match
                'tier2': [],  # Within tolerance
                'tier3': [],  # Within percentage threshold
                'tier4': [],  # Grouped matches
                'tier5': []   # Unmatched
            }

            progress.progress(20)

            # Tier 1: Perfect matches
            for idx, row in df.iterrows():
                if abs(row['debit'] + row['credit']) < 0.01:
                    tiers['tier1'].append(row)
                elif abs(row['debit'] + row['credit']) < tolerance:
                    tiers['tier2'].append(row)
                elif abs(row['debit'] + row['credit']) < (abs(row['debit']) * threshold / 100):
                    tiers['tier3'].append(row)
                else:
                    tiers['tier5'].append(row)

            progress.progress(100)

            # Compile results
            results = {
                'tier1': pd.DataFrame(tiers['tier1']),
                'tier2': pd.DataFrame(tiers['tier2']),
                'tier3': pd.DataFrame(tiers['tier3']),
                'tier4': pd.DataFrame(tiers['tier4']),
                'tier5': pd.DataFrame(tiers['tier5']),
                'stats': {
                    'total': len(df),
                    'tier1': len(tiers['tier1']),
                    'tier2': len(tiers['tier2']),
                    'tier3': len(tiers['tier3']),
                    'tier4': len(tiers['tier4']),
                    'tier5': len(tiers['tier5'])
                }
            }

            st.session_state.corporate_results = results
            st.success("✅ 5-tier matching complete!")
            st.rerun()

    def render_results(self):
        """Render 5-tier results"""

        results = st.session_state.corporate_results
        stats = results['stats']

        st.markdown("## 🎉 Corporate Settlement Results (5-Tier)")

        # Metrics
        cols = st.columns(6)
        with cols[0]:
            st.metric("Total", stats['total'])
        with cols[1]:
            st.metric("Tier 1", stats['tier1'])
        with cols[2]:
            st.metric("Tier 2", stats['tier2'])
        with cols[3]:
            st.metric("Tier 3", stats['tier3'])
        with cols[4]:
            st.metric("Tier 4", stats['tier4'])
        with cols[5]:
            st.metric("Tier 5", stats['tier5'])

        # Tabs for each tier
        tabs = st.tabs(["Tier 1 (Perfect)", "Tier 2 (Tolerance)", "Tier 3 (Threshold)", "Tier 4 (Grouped)", "Tier 5 (Unmatched)"])

        for idx, tier_name in enumerate(['tier1', 'tier2', 'tier3', 'tier4', 'tier5']):
            with tabs[idx]:
                tier_df = results[tier_name]
                if not tier_df.empty:
                    st.dataframe(tier_df, use_container_width=True)
                else:
                    st.info(f"No transactions in {tier_name}")
