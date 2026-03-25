"""
Base Workflow Class
==================
Shared functionality for all reconciliation workflow components.
Eliminates code duplication across FNB, ABSA, Kazang, Bidvest, and Corporate workflows.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

# Shared CSS for all workflows - extracted to avoid duplication
WORKFLOW_CSS = """
<style>
    .gradient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .gradient-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .gradient-header p { color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-card h3 { margin: 0; color: #666; font-size: 0.9rem; }
    .metric-card h2 { margin: 0.3rem 0 0 0; color: #333; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
"""


class BaseWorkflow(ABC):
    """
    Abstract base class for all reconciliation workflows.

    Subclasses must implement:
        - workflow_key: str property (e.g. 'fnb', 'absa')
        - workflow_title: str property (e.g. 'FNB Bank Reconciliation')
        - workflow_subtitle: str property
        - workflow_icon: str property (e.g. '🏦')
        - _get_session_state_keys(): dict of default session state values
        - _get_column_config(): list of column configuration dicts
        - render(): main render method
    """

    def __init__(self):
        """Initialize workflow with session state."""
        self.initialize_session_state()

    @property
    @abstractmethod
    def workflow_key(self) -> str:
        """Unique prefix for session state keys (e.g. 'fnb', 'absa')."""
        ...

    @property
    @abstractmethod
    def workflow_title(self) -> str:
        """Title displayed in the workflow header."""
        ...

    @property
    @abstractmethod
    def workflow_subtitle(self) -> str:
        """Subtitle displayed in the workflow header."""
        ...

    @property
    @abstractmethod
    def workflow_icon(self) -> str:
        """Emoji icon for the workflow."""
        ...

    @abstractmethod
    def _get_session_state_keys(self) -> Dict[str, Any]:
        """Return dict of session state key suffixes and their default values."""
        ...

    @abstractmethod
    def render(self):
        """Main render method for the workflow."""
        ...

    # =============================================
    # SESSION STATE MANAGEMENT
    # =============================================

    def initialize_session_state(self):
        """Initialize all session state keys with defaults."""
        defaults = self._get_session_state_keys()
        for key_suffix, default_value in defaults.items():
            full_key = f"{self.workflow_key}_{key_suffix}"
            if full_key not in st.session_state:
                st.session_state[full_key] = default_value

    def get_state(self, key_suffix: str, default=None):
        """Get a session state value by key suffix."""
        return st.session_state.get(f"{self.workflow_key}_{key_suffix}", default)

    def set_state(self, key_suffix: str, value):
        """Set a session state value by key suffix."""
        st.session_state[f"{self.workflow_key}_{key_suffix}"] = value

    def cleanup_state(self):
        """Remove all session state keys for this workflow."""
        prefix = f"{self.workflow_key}_"
        keys_to_remove = [k for k in st.session_state if k.startswith(prefix)]
        for k in keys_to_remove:
            del st.session_state[k]
        logger.info(f"Cleaned up {len(keys_to_remove)} session state keys for {self.workflow_key}")

    # =============================================
    # UI RENDERING HELPERS
    # =============================================

    def render_header(self):
        """Render the workflow header with gradient styling."""
        st.markdown(WORKFLOW_CSS, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="gradient-header">
            <h1>{self.workflow_icon} {self.workflow_title}</h1>
            <p>{self.workflow_subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

    def render_file_uploaders(
        self,
        ledger_label: str = "Upload Ledger File",
        statement_label: str = "Upload Statement File",
        file_types: list = None
    ) -> Tuple[Optional[Any], Optional[Any]]:
        """Render file upload widgets for ledger and statement."""
        if file_types is None:
            file_types = ['xlsx', 'xls', 'csv']

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 📒 {ledger_label}")
            ledger_file = st.file_uploader(
                ledger_label, type=file_types,
                key=f"{self.workflow_key}_ledger_uploader"
            )
        with col2:
            st.markdown(f"### 📄 {statement_label}")
            statement_file = st.file_uploader(
                statement_label, type=file_types,
                key=f"{self.workflow_key}_statement_uploader"
            )

        return ledger_file, statement_file

    def render_column_mapping(
        self,
        df: pd.DataFrame,
        columns_config: List[Dict[str, str]],
        source: str = "ledger"
    ) -> Dict[str, str]:
        """
        Render column selector dropdowns.

        Args:
            df: DataFrame whose columns to select from
            columns_config: List of dicts with 'label' and 'key' for each selector
            source: 'ledger' or 'statement' for unique keys

        Returns:
            Dict mapping config keys to selected column names
        """
        num_cols = len(columns_config)
        cols = st.columns(num_cols)
        selected = {}

        for i, config in enumerate(columns_config):
            with cols[i]:
                selected[config['key']] = st.selectbox(
                    config['label'],
                    df.columns.tolist(),
                    key=f"{self.workflow_key}_{source}_{config['key']}"
                )

        return selected

    def render_matching_settings(
        self,
        show_fuzzy: bool = True,
        show_date_tolerance: bool = True,
        show_amount_tolerance: bool = True
    ) -> Dict[str, Any]:
        """Render matching threshold settings."""
        settings = {}

        st.markdown("### ⚙️ Matching Settings")
        cols = st.columns(3)

        if show_fuzzy:
            with cols[0]:
                settings['fuzzy_threshold'] = st.slider(
                    "Fuzzy Match Threshold (%)",
                    min_value=50, max_value=100, value=85,
                    key=f"{self.workflow_key}_fuzzy_threshold",
                    help="Minimum similarity score for fuzzy reference matching"
                )

        if show_date_tolerance:
            with cols[1]:
                settings['date_tolerance'] = st.slider(
                    "Date Tolerance (days)",
                    min_value=0, max_value=30, value=3,
                    key=f"{self.workflow_key}_date_tolerance",
                    help="Maximum days difference for date matching"
                )

        if show_amount_tolerance:
            with cols[2]:
                settings['amount_tolerance'] = st.slider(
                    "Amount Tolerance (%)",
                    min_value=0.0, max_value=5.0, value=0.1, step=0.1,
                    key=f"{self.workflow_key}_amount_tolerance",
                    help="Maximum percentage difference for amount matching"
                )

        return settings

    def render_action_buttons(self) -> Dict[str, bool]:
        """Render Start/Reset/Clear action buttons."""
        col1, col2, col3 = st.columns(3)
        buttons = {}

        with col1:
            buttons['start'] = st.button(
                "🚀 Start Reconciliation",
                width="stretch",
                key=f"{self.workflow_key}_start_btn",
                type="primary"
            )
        with col2:
            buttons['reset'] = st.button(
                "🔄 Reset",
                width="stretch",
                key=f"{self.workflow_key}_reset_btn"
            )
        with col3:
            buttons['clear'] = st.button(
                "🗑️ Clear All",
                width="stretch",
                key=f"{self.workflow_key}_clear_btn"
            )

        return buttons

    def render_results_metrics(self, stats: Dict[str, Any]):
        """Render results summary metrics."""
        total = stats.get('total', 0)
        matched = stats.get('matched', 0)
        unmatched_ledger = stats.get('unmatched_ledger', 0)
        unmatched_statement = stats.get('unmatched_statement', 0)
        match_rate = stats.get('match_rate', 0)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Transactions", f"{total:,}")
        with col2:
            st.metric("Matched", f"{matched:,}")
        with col3:
            st.metric("Unmatched Ledger", f"{unmatched_ledger:,}")
        with col4:
            st.metric("Unmatched Statement", f"{unmatched_statement:,}")
        with col5:
            st.metric("Match Rate", f"{match_rate:.1f}%")

    def render_export_button(
        self,
        results: Dict[str, Any],
        filename_prefix: Optional[str] = None
    ) -> bool:
        """Render export to Excel button."""
        prefix = filename_prefix or self.workflow_key
        return st.button(
            "📥 Export All Results to Excel",
            width="stretch",
            key=f"{self.workflow_key}_export_btn"
        )

    def render_save_to_db_button(self) -> bool:
        """Render save to database button."""
        return st.button(
            "💾 Save to Database",
            width="stretch",
            key=f"{self.workflow_key}_save_db_btn",
            type="primary"
        )

    # =============================================
    # DATA HELPERS
    # =============================================

    @staticmethod
    def load_file(file) -> Optional[pd.DataFrame]:
        """Load a file into a DataFrame with automatic type detection."""
        if file is None:
            return None
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, low_memory=False)
            else:
                df = pd.read_excel(file, engine='openpyxl')

            # Normalize data types to prevent Arrow serialization errors
            from utils.file_loader import normalize_dataframe_types
            df = normalize_dataframe_types(df)

            return df
        except Exception as e:
            logger.error(f"Failed to load file {getattr(file, 'name', 'unknown')}: {e}")
            st.error(f"Error loading file: {e}")
            return None

    @staticmethod
    def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize DataFrame for Arrow serialization compatibility."""
        from utils.file_loader import sanitize_for_display
        return sanitize_for_display(df)
