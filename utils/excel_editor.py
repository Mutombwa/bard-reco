"""
Excel-Like Data Editor Component
================================
Provides full Excel-like editing capabilities for DataFrames
- View, Edit, Add, Insert, Delete rows/columns
- Copy/Paste from Excel
- Save changes
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, Tuple

class ExcelEditor:
    """Excel-like data editor with full CRUD operations"""
    
    def __init__(self, data: pd.DataFrame, title: str = "Data Editor", key_prefix: str = "editor"):
        """
        Initialize Excel Editor
        
        Args:
            data: DataFrame to edit
            title: Editor title
            key_prefix: Unique prefix for session state keys
        """
        self.data = data.copy() if data is not None else pd.DataFrame()
        self.title = title
        self.key_prefix = key_prefix
        
        # Initialize session state
        if f'{key_prefix}_edited_data' not in st.session_state:
            st.session_state[f'{key_prefix}_edited_data'] = self.data.copy()
        
        if f'{key_prefix}_show_editor' not in st.session_state:
            st.session_state[f'{key_prefix}_show_editor'] = False
    
    def render(self) -> Optional[pd.DataFrame]:
        """
        Render the editor interface
        
        Returns:
            Modified DataFrame if saved, None otherwise
        """
        # Get current edited data
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        
        # Header with action buttons
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"### {self.title}")
            st.caption(f"📊 {len(edited_data)} rows × {len(edited_data.columns)} columns")
        
        with col2:
            if st.button("➕ Add Row", key=f"{self.key_prefix}_add_row", use_container_width=True):
                self._add_row()
                st.rerun()
        
        with col3:
            if st.button("📥 Insert Row", key=f"{self.key_prefix}_insert_row", use_container_width=True):
                self._insert_row_dialog()
        
        with col4:
            if st.button("❌ Delete Row", key=f"{self.key_prefix}_delete_row", use_container_width=True):
                self._delete_row_dialog()
        
        with col5:
            if st.button("🔄 Reset", key=f"{self.key_prefix}_reset", use_container_width=True):
                st.session_state[f'{self.key_prefix}_edited_data'] = self.data.copy()
                st.success("✅ Data reset to original")
                st.rerun()
        
        with col6:
            if st.button("💾 Save", key=f"{self.key_prefix}_save", type="primary", use_container_width=True):
                return edited_data.copy()
        
        st.markdown("---")
        
        # Column management
        with st.expander("🗂️ Column Management", expanded=False):
            col_action = st.radio(
                "Choose action",
                ["Add Column", "Delete Column", "Rename Column"],
                key=f"{self.key_prefix}_col_action",
                horizontal=True
            )
            
            if col_action == "Add Column":
                self._add_column_form()
            elif col_action == "Delete Column":
                self._delete_column_form()
            else:
                self._rename_column_form()
        
        # Main data editor
        st.markdown("### 📝 Edit Data")
        st.info("💡 **Tip:** You can edit cells directly, copy from Excel and paste here!")
        
        # Make data editor with proper configuration
        edited_df = st.data_editor(
            edited_data,
            use_container_width=True,
            num_rows="fixed",  # Don't allow adding rows through editor (use buttons instead)
            key=f"{self.key_prefix}_data_grid",
            height=400,
            column_config={
                col: st.column_config.TextColumn(
                    col,
                    width="medium",
                    help=f"Edit {col}"
                ) for col in edited_data.columns
            }
        )
        
        # Update session state with edited data
        st.session_state[f'{self.key_prefix}_edited_data'] = edited_df
        
        # Show changes summary
        if not edited_data.equals(self.data):
            st.warning("⚠️ **You have unsaved changes!** Click 'Save' to apply them.")
            
            with st.expander("📊 View Changes Summary"):
                st.write(f"**Original rows:** {len(self.data)}")
                st.write(f"**Current rows:** {len(edited_df)}")
                st.write(f"**Original columns:** {len(self.data.columns)}")
                st.write(f"**Current columns:** {len(edited_df.columns)}")
        
        return None
    
    def _add_row(self):
        """Add a new empty row at the end"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        new_row = {col: "" for col in edited_data.columns}
        st.session_state[f'{self.key_prefix}_edited_data'] = pd.concat(
            [edited_data, pd.DataFrame([new_row])],
            ignore_index=True
        )
    
    def _insert_row_dialog(self):
        """Show dialog to insert row at specific position"""
        st.session_state[f'{self.key_prefix}_show_insert'] = True
    
    def _delete_row_dialog(self):
        """Show dialog to delete specific row"""
        st.session_state[f'{self.key_prefix}_show_delete'] = True
    
    def _add_column_form(self):
        """Form to add a new column"""
        with st.form(f"{self.key_prefix}_add_column_form"):
            col_name = st.text_input("New Column Name", key=f"{self.key_prefix}_new_col_name")
            default_value = st.text_input("Default Value (optional)", key=f"{self.key_prefix}_new_col_default")
            
            if st.form_submit_button("➕ Add Column", use_container_width=True):
                if col_name:
                    edited_data = st.session_state[f'{self.key_prefix}_edited_data']
                    edited_data[col_name] = default_value if default_value else ""
                    st.session_state[f'{self.key_prefix}_edited_data'] = edited_data
                    st.success(f"✅ Column '{col_name}' added!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a column name")
    
    def _delete_column_form(self):
        """Form to delete a column"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        
        if len(edited_data.columns) == 0:
            st.warning("⚠️ No columns to delete")
            return
        
        col_to_delete = st.selectbox(
            "Select Column to Delete",
            options=edited_data.columns.tolist(),
            key=f"{self.key_prefix}_del_col_select"
        )
        
        if st.button("🗑️ Delete Column", key=f"{self.key_prefix}_del_col_btn", use_container_width=True):
            if col_to_delete:
                edited_data = edited_data.drop(columns=[col_to_delete])
                st.session_state[f'{self.key_prefix}_edited_data'] = edited_data
                st.success(f"✅ Column '{col_to_delete}' deleted!")
                st.rerun()
    
    def _rename_column_form(self):
        """Form to rename a column"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        
        if len(edited_data.columns) == 0:
            st.warning("⚠️ No columns to rename")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            old_name = st.selectbox(
                "Select Column",
                options=edited_data.columns.tolist(),
                key=f"{self.key_prefix}_rename_col_select"
            )
        
        with col2:
            new_name = st.text_input(
                "New Name",
                value=old_name,
                key=f"{self.key_prefix}_rename_col_new"
            )
        
        if st.button("✏️ Rename Column", key=f"{self.key_prefix}_rename_col_btn", use_container_width=True):
            if new_name and old_name != new_name:
                edited_data = edited_data.rename(columns={old_name: new_name})
                st.session_state[f'{self.key_prefix}_edited_data'] = edited_data
                st.success(f"✅ Column renamed: '{old_name}' → '{new_name}'")
                st.rerun()
            elif not new_name:
                st.error("❌ Please enter a new name")


