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
        Render column selection UI with select all/deselect all functionality
        
        Returns:
            Tuple of (selected_ledger_cols, selected_statement_cols) in user-selected order
        """
        st.markdown("### 📋 Select Columns to Download")
        st.markdown("Choose which columns to include in your report. Columns appear in the order you select them.")
        
        # Initialize session state for tracking selection order
        if f'{workflow_name}_ledger_selection_order' not in st.session_state:
            st.session_state[f'{workflow_name}_ledger_selection_order'] = []
        if f'{workflow_name}_statement_selection_order' not in st.session_state:
            st.session_state[f'{workflow_name}_statement_selection_order'] = []
        
        col1, col2 = st.columns(2)
        
        # LEDGER COLUMNS
        with col1:
            st.markdown("**📊 Ledger Columns**")
            
            # Select/Deselect All buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("✅ Select All Ledger", key=f"{workflow_name}_select_all_ledger", use_container_width=True):
                    st.session_state[f'{workflow_name}_ledger_selection_order'] = ledger_cols.copy()
                    st.rerun()
            with btn_col2:
                if st.button("❌ Deselect All Ledger", key=f"{workflow_name}_deselect_all_ledger", use_container_width=True):
                    st.session_state[f'{workflow_name}_ledger_selection_order'] = []
                    st.rerun()
            
            st.markdown("---")
            
            # Checkboxes for each ledger column
            current_selection_order = st.session_state[f'{workflow_name}_ledger_selection_order'].copy()
            
            for col in ledger_cols:
                is_selected = col in current_selection_order
                
                # Use checkbox with callback to maintain order
                if st.checkbox(
                    col, 
                    value=is_selected,
                    key=f"{workflow_name}_ledger_{col}"
                ):
                    # Add to order if not already there
                    if col not in current_selection_order:
                        current_selection_order.append(col)
                else:
                    # Remove from order if unchecked
                    if col in current_selection_order:
                        current_selection_order.remove(col)
            
            # Update session state with new order
            st.session_state[f'{workflow_name}_ledger_selection_order'] = current_selection_order
            
            # Show selection order
            if current_selection_order:
                st.info(f"📌 Selected ({len(current_selection_order)}): {', '.join(current_selection_order)}")
            else:
                st.warning("⚠️ No ledger columns selected")
        
        # STATEMENT COLUMNS
        with col2:
            st.markdown("**🏦 Statement Columns**")
            
            # Select/Deselect All buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("✅ Select All Statement", key=f"{workflow_name}_select_all_statement", use_container_width=True):
                    st.session_state[f'{workflow_name}_statement_selection_order'] = statement_cols.copy()
                    st.rerun()
            with btn_col2:
                if st.button("❌ Deselect All Statement", key=f"{workflow_name}_deselect_all_statement", use_container_width=True):
                    st.session_state[f'{workflow_name}_statement_selection_order'] = []
                    st.rerun()
            
            st.markdown("---")
            
            # Checkboxes for each statement column
            current_selection_order = st.session_state[f'{workflow_name}_statement_selection_order'].copy()
            
            for col in statement_cols:
                is_selected = col in current_selection_order
                
                if st.checkbox(
                    col,
                    value=is_selected,
                    key=f"{workflow_name}_statement_{col}"
                ):
                    # Add to order if not already there
                    if col not in current_selection_order:
                        current_selection_order.append(col)
                else:
                    # Remove from order if unchecked
                    if col in current_selection_order:
                        current_selection_order.remove(col)
            
            # Update session state with new order
            st.session_state[f'{workflow_name}_statement_selection_order'] = current_selection_order
            
            # Show selection order
            if current_selection_order:
                st.info(f"📌 Selected ({len(current_selection_order)}): {', '.join(current_selection_order)}")
            else:
                st.warning("⚠️ No statement columns selected")
        
        # Return the ordered selections
        return (
            st.session_state[f'{workflow_name}_ledger_selection_order'],
            st.session_state[f'{workflow_name}_statement_selection_order']
        )
    
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
