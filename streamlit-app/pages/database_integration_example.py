"""
Database Integration Example for FNB Workflow
==============================================
This example shows how to integrate SQL Server saving into the FNB workflow
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.sql_database import ReconciliationDatabase


def save_fnb_results_to_database():
    """
    Save FNB reconciliation results to SQL Server database
    Call this function after reconciliation is complete
    """
    # Check if database is configured
    if 'sql_connection_string' not in st.session_state:
        st.warning("⚠️ Database not configured. Go to Database Config to set up SQL Server.")
        return False
    
    # Check if reconciliation results exist
    if 'fnb_matches' not in st.session_state or st.session_state['fnb_matches'] is None:
        st.error("No reconciliation results to save")
        return False
    
    try:
        # Initialize database connection
        db = ReconciliationDatabase(st.session_state['sql_connection_string'])
        
        if not db.connect():
            st.error("Failed to connect to database")
            return False
        
        # Create a new reconciliation session
        username = st.session_state.get('username', 'Unknown')
        session_id = db.create_session('FNB', username)
        
        if not session_id:
            st.error("Failed to create reconciliation session")
            db.disconnect()
            return False
        
        st.info(f"📝 Created reconciliation session #{session_id}")
        
        # Save matched transactions
        matched_df = st.session_state['fnb_matches']
        if not matched_df.empty:
            if db.save_matched_transactions(session_id, matched_df):
                st.success(f"✅ Saved {len(matched_df)} matched transactions")
            else:
                st.error("Failed to save matched transactions")
        
        # Save split transactions
        split_matches = st.session_state.get('fnb_split_matches', [])
        if split_matches:
            if db.save_split_transactions(session_id, split_matches):
                st.success(f"✅ Saved {len(split_matches)} split transactions")
            else:
                st.error("Failed to save split transactions")
        
        # Save unmatched transactions
        unmatched_ledger = st.session_state.get('fnb_unmatched_ledger', pd.DataFrame())
        unmatched_statement = st.session_state.get('fnb_unmatched_statement', pd.DataFrame())
        
        if not unmatched_ledger.empty or not unmatched_statement.empty:
            if db.save_unmatched_transactions(session_id, unmatched_ledger, unmatched_statement):
                total_unmatched = len(unmatched_ledger) + len(unmatched_statement)
                st.success(f"✅ Saved {total_unmatched} unmatched transactions")
            else:
                st.error("Failed to save unmatched transactions")
        
        # Calculate statistics and complete session
        total_matched = len(matched_df)
        total_unmatched = len(unmatched_ledger) + len(unmatched_statement)
        total_transactions = total_matched + total_unmatched
        match_rate = (total_matched / total_transactions * 100) if total_transactions > 0 else 0
        
        if db.complete_session(session_id, total_matched, total_unmatched, match_rate):
            st.success(f"✅ Session completed - Match Rate: {match_rate:.2f}%")
        
        # Store session ID in session state for reference
        st.session_state['last_saved_session_id'] = session_id
        
        db.disconnect()
        return True
        
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False


def show_save_to_database_button():
    """
    Display a button to save current reconciliation results to database
    Add this to your FNB workflow after showing results
    """
    st.divider()
    st.subheader("💾 Save to Database")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Save reconciliation results to SQL Server for permanent storage and reporting")
    
    with col2:
        if st.button("💾 Save Results", use_container_width=True, type="primary"):
            with st.spinner("Saving to database..."):
                if save_fnb_results_to_database():
                    st.balloons()
                    st.success("🎉 Results saved successfully!")
                    
                    # Show session ID
                    if 'last_saved_session_id' in st.session_state:
                        st.info(f"Session ID: {st.session_state['last_saved_session_id']}")


# Integration instructions to add to FNB workflow:
"""
HOW TO INTEGRATE INTO FNB WORKFLOW:
====================================

1. Import this module at the top of fnb_workflow.py:
   from pages.database_integration_example import show_save_to_database_button, save_fnb_results_to_database

2. After displaying reconciliation results (after the tabs with matched/unmatched/splits),
   add this line:
   show_save_to_database_button()

3. Optionally, you can also add an auto-save option:
   if st.session_state.get('auto_save_to_db', False):
       save_fnb_results_to_database()

This will allow users to save their reconciliation results to the database with one click!
"""
