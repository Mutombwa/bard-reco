"""
Data Cleaning Utilities for Reconciliation App
==============================================
Robust data cleaning functions to handle Excel paste issues and data type conversions
"""

import pandas as pd
import numpy as np
import re


def clean_amount_column(series: pd.Series, column_name: str = "Amount") -> pd.Series:
    """
    Clean and convert amount column to proper numeric format.
    Handles common issues from Excel copy/paste:
    - Currency symbols ($, €, £, R, etc.)
    - Thousand separators (commas)
    - Accounting format negatives (parentheses)
    - Text formatting
    - Extra whitespace

    Args:
        series: pandas Series containing amount data
        column_name: Name of the column (for error reporting)

    Returns:
        pandas Series with properly converted numeric values
    """
    def parse_amount(val):
        """Parse a single amount value"""
        # Handle None, NaN, or empty
        if pd.isna(val) or val == '' or val is None:
            return 0.0

        # Convert to string for processing
        val_str = str(val).strip()

        # If already numeric, try direct conversion
        if isinstance(val, (int, float, np.integer, np.floating)):
            return float(val)

        # Remove common currency symbols
        val_str = re.sub(r'[$€£¥₹R₦₨฿₩₪₫]', '', val_str)

        # Remove thousand separators (commas, spaces, apostrophes)
        val_str = val_str.replace(',', '').replace(' ', '').replace("'", '')

        # Handle accounting format for negatives: (1234.56) -> -1234.56
        is_negative = False
        if val_str.startswith('(') and val_str.endswith(')'):
            is_negative = True
            val_str = val_str[1:-1]

        # Handle negative signs at end (some formats)
        if val_str.endswith('-'):
            is_negative = True
            val_str = val_str[:-1]

        # Remove any remaining non-numeric characters except decimal point and minus
        val_str = re.sub(r'[^\d.\-]', '', val_str)

        # Handle multiple decimal points (keep only the last one)
        parts = val_str.split('.')
        if len(parts) > 2:
            # Multiple decimals - keep last one as decimal separator
            val_str = ''.join(parts[:-1]) + '.' + parts[-1]

        # Try to convert to float
        try:
            amount = float(val_str) if val_str else 0.0
            return -abs(amount) if is_negative else amount
        except (ValueError, TypeError):
            # If still can't convert, return 0 and log warning
            print(f"Warning: Could not convert '{val}' to numeric in column '{column_name}'. Using 0.0")
            return 0.0

    # Apply the parsing function
    cleaned = series.apply(parse_amount)

    # Verify we have numeric data
    if not pd.api.types.is_numeric_dtype(cleaned):
        cleaned = pd.to_numeric(cleaned, errors='coerce').fillna(0.0)

    return cleaned


def clean_dataframe_amounts(df: pd.DataFrame, amount_columns: list = None) -> pd.DataFrame:
    """
    Clean all amount columns in a DataFrame.

    Args:
        df: DataFrame to clean
        amount_columns: List of column names to clean. If None, auto-detect columns
                       containing 'amount', 'debit', 'credit', 'balance'

    Returns:
        DataFrame with cleaned amount columns
    """
    df_clean = df.copy()

    # Auto-detect amount columns if not specified
    if amount_columns is None:
        amount_keywords = ['amount', 'debit', 'credit', 'balance', 'total', 'value', 'amt']
        amount_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in amount_keywords):
                amount_columns.append(col)

    # Clean each amount column
    for col in amount_columns:
        if col in df_clean.columns:
            print(f"Cleaning amount column: {col}")
            df_clean[col] = clean_amount_column(df_clean[col], col)

    return df_clean


def validate_dataframe_amounts(df: pd.DataFrame, amount_columns: list = None) -> dict:
    """
    Validate amount columns and return statistics.

    Args:
        df: DataFrame to validate
        amount_columns: List of column names to validate

    Returns:
        Dictionary with validation statistics for each column
    """
    if amount_columns is None:
        amount_keywords = ['amount', 'debit', 'credit', 'balance', 'total', 'value', 'amt']
        amount_columns = [col for col in df.columns
                         if any(keyword in col.lower() for keyword in amount_keywords)]

    validation_results = {}

    for col in amount_columns:
        if col not in df.columns:
            continue

        result = {
            'column': col,
            'total_rows': len(df),
            'zero_values': 0,
            'negative_values': 0,
            'positive_values': 0,
            'null_values': 0,
            'non_numeric_original': 0,
            'min_value': None,
            'max_value': None,
            'sum': None
        }

        # Check original data for non-numeric
        original_numeric = pd.to_numeric(df[col], errors='coerce')
        result['non_numeric_original'] = original_numeric.isna().sum()
        result['null_values'] = df[col].isna().sum()

        # After cleaning
        cleaned = clean_amount_column(df[col], col)
        result['zero_values'] = (cleaned == 0).sum()
        result['negative_values'] = (cleaned < 0).sum()
        result['positive_values'] = (cleaned > 0).sum()
        result['min_value'] = cleaned.min()
        result['max_value'] = cleaned.max()
        result['sum'] = cleaned.sum()

        validation_results[col] = result

    return validation_results


def format_amount_for_display(amount: float, currency_symbol: str = "", decimals: int = 2) -> str:
    """
    Format amount for display with proper thousand separators and currency.

    Args:
        amount: Numeric amount
        currency_symbol: Currency symbol to prepend (e.g., "$", "R", "€")
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if pd.isna(amount):
        return ""

    # Handle negative amounts in accounting format
    is_negative = amount < 0
    abs_amount = abs(amount)

    # Format with thousand separators
    formatted = f"{abs_amount:,.{decimals}f}"

    # Add currency symbol if provided
    if currency_symbol:
        formatted = f"{currency_symbol}{formatted}"

    # Add negative formatting
    if is_negative:
        formatted = f"({formatted})"

    return formatted
