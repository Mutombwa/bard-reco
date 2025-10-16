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

        # Initialize edited_data only if it doesn't exist OR if column count changed
        # This preserves paste/edit operations while allowing new columns to be added
        if f'{key_prefix}_edited_data' not in st.session_state:
            st.session_state[f'{key_prefix}_edited_data'] = self.data.copy()
        else:
            # Check if columns have changed (new columns added externally)
            existing_cols = set(st.session_state[f'{key_prefix}_edited_data'].columns)
            new_cols = set(self.data.columns)

            # If new columns were added, merge them in
            if new_cols != existing_cols:
                added_cols = new_cols - existing_cols
                for col in added_cols:
                    st.session_state[f'{key_prefix}_edited_data'][col] = self.data[col]

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
        
        # Bulk Paste from Excel with Preview
        with st.expander("📋 Bulk Paste from Excel", expanded=False):
            st.markdown("**Paste multiple rows from Excel:**")
            st.caption("1. Copy rows from Excel (Ctrl+C)\n2. Paste in the box below (Ctrl+V)\n3. Preview and validate\n4. Click 'Paste Data'")

            paste_data = st.text_area(
                "Paste Excel data here (tab-separated)",
                height=150,
                key=f"{self.key_prefix}_paste_area",
                placeholder="Copy from Excel and paste here..."
            )

            # Show preview if data is pasted
            if paste_data and paste_data.strip():
                preview_df = self._preview_paste_data(paste_data)
                if preview_df is not None:
                    st.markdown("**Preview (first 5 rows):**")
                    st.dataframe(preview_df.head(5), use_container_width=True)
                    st.caption(f"📊 Ready to paste: {len(preview_df)} rows × {len(preview_df.columns)} columns")

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

        # Professional Data Manipulation Tools
        with st.expander("🔧 Professional Data Tools", expanded=False):
            tool_tabs = st.tabs(["🔍 Find & Replace", "🔀 Sort Data", "🧹 Remove Duplicates", "📊 Filter Data"])

            with tool_tabs[0]:
                self._find_replace_tool()

            with tool_tabs[1]:
                self._sort_data_tool()

            with tool_tabs[2]:
                self._remove_duplicates_tool()

            with tool_tabs[3]:
                self._filter_data_tool()
        
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
        
        # Create proper column configuration based on ACTUAL dtypes (not column names)
        column_config = {}
        for col in edited_data.columns:
            dtype = str(edited_data[col].dtype)

            # ONLY configure datetime if the dtype is actually datetime, not just if name contains 'date'
            if 'datetime' in dtype:
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
            # Handle text columns (including date columns that are still strings)
            else:
                column_config[col] = st.column_config.TextColumn(
                    col,
                    help=f"Text column ({dtype})",
                    width="medium"
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

    def _preview_paste_data(self, paste_text: str) -> Optional[pd.DataFrame]:
        """Preview pasted data before applying it"""
        try:
            edited_data = st.session_state[f'{self.key_prefix}_edited_data'].copy()

            # Split by newlines
            lines = paste_text.replace('\r\n', '\n').strip().split('\n')
            lines = [line for line in lines if line.strip()]

            if not lines:
                return None

            # Split each line by tabs
            rows = [line.split('\t') for line in lines]

            # Get max columns
            max_cols = max(len(row) for row in rows)

            # Check if column count matches
            if max_cols > len(edited_data.columns):
                st.error(f"⚠️ Column mismatch: Pasted {max_cols} cols, table has {len(edited_data.columns)} cols")
                return None

            # Pad rows
            for row in rows:
                while len(row) < max_cols:
                    row.append("")

            # Create preview DataFrame with the right column names
            preview_cols = edited_data.columns[:max_cols].tolist()
            preview_df = pd.DataFrame(rows, columns=preview_cols)

            return preview_df

        except Exception as e:
            st.error(f"❌ Preview error: {str(e)}")
            return None
    
    def _bulk_paste(self, paste_text: str, position: str):
        """Paste bulk data from Excel with intelligent type detection - Returns True if successful"""
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

            # Validate column count
            max_cols = max(len(row) for row in rows)

            if max_cols > len(edited_data.columns):
                st.error(f"❌ Too many columns! Pasted data has {max_cols} columns, but table has {len(edited_data.columns)} columns.")
                st.info(f"Table columns: {', '.join(edited_data.columns)}")
                return False

            # Pad shorter rows with empty strings - pad to match the FULL table columns
            for row in rows:
                while len(row) < len(edited_data.columns):
                    row.append("")
                # Truncate if too long
                if len(row) > len(edited_data.columns):
                    row = row[:len(edited_data.columns)]

            # Create DataFrame with ALL table columns
            pasted_df = pd.DataFrame(rows, columns=edited_data.columns.tolist())

            # Smart type conversion to match original data types
            conversion_errors = []
            for col in pasted_df.columns:
                if col not in edited_data.columns:
                    continue

                # Get a sample of original data to determine type
                original_dtype = str(edited_data[col].dtype)

                # Skip if column has no data in pasted rows (all empty)
                if pasted_df[col].astype(str).str.strip().eq('').all():
                    continue

                # Handle datetime columns with multiple format attempts
                if 'date' in col.lower() or 'datetime' in original_dtype:
                    # Store original values before conversion attempts
                    original_values = pasted_df[col].copy()

                    # Try multiple common date formats from Excel
                    date_formats = [
                        '%Y-%m-%d %H:%M:%S',  # Standard format
                        '%m/%d/%Y %H:%M:%S',  # US format with time
                        '%d/%m/%Y %H:%M:%S',  # EU format with time
                        '%Y-%m-%d',           # ISO date only
                        '%m/%d/%Y',           # US date only
                        '%d/%m/%Y',           # EU date only
                        '%Y/%m/%d %H:%M:%S',  # Alternative ISO with time
                        '%d-%m-%Y %H:%M:%S',  # Alternative EU with time
                        '%m-%d-%Y %H:%M:%S'   # Alternative US with time
                    ]

                    # Try formats in order
                    converted = False
                    best_conversion = None
                    best_success_rate = 0

                    for fmt in date_formats:
                        try:
                            temp_conversion = pd.to_datetime(original_values, format=fmt, errors='coerce')
                            success_rate = temp_conversion.notna().sum() / len(temp_conversion)

                            # Keep the conversion with the highest success rate
                            if success_rate > best_success_rate:
                                best_conversion = temp_conversion
                                best_success_rate = success_rate

                            # If we got >80% success, use this format
                            if success_rate > 0.8:
                                pasted_df[col] = temp_conversion
                                converted = True
                                break
                        except:
                            continue

                    # If none worked well, try pandas' automatic inference
                    if not converted and best_success_rate > 0:
                        pasted_df[col] = best_conversion
                        converted = True
                    elif not converted:
                        pasted_df[col] = pd.to_datetime(original_values, errors='coerce', infer_datetime_format=True)

                    # Report if dates failed to parse
                    failed_count = pasted_df[col].isna().sum()
                    if failed_count > 0:
                        conversion_errors.append(f"⚠️ {failed_count} date(s) in '{col}' could not be parsed")

                # Handle numeric columns (int and float)
                elif 'float' in original_dtype or 'int' in original_dtype:
                    # Remove common formatting (commas, currency symbols)
                    cleaned_values = pasted_df[col].astype(str).str.replace(',', '', regex=False)
                    cleaned_values = cleaned_values.str.replace('$', '', regex=False)
                    cleaned_values = cleaned_values.str.replace('€', '', regex=False)
                    cleaned_values = cleaned_values.str.replace('£', '', regex=False)
                    cleaned_values = cleaned_values.str.strip()

                    # Convert to numeric
                    pasted_df[col] = pd.to_numeric(cleaned_values, errors='coerce')

                    # Maintain integer type if original was integer
                    if 'int' in original_dtype:
                        pasted_df[col] = pasted_df[col].fillna(0).astype('int64')

                    # Report conversion issues
                    failed_count = pasted_df[col].isna().sum()
                    if failed_count > 0 and 'float' in original_dtype:
                        conversion_errors.append(f"⚠️ {failed_count} value(s) in '{col}' could not be converted to number")

                # Handle text columns - preserve as-is but convert to string
                else:
                    # Convert to string but keep empty strings as empty (don't replace with 'nan')
                    pasted_df[col] = pasted_df[col].astype(str)
                    # Only replace the string 'nan' that pandas creates, not actual data
                    pasted_df[col] = pasted_df[col].replace({'nan': '', 'None': ''})

            # Show conversion warnings if any
            if conversion_errors:
                st.warning("**Data Conversion Warnings:**\n" + "\n".join(conversion_errors[:5]))  # Show first 5

            # Apply based on position
            # NOTE: Always convert datetime columns back to strings before storing
            # This prevents Streamlit column config errors
            for col in pasted_df.columns:
                if pasted_df[col].dtype.name.startswith('datetime'):
                    pasted_df[col] = pasted_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    # Replace NaT with empty string
                    pasted_df[col] = pasted_df[col].fillna('')

            if position == "Replace all data":
                st.session_state[f'{self.key_prefix}_edited_data'] = pasted_df
            elif position == "Start of data":
                st.session_state[f'{self.key_prefix}_edited_data'] = pd.concat([pasted_df, edited_data], ignore_index=True)
            else:  # End of data
                st.session_state[f'{self.key_prefix}_edited_data'] = pd.concat([edited_data, pasted_df], ignore_index=True)

            return True

        except Exception as e:
            st.error(f"❌ Paste error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
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

    def _find_replace_tool(self):
        """Find and replace values in data"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']

        if len(edited_data.columns) == 0:
            st.warning("⚠️ No data to search")
            return

        with st.form(f"{self.key_prefix}_find_replace_form"):
            col1, col2 = st.columns(2)

            with col1:
                search_col = st.selectbox(
                    "Column to search",
                    options=["All Columns"] + edited_data.columns.tolist(),
                    key=f"{self.key_prefix}_search_col"
                )

            with col2:
                search_type = st.radio(
                    "Search type",
                    ["Exact match", "Contains", "Starts with", "Ends with"],
                    key=f"{self.key_prefix}_search_type",
                    horizontal=True
                )

            find_value = st.text_input("Find", key=f"{self.key_prefix}_find_val")
            replace_value = st.text_input("Replace with", key=f"{self.key_prefix}_replace_val")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                find_btn = st.form_submit_button("🔍 Find", use_container_width=True)
            with col_btn2:
                replace_btn = st.form_submit_button("🔄 Replace All", use_container_width=True)

            if find_btn and find_value:
                # Find matches
                matches = self._find_matches(edited_data, search_col, find_value, search_type)
                if matches > 0:
                    st.success(f"✅ Found {matches} match(es)")
                else:
                    st.info("No matches found")

            if replace_btn and find_value:
                # Perform replacement
                count = self._replace_values(search_col, find_value, replace_value, search_type)
                if count > 0:
                    st.success(f"✅ Replaced {count} value(s)")
                    st.rerun()
                else:
                    st.info("No matches found to replace")

    def _find_matches(self, df: pd.DataFrame, column: str, value: str, search_type: str) -> int:
        """Count matches in dataframe"""
        count = 0
        columns_to_search = df.columns if column == "All Columns" else [column]

        for col in columns_to_search:
            if df[col].dtype == 'object':
                if search_type == "Exact match":
                    count += (df[col].astype(str) == value).sum()
                elif search_type == "Contains":
                    count += df[col].astype(str).str.contains(value, case=False, na=False).sum()
                elif search_type == "Starts with":
                    count += df[col].astype(str).str.startswith(value, na=False).sum()
                elif search_type == "Ends with":
                    count += df[col].astype(str).str.endswith(value, na=False).sum()

        return count

    def _replace_values(self, column: str, find_value: str, replace_value: str, search_type: str) -> int:
        """Replace values in dataframe"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data'].copy()
        count = 0
        columns_to_search = edited_data.columns if column == "All Columns" else [column]

        for col in columns_to_search:
            if edited_data[col].dtype == 'object':
                if search_type == "Exact match":
                    mask = edited_data[col].astype(str) == find_value
                    count += mask.sum()
                    edited_data.loc[mask, col] = replace_value
                elif search_type == "Contains":
                    mask = edited_data[col].astype(str).str.contains(find_value, case=False, na=False)
                    count += mask.sum()
                    edited_data.loc[mask, col] = edited_data.loc[mask, col].astype(str).str.replace(find_value, replace_value, case=False)
                elif search_type == "Starts with":
                    mask = edited_data[col].astype(str).str.startswith(find_value, na=False)
                    count += mask.sum()
                    edited_data.loc[mask, col] = edited_data.loc[mask, col].astype(str).str.replace(f'^{find_value}', replace_value, regex=True)
                elif search_type == "Ends with":
                    mask = edited_data[col].astype(str).str.endswith(find_value, na=False)
                    count += mask.sum()
                    edited_data.loc[mask, col] = edited_data.loc[mask, col].astype(str).str.replace(f'{find_value}$', replace_value, regex=True)

        st.session_state[f'{self.key_prefix}_edited_data'] = edited_data
        return count

    def _sort_data_tool(self):
        """Sort data by columns"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']

        if len(edited_data.columns) == 0:
            st.warning("⚠️ No data to sort")
            return

        st.markdown("**Sort your data by one or more columns:**")

        col1, col2 = st.columns(2)

        with col1:
            sort_col = st.selectbox(
                "Sort by column",
                options=edited_data.columns.tolist(),
                key=f"{self.key_prefix}_sort_col"
            )

        with col2:
            sort_order = st.radio(
                "Order",
                ["Ascending", "Descending"],
                key=f"{self.key_prefix}_sort_order",
                horizontal=True
            )

        if st.button("🔀 Sort Data", key=f"{self.key_prefix}_sort_btn", use_container_width=True):
            ascending = (sort_order == "Ascending")
            sorted_data = edited_data.sort_values(by=sort_col, ascending=ascending).reset_index(drop=True)
            st.session_state[f'{self.key_prefix}_edited_data'] = sorted_data
            st.success(f"✅ Data sorted by '{sort_col}' ({sort_order})")
            st.rerun()

    def _remove_duplicates_tool(self):
        """Remove duplicate rows"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']

        if len(edited_data) == 0:
            st.warning("⚠️ No data available")
            return

        st.markdown("**Remove duplicate rows from your data:**")

        dup_option = st.radio(
            "Duplicate detection",
            ["Based on all columns", "Based on specific columns"],
            key=f"{self.key_prefix}_dup_option"
        )

        subset_cols = None
        if dup_option == "Based on specific columns":
            subset_cols = st.multiselect(
                "Select columns to check for duplicates",
                options=edited_data.columns.tolist(),
                key=f"{self.key_prefix}_dup_cols"
            )

        keep_option = st.radio(
            "Keep which duplicate?",
            ["First occurrence", "Last occurrence"],
            key=f"{self.key_prefix}_keep_option",
            horizontal=True
        )

        # Show duplicate count
        if dup_option == "Based on all columns":
            dup_count = edited_data.duplicated().sum()
        else:
            if subset_cols:
                dup_count = edited_data.duplicated(subset=subset_cols).sum()
            else:
                dup_count = 0

        st.info(f"📊 Found {dup_count} duplicate row(s)")

        if st.button("🧹 Remove Duplicates", key=f"{self.key_prefix}_remove_dup_btn", use_container_width=True):
            if dup_option == "Based on specific columns" and not subset_cols:
                st.error("❌ Please select at least one column")
                return

            keep = 'first' if keep_option == "First occurrence" else 'last'
            if dup_option == "Based on all columns":
                cleaned_data = edited_data.drop_duplicates(keep=keep).reset_index(drop=True)
            else:
                cleaned_data = edited_data.drop_duplicates(subset=subset_cols, keep=keep).reset_index(drop=True)

            removed = len(edited_data) - len(cleaned_data)
            st.session_state[f'{self.key_prefix}_edited_data'] = cleaned_data
            st.success(f"✅ Removed {removed} duplicate row(s)")
            st.rerun()

    def _filter_data_tool(self):
        """Filter data based on conditions"""
        edited_data = st.session_state[f'{self.key_prefix}_edited_data']

        if len(edited_data.columns) == 0:
            st.warning("⚠️ No data to filter")
            return

        st.markdown("**Filter rows based on conditions:**")

        col1, col2 = st.columns(2)

        with col1:
            filter_col = st.selectbox(
                "Column to filter",
                options=edited_data.columns.tolist(),
                key=f"{self.key_prefix}_filter_col"
            )

        with col2:
            filter_op = st.selectbox(
                "Condition",
                ["Equals", "Contains", "Greater than", "Less than", "Not empty", "Is empty"],
                key=f"{self.key_prefix}_filter_op"
            )

        filter_value = ""
        if filter_op not in ["Not empty", "Is empty"]:
            filter_value = st.text_input("Value", key=f"{self.key_prefix}_filter_val")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Show Filtered", key=f"{self.key_prefix}_show_filter_btn", use_container_width=True):
                filtered = self._apply_filter(edited_data, filter_col, filter_op, filter_value)
                if filtered is not None:
                    st.markdown(f"**Preview ({len(filtered)} rows):**")
                    st.dataframe(filtered.head(20), use_container_width=True)

        with col_btn2:
            if st.button("✂️ Keep Only Filtered", key=f"{self.key_prefix}_keep_filter_btn", use_container_width=True):
                filtered = self._apply_filter(edited_data, filter_col, filter_op, filter_value)
                if filtered is not None and len(filtered) > 0:
                    st.session_state[f'{self.key_prefix}_edited_data'] = filtered.reset_index(drop=True)
                    st.success(f"✅ Kept {len(filtered)} filtered row(s), removed {len(edited_data) - len(filtered)} row(s)")
                    st.rerun()
                elif filtered is not None:
                    st.warning("⚠️ No rows match the filter. Data unchanged.")

    def _apply_filter(self, df: pd.DataFrame, column: str, operation: str, value: str) -> Optional[pd.DataFrame]:
        """Apply filter to dataframe"""
        try:
            if operation == "Equals":
                return df[df[column].astype(str) == value]
            elif operation == "Contains":
                return df[df[column].astype(str).str.contains(value, case=False, na=False)]
            elif operation == "Greater than":
                return df[pd.to_numeric(df[column], errors='coerce') > float(value)]
            elif operation == "Less than":
                return df[pd.to_numeric(df[column], errors='coerce') < float(value)]
            elif operation == "Not empty":
                return df[df[column].notna() & (df[column].astype(str).str.strip() != '')]
            elif operation == "Is empty":
                return df[df[column].isna() | (df[column].astype(str).str.strip() == '')]
            return df
        except Exception as e:
            st.error(f"❌ Filter error: {str(e)}")
            return None


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
