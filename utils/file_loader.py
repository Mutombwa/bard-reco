"""
Optimized File Loading Utilities
=================================
Fast, cached file loading with proper data type handling
"""

import streamlit as st
import pandas as pd
import io
import hashlib
from typing import Optional, Tuple


@st.cache_data(ttl=3600, show_spinner=False)
def read_file_cached(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Cached file reading with automatic type detection.

    Args:
        file_bytes: File content as bytes
        file_name: Original filename

    Returns:
        DataFrame with normalized data types
    """
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))

        # Normalize data types to prevent Arrow serialization errors
        df = normalize_dataframe_types(df)

        return df
    except Exception as e:
        st.error(f"❌ Error reading {file_name}: {str(e)}")
        return pd.DataFrame()


def normalize_dataframe_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column types to prevent Arrow serialization errors.

    This fixes the issue where mixed types cause conversion failures.
    IMPORTANT: Date columns are preserved in their original format and NOT converted.
    """
    df = df.copy()

    for col in df.columns:
        # Skip if already a proper numeric or datetime type
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        # Handle object dtype columns
        if df[col].dtype == 'object':
            # SKIP datetime conversion - preserve original date format
            # This ensures dates remain exactly as imported without any conversion
            # Special handling: dates like 20251118 (YYYYMMDD) should stay as strings
            
            # Check if this column contains YYYYMMDD format dates (8-digit numbers)
            # These are common in ABSA statements
            sample = df[col].dropna().head(100).astype(str).str.strip()
            if len(sample) > 0:
                # Pattern for YYYYMMDD: exactly 8 digits starting with 19xx or 20xx
                yyyymmdd_pattern = sample.str.match(r'^(19|20)\d{6}$')
                if yyyymmdd_pattern.sum() / len(sample) >= 0.5:
                    # This looks like YYYYMMDD dates - keep as string, don't convert to number
                    df[col] = df[col].astype(str).replace('nan', '')
                    continue

            # Try numeric conversion (but skip date-like columns)
            try:
                # Check if it looks like numbers (but not dates)
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    # Remove common number formatting
                    cleaned = sample.astype(str).str.replace(',', '').str.replace('R', '').str.strip()
                    converted = pd.to_numeric(cleaned, errors='coerce')

                    non_null_count = sample.notna().sum()
                    valid_numbers = converted.notna().sum()

                    if non_null_count > 0 and (valid_numbers / non_null_count) >= 0.5:
                        # Apply to full column
                        df[col] = pd.to_numeric(
                            df[col].astype(str).str.replace(',', '').str.replace('R', '').str.strip(),
                            errors='coerce'
                        )
                        continue
            except:
                pass

            # Default: ensure consistent string type
            df[col] = df[col].astype(str).replace('nan', '')

    return df


def compute_file_hash(file_bytes: bytes) -> str:
    """Compute MD5 hash of file content for change detection"""
    return hashlib.md5(file_bytes).hexdigest()


def load_uploaded_file(
    uploaded_file,
    session_key: str,
    hash_key: str,
    show_progress: bool = True
) -> Tuple[Optional[pd.DataFrame], bool]:
    """
    Load uploaded file with caching and change detection.

    Args:
        uploaded_file: Streamlit UploadedFile object
        session_key: Session state key to store DataFrame
        hash_key: Session state key to store file hash
        show_progress: Whether to show loading spinner

    Returns:
        Tuple of (DataFrame, is_new_file)
    """
    if uploaded_file is None:
        return None, False

    # Get file content
    file_bytes = uploaded_file.getvalue()
    file_hash = compute_file_hash(file_bytes)

    # Check if this is a new file
    is_new = hash_key not in st.session_state or st.session_state[hash_key] != file_hash

    if is_new:
        # Load new file
        if show_progress:
            with st.spinner(f"📊 Loading {uploaded_file.name}..."):
                df = read_file_cached(file_bytes, uploaded_file.name)
        else:
            df = read_file_cached(file_bytes, uploaded_file.name)

        # Store in session state
        st.session_state[session_key] = df
        st.session_state[hash_key] = file_hash

        return df, True
    else:
        # Return existing data
        return st.session_state.get(session_key), False


def get_dataframe_info(df: pd.DataFrame) -> str:
    """Get formatted info string about DataFrame"""
    if df is None or df.empty:
        return "No data"
    return f"{len(df):,} rows × {len(df.columns)} columns"
