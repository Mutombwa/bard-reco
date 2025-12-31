"""
Session History Component
=========================
Displays reconciliation history and allows users to view past sessions.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict

# Import database service
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_db import get_db, SupabaseDB
except ImportError:
    get_db = None
    SupabaseDB = None


class SessionHistory:
    """Component for displaying reconciliation session history"""

    def __init__(self):
        self.db = get_db() if get_db else None

    def render(self):
        """Render the session history component"""
        st.markdown("""
        <style>
        .history-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 1rem;
        }
        .history-item {
            background: #f8f9fa;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 8px 8px 0;
        }
        .status-completed {
            color: #059669;
            font-weight: bold;
        }
        .status-in_progress {
            color: #f59e0b;
            font-weight: bold;
        }
        .status-failed {
            color: #dc2626;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("### Session History")

        # Filter options
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            workflow_filter = st.selectbox(
                "Filter by Workflow",
                ["All", "FNB", "ABSA", "Kazang", "Corporate", "Bidvest"],
                key="history_workflow_filter"
            )

        with col2:
            limit = st.selectbox(
                "Show",
                [10, 25, 50, 100],
                key="history_limit"
            )

        with col3:
            if st.button("Refresh", key="refresh_history"):
                st.rerun()

        # Get session history
        sessions = self._get_sessions(
            workflow_type=workflow_filter if workflow_filter != "All" else None,
            limit=limit
        )

        if not sessions:
            st.info("No reconciliation sessions found. Run a reconciliation to see history here.")
            return

        # Display sessions
        for session in sessions:
            self._render_session_card(session)

    def _get_sessions(
        self,
        workflow_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get sessions from database or local storage"""
        if self.db and self.db.is_enabled():
            return self.db.get_session_history(
                workflow_type=workflow_type,
                limit=limit
            )

        # Fallback to local session state
        if 'local_sessions' not in st.session_state:
            return []

        sessions = list(st.session_state.local_sessions.values())

        if workflow_type:
            sessions = [s for s in sessions if s.get("workflow_type") == workflow_type]

        # Sort by created_at descending
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return sessions[:limit]

    def _render_session_card(self, session: Dict):
        """Render a single session card"""
        session_id = session.get("id", "")[:8]
        session_name = session.get("session_name", "Unnamed Session")
        workflow_type = session.get("workflow_type", "Unknown")
        status = session.get("status", "unknown")
        created_at = session.get("created_at", "")

        # Parse date
        if created_at:
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    date_str = str(created_at)
            except:
                date_str = created_at
        else:
            date_str = "Unknown"

        # Get metrics
        total_matched = session.get("total_matched", 0)
        total_unmatched_ledger = session.get("total_unmatched_ledger", 0)
        total_unmatched_statement = session.get("total_unmatched_statement", 0)
        match_rate = session.get("match_rate", 0)

        # Workflow icon
        icons = {
            "FNB": "",
            "ABSA": "",
            "Kazang": "",
            "Corporate": "",
            "Bidvest": ""
        }
        icon = icons.get(workflow_type, "")

        # Status styling
        status_class = f"status-{status}"

        with st.expander(f"{icon} {workflow_type} | {session_name} | {date_str}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Matched", f"{total_matched:,}")

            with col2:
                st.metric("Unmatched (Ledger)", f"{total_unmatched_ledger:,}")

            with col3:
                st.metric("Unmatched (Statement)", f"{total_unmatched_statement:,}")

            with col4:
                st.metric("Match Rate", f"{match_rate:.1f}%")

            # Status badge
            st.markdown(f"**Status:** <span class='{status_class}'>{status.upper()}</span>", unsafe_allow_html=True)
            st.caption(f"Session ID: {session_id}")

            # View details button
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("View Details", key=f"view_{session.get('id', '')}"):
                    st.session_state.selected_session_id = session.get("id")
                    st.session_state.show_session_details = True


class SaveResultsDialog:
    """Dialog for saving reconciliation results to database"""

    @staticmethod
    def render(
        workflow_type: str,
        matched_count: int,
        unmatched_ledger_count: int,
        unmatched_statement_count: int,
        on_save_callback=None
    ):
        """
        Render the save results dialog.

        Args:
            workflow_type: Type of workflow (FNB, ABSA, etc.)
            matched_count: Number of matched transactions
            unmatched_ledger_count: Number of unmatched ledger items
            unmatched_statement_count: Number of unmatched statement items
            on_save_callback: Callback function when save is clicked
        """
        st.markdown("---")
        st.markdown("### Save Results")

        db = get_db() if get_db else None
        db_status = "Supabase (Cloud)" if db and db.is_enabled() else "Local Storage"

        st.info(f"Storage: **{db_status}**")

        # Session name input
        default_name = f"{workflow_type} Reconciliation - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        session_name = st.text_input(
            "Session Name",
            value=default_name,
            key=f"save_session_name_{workflow_type}"
        )

        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Matched", matched_count)
        with col2:
            st.metric("Unmatched (Ledger)", unmatched_ledger_count)
        with col3:
            st.metric("Unmatched (Statement)", unmatched_statement_count)

        # Save button
        if st.button("Save to Database", type="primary", use_container_width=True, key=f"save_btn_{workflow_type}"):
            if on_save_callback:
                success = on_save_callback(session_name)
                if success:
                    st.success("Results saved successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save results. Please try again.")
            else:
                st.warning("Save callback not configured.")


def render_session_history():
    """Convenience function to render session history"""
    history = SessionHistory()
    history.render()


def render_save_dialog(
    workflow_type: str,
    matched_count: int,
    unmatched_ledger_count: int,
    unmatched_statement_count: int,
    on_save_callback=None
):
    """Convenience function to render save dialog"""
    SaveResultsDialog.render(
        workflow_type=workflow_type,
        matched_count=matched_count,
        unmatched_ledger_count=unmatched_ledger_count,
        unmatched_statement_count=unmatched_statement_count,
        on_save_callback=on_save_callback
    )
