"""
Advanced Data Editor Component for Streamlit
============================================
Excel-like editing capabilities with paste support and advanced features
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

class DataEditor:
    """
    Modern data editor component with Excel-like features
    """

    def __init__(self, df, data_type="data"):
        self.df = df.copy()
        self.original_df = df.copy()
        self.data_type = data_type
        self.undo_stack = []
        self.redo_stack = []

    def render(self):
        """Render the data editor interface"""

        st.markdown(f"### ✏️ {self.data_type.title()} Data Editor")

        # Toolbar
        self.render_toolbar()

        # Main editor
        st.markdown("#### 📊 Data Grid")

        # Use Streamlit's built-in data editor
        edited_df = st.data_editor(
            self.df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{self.data_type}",
            height=500,
            column_config=self._get_column_config()
        )

        # Paste from clipboard section
        st.markdown("---")
        with st.expander("📋 Paste from Excel"):
            st.markdown("**Copy data from Excel and paste here:**")

            paste_data = st.text_area(
                "Paste Excel Data (Ctrl+V)",
                height=150,
                placeholder="Copy from Excel and paste here...",
                key=f"paste_area_{self.data_type}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Replace All Data", use_container_width=True):
                    if paste_data:
                        parsed_df = self._parse_clipboard(paste_data)
                        if parsed_df is not None:
                            edited_df = parsed_df
                            st.success(f"✅ Replaced with {len(parsed_df)} rows!")
                            st.rerun()

            with col2:
                if st.button("➕ Append Data", use_container_width=True):
                    if paste_data:
                        parsed_df = self._parse_clipboard(paste_data)
                        if parsed_df is not None:
                            edited_df = pd.concat([edited_df, parsed_df], ignore_index=True)
                            st.success(f"✅ Appended {len(parsed_df)} rows!")
                            st.rerun()

            with col3:
                if st.button("🔄 Clear Paste Area", use_container_width=True):
                    st.rerun()

        # Filter and search
        st.markdown("---")
        with st.expander("🔍 Filter & Search"):
            col1, col2 = st.columns(2)

            with col1:
                search_column = st.selectbox("Search Column", ["All"] + list(edited_df.columns))
                search_term = st.text_input("Search Term")

            with col2:
                if st.button("🔍 Apply Filter"):
                    if search_term:
                        filtered_df = self._filter_data(edited_df, search_column, search_term)
                        st.dataframe(filtered_df, use_container_width=True)

        # Statistics
        st.markdown("---")
        st.markdown("#### 📊 Data Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Rows", len(edited_df))
        with col2:
            st.metric("Total Columns", len(edited_df.columns))
        with col3:
            missing_values = edited_df.isnull().sum().sum()
            st.metric("Missing Values", missing_values)
        with col4:
            duplicates = edited_df.duplicated().sum()
            st.metric("Duplicate Rows", duplicates)

        # Save/Cancel buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                return edited_df

        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                return None

        return None

    def render_toolbar(self):
        """Render editor toolbar"""

        cols = st.columns(6)

        with cols[0]:
            if st.button("➕ Add Row", use_container_width=True):
                self._add_row()

        with cols[1]:
            if st.button("➖ Delete Row", use_container_width=True):
                st.info("Select rows in the editor and delete using Delete key")

        with cols[2]:
            if st.button("➕ Add Column", use_container_width=True):
                st.session_state.show_add_column = True

        with cols[3]:
            if st.button("🔄 Reset", use_container_width=True):
                self.df = self.original_df.copy()
                st.rerun()

        with cols[4]:
            if st.button("📥 Export CSV", use_container_width=True):
                csv = self.df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"{self.data_type}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

        with cols[5]:
            if st.button("📊 Export Excel", use_container_width=True):
                # Generate Excel file
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    self.df.to_excel(writer, index=False, sheet_name='Data')
                excel_data = output.getvalue()

                st.download_button(
                    "Download Excel",
                    excel_data,
                    f"{self.data_type}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    def _get_column_config(self):
        """Get column configuration for data editor"""

        config = {}
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                config[col] = st.column_config.NumberColumn(
                    col,
                    help=f"Numeric column: {col}",
                    format="%.2f"
                )
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                config[col] = st.column_config.DateColumn(
                    col,
                    help=f"Date column: {col}",
                    format="YYYY-MM-DD"
                )
            else:
                config[col] = st.column_config.TextColumn(
                    col,
                    help=f"Text column: {col}"
                )

        return config

    def _parse_clipboard(self, clipboard_text):
        """Parse clipboard data from Excel"""

        try:
            lines = clipboard_text.strip().split('\n')

            if not lines:
                st.error("❌ No data found in clipboard")
                return None

            # Parse tab-separated data
            data = []
            for line in lines:
                if '\t' in line:
                    row = line.split('\t')
                else:
                    row = line.split(',')
                data.append(row)

            # Ask if first row is header
            has_header = st.checkbox(
                "First row contains headers",
                value=True,
                key=f"header_check_{datetime.now().timestamp()}"
            )

            if has_header:
                headers = data[0]
                data_rows = data[1:]
            else:
                headers = [f"Column_{i+1}" for i in range(len(data[0]))]
                data_rows = data

            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)

            # Clean and convert data
            df = self._clean_dataframe(df)

            st.info(f"📊 Parsed {len(df)} rows × {len(df.columns)} columns")

            return df

        except Exception as e:
            st.error(f"❌ Failed to parse clipboard data: {e}")
            return None

    def _clean_dataframe(self, df):
        """Clean and convert DataFrame types"""

        # Strip whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()

        # Try to convert numeric columns
        for col in df.columns:
            # Try numeric conversion
            try:
                def parse_numeric(val):
                    if pd.isna(val) or val == '' or val is None:
                        return None

                    val_str = str(val).strip()

                    # Remove currency symbols and formatting
                    val_str = val_str.replace('$', '').replace('€', '').replace('£', '').replace('R', '')
                    val_str = val_str.replace(',', '')  # Remove thousand separators
                    val_str = val_str.replace(' ', '')  # Remove spaces

                    # Handle parentheses for negative numbers
                    if val_str.startswith('(') and val_str.endswith(')'):
                        val_str = '-' + val_str[1:-1]

                    try:
                        return float(val_str)
                    except (ValueError, TypeError):
                        return val

                converted = df[col].apply(parse_numeric)
                numeric_count = pd.to_numeric(converted, errors='coerce').notna().sum()

                if numeric_count > 0:
                    df[col] = pd.to_numeric(converted, errors='coerce').fillna(converted)

            except Exception:
                pass

            # Try date conversion
            try:
                if df[col].dtype == 'object':
                    date_col = pd.to_datetime(df[col], errors='coerce')
                    if date_col.notna().sum() > len(df) * 0.5:  # More than 50% valid dates
                        df[col] = date_col
            except Exception:
                pass

        return df

    def _filter_data(self, df, column, search_term):
        """Filter DataFrame by search term"""

        if column == "All":
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            return df[mask]
        else:
            mask = df[column].astype(str).str.contains(search_term, case=False, na=False)
            return df[mask]

    def _add_row(self):
        """Add empty row to DataFrame"""

        new_row = pd.Series([None] * len(self.df.columns), index=self.df.columns)
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()
