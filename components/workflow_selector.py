"""
Workflow Selector Component
===========================
Select between FNB, Bidvest, and Corporate Settlements workflows
"""

import streamlit as st

class WorkflowSelector:
    """Workflow selection interface"""

    def __init__(self):
        self.workflows = {
            'fnb': {
                'name': '🏦 FNB Workflow',
                'description': 'Bank reconciliation with FNB-specific matching logic',
                'features': ['Date matching', 'Reference matching', 'Amount matching', 'Advanced filtering']
            },
            'absa': {
                'name': '🏦 ABSA Workflow',
                'description': 'ABSA Bank reconciliation with auto Reference & Fee extraction',
                'features': ['Auto extract Reference', 'Auto extract Fee', 'Date matching', 'Amount matching']
            },
            'bidvest': {
                'name': '🏢 Bidvest Workflow',
                'description': 'Bidvest settlement reconciliation with batch processing',
                'features': ['Batch matching', 'Foreign currency', 'Settlement tracking', 'Advanced reporting']
            },
            'corporate': {
                'name': '💼 Corporate Settlements',
                'description': 'Corporate settlement matching with multi-tier batch processing',
                'features': ['5-tier matching', 'Ultra-fast processing', 'Batch separation', 'Professional export']
            }
        }

    def render(self):
        """Render workflow selection page"""

        st.markdown("""
        <div class="gradient-header">
            <h1>🎯 Select Your Workflow</h1>
            <p>Choose the reconciliation workflow that matches your needs</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Display workflow cards
        cols = st.columns(3)

        for idx, (key, workflow) in enumerate(self.workflows.items()):
            with cols[idx]:
                self._render_workflow_card(key, workflow)

        st.markdown("---")

        # Quick comparison table
        st.markdown("### 📊 Workflow Comparison")

        comparison_data = {
            'Feature': ['Best For', 'Speed', 'Complexity', 'Batch Support', 'Currency Support'],
            '🏦 FNB': ['Bank Statements', 'Fast', 'Medium', 'No', 'ZAR'],
            '🏢 Bidvest': ['Settlements', 'Fast', 'Medium', 'Yes', 'Multi'],
            '💼 Corporate': ['Bulk Settlements', 'Ultra-Fast', 'Low', 'Yes (5-tier)', 'Multi']
        }

        st.table(comparison_data)

    def _render_workflow_card(self, key, workflow):
        """Render a single workflow card"""

        st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
            border-left: 4px solid #3498db;
        ">
            <h3>{workflow['name']}</h3>
            <p style="color: #666;">{workflow['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Features
        st.markdown("**Features:**")
        for feature in workflow['features']:
            st.markdown(f"• {feature}")

        # Select button
        if st.button(f"Select {workflow['name']}", key=f"select_{key}", use_container_width=True, type="primary"):
            st.session_state.selected_workflow = key
            st.rerun()
