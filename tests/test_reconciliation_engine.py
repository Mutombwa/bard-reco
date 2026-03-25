"""
Tests for the reconciliation engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.reconciliation_engine import ReconciliationEngine


class TestReconciliationEngine:
    """Test the ReconciliationEngine class."""

    def test_initialization(self, sample_ledger_df, sample_statement_df):
        """Test engine initializes without errors."""
        engine = ReconciliationEngine(
            ledger_df=sample_ledger_df,
            statement_df=sample_statement_df,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )
        assert engine is not None
        assert len(engine.ledger_df) == 10
        assert len(engine.statement_df) == 10

    def test_perfect_matches(self, matching_ledger_statement):
        """Test that perfect matches are found correctly."""
        ledger, statement = matching_ledger_statement

        engine = ReconciliationEngine(
            ledger_df=ledger,
            statement_df=statement,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
            date_tolerance=3,
        )

        results = engine.reconcile()

        # TXN001 and TXN002 should be perfect matches (exact ref, amount, date within tolerance)
        assert results['perfect_match_count'] >= 2
        assert results['match_rate'] > 0

    def test_fuzzy_matches(self, fuzzy_match_data):
        """Test that fuzzy matches work with similar references."""
        ledger, statement = fuzzy_match_data

        engine = ReconciliationEngine(
            ledger_df=ledger,
            statement_df=statement,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
            fuzzy_threshold=70,
            date_tolerance=3,
        )

        results = engine.reconcile()

        total_matched = results['perfect_match_count'] + results['fuzzy_match_count']
        assert total_matched >= 2  # At least some should match fuzzily

    def test_unmatched_collected(self, matching_ledger_statement):
        """Test that unmatched transactions are collected."""
        ledger, statement = matching_ledger_statement

        engine = ReconciliationEngine(
            ledger_df=ledger,
            statement_df=statement,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )

        results = engine.reconcile()

        # Should have some unmatched (NOMATCH and ORPHAN-S)
        assert results['unmatched_count'] > 0

    def test_empty_dataframes(self):
        """Test engine handles empty DataFrames gracefully."""
        empty_df = pd.DataFrame({
            'Date': [], 'Reference': [], 'Description': [],
            'Amount': []
        })

        engine = ReconciliationEngine(
            ledger_df=empty_df,
            statement_df=empty_df,
            ledger_amount_col='Amount',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )

        results = engine.reconcile()
        assert results['perfect_match_count'] == 0
        assert results['fuzzy_match_count'] == 0
        assert results['unmatched_count'] == 0

    def test_amount_parsing(self, sample_ledger_df, sample_statement_df):
        """Test amount parsing handles various formats."""
        engine = ReconciliationEngine(
            ledger_df=sample_ledger_df,
            statement_df=sample_statement_df,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )

        assert engine._parse_amount('1,234.56') == 1234.56
        assert engine._parse_amount('R1,234.56') == 1234.56
        assert engine._parse_amount('(500.00)') == -500.00
        assert engine._parse_amount('$1 000.50') == 1000.50
        assert engine._parse_amount(None) == 0.0
        assert engine._parse_amount('') == 0.0
        assert engine._parse_amount('abc') == 0.0

    def test_results_structure(self, matching_ledger_statement):
        """Test that results have the expected structure."""
        ledger, statement = matching_ledger_statement

        engine = ReconciliationEngine(
            ledger_df=ledger,
            statement_df=statement,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )

        results = engine.reconcile()

        # Check all expected keys exist
        expected_keys = [
            'perfect_matches', 'fuzzy_matches', 'balanced', 'unmatched',
            'perfect_match_count', 'fuzzy_match_count', 'balanced_count',
            'unmatched_count', 'match_rate', 'timestamp'
        ]
        for key in expected_keys:
            assert key in results, f"Missing key: {key}"

        # DataFrames should be DataFrames
        assert isinstance(results['perfect_matches'], pd.DataFrame)
        assert isinstance(results['fuzzy_matches'], pd.DataFrame)
        assert isinstance(results['unmatched'], pd.DataFrame)

        # match_rate should be a valid percentage
        assert 0 <= results['match_rate'] <= 100

    def test_progress_callback(self, matching_ledger_statement):
        """Test that progress callback is called."""
        ledger, statement = matching_ledger_statement

        engine = ReconciliationEngine(
            ledger_df=ledger,
            statement_df=statement,
            ledger_amount_col='Debit',
            statement_amount_col='Amount',
            ledger_date_col='Date',
            statement_date_col='Date',
            ledger_ref_col='Reference',
            statement_ref_col='Reference',
        )

        callback_calls = []
        def progress_cb(current, total):
            callback_calls.append((current, total))

        engine.reconcile(progress_callback=progress_cb)
        assert len(callback_calls) >= 1


class TestAmountParsing:
    """Test amount parsing edge cases."""

    def _make_engine(self):
        df = pd.DataFrame({'Date': ['2024-01-01'], 'Ref': ['X'], 'Amt': [0]})
        return ReconciliationEngine(
            df, df, 'Amt', 'Amt', 'Date', 'Date', 'Ref', 'Ref'
        )

    def test_currency_symbols(self):
        engine = self._make_engine()
        assert engine._parse_amount('$100') == 100.0
        assert engine._parse_amount('€200') == 200.0
        assert engine._parse_amount('£300') == 300.0
        assert engine._parse_amount('R400') == 400.0

    def test_thousand_separators(self):
        engine = self._make_engine()
        assert engine._parse_amount('1,000') == 1000.0
        assert engine._parse_amount('1 000') == 1000.0
        assert engine._parse_amount('1,000,000.50') == 1000000.50

    def test_negative_parentheses(self):
        engine = self._make_engine()
        assert engine._parse_amount('(100)') == -100.0
        assert engine._parse_amount('(1,234.56)') == -1234.56

    def test_nan_and_none(self):
        engine = self._make_engine()
        assert engine._parse_amount(None) == 0.0
        assert engine._parse_amount(float('nan')) == 0.0
        assert engine._parse_amount('') == 0.0
