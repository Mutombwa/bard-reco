"""
Test configuration and shared fixtures for BARD-RECO tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ledger_df():
    """Create a sample ledger DataFrame for testing."""
    return pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Reference': [f'REF{i:04d}' for i in range(10)],
        'Description': [f'Transaction {i}' for i in range(10)],
        'Debit': [100.0 * (i + 1) if i % 2 == 0 else 0.0 for i in range(10)],
        'Credit': [0.0 if i % 2 == 0 else 100.0 * (i + 1) for i in range(10)],
    })


@pytest.fixture
def sample_statement_df():
    """Create a sample statement DataFrame for testing."""
    return pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Reference': [f'REF{i:04d}' for i in range(10)],
        'Description': [f'Bank Transaction {i}' for i in range(10)],
        'Amount': [100.0 * (i + 1) * (1 if i % 2 == 0 else -1) for i in range(10)],
    })


@pytest.fixture
def matching_ledger_statement():
    """Create ledger and statement with known matching transactions."""
    ledger = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-05', '2024-01-10'],
        'Reference': ['TXN001', 'TXN002', 'TXN003', 'SPLIT-A', 'NOMATCH'],
        'Description': ['Payment A', 'Payment B', 'Payment C', 'Split Part 1', 'Orphan'],
        'Debit': [500.00, 1000.00, 750.00, 300.00, 200.00],
        'Credit': [0.0, 0.0, 0.0, 0.0, 0.0],
    })

    statement = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-04', '2024-01-06', '2024-01-15'],
        'Reference': ['TXN001', 'TXN002', 'TXN003-V', 'SPLIT-A', 'ORPHAN-S'],
        'Description': ['Deposit A', 'Deposit B', 'Deposit C variant', 'Split Match', 'No Match'],
        'Amount': [500.00, 1000.00, 750.00, 300.00, 999.99],
    })

    return ledger, statement


@pytest.fixture
def fuzzy_match_data():
    """Create data with references that should fuzzy match."""
    ledger = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Reference': ['PAYMENT-12345', 'INV/2024/001', 'RJ00012345678'],
        'Description': ['Payment 1', 'Invoice 1', 'RJ Number'],
        'Debit': [100.0, 200.0, 300.0],
        'Credit': [0.0, 0.0, 0.0],
    })

    statement = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Reference': ['PAYMENT 12345', 'INV-2024-001', 'RJ 00012345678'],
        'Description': ['Pay 1', 'Inv 1', 'RJ Num'],
        'Amount': [100.0, 200.0, 300.0],
    })

    return ledger, statement
