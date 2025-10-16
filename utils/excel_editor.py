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
        
        # Always use the latest data from parent (including dynamically added columns)
        # This ensures we see columns added by Add Reference, RJ & Payment Ref, etc.
        st.session_state[f'{key_prefix}_edited_data'] = self.data.copy()
        
        if f'{key_prefix}_show_editor' not in st.session_state:
            st.session_state[f'{key_prefix}_show_editor'] = False
        
        if f'{key_prefix}_show_insert' not in st.session_state:
            st.session_state[f'{key_prefix}_show_insert'] = False
        
        if f'{key_prefix}_show_delete' not in st.session_state:
            st.session_state[f'{key_prefix}_show_delete'] = False
    
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
            if st.button("➕ Add Row [A]", key=f"{self.key_prefix}_add_row", help="Add empty row at bottom", use_container_width=True):
                self._add_row()
                st.rerun()
        
        with col3:
            if st.button("� Insert Row", key=f"{self.key_prefix}_insert_btn", help="Insert row at position", use_container_width=True):
                st.session_state[f'{self.key_prefix}_show_insert'] = True
                st.rerun()
        
        with col4:
            if st.button("🗑️ Delete Row", key=f"{self.key_prefix}_delete_btn", help="Delete specific row", use_container_width=True):
                st.session_state[f'{self.key_prefix}_show_delete'] = True
                st.rerun()
        
        with col5:
            if st.button("🔄 Reset [R]", key=f"{self.key_prefix}_reset", help="Reset to original", use_container_width=True):
                st.session_state[f'{self.key_prefix}_edited_data'] = self.data.copy()
                st.success("✅ Data reset to original")
                st.rerun()
        
        with col6:
            if st.button("💾 Save [S]", key=f"{self.key_prefix}_save", type="primary", help="Save all changes", use_container_width=True):
                return edited_data.copy()
        
        st.markdown("---")
        
        # Insert Row Dialog
        if st.session_state.get(f'{self.key_prefix}_show_insert', False):
            with st.container():
                st.markdown("#### 📥 Insert Row at Position")
                self._insert_row_dialog()
                if st.button("❌ Cancel", key=f"{self.key_prefix}_cancel_insert"):
                    st.session_state[f'{self.key_prefix}_show_insert'] = False
                    st.rerun()
                st.markdown("---")
        
        # Delete Row Dialog
        if st.session_state.get(f'{self.key_prefix}_show_delete', False):
            with st.container():
                st.markdown("#### 🗑️ Delete Row")
                self._delete_row_dialog()
                if st.button("❌ Cancel", key=f"{self.key_prefix}_cancel_delete"):
                    st.session_state[f'{self.key_prefix}_show_delete'] = False
                    st.rerun()
                st.markdown("---")
        
        # Bulk Paste from Excel
        with st.expander("📋 Bulk Paste from Excel", expanded=False):
            st.markdown("**Paste multiple rows from Excel:**")
            st.caption("1. Copy rows from Excel (Ctrl+C)\n2. Paste in the box below (Ctrl+V)\n3. Click 'Paste Data'")
            
            paste_data = st.text_area(
                "Paste Excel data here (tab-separated)",
                height=150,
                key=f"{self.key_prefix}_paste_area",
                placeholder="Copy from Excel and paste here..."
            )
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                paste_position = st.selectbox(
                    "Paste at",
                    ["End of data", "Replace all data", "Start of data"],
                    key=f"{self.key_prefix}_paste_pos"
                )
            
            with col_p2:
                if st.button("📋 Paste Data", key=f"{self.key_prefix}_do_paste", use_container_width=True):
                    if paste_data and paste_data.strip():
                        success = self._bulk_paste(paste_data, paste_position)
                        if success:
                            st.success("✅ Data pasted successfully!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Please paste data in the text area first")
        
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
        
        # Add keyboard shortcut handlers
        st.markdown(f"""
        <script>
        document.addEventListener('keydown', function(e) {{
            // Don't trigger if user is typing in an input field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {{
                return;
            }}
            
            // Handle keyboard shortcuts
            if (e.key === 'a' || e.key === 'A') {{
                e.preventDefault();
                // Trigger Add Row button
                const addBtn = document.querySelector('[data-testid="stButton"] button:has-text("Add Row")');
                if (addBtn) addBtn.click();
            }} else if (e.key === 's' || e.key === 'S') {{
                e.preventDefault();
                // Trigger Save button
                const saveBtn = document.querySelector('[data-testid="stButton"] button:has-text("Save")');
                if (saveBtn) saveBtn.click();
            }} else if (e.key === 'r' || e.key === 'R') {{
                e.preventDefault();
                // Trigger Reset button
                const resetBtn = document.querySelector('[data-testid="stButton"] button:has-text("Reset")');
                if (resetBtn) resetBtn.click();
            }}
        }});
        </script>
        """, unsafe_allow_html=True)
        
        # Create proper column configuration based on dtypes
        column_config = {}
        for col in edited_data.columns:
            dtype = str(edited_data[col].dtype)
            
            # Handle date/datetime columns
            if 'date' in col.lower() or 'datetime' in dtype:
                column_config[col] = st.column_config.DatetimeColumn(
                    col,
                    help=f"Date column",
                    format="YYYY-MM-DD HH:mm:ss"
                )
            # Handle float columns
            elif 'float' in dtype:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    help=f"Numeric column ({dtype})",
                    format="%.2f"
                )
            # Handle integer columns
            elif 'int' in dtype:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    help=f"Numeric column ({dtype})",
                    format="%d"
                )
            # Handle text columns
            else:
                column_config[col] = st.column_config.TextColumn(
                    col,
                    help=f"Text column ({dtype})"
                )
        
        # Make data editor with proper column configuration and row selection
        edited_df = st.data_editor(
            edited_data,
            use_container_width=True,
            num_rows="dynamic",  # Allow adding/deleting rows directly in the editor
            key=f"{self.key_prefix}_data_grid",
            height=400,
            column_config=column_config,
            hide_index=False  # Show row numbers for easier selection
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
    
    def _bulk_paste(self, paste_text: str, position: str):
        """Paste bulk data from Excel - Returns True if successful"""
        try:
            edited_data = st.session_state[f'{self.key_prefix}_edited_data'].copy()
            
            # Split by newlines (handle both \r\n and \n)
            lines = paste_text.replace('\r\n', '\n').strip().split('\n')
            lines = [line for line in lines if line.strip()]
            
            if not lines:
                st.error("❌ No data found in paste area!")
                return False
            
            # Split each line by tabs
            rows = [line.split('\t') for line in lines]
            
            # Pad rows to match table column count
            max_cols = max(len(row) for row in rows)
            
            if max_cols > len(edited_data.columns):
                st.error(f"❌ Too many columns! Pasted data has {max_cols} columns, but table has {len(edited_data.columns)} columns.")
                st.info(f"Table columns: {', '.join(edited_data.columns)}")
                return False
            
            # Pad shorter rows with empty strings
            for row in rows:
                while len(row) < len(edited_data.columns):
                    row.append("")
            
            # Create DataFrame
            pasted_df = pd.DataFrame(rows, columns=edited_data.columns)
            
            # Convert types to match original
            for col in pasted_df.columns:
                original_dtype = str(edited_data[col].dtype)
                
                # Handle dates
                if 'date' in col.lower() or 'datetime' in original_dtype:
                    pasted_df[col] = pd.to_datetime(pasted_df[col], format='%m/%d/%Y %H:%M:%S', errors='coerce')
                    # Try alternative format if many failed
                    if pasted_df[col].isna().sum() > len(pasted_df) * 0.5:
                        pasted_df[col] = pd.to_datetime(pasted_df[col], format='%m/%d/%Y %H:%M', errors='coerce')
                # Handle numbers
                elif 'float' in original_dtype or 'int' in original_dtype:
                    pasted_df[col] = pd.to_numeric(pasted_df[col], errors='ignore')
            
            # Apply based on position
            if position == "Replace all data":
                st.session_state[f'{self.key_prefix}_edited_data'] = pasted_df
            elif position == "Start of data":
                st.session_state[f'{self.key_prefix}_edited_data'] = pd.concat([pasted_df, edited_data], ignore_index=True)
            else:  # End of data
                st.session_state[f'{self.key_prefix}_edited_data'] = pd.concat([edited_data, pasted_df], ignore_index=True)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Paste error: {str(e)}")
            return False
    
    def _insert_row_dialog(self):
        """Show dialog to insert row at specific position"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        
        with st.form(f"{self.key_prefix}_insert_row_form"):
            st.write("**Insert Row at Position**")
            position = st.number_input(
                "Insert before row number (1-based)",
                min_value=1,
                max_value=len(edited_data) + 1,
                value=len(edited_data) + 1,
                key=f"{self.key_prefix}_insert_pos"
            )
            
            if st.form_submit_button("📥 Insert Row", use_container_width=True):
                # Convert to 0-based index
                pos = int(position) - 1
                
                # Insert empty row
                new_row = {col: "" for col in edited_data.columns}
                top = edited_data.iloc[:pos]
                bottom = edited_data.iloc[pos:]
                new_df = pd.concat([top, pd.DataFrame([new_row]), bottom], ignore_index=True)
                
                st.session_state[f'{self.key_prefix}_edited_data'] = new_df
                st.session_state[f'{self.key_prefix}_show_insert'] = False  # Close dialog
                st.success(f"✅ Row inserted at position {position}!")
                st.rerun()
    
    def _delete_row_dialog(self):
        """Show dialog to delete specific row"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']
        
        if len(edited_data) == 0:
            st.warning("⚠️ No rows to delete")
            return
        
        with st.form(f"{self.key_prefix}_delete_row_form"):
            st.write("**Delete Row**")
            position = st.number_input(
                "Row number to delete (1-based)",
                min_value=1,
                max_value=len(edited_data),
                value=1,
                key=f"{self.key_prefix}_delete_pos"
            )
            
            # Show preview of row to delete
            st.write(f"**Row {position} preview:**")
            st.dataframe(edited_data.iloc[[int(position)-1]], use_container_width=True)
            
            if st.form_submit_button("🗑️ Delete Row", use_container_width=True):
                # Convert to 0-based index
                pos = int(position) - 1
                
                # Delete row
                new_df = edited_data.drop(edited_data.index[pos]).reset_index(drop=True)
                st.session_state[f'{self.key_prefix}_edited_data'] = new_df
                st.session_state[f'{self.key_prefix}_show_delete'] = False  # Close dialog
                st.success(f"✅ Row {position} deleted!")
                st.rerun()
    
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
