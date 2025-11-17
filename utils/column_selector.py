"""
Column Selector Utility
=======================
Provides column selection UI for customized report downloads
"""

import streamlit as st
import pandas as pd
from typing import List, Tuple


class ColumnSelector:
    """Column selection component for customized exports"""

    @staticmethod
    def render_column_selector(ledger_cols: List[str], statement_cols: List[str], 
                               workflow_name: str) -> Tuple[List[str], List[str]]:
        """
        Render column selection UI with proper click-order tracking
        
        Returns:
            Tuple of (selected_ledger_cols, selected_statement_cols) in user-selected order
        """
        st.markdown("### 📋 Select Columns to Download")
        st.markdown("Choose which columns to include in your report. **Columns appear in the order you select them.**")
        
        # Initialize session state for tracking selection order with click sequence
        if f'{workflow_name}_ledger_selection_dict' not in st.session_state:
            st.session_state[f'{workflow_name}_ledger_selection_dict'] = {}  # {col: click_index}
        if f'{workflow_name}_statement_selection_dict' not in st.session_state:
            st.session_state[f'{workflow_name}_statement_selection_dict'] = {}
        if f'{workflow_name}_selection_counter' not in st.session_state:
            st.session_state[f'{workflow_name}_selection_counter'] = 0
        
        # Validate selection dictionaries - remove any columns that no longer exist
        ledger_dict = st.session_state[f'{workflow_name}_ledger_selection_dict']
        statement_dict = st.session_state[f'{workflow_name}_statement_selection_dict']
        
        # Clean up stale selections
        for col in list(ledger_dict.keys()):
            if col not in ledger_cols:
                del ledger_dict[col]
        for col in list(statement_dict.keys()):
            if col not in statement_cols:
                del statement_dict[col]
        
        # Select All / Deselect All buttons
        st.markdown("---")
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)
        
        with btn_col1:
            if st.button("✅ Select All Ledger", use_container_width=True, key=f"{workflow_name}_select_all_ledger"):
                selection_dict = st.session_state[f'{workflow_name}_ledger_selection_dict']
                # Add all ledger columns in their natural order
                for col in ledger_cols:
                    if col not in selection_dict:
                        st.session_state[f'{workflow_name}_selection_counter'] += 1
                        selection_dict[col] = st.session_state[f'{workflow_name}_selection_counter']
                st.session_state[f'{workflow_name}_ledger_selection_dict'] = selection_dict
        
        with btn_col2:
            if st.button("❌ Deselect All Ledger", use_container_width=True, key=f"{workflow_name}_deselect_all_ledger"):
                st.session_state[f'{workflow_name}_ledger_selection_dict'] = {}
        
        with btn_col3:
            if st.button("✅ Select All Statement", use_container_width=True, key=f"{workflow_name}_select_all_statement"):
                selection_dict = st.session_state[f'{workflow_name}_statement_selection_dict']
                # Add all statement columns in their natural order
                for col in statement_cols:
                    if col not in selection_dict:
                        st.session_state[f'{workflow_name}_selection_counter'] += 1
                        selection_dict[col] = st.session_state[f'{workflow_name}_selection_counter']
                st.session_state[f'{workflow_name}_statement_selection_dict'] = selection_dict
        
        with btn_col4:
            if st.button("❌ Deselect All Statement", use_container_width=True, key=f"{workflow_name}_deselect_all_statement"):
                st.session_state[f'{workflow_name}_statement_selection_dict'] = {}
        
        with btn_col5:
            if st.button("🔄 Reset All", use_container_width=True, key=f"{workflow_name}_reset_all_selections"):
                st.session_state[f'{workflow_name}_ledger_selection_dict'] = {}
                st.session_state[f'{workflow_name}_statement_selection_dict'] = {}
                st.session_state[f'{workflow_name}_selection_counter'] = 0
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        # LEDGER COLUMNS
        with col1:
            st.markdown("**📊 Ledger Columns**")
            st.markdown("---")
            
            # Get current selection dict (make a copy to avoid reference issues)
            selection_dict = dict(st.session_state[f'{workflow_name}_ledger_selection_dict'])
            
            # Checkboxes for each ledger column - track click order
            for col in ledger_cols:
                is_selected = col in selection_dict
                
                # Use checkbox with current state
                checked = st.checkbox(
                    col, 
                    value=is_selected,
                    key=f"{workflow_name}_ledger_{col}"
                )
                
                # Update selection dict based on checkbox state
                if checked and col not in selection_dict:
                    # Newly checked - assign next sequence number
                    st.session_state[f'{workflow_name}_selection_counter'] += 1
                    selection_dict[col] = st.session_state[f'{workflow_name}_selection_counter']
                    st.session_state[f'{workflow_name}_ledger_selection_dict'] = selection_dict
                elif not checked and col in selection_dict:
                    # Unchecked - remove from dict
                    del selection_dict[col]
                    st.session_state[f'{workflow_name}_ledger_selection_dict'] = selection_dict
            
            # Build ordered list sorted by click sequence
            ledger_ordered = sorted(selection_dict.keys(), key=lambda x: selection_dict[x])
            
            # DEBUG: Show the dictionary for debugging
            if ledger_ordered:
                debug_info = {col: selection_dict[col] for col in ledger_ordered}
                st.info(f"📌 Selected ({len(ledger_ordered)}): {', '.join(ledger_ordered)}")
                with st.expander("🔍 Debug: Click Sequence Numbers"):
                    st.json(debug_info)
            else:
                st.warning("⚠️ No ledger columns selected")
        
        # STATEMENT COLUMNS
        with col2:
            st.markdown("**🏦 Statement Columns**")
            st.markdown("---")
            
            # Get current selection dict (make a copy to avoid reference issues)
            selection_dict = dict(st.session_state[f'{workflow_name}_statement_selection_dict'])
            
            # Checkboxes for each statement column - track click order
            for col in statement_cols:
                is_selected = col in selection_dict
                
                # Use checkbox with current state
                checked = st.checkbox(
                    col,
                    value=is_selected,
                    key=f"{workflow_name}_statement_{col}"
                )
                
                # Update selection dict based on checkbox state
                if checked and col not in selection_dict:
                    # Newly checked - assign next sequence number
                    st.session_state[f'{workflow_name}_selection_counter'] += 1
                    selection_dict[col] = st.session_state[f'{workflow_name}_selection_counter']
                    st.session_state[f'{workflow_name}_statement_selection_dict'] = selection_dict
                elif not checked and col in selection_dict:
                    # Unchecked - remove from dict
                    del selection_dict[col]
                    st.session_state[f'{workflow_name}_statement_selection_dict'] = selection_dict
            
            # Build ordered list sorted by click sequence
            statement_ordered = sorted(selection_dict.keys(), key=lambda x: selection_dict[x])
            
            # DEBUG: Show the dictionary for debugging
            if statement_ordered:
                debug_info = {col: selection_dict[col] for col in statement_ordered}
                st.info(f"📌 Selected ({len(statement_ordered)}): {', '.join(statement_ordered)}")
                with st.expander("🔍 Debug: Click Sequence Numbers"):
                    st.json(debug_info)
            else:
                st.warning("⚠️ No statement columns selected")
        
        # Return the ordered selections
        return (ledger_ordered, statement_ordered)
    
    @staticmethod
    def filter_dataframe_columns(df: pd.DataFrame, selected_cols: List[str], prefix: str) -> pd.DataFrame:
        """
        Filter dataframe to only include selected columns (with prefix)
        
        Args:
            df: DataFrame to filter
            selected_cols: List of column names (without prefix)
            prefix: Prefix to add to column names (e.g., 'Ledger_' or 'Statement_')
        
        Returns:
            Filtered DataFrame with only selected columns
        """
        # Build list of prefixed column names that exist in the dataframe
        columns_to_keep = [f"{prefix}{col}" for col in selected_cols if f"{prefix}{col}" in df.columns]
        
        # Return filtered dataframe
        if columns_to_keep:
            return df[columns_to_keep]
        else:
            # Return empty dataframe with no columns if nothing selected
            return pd.DataFrame()
    
    @staticmethod
    def build_master_columns(ledger_cols: List[str], statement_cols: List[str]) -> List[str]:
        """
        Build master column list with separator columns
        
        Args:
            ledger_cols: Selected ledger columns in user order
            statement_cols: Selected statement columns in user order
        
        Returns:
            List of all column names including separators
        """
        master_columns = []
        
        # Add ledger columns with prefix
        for col in ledger_cols:
            master_columns.append(f'Ledger_{col}')
        
        # Add separator columns (only if both sides have columns)
        if ledger_cols and statement_cols:
            master_columns.extend(['', ' '])  # 2 empty separator columns
        
        # Add statement columns with prefix
        for col in statement_cols:
            master_columns.append(f'Statement_{col}')
        
        return master_columns
