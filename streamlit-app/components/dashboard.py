"""
Professional Dashboard Component
=================================
Advanced analytics, metrics, and insights for reconciliation workflows
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import json
import os

class Dashboard:
    """Professional interactive dashboard with real-time analytics"""

    def __init__(self):
        self.load_data()
        self.initialize_history()

    def load_data(self):
        """Load dashboard data from session state and database"""
        # Check for results from different workflows in session state
        self.fnb_results = st.session_state.get('fnb_results')
        self.bidvest_results = st.session_state.get('bidvest_results')
        self.corporate_results = st.session_state.get('corporate_results')
        
        # Also try to load from database
        self.load_from_database()

    def initialize_history(self):
        """Initialize reconciliation history tracking"""
        if 'reconciliation_history' not in st.session_state:
            st.session_state.reconciliation_history = []
    
    def load_from_database(self):
        """Load latest reconciliation results from database"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
            from database import get_db
            
            db = get_db()
            
            # Get the most recent FNB result if not in session state
            if not self.fnb_results:
                recent_results = db.list_results('FNB', limit=1)
                if recent_results:
                    result_id = recent_results[0][0]
                    result_data = db.get_result(result_id)
                    if result_data:
                        self.fnb_results = result_data
                    
            # Get the most recent Bidvest result if not in session state
            if not self.bidvest_results:
                recent_results = db.list_results('Bidvest', limit=1)
                if recent_results:
                    result_id = recent_results[0][0]
                    result_data = db.get_result(result_id)
                    if result_data:
                        self.bidvest_results = result_data
                    
            # Get the most recent Corporate result if not in session state
            if not self.corporate_results:
                recent_results = db.list_results('Corporate', limit=1)
                if recent_results:
                    result_id = recent_results[0][0]
                    result_data = db.get_result(result_id)
                    if result_data:
                        self.corporate_results = result_data
                    
        except Exception as e:
            # Silently fail if database not available
            pass

    def render(self):
        """Render professional dashboard with transaction category navigation"""

        # Header
        st.markdown("""
        <style>
        .gradient-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        .gradient-header h1 {
            color: white;
            margin: 0;
            font-size: 2.5rem;
        }
        .gradient-header p {
            color: #e0e7ff;
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.3);
        }
        .success-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 5px 20px rgba(79, 172, 254, 0.3);
        }
        .warning-card {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 5px 20px rgba(250, 112, 154, 0.3);
        }
        .info-card {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: #333;
            text-align: center;
            box-shadow: 0 5px 20px rgba(168, 237, 234, 0.3);
        }
        .metric-card h3, .success-card h3, .warning-card h3, .info-card h3 {
            margin: 0;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .metric-card h1, .success-card h1, .warning-card h1, .info-card h1 {
            margin: 0.5rem 0;
            font-size: 2.5rem;
            font-weight: bold;
        }
        .metric-card p, .success-card p, .warning-card p, .info-card p {
            margin: 0;
            font-size: 0.85rem;
            opacity: 0.8;
        }
        .workflow-card {
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            background: white;
            transition: all 0.3s;
        }
        .workflow-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
        }
        .nav-button {
            display: inline-block;
            padding: 12px 24px;
            margin: 5px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid #e5e7eb;
            background: white;
        }
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .nav-button-active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
        }
        </style>

        <div class="gradient-header">
            <h1>🏠 Reconciliation Dashboard</h1>
            <p>📊 Real-time insights and analytics</p>
        </div>
        """, unsafe_allow_html=True)

        # Transaction Category Navigation
        st.markdown("### 📊 Transaction Categories")
        self.render_transaction_navigation()

        st.markdown("---")

        # Quick Stats Section
        st.subheader("📈 Key Metrics")
        self.render_quick_stats()

        st.markdown("---")

        # Charts Section - Show only match distribution
        st.subheader("📊 Match Distribution")
        self.render_match_distribution_chart()

        st.markdown("---")

        # Recent Activity and Audit Trail
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🕐 Recent Activity")
            self.render_recent_activity()
        
        with col2:
            st.subheader("📋 Audit Trail")
            self.render_audit_trail()

        # Removed unnecessary tips section for cleaner dashboard

    def render_transaction_navigation(self):
        """Render professional transaction category navigation bar"""

        # Initialize selected category in session state
        if 'selected_category' not in st.session_state:
            st.session_state.selected_category = 'all'

        # Create navigation buttons in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✅ Matched", use_container_width=True, type="primary" if st.session_state.selected_category == 'matched' else "secondary"):
                st.session_state.selected_category = 'matched'
                st.rerun()
            if st.button("🔄 Split Transactions", use_container_width=True, type="primary" if st.session_state.selected_category == 'split' else "secondary"):
                st.session_state.selected_category = 'split'
                st.rerun()

        with col2:
            if st.button("📊 All Transactions", use_container_width=True, type="primary" if st.session_state.selected_category == 'all' else "secondary"):
                st.session_state.selected_category = 'all'
                st.rerun()
            if st.button("🎯 Balanced By Fuzzy", use_container_width=True, type="primary" if st.session_state.selected_category == 'fuzzy' else "secondary"):
                st.session_state.selected_category = 'fuzzy'
                st.rerun()

        with col3:
            if st.button("❌ Unmatched Ledger", use_container_width=True, type="primary" if st.session_state.selected_category == 'unmatched_ledger' else "secondary"):
                st.session_state.selected_category = 'unmatched_ledger'
                st.rerun()
            if st.button("💱 Foreign Credits", use_container_width=True, type="primary" if st.session_state.selected_category == 'foreign' else "secondary"):
                st.session_state.selected_category = 'foreign'
                st.rerun()

        with col4:
            if st.button("⚠️ Unmatched Statement", use_container_width=True, type="primary" if st.session_state.selected_category == 'unmatched_statement' else "secondary"):
                st.session_state.selected_category = 'unmatched_statement'
                st.rerun()

        # Display selected category transactions
        st.markdown("---")
        self.display_category_transactions(st.session_state.selected_category)

    def display_category_transactions(self, category):
        """Display transactions for the selected category"""

        st.markdown(f"### 📋 {self.get_category_title(category)}")

        # Get transactions based on category
        transactions = self.get_transactions_by_category(category)

        if transactions is not None and len(transactions) > 0:
            # Display count
            st.info(f"📊 Found {len(transactions)} transaction(s) in this category")

            # Clean data - replace None/NaN with empty strings
            transactions_clean = transactions.fillna('')
            
            # Display the data
            st.dataframe(
                transactions_clean,
                use_container_width=True,
                height=400
            )

            # Add export button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True, key=f'export_csv_{category}'):
                    csv = transactions_clean.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"{category}_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key=f'download_csv_{category}'
                    )
            with col2:
                if st.button("📊 Export to Excel", use_container_width=True, key=f'export_excel_{category}'):
                    st.info("Excel export functionality - Save as .xlsx format")
        else:
            st.success(f"✅ No transactions found in '{self.get_category_title(category)}' category")

    def get_category_title(self, category):
        """Get display title for category"""
        titles = {
            'all': 'All Transactions',
            'matched': 'Matched Transactions',
            'split': 'Split Transactions',
            'fuzzy': 'Balanced By Fuzzy Matching',
            'unmatched_ledger': 'Unmatched Ledger Transactions',
            'unmatched_statement': 'Unmatched Statement Transactions',
            'foreign': 'Foreign Credit Transactions'
        }
        return titles.get(category, 'Unknown Category')

    def get_transactions_by_category(self, category):
        """Get transactions filtered by category"""

        # Collect all available transaction data from workflows
        all_transactions = []

        # From FNB workflow
        if self.fnb_results:
            # Matched transactions (includes Perfect, Fuzzy, Foreign)
            if 'matched' in self.fnb_results and not self.fnb_results['matched'].empty:
                matched = self.fnb_results['matched'].copy()
                matched['source'] = 'FNB Workflow'
                matched['category'] = 'Matched'
                all_transactions.append(matched)

            # Unmatched ledger
            if 'unmatched_ledger' in self.fnb_results and not self.fnb_results['unmatched_ledger'].empty:
                unmatched_l = self.fnb_results['unmatched_ledger'].copy()
                unmatched_l['source'] = 'FNB Workflow'
                unmatched_l['category'] = 'Unmatched Ledger'
                all_transactions.append(unmatched_l)

            # Unmatched statement
            if 'unmatched_statement' in self.fnb_results and not self.fnb_results['unmatched_statement'].empty:
                unmatched_s = self.fnb_results['unmatched_statement'].copy()
                unmatched_s['source'] = 'FNB Workflow'
                unmatched_s['category'] = 'Unmatched Statement'
                all_transactions.append(unmatched_s)

        # From Bidvest workflow
        if self.bidvest_results:
            if 'matched' in self.bidvest_results:
                matched = self.bidvest_results['matched'].copy()
                matched['source'] = 'Bidvest Workflow'
                matched['category'] = 'Matched'
                all_transactions.append(matched)

            if 'unmatched_ledger' in self.bidvest_results:
                unmatched_l = self.bidvest_results['unmatched_ledger'].copy()
                unmatched_l['source'] = 'Bidvest Workflow'
                unmatched_l['category'] = 'Unmatched Ledger'
                all_transactions.append(unmatched_l)

        # From Corporate workflow
        if self.corporate_results:
            if 'matched' in self.corporate_results:
                matched = self.corporate_results['matched'].copy()
                matched['source'] = 'Corporate Workflow'
                matched['category'] = 'Matched'
                all_transactions.append(matched)

        # Combine all transactions
        if not all_transactions:
            return None

        combined = pd.concat(all_transactions, ignore_index=True)

        # Filter by category
        if category == 'all':
            return combined
        elif category == 'matched':
            return combined[combined['category'] == 'Matched']
        elif category == 'unmatched_ledger':
            return combined[combined['category'] == 'Unmatched Ledger']
        elif category == 'unmatched_statement':
            return combined[combined['category'] == 'Unmatched Statement']
        elif category == 'split':
            # Return split transactions from FNB results
            if self.fnb_results and 'split_matches' in self.fnb_results:
                splits = self.fnb_results['split_matches']
                if splits and len(splits) > 0:
                    # Convert split list to DataFrame for display
                    split_data = []
                    for i, split in enumerate(splits):
                        split_type = split.get('split_type', 'Unknown')
                        items_count = split.get('items_count', len(split.get('ledger_indices', [])))
                        
                        split_data.append({
                            'Split #': i + 1,
                            'Type': split_type.replace('_', ' ').title(),
                            'Total Amount': split.get('total_amount', 0),
                            'Statement Amount': split.get('statement_amount', 0),
                            'Items Count': items_count,
                            'Match %': f"{split.get('similarity', 0):.1f}%"
                        })
                    return pd.DataFrame(split_data)
            return pd.DataFrame()
        elif category == 'fuzzy':
            # Filter for fuzzy matched transactions from Match_Type column
            matched_df = combined[combined['category'] == 'Matched']
            if 'Match_Type' in matched_df.columns:
                return matched_df[matched_df['Match_Type'] == 'Fuzzy']
            return pd.DataFrame()
        elif category == 'foreign':
            # Filter for foreign credits from Match_Type column
            matched_df = combined[combined['category'] == 'Matched']
            if 'Match_Type' in matched_df.columns:
                return matched_df[matched_df['Match_Type'] == 'Foreign_Credit']
            return pd.DataFrame()

        return combined

    def render_quick_stats(self):
        """Render quick statistics cards with real data"""

        # Aggregate data from all workflows
        total_matched = 0
        total_unmatched = 0
        total_processed = 0
        success_rate = 0
        avg_time = 0

        # Get FNB results using the correct keys
        if self.fnb_results:
            # Count matched transactions
            total_matched += self.fnb_results.get('total_matched', 0)
            
            # Count unmatched
            total_unmatched += self.fnb_results.get('unmatched_ledger_count', 0)
            total_unmatched += self.fnb_results.get('unmatched_statement_count', 0)
            
            # Total processed
            if 'matched' in self.fnb_results and not self.fnb_results['matched'].empty:
                total_processed += len(self.fnb_results['matched'])
            total_processed += total_unmatched
            
            # Processing time if available
            avg_time = self.fnb_results.get('processing_time', 0)

        if self.bidvest_results and 'summary' in self.bidvest_results:
            summary = self.bidvest_results['summary']
            total_matched += summary.get('exact_matches', 0) + summary.get('grouped_matches', 0)
            total_unmatched += summary.get('unmatched_ledger', 0) + summary.get('unmatched_statement', 0)
            total_processed += summary.get('total_ledger', 0) + summary.get('total_statement', 0)
            if 'processing_time' in summary:
                avg_time = summary['processing_time']

        if total_processed > 0:
            success_rate = round((total_matched / (total_matched + total_unmatched)) * 100, 1)

        # Compact metric cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("✅ Matched", f"{total_matched:,}", delta=None)

        with col2:
            st.metric("❌ Unmatched", f"{total_unmatched:,}", delta=None)

        with col3:
            st.metric("📊 Success Rate", f"{success_rate}%", delta=None)

        with col4:
            st.metric("⚡ Processing", f"{avg_time:.1f}s", delta=None)


    def render_match_distribution_chart(self):
        """Render match distribution pie chart"""

        st.markdown("**Match Distribution**")

        # Aggregate match data from FNB results
        perfect_matches = 0
        fuzzy_matches = 0
        foreign_credits = 0
        split_matches = 0
        unmatched = 0

        if self.fnb_results:
            perfect_matches = self.fnb_results.get('perfect_match_count', 0)
            fuzzy_matches = self.fnb_results.get('fuzzy_match_count', 0)
            foreign_credits = self.fnb_results.get('foreign_credits_count', 0)
            split_matches = self.fnb_results.get('split_count', 0)
            unmatched = self.fnb_results.get('unmatched_ledger_count', 0) + self.fnb_results.get('unmatched_statement_count', 0)

        if self.bidvest_results and 'summary' in self.bidvest_results:
            summary = self.bidvest_results['summary']
            perfect_matches += summary.get('exact_matches', 0)
            split_matches += summary.get('grouped_matches', 0)
            unmatched += summary.get('unmatched_ledger', 0) + summary.get('unmatched_statement', 0)

        if perfect_matches + fuzzy_matches + foreign_credits + split_matches + unmatched > 0:
            data = {
                'Type': ['Perfect Matches', 'Fuzzy Matches', 'Foreign Credits', 'Split Transactions', 'Unmatched'],
                'Count': [perfect_matches, fuzzy_matches, foreign_credits, split_matches, unmatched]
            }

            df = pd.DataFrame(data)
            df = df[df['Count'] > 0]  # Remove zero values

            fig = px.pie(
                df,
                values='Count',
                names='Type',
                color='Type',
                color_discrete_map={
                    'Perfect Matches': '#10b981',
                    'Fuzzy Matches': '#3b82f6',
                    'Foreign Credits': '#8b5cf6',
                    'Split Transactions': '#f59e0b',
                    'Unmatched': '#ef4444'
                },
                hole=0.4
            )

            fig.update_layout(
                showlegend=True,
                height=350,
                margin=dict(t=30, b=0, l=0, r=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No reconciliation data yet. Run a workflow to see match distribution.")

    def render_reconciliation_trend(self):
        """Render reconciliation trend chart"""

        st.markdown("**Reconciliation Trend**")

        # Get history data
        history = st.session_state.get('reconciliation_history', [])

        if len(history) > 0:
            df = pd.DataFrame(history)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['matched'],
                name='Matched',
                mode='lines+markers',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8)
            ))

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['unmatched'],
                name='Unmatched',
                mode='lines+markers',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=8)
            ))

            fig.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                hovermode='x unified',
                xaxis_title="Date",
                yaxis_title="Transactions"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            # Show sample trend
            dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
            matched = [120, 135, 145, 150, 160, 155, 170]
            unmatched = [30, 25, 20, 18, 15, 12, 10]

            df = pd.DataFrame({
                'Date': dates,
                'Matched': matched,
                'Unmatched': unmatched
            })

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Matched'],
                name='Matched (Sample)',
                mode='lines+markers',
                line=dict(color='#10b981', width=3, dash='dot'),
                marker=dict(size=8)
            ))

            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Unmatched'],
                name='Unmatched (Sample)',
                mode='lines+markers',
                line=dict(color='#ef4444', width=3, dash='dot'),
                marker=dict(size=8)
            ))

            fig.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                hovermode='x unified',
                xaxis_title="Date",
                yaxis_title="Transactions"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption("📈 Sample data shown. Run reconciliations to see your actual trends.")

    def render_recent_activity(self):
        """Render recent reconciliation activity"""

        activities = []

        if self.fnb_results:
            total_matched = self.fnb_results.get('total_matched', 0)
            total_unmatched = self.fnb_results.get('unmatched_ledger_count', 0) + self.fnb_results.get('unmatched_statement_count', 0)
            total_items = total_matched + total_unmatched
            rate = round((total_matched / total_items * 100), 1) if total_items > 0 else 0
            
            activities.append({
                'workflow': '🏦 FNB Workflow',
                'time': self.fnb_results.get('timestamp', 'Recently'),
                'matches': total_matched,
                'rate': rate
            })

        if self.bidvest_results and 'summary' in self.bidvest_results:
            summary = self.bidvest_results['summary']
            total_matches = summary.get('exact_matches', 0) + summary.get('grouped_matches', 0)
            total_items = summary.get('total_ledger', 0)
            rate = round((total_matches / total_items * 100), 1) if total_items > 0 else 0

            activities.append({
                'workflow': '💼 Bidvest Workflow',
                'time': 'Recently',
                'matches': total_matches,
                'rate': rate
            })

        if activities:
            for act in activities:
                st.markdown(f"""
                <div class="workflow-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0;">{act['workflow']}</h4>
                            <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">
                                {act['time']}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #10b981;">
                                {act['matches']:,}
                            </p>
                            <p style="margin: 0; color: #6b7280; font-size: 0.85rem;">
                                {act['rate']}% match rate
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📋 No recent activity. Start a reconciliation workflow to see your activity here.")

    def render_audit_trail(self):
        """Render audit trail of user actions"""
        audit_trail = st.session_state.get('audit_trail', [])
        
        if audit_trail:
            # Show last 5 entries
            recent_audits = audit_trail[-5:]
            
            for audit in reversed(recent_audits):
                action_icon = {
                    'SAVE_RESULTS': '💾',
                    'RUN_RECONCILIATION': '▶️',
                    'EXPORT_DATA': '📥',
                    'DELETE_RESULT': '🗑️',
                    'EDIT_DATA': '✏️'
                }.get(audit['action'], '📌')
                
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 0.75rem; background: #f9fafb; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #667eea;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <span style="font-size: 1.1rem;">{action_icon}</span>
                                <strong>{audit['action'].replace('_', ' ').title()}</strong>
                            </div>
                            <span style="color: #6b7280; font-size: 0.85rem;">{audit['timestamp']}</span>
                        </div>
                        <div style="margin-top: 0.25rem; color: #6b7280; font-size: 0.85rem;">
                            User: {audit.get('user', 'N/A')} | Workflow: {audit.get('workflow', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if st.button("📖 View Full Audit Log", key='view_full_audit'):
                with st.expander("Complete Audit Trail", expanded=True):
                    audit_df = pd.DataFrame(audit_trail)
                    st.dataframe(audit_df, use_container_width=True, height=300)
                    
                    # Export audit log
                    st.download_button(
                        "📥 Export Audit Log",
                        audit_df.to_csv(index=False),
                        f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
        else:
            st.info("📋 No audit entries yet. Actions will be logged here.")

    def render_tips(self):
        """Render helpful tips and shortcuts"""

        with st.expander("💡 Tips & Best Practices"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                **🚀 Quick Workflow Selection:**
                - Use the workflow selector from sidebar
                - Or click quick action buttons above
                - Keyboard shortcut: Navigate with Tab

                **📁 Data Preparation:**
                - Ensure clean date formats
                - Remove special characters from amounts
                - Use consistent column headers
                """)

            with col2:
                st.markdown("""
                **🎯 Matching Tips:**
                - FNB: Adjust similarity threshold (default 85%)
                - Bidvest: Verify Date+1 logic is correct
                - Corporate: Set proper tolerance parameters

                **📊 Export Options:**
                - Download individual result sheets (CSV)
                - Or complete Excel workbook with all sheets
                - Results show all columns side-by-side
                """)

        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Common Questions:**

            1. **How do I run a reconciliation?**
               - Select a workflow from the sidebar or dashboard
               - Upload your ledger and statement files
               - Configure column mappings
               - Click "Start Reconciliation"

            2. **What file formats are supported?**
               - Excel (.xlsx, .xls)
               - CSV (.csv)

            3. **How are matches determined?**
               - FNB: Weighted scoring (Date 30%, Reference 40%, Amount 30%)
               - Bidvest: Date+1 exact match + grouped matches
               - Corporate: 5-tier batch system

            4. **Can I save my results?**
               - Yes! Use the "Export" buttons to download results
               - Save as CSV (individual sheets) or Excel (complete workbook)

            For more help, contact support or check the documentation.
            """)
