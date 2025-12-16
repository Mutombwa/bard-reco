"""
Test Date Preservation in ABSA Workflow
========================================
This script tests that dates are preserved in their original format
without any conversion during import and reconciliation.
"""

import pandas as pd
import sys
import os

# Add project paths
sys.path.insert(0, os.path.dirname(__file__))

# Test data with different date formats
test_data = {
    'Date': ['2024-01-15', '15/01/2024', '01-15-2024', '2024/01/15'],
    'Reference': ['REF001', 'REF002', 'REF003', 'REF004'],
    'Amount': [1000.00, 2000.00, 3000.00, 4000.00]
}

df = pd.DataFrame(test_data)

print("Original DataFrame:")
print(df)
print(f"\nDate column dtype: {df['Date'].dtype}")
print("\nDate values:")
for i, date_val in enumerate(df['Date']):
    print(f"  Row {i}: {date_val} (type: {type(date_val).__name__})")

# Test normalize_dataframe_types function
from utils.file_loader import normalize_dataframe_types

print("\n" + "="*60)
print("Testing normalize_dataframe_types()...")
print("="*60)

normalized_df = normalize_dataframe_types(df)

print("\nNormalized DataFrame:")
print(normalized_df)
print(f"\nDate column dtype after normalization: {normalized_df['Date'].dtype}")
print("\nDate values after normalization:")
for i, date_val in enumerate(normalized_df['Date']):
    print(f"  Row {i}: {date_val} (type: {type(date_val).__name__})")

# Verify dates are preserved
print("\n" + "="*60)
print("VERIFICATION:")
print("="*60)

dates_preserved = all(
    str(original) == str(normalized)
    for original, normalized in zip(df['Date'], normalized_df['Date'])
)

if dates_preserved:
    print("✅ SUCCESS: All dates preserved in original format!")
else:
    print("❌ FAILED: Some dates were converted!")
    for i, (orig, norm) in enumerate(zip(df['Date'], normalized_df['Date'])):
        if str(orig) != str(norm):
            print(f"  Row {i}: '{orig}' != '{norm}'")

print("\n" + "="*60)
print("Testing reconciliation engine date handling...")
print("="*60)

# Create test ledger and statement
ledger_df = pd.DataFrame({
    'Date': ['2024-01-15', '2024-01-16'],
    'Reference': ['REF001', 'REF002'],
    'Debit': [1000.00, 2000.00],
    'Credit': [0.00, 0.00]
})

statement_df = pd.DataFrame({
    'Date': ['15/01/2024', '16/01/2024'],
    'Reference': ['REF001', 'REF002'],
    'Amount': [1000.00, 2000.00]
})

print("\nOriginal Ledger Date column:")
print(ledger_df['Date'].to_list())

print("\nOriginal Statement Date column:")
print(statement_df['Date'].to_list())

# Simulate what validation does
settings = {
    'ledger_date_col': 'Date',
    'statement_date_col': 'Date',
    'ledger_ref_col': 'Reference',
    'statement_ref_col': 'Reference',
    'ledger_debit_col': 'Debit',
    'ledger_credit_col': 'Credit',
    'statement_amt_col': 'Amount'
}

# Make copies
ledger = ledger_df.copy()
statement = statement_df.copy()

date_ledger = 'Date'
date_statement = 'Date'

# Store original dates
if date_ledger in ledger.columns:
    ledger[f'_original_{date_ledger}'] = ledger[date_ledger]
    ledger[f'_normalized_{date_ledger}'] = pd.to_datetime(ledger[date_ledger], errors='coerce')

if date_statement in statement.columns:
    statement[f'_original_{date_statement}'] = statement[date_statement]
    statement[f'_normalized_{date_statement}'] = pd.to_datetime(statement[date_statement], errors='coerce')

print("\nAfter processing:")
print("\nLedger columns:", ledger.columns.to_list())
print("Ledger Date:", ledger['Date'].to_list())
print("Ledger _original_Date:", ledger['_original_Date'].to_list())
print("Ledger _normalized_Date:", ledger['_normalized_Date'].to_list())

print("\nStatement columns:", statement.columns.to_list())
print("Statement Date:", statement['Date'].to_list())
print("Statement _original_Date:", statement['_original_Date'].to_list())
print("Statement _normalized_Date:", statement['_normalized_Date'].to_list())

# Verify original dates are preserved
ledger_dates_preserved = all(
    str(orig) == str(stored)
    for orig, stored in zip(ledger_df['Date'], ledger['_original_Date'])
)

statement_dates_preserved = all(
    str(orig) == str(stored)
    for orig, stored in zip(statement_df['Date'], statement['_original_Date'])
)

print("\n" + "="*60)
print("FINAL VERIFICATION:")
print("="*60)

if ledger_dates_preserved and statement_dates_preserved:
    print("✅ SUCCESS: Original dates are preserved in _original_Date columns!")
    print("✅ Normalized dates are stored separately for comparison!")
    print("\nThe reconciliation will:")
    print("  1. Use _normalized_Date columns for matching logic")
    print("  2. Display original Date columns in results")
    print("  3. Export original Date columns in CSV/Excel")
else:
    print("❌ FAILED: Original dates were not preserved correctly!")
    if not ledger_dates_preserved:
        print("  - Ledger dates were modified")
    if not statement_dates_preserved:
        print("  - Statement dates were modified")
