"""
Report Generator
===============
Generate PDF and HTML reports
"""

from datetime import datetime
from pathlib import Path
from typing import Dict

def generate_report(results: Dict, username: str) -> str:
    """
    Generate HTML report for reconciliation results

    Args:
        results: Reconciliation results dictionary
        username: Username for file naming

    Returns:
        Path to generated report
    """

    # Create reports directory
    reports_dir = Path(__file__).parent.parent / 'data' / 'reports' / username
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{timestamp}.html"
    filepath = reports_dir / filename

    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reconciliation Report - {timestamp}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            h1 {{
                margin: 0;
                font-size: 36px;
            }}
            .subtitle {{
                margin-top: 10px;
                opacity: 0.9;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .metric-card {{
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                opacity: 0.9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #3498db;
                color: white;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #ddd;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💼 BARD-RECO</h1>
                <h2>Reconciliation Report</h2>
                <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
                <p class="subtitle">User: {username}</p>
            </div>

            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Perfect Matches</div>
                    <div class="metric-value">{results.get('perfect_match_count', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Fuzzy Matches</div>
                    <div class="metric-value">{results.get('fuzzy_match_count', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Balanced</div>
                    <div class="metric-value">{results.get('balanced_count', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Unmatched</div>
                    <div class="metric-value">{results.get('unmatched_count', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Match Rate</div>
                    <div class="metric-value">{results.get('match_rate', 0):.1f}%</div>
                </div>
            </div>

            <h2>Summary</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
                <tr>
                    <td>Perfect Matches</td>
                    <td>{results.get('perfect_match_count', 0)}</td>
                    <td>{_calculate_percentage(results, 'perfect_match_count')}%</td>
                </tr>
                <tr>
                    <td>Fuzzy Matches</td>
                    <td>{results.get('fuzzy_match_count', 0)}</td>
                    <td>{_calculate_percentage(results, 'fuzzy_match_count')}%</td>
                </tr>
                <tr>
                    <td>Balanced</td>
                    <td>{results.get('balanced_count', 0)}</td>
                    <td>{_calculate_percentage(results, 'balanced_count')}%</td>
                </tr>
                <tr>
                    <td>Unmatched</td>
                    <td>{results.get('unmatched_count', 0)}</td>
                    <td>{_calculate_percentage(results, 'unmatched_count')}%</td>
                </tr>
            </table>

            <div class="footer">
                <p><strong>BARD-RECO</strong> - Modern Reconciliation System</p>
                <p>This report was automatically generated by BARD-RECO</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return str(filepath)

def _calculate_percentage(results: Dict, key: str) -> float:
    """Calculate percentage of total"""

    total = (
        results.get('perfect_match_count', 0) +
        results.get('fuzzy_match_count', 0) +
        results.get('balanced_count', 0) +
        results.get('unmatched_count', 0)
    )

    if total == 0:
        return 0.0

    return round((results.get(key, 0) / total) * 100, 1)
