"""
Export Utilities
===============
Export reconciliation results to various formats
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import xlsxwriter

def export_to_excel(results: dict, username: str) -> str:
    """
    Export reconciliation results to Excel

    Args:
        results: Reconciliation results dictionary
        username: Username for file naming

    Returns:
        Path to exported file
    """

    # Create exports directory
    exports_dir = Path(__file__).parent.parent / 'data' / 'exports' / username
    exports_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reconciliation_{timestamp}.xlsx"
    filepath = exports_dir / filename

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3498db',
            'font_color': 'white',
            'border': 1
        })

        # Write summary sheet
        _write_summary_sheet(writer, results, header_format)

        # Write matches sheets
        if not results.get('perfect_matches', pd.DataFrame()).empty:
            results['perfect_matches'].to_excel(
                writer,
                sheet_name='Perfect Matches',
                index=False
            )
            _format_sheet(writer, 'Perfect Matches', header_format)

        if not results.get('fuzzy_matches', pd.DataFrame()).empty:
            results['fuzzy_matches'].to_excel(
                writer,
                sheet_name='Fuzzy Matches',
                index=False
            )
            _format_sheet(writer, 'Fuzzy Matches', header_format)

        if not results.get('balanced', pd.DataFrame()).empty:
            results['balanced'].to_excel(
                writer,
                sheet_name='Balanced',
                index=False
            )
            _format_sheet(writer, 'Balanced', header_format)

        if not results.get('unmatched', pd.DataFrame()).empty:
            results['unmatched'].to_excel(
                writer,
                sheet_name='Unmatched',
                index=False
            )
            _format_sheet(writer, 'Unmatched', header_format)

    return str(filepath)

def _write_summary_sheet(writer, results: dict, header_format):
    """Write summary sheet"""

    summary_data = {
        'Metric': [
            'Total Perfect Matches',
            'Total Fuzzy Matches',
            'Total Balanced',
            'Total Unmatched',
            'Match Rate (%)',
            'Timestamp'
        ],
        'Value': [
            results.get('perfect_match_count', 0),
            results.get('fuzzy_match_count', 0),
            results.get('balanced_count', 0),
            results.get('unmatched_count', 0),
            f"{results.get('match_rate', 0):.2f}",
            results.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    _format_sheet(writer, 'Summary', header_format)

def _format_sheet(writer, sheet_name: str, header_format):
    """Format Excel sheet"""

    worksheet = writer.sheets[sheet_name]
    workbook = writer.book

    # Apply header format
    for col_num, value in enumerate(pd.read_excel(writer, sheet_name=sheet_name).columns.values):
        worksheet.write(0, col_num, value, header_format)

    # Auto-adjust column width
    for i, col in enumerate(pd.read_excel(writer, sheet_name=sheet_name).columns):
        column_len = max(
            pd.read_excel(writer, sheet_name=sheet_name)[col].astype(str).str.len().max(),
            len(col)
        ) + 2
        worksheet.set_column(i, i, column_len)

def export_to_csv(results: dict, username: str) -> str:
    """Export results to CSV files"""

    exports_dir = Path(__file__).parent.parent / 'data' / 'exports' / username
    exports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    files = []

    # Export each result type
    for key in ['perfect_matches', 'fuzzy_matches', 'balanced', 'unmatched']:
        df = results.get(key, pd.DataFrame())
        if not df.empty:
            filename = f"{key}_{timestamp}.csv"
            filepath = exports_dir / filename
            df.to_csv(filepath, index=False)
            files.append(str(filepath))

    return ', '.join(files)
