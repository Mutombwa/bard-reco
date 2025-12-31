"""
Professional Dashboard Component - BARD-RECO
=============================================
Modern analytics dashboard with real-time metrics, session tracking,
and historical batch management for all reconciliation workflows.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import json
import os
import sys

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Import database service
try:
    from supabase_db import get_db, SupabaseDB
except ImportError:
    get_db = None
    SupabaseDB = None


class Dashboard:
    """Professional Dashboard with comprehensive workflow tracking"""

    # Workflow configurations
    WORKFLOWS = {
        'FNB': {'icon': '🏦', 'color': '#1e40af', 'session_key': 'fnb_results'},
        'ABSA': {'icon': '🏦', 'color': '#059669', 'session_key': 'absa_results'},
        'Kazang': {'icon': '💳', 'color': '#f59e0b', 'session_key': 'kazang_results'},
        'Bidvest': {'icon': '💼', 'color': '#7c3aed', 'session_key': 'bidvest_results'},
        'Corporate': {'icon': '🏢', 'color': '#dc2626', 'session_key': 'corporate_results'},
    }

    def __init__(self):
        self.db = get_db() if get_db else None
        self._init_session_state()

    def _init_session_state(self):
        """Initialize dashboard session state"""
        if 'dash_view' not in st.session_state:
            st.session_state.dash_view = 'overview'
        if 'dash_selected_session' not in st.session_state:
            st.session_state.dash_selected_session = None

    def render(self):
        """Main render method for the dashboard"""
        # Inject custom CSS
        self._inject_styles()

        # Navigation tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 Overview",
            "📜 Session History",
            "📥 Batch Downloads"
        ])

        with tab1:
            self._render_overview()

        with tab2:
            self._render_session_history()

        with tab3:
            self._render_batch_downloads()

    def _inject_styles(self):
        """Inject custom CSS for modern styling"""
        st.markdown("""
        <style>
        .dashboard-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
            padding: 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(30, 58, 138, 0.3);
        }
        .dashboard-header h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        .dashboard-header p {
            color: #bfdbfe;
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3b82f6;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        .workflow-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 8px;
        }
        .session-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        .session-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        }
        .status-completed { color: #059669; font-weight: 600; }
        .status-in_progress { color: #f59e0b; font-weight: 600; }
        .status-failed { color: #dc2626; font-weight: 600; }
        .activity-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            border-left: 3px solid #3b82f6;
        }
        .no-data-message {
            text-align: center;
            padding: 3rem;
            background: #f1f5f9;
            border-radius: 12px;
            color: #64748b;
        }
        </style>
        """, unsafe_allow_html=True)

    def _render_overview(self):
        """Render the overview tab with metrics and charts"""
        # Header
        st.markdown("""
        <div class="dashboard-header">
            <h1>📊 Reconciliation Dashboard</h1>
            <p>Real-time analytics and insights across all workflows</p>
        </div>
        """, unsafe_allow_html=True)

        # Current Session Metrics
        st.subheader("🎯 Current Session Summary")
        self._render_current_session_metrics()

        st.markdown("---")

        # Charts Section
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Match Distribution")
            self._render_match_distribution_chart()

        with col2:
            st.subheader("📊 Workflow Comparison")
            self._render_workflow_comparison_chart()

        st.markdown("---")

        # Recent Activity
        st.subheader("🕐 Recent Activity")
        self._render_recent_activity()

    def _render_current_session_metrics(self):
        """Render metrics for all workflows in current session"""
        # Collect metrics from all workflows
        total_matched = 0
        total_unmatched = 0
        workflow_data = []

        for wf_name, wf_config in self.WORKFLOWS.items():
            results = st.session_state.get(wf_config['session_key'])
            if results:
                matched = results.get('total_matched', 0) or results.get('perfect_match_count', 0) + results.get('fuzzy_match_count', 0) + results.get('foreign_credits_count', 0)
                unmatched_l = results.get('unmatched_ledger_count', 0) or len(results.get('unmatched_ledger', []))
                unmatched_s = results.get('unmatched_statement_count', 0) or len(results.get('unmatched_statement', []))
                unmatched = unmatched_l + unmatched_s

                total_matched += matched
                total_unmatched += unmatched

                workflow_data.append({
                    'name': wf_name,
                    'icon': wf_config['icon'],
                    'color': wf_config['color'],
                    'matched': matched,
                    'unmatched': unmatched,
                    'timestamp': results.get('timestamp', 'Recently')
                })

        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("✅ Total Matched", f"{total_matched:,}")
        with col2:
            st.metric("❌ Total Unmatched", f"{total_unmatched:,}")
        with col3:
            total = total_matched + total_unmatched
            rate = (total_matched / total * 100) if total > 0 else 0
            st.metric("📊 Match Rate", f"{rate:.1f}%")
        with col4:
            st.metric("🔄 Active Workflows", len(workflow_data))

        # Workflow breakdown
        if workflow_data:
            st.markdown("#### Workflow Breakdown")
            cols = st.columns(len(workflow_data))
            for i, wf in enumerate(workflow_data):
                with cols[i]:
                    wf_total = wf['matched'] + wf['unmatched']
                    wf_rate = (wf['matched'] / wf_total * 100) if wf_total > 0 else 0
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {wf['color']}22 0%, {wf['color']}11 100%);
                                padding: 1rem; border-radius: 10px; border-left: 4px solid {wf['color']};">
                        <h4 style="margin: 0;">{wf['icon']} {wf['name']}</h4>
                        <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold;">{wf['matched']:,}</p>
                        <p style="margin: 0; color: #64748b; font-size: 0.85rem;">matched ({wf_rate:.0f}%)</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 No reconciliation data in current session. Run a workflow to see metrics here.")

    def _render_match_distribution_chart(self):
        """Render pie chart of match distribution"""
        # Aggregate data
        perfect = 0
        fuzzy = 0
        foreign = 0
        split = 0
        unmatched = 0

        for wf_name, wf_config in self.WORKFLOWS.items():
            results = st.session_state.get(wf_config['session_key'])
            if results:
                perfect += results.get('perfect_match_count', 0)
                fuzzy += results.get('fuzzy_match_count', 0)
                foreign += results.get('foreign_credits_count', 0)
                split += len(results.get('split_matches', []))
                unmatched += results.get('unmatched_ledger_count', 0) + results.get('unmatched_statement_count', 0)

        total = perfect + fuzzy + foreign + split + unmatched

        if total > 0:
            data = []
            colors = []
            if perfect > 0:
                data.append({'Type': 'Perfect Match', 'Count': perfect})
                colors.append('#10b981')
            if fuzzy > 0:
                data.append({'Type': 'Fuzzy Match', 'Count': fuzzy})
                colors.append('#3b82f6')
            if foreign > 0:
                data.append({'Type': 'Foreign Credits', 'Count': foreign})
                colors.append('#8b5cf6')
            if split > 0:
                data.append({'Type': 'Split Transactions', 'Count': split})
                colors.append('#f59e0b')
            if unmatched > 0:
                data.append({'Type': 'Unmatched', 'Count': unmatched})
                colors.append('#ef4444')

            df = pd.DataFrame(data)
            fig = px.pie(df, values='Count', names='Type', color='Type',
                        color_discrete_sequence=colors, hole=0.4)
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            fig.update_traces(textposition='inside', textinfo='value+percent')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div class="no-data-message">
                <p style="font-size: 2rem; margin: 0;">📊</p>
                <p>No match data available yet</p>
                <p style="font-size: 0.85rem;">Run a reconciliation to see the distribution</p>
            </div>
            """, unsafe_allow_html=True)

    def _render_workflow_comparison_chart(self):
        """Render bar chart comparing workflows"""
        workflow_data = []

        for wf_name, wf_config in self.WORKFLOWS.items():
            results = st.session_state.get(wf_config['session_key'])
            if results:
                matched = results.get('total_matched', 0) or (
                    results.get('perfect_match_count', 0) +
                    results.get('fuzzy_match_count', 0) +
                    results.get('foreign_credits_count', 0)
                )
                unmatched = (results.get('unmatched_ledger_count', 0) +
                           results.get('unmatched_statement_count', 0))
                workflow_data.append({
                    'Workflow': wf_name,
                    'Matched': matched,
                    'Unmatched': unmatched
                })

        if workflow_data:
            df = pd.DataFrame(workflow_data)
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Matched', x=df['Workflow'], y=df['Matched'],
                                marker_color='#10b981'))
            fig.add_trace(go.Bar(name='Unmatched', x=df['Workflow'], y=df['Unmatched'],
                                marker_color='#ef4444'))
            fig.update_layout(
                barmode='group',
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                yaxis_title="Transactions"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div class="no-data-message">
                <p style="font-size: 2rem; margin: 0;">📈</p>
                <p>No workflow data to compare</p>
                <p style="font-size: 0.85rem;">Run reconciliations across workflows to see comparison</p>
            </div>
            """, unsafe_allow_html=True)

    def _render_recent_activity(self):
        """Render recent activity from all workflows"""
        activities = []

        for wf_name, wf_config in self.WORKFLOWS.items():
            results = st.session_state.get(wf_config['session_key'])
            if results:
                matched = results.get('total_matched', 0) or (
                    results.get('perfect_match_count', 0) +
                    results.get('fuzzy_match_count', 0)
                )
                unmatched = (results.get('unmatched_ledger_count', 0) +
                           results.get('unmatched_statement_count', 0))
                total = matched + unmatched
                rate = (matched / total * 100) if total > 0 else 0

                activities.append({
                    'workflow': wf_name,
                    'icon': wf_config['icon'],
                    'color': wf_config['color'],
                    'matched': matched,
                    'rate': rate,
                    'timestamp': results.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))
                })

        if activities:
            for act in activities:
                st.markdown(f"""
                <div class="activity-item" style="border-left-color: {act['color']};">
                    <div style="flex: 1;">
                        <strong>{act['icon']} {act['workflow']}</strong>
                        <span style="color: #64748b; margin-left: 1rem; font-size: 0.85rem;">{act['timestamp']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.25rem; font-weight: bold; color: #10b981;">{act['matched']:,}</span>
                        <span style="color: #64748b; margin-left: 0.5rem;">({act['rate']:.0f}% match)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📋 No recent activity. Run a reconciliation to see activity here.")

    def _render_session_history(self):
        """Render session history with filters"""
        st.markdown("""
        <div class="dashboard-header" style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);">
            <h1>📜 Session History</h1>
            <p>View and manage all historical reconciliation sessions</p>
        </div>
        """, unsafe_allow_html=True)

        # Filters
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            workflow_filter = st.selectbox(
                "Filter by Workflow",
                ["All", "FNB", "ABSA", "Kazang", "Bidvest", "Corporate"],
                key="hist_workflow_filter"
            )

        with col2:
            limit = st.selectbox(
                "Show Records",
                [10, 25, 50, 100],
                key="hist_limit"
            )

        with col3:
            st.write("")  # Spacer
            refresh = st.button("🔄 Refresh", key="hist_refresh", use_container_width=True)

        # Get sessions
        sessions = self._get_sessions(
            workflow_type=workflow_filter if workflow_filter != "All" else None,
            limit=limit
        )

        if sessions:
            st.success(f"📊 Found {len(sessions)} session(s)")

            for session in sessions:
                self._render_session_card(session)
        else:
            st.markdown("""
            <div class="no-data-message">
                <p style="font-size: 3rem; margin: 0;">📭</p>
                <h3>No Sessions Found</h3>
                <p>Run a reconciliation and save results to see history here.</p>
                <p style="font-size: 0.85rem; color: #94a3b8;">
                    Use the "Save Results to Database" button after running any workflow.
                </p>
            </div>
            """, unsafe_allow_html=True)

    def _get_sessions(self, workflow_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get sessions from database or local storage"""
        # Try Supabase first
        if self.db and self.db.is_enabled():
            try:
                return self.db.get_session_history(workflow_type=workflow_type, limit=limit)
            except Exception as e:
                st.warning(f"Could not load from database: {e}")

        # Fallback to local sessions
        if 'local_sessions' not in st.session_state:
            return []

        sessions = list(st.session_state.local_sessions.values())

        if workflow_type:
            sessions = [s for s in sessions if s.get("workflow_type") == workflow_type]

        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return sessions[:limit]

    def _render_session_card(self, session: Dict):
        """Render a single session card"""
        session_id = session.get("id", "")
        session_name = session.get("session_name", "Unnamed Session")
        workflow_type = session.get("workflow_type", "Unknown")
        status = session.get("status", "unknown")
        created_at = session.get("created_at", "")

        # Get workflow config
        wf_config = self.WORKFLOWS.get(workflow_type, {'icon': '📋', 'color': '#64748b'})

        # Parse date
        date_str = self._format_datetime(created_at)

        # Get metrics
        total_matched = session.get("total_matched", 0)
        total_unmatched_ledger = session.get("total_unmatched_ledger", 0)
        total_unmatched_statement = session.get("total_unmatched_statement", 0)
        match_rate = session.get("match_rate", 0)

        with st.container():
            st.markdown(f"""
            <div class="session-card" style="border-left: 4px solid {wf_config['color']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div>
                        <span style="font-size: 1.5rem;">{wf_config['icon']}</span>
                        <strong style="font-size: 1.1rem; margin-left: 0.5rem;">{session_name}</strong>
                        <span class="workflow-badge" style="background: {wf_config['color']}22; color: {wf_config['color']}; margin-left: 0.5rem;">
                            {workflow_type}
                        </span>
                    </div>
                    <span style="color: #64748b; font-size: 0.9rem;">{date_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

            with col1:
                st.metric("Matched", f"{total_matched:,}")
            with col2:
                st.metric("Unmatched (L)", f"{total_unmatched_ledger:,}")
            with col3:
                st.metric("Unmatched (S)", f"{total_unmatched_statement:,}")
            with col4:
                st.metric("Match Rate", f"{match_rate:.1f}%")
            with col5:
                if st.button("📥 Download", key=f"dl_{session_id[:8]}", use_container_width=True):
                    st.session_state.download_session_id = session_id
                    st.session_state.dash_view = 'download'

    def _render_batch_downloads(self):
        """Render batch download section"""
        st.markdown("""
        <div class="dashboard-header" style="background: linear-gradient(135deg, #059669 0%, #10b981 100%);">
            <h1>📥 Batch Downloads</h1>
            <p>Download reconciliation results from any session</p>
        </div>
        """, unsafe_allow_html=True)

        # Current session downloads
        st.subheader("📊 Download from Current Session")

        available_downloads = []
        for wf_name, wf_config in self.WORKFLOWS.items():
            results = st.session_state.get(wf_config['session_key'])
            if results:
                available_downloads.append({
                    'name': wf_name,
                    'icon': wf_config['icon'],
                    'color': wf_config['color'],
                    'results': results
                })

        if available_downloads:
            cols = st.columns(len(available_downloads))
            for i, dl in enumerate(available_downloads):
                with cols[i]:
                    self._render_download_card(dl['name'], dl['icon'], dl['color'], dl['results'])
        else:
            st.info("📊 No reconciliation results in current session. Run a workflow first.")

        st.markdown("---")

        # Historical downloads
        st.subheader("📜 Download from History")

        # Get recent sessions
        sessions = self._get_sessions(limit=10)

        if sessions:
            selected_session = st.selectbox(
                "Select a session to download",
                options=sessions,
                format_func=lambda x: f"{x.get('workflow_type', 'Unknown')} - {x.get('session_name', 'Unnamed')} ({self._format_datetime(x.get('created_at', ''))})",
                key="download_session_select"
            )

            if selected_session:
                session_id = selected_session.get('id')
                st.info(f"📋 Session ID: {session_id[:8]}...")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📥 Download Matched", key="dl_matched_hist", use_container_width=True, type="primary"):
                        self._download_session_data(session_id, 'matched')

                with col2:
                    if st.button("📥 Download Unmatched", key="dl_unmatched_hist", use_container_width=True):
                        self._download_session_data(session_id, 'unmatched')

                with col3:
                    if st.button("📥 Download All", key="dl_all_hist", use_container_width=True):
                        self._download_session_data(session_id, 'all')
        else:
            st.info("📭 No historical sessions available. Save a reconciliation result to enable downloads.")

    def _render_download_card(self, workflow_name: str, icon: str, color: str, results: Dict):
        """Render download card for a workflow"""
        matched_count = results.get('total_matched', 0) or len(results.get('matched', []))
        unmatched_count = (results.get('unmatched_ledger_count', 0) +
                         results.get('unmatched_statement_count', 0))

        st.markdown(f"""
        <div style="background: {color}11; padding: 1rem; border-radius: 10px; border: 1px solid {color}33; text-align: center;">
            <p style="font-size: 2rem; margin: 0;">{icon}</p>
            <h4 style="margin: 0.5rem 0;">{workflow_name}</h4>
            <p style="color: #64748b; margin: 0; font-size: 0.85rem;">
                {matched_count:,} matched | {unmatched_count:,} unmatched
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            matched_df = results.get('matched')
            if matched_df is not None and len(matched_df) > 0:
                csv = matched_df.to_csv(index=False)
                st.download_button(
                    "📥 Matched",
                    csv,
                    f"{workflow_name}_matched_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key=f"dl_matched_{workflow_name}",
                    use_container_width=True
                )

        with col2:
            # Combine unmatched
            unmatched_l = results.get('unmatched_ledger', pd.DataFrame())
            unmatched_s = results.get('unmatched_statement', pd.DataFrame())

            if (isinstance(unmatched_l, pd.DataFrame) and len(unmatched_l) > 0) or \
               (isinstance(unmatched_s, pd.DataFrame) and len(unmatched_s) > 0):

                # Create combined unmatched CSV
                csv_parts = []
                if isinstance(unmatched_l, pd.DataFrame) and len(unmatched_l) > 0:
                    csv_parts.append("UNMATCHED LEDGER")
                    csv_parts.append(unmatched_l.to_csv(index=False))
                if isinstance(unmatched_s, pd.DataFrame) and len(unmatched_s) > 0:
                    csv_parts.append("\nUNMATCHED STATEMENT")
                    csv_parts.append(unmatched_s.to_csv(index=False))

                st.download_button(
                    "📥 Unmatched",
                    "\n".join(csv_parts),
                    f"{workflow_name}_unmatched_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key=f"dl_unmatched_{workflow_name}",
                    use_container_width=True
                )

    def _download_session_data(self, session_id: str, data_type: str):
        """Download data from a historical session"""
        if not self.db or not self.db.is_enabled():
            # Try local session
            if 'local_sessions' in st.session_state and session_id in st.session_state.local_sessions:
                session_data = st.session_state.local_sessions[session_id]
                st.info("📥 Preparing download from local storage...")
                # Create download
                if data_type == 'matched':
                    data = session_data.get('matched', [])
                    if data:
                        df = pd.DataFrame(data)
                        st.download_button(
                            "📥 Download Now",
                            df.to_csv(index=False),
                            f"matched_{session_id[:8]}.csv",
                            "text/csv"
                        )
                    else:
                        st.warning("No matched data found")
            else:
                st.warning("Session not found in local storage")
            return

        try:
            session_details = self.db.get_session_details(session_id)
            if session_details:
                st.success("📥 Data loaded! Click below to download.")

                if data_type in ['matched', 'all']:
                    matched = session_details.get('matched_transactions', [])
                    if matched:
                        df = pd.DataFrame(matched)
                        st.download_button(
                            "📥 Download Matched Transactions",
                            df.to_csv(index=False),
                            f"matched_{session_id[:8]}.csv",
                            "text/csv",
                            key=f"dl_m_{session_id[:8]}"
                        )

                if data_type in ['unmatched', 'all']:
                    unmatched = session_details.get('unmatched_transactions', [])
                    if unmatched:
                        df = pd.DataFrame(unmatched)
                        st.download_button(
                            "📥 Download Unmatched Transactions",
                            df.to_csv(index=False),
                            f"unmatched_{session_id[:8]}.csv",
                            "text/csv",
                            key=f"dl_u_{session_id[:8]}"
                        )
            else:
                st.error("Could not load session details")

        except Exception as e:
            st.error(f"Error loading session: {e}")

    def _format_datetime(self, dt_value) -> str:
        """Format datetime for display"""
        if not dt_value:
            return "Unknown"
        try:
            if isinstance(dt_value, str):
                dt = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d %H:%M")
            return str(dt_value)
        except:
            return str(dt_value)


# Convenience function for backward compatibility
def render_session_history():
    """Render just the session history section"""
    dashboard = Dashboard()
    dashboard._render_session_history()