def show_data_viewer(data: pd.DataFrame, title: str = "Data Viewer", key_prefix: str = "viewer"):
    """
    Simple data viewer with edit and save capabilities
    
    Args:
        data: DataFrame to view/edit
        title: Viewer title
        key_prefix: Unique prefix for session state
    
    Returns:
        Modified DataFrame if saved, None otherwise
    """
    editor = ExcelEditor(data, title, key_prefix)
    return editor.render()


# Row operations helper functions
def insert_row_at_position(df: pd.DataFrame, position: int) -> pd.DataFrame:
    """Insert empty row at specific position"""
    empty_row = {col: "" for col in df.columns}
    top = df.iloc[:position]
    bottom = df.iloc[position:]
    return pd.concat([top, pd.DataFrame([empty_row]), bottom], ignore_index=True)


def delete_row_at_position(df: pd.DataFrame, position: int) -> pd.DataFrame:
    """Delete row at specific position"""
    return df.drop(df.index[position]).reset_index(drop=True)


def bulk_paste_data(df: pd.DataFrame, pasted_text: str, start_row: int = 0) -> pd.DataFrame:
    """
    Paste data from Excel (tab/newline separated) into DataFrame
    
    Args:
        df: Target DataFrame
        pasted_text: Text copied from Excel
        start_row: Row position to start pasting
    
    Returns:
        Updated DataFrame
    """
    # Split by lines
    lines = pasted_text.strip().split('\n')
    
    # Split each line by tabs
    rows = [line.split('\t') for line in lines]
    
    # Convert to DataFrame
    pasted_df = pd.DataFrame(rows)
    
    # If columns match, replace data
    if len(pasted_df.columns) == len(df.columns):
        pasted_df.columns = df.columns
        
        # Replace from start_row
        if start_row == 0:
            return pasted_df
        else:
            top = df.iloc[:start_row]
            return pd.concat([top, pasted_df], ignore_index=True)
    else:
        raise ValueError(f"Column count mismatch: Pasted data has {len(pasted_df.columns)} columns, but DataFrame has {len(df.columns)}")
