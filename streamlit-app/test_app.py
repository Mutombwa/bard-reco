"""
Simple test to verify Streamlit and ultra-fast engine work
"""
import streamlit as st
import pandas as pd
import numpy as np

st.title("🧪 FNB Workflow Test Page")

st.header("1. Basic Streamlit Test")
st.success("✅ Streamlit is working!")

st.header("2. Import Test")
try:
    from components.fnb_workflow_ultra_fast import UltraFastFNBReconciler
    st.success("✅ Ultra-fast engine imported successfully!")

    # Try to instantiate
    reconciler = UltraFastFNBReconciler()
    st.success("✅ Reconciler instantiated successfully!")

except Exception as e:
    st.error(f"❌ Import failed: {e}")
    import traceback
    st.code(traceback.format_exc())

st.header("3. Sample Reconciliation Test")

# Create sample data
if st.button("Run Sample Reconciliation"):
    try:
        # Sample ledger
        ledger = pd.DataFrame({
            'Date': pd.date_range('2024-10-01', periods=5),
            'Reference': ['ABC123', 'DEF456', 'GHI789', 'JKL012', 'MNO345'],
            'Debit': [0, 1000, 0, 1500, 0],
            'Credit': [500, 0, 750, 0, 2000]
        })

        # Sample statement
        statement = pd.DataFrame({
            'Date': pd.date_range('2024-10-01', periods=5),
            'Reference': ['ABC123', 'DEF456', 'GHI789', 'JKL012', 'MNO345'],
            'Amount': [-500, 1000, -750, 1500, -2000]
        })

        # Settings
        settings = {
            'ledger_date_col': 'Date',
            'ledger_ref_col': 'Reference',
            'ledger_debit_col': 'Debit',
            'ledger_credit_col': 'Credit',
            'statement_date_col': 'Date',
            'statement_ref_col': 'Reference',
            'statement_amt_col': 'Amount',
            'match_dates': True,
            'match_references': True,
            'match_amounts': True,
            'fuzzy_ref': True,
            'similarity_ref': 85,
            'use_debits_only': False,
            'use_credits_only': False,
            'use_both_debit_credit': True,
            'date_tolerance': False
        }

        st.write("**Sample Ledger:**")
        st.dataframe(ledger)

        st.write("**Sample Statement:**")
        st.dataframe(statement)

        # Run reconciliation
        from components.fnb_workflow_ultra_fast import UltraFastFNBReconciler
        reconciler = UltraFastFNBReconciler()

        results = reconciler.reconcile(ledger, statement, settings)

        st.success("✅ Reconciliation completed!")

        st.write("**Results:**")
        st.write(f"- Perfect matches: {results.get('perfect_match_count', 0)}")
        st.write(f"- Fuzzy matches: {results.get('fuzzy_match_count', 0)}")
        st.write(f"- Foreign credits: {results.get('foreign_credits_count', 0)}")
        st.write(f"- Split transactions: {len(results.get('split_matches', []))}")

        if not results['matched'].empty:
            st.write("**Matched Pairs:**")
            st.dataframe(results['matched'])

    except Exception as e:
        st.error(f"❌ Reconciliation failed: {e}")
        import traceback
        st.code(traceback.format_exc())

st.header("4. File Verification")
import os
st.write("**Current directory:**", os.getcwd())
st.write("**Files exist:**")
st.write(f"- fnb_workflow.py: {os.path.exists('components/fnb_workflow.py')}")
st.write(f"- fnb_workflow_ultra_fast.py: {os.path.exists('components/fnb_workflow_ultra_fast.py')}")

st.header("5. Git Status")
import subprocess
try:
    result = subprocess.run(['git', 'log', '--oneline', '-3'],
                          capture_output=True, text=True, cwd='.')
    st.code(result.stdout)
except:
    st.warning("Could not run git command")
