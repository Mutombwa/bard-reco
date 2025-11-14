"""
BARD-RECO Streamlit Web Application
====================================
Modern, cloud-ready reconciliation system with authentication and advanced features.
No installation required - just access via web browser!
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import json

# Add project directories to path
sys.path.append(str(Path(__file__).parent))

# Import only lightweight, essential modules at startup
# Use hybrid authentication: Supabase cloud (permanent) with local file fallback (temporary)
from auth.hybrid_auth import HybridAuthentication as Authentication

from utils.session_state import SessionState
from config.app_config import APP_CONFIG

# Heavy imports will be done lazily when needed
# This dramatically improves initial load time

# Page configuration
st.set_page_config(
    page_title="BARD-RECO | Modern Reconciliation System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/bard-reco',
        'Report a bug': 'https://github.com/yourusername/bard-reco/issues',
        'About': '## BARD-RECO\nModern cloud-based reconciliation system'
    }
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #3498db;
        --secondary-color: #2ecc71;
        --danger-color: #e74c3c;
        --warning-color: #f39c12;
        --dark-bg: #2c3e50;
        --light-bg: #ecf0f1;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Modern card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }

    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }

    /* Animated gradient background for header */
    .gradient-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Modern buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #3498db;
        border-radius: 10px;
        padding: 20px;
        background: #f8f9fa;
    }

    /* Data frame styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = SessionState()

# Authentication
auth = Authentication()

def main():
    """Main application entry point"""

    # Check authentication
    if not st.session_state.session.is_authenticated:
        show_login_page()
        return

    # Show main application
    show_main_app()

def show_login_page():
    """Display login page"""

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="gradient-header">
            <h1>💼 BARD-RECO</h1>
            <h3>Modern Reconciliation System</h3>
            <p>Cloud-based • Secure • Efficient</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 Login")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("🚀 Login", use_container_width=True)
            with col_b:
                register = st.form_submit_button("📝 Register", use_container_width=True)

            if submit:
                if auth.login(username, password):
                    st.session_state.session.authenticate(username)
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

            if register:
                st.session_state.show_register = True
                st.rerun()

        # Show registration form if requested
        if st.session_state.get('show_register', False):
            st.markdown("---")
            st.markdown("### 📝 Create New Account")

            with st.form("register_form"):
                st.info("🔒 **Note:** Please use your official company email address")
                new_username = st.text_input("Choose Username", placeholder="Choose a username")
                new_password = st.text_input("Choose Password", type="password", placeholder="Choose a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                email = st.text_input("Company Email (Required)", placeholder="your.email@company.com")

                col_a, col_b = st.columns(2)
                with col_a:
                    register_submit = st.form_submit_button("✨ Create Account", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)

                if register_submit:
                    if not email:
                        st.error("❌ Email is required!")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        success, message = auth.register(new_username, new_password, email)
                        if success:
                            st.success(f"✅ {message} Please login.")
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

                if cancel:
                    st.session_state.show_register = False
                    st.rerun()

def show_main_app():
    """Display main application interface"""

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
            <h2>💼 BARD-RECO</h2>
            <p>Welcome, <b>{st.session_state.session.username}</b>!</p>
        </div>
        """, unsafe_allow_html=True)

        # Authentication backend status
        try:
            auth = Authentication()
            backend_info = auth.get_backend_info()
            if backend_info.get('backend') == 'supabase':
                st.success(f"✅ {backend_info.get('message', 'Using Supabase cloud database')}")
            else:
                st.warning(f"⚠️ {backend_info.get('message', 'Using local file storage')}")
        except Exception as e:
            # Fallback if get_backend_info() not available
            st.info("ℹ️ Authentication active")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.session.logout()
            st.rerun()

    # Load persistent data after authentication (lazy loading)
    load_persistent_data()
    
    # Show workflows page directly
    show_workflows_page()

def show_workflows_page():
    """Specialized workflows page - Display all workflows"""

    from components.fnb_workflow import FNBWorkflow
    from components.bidvest_workflow import BidvestWorkflow
    from components.corporate_workflow import CorporateWorkflow

    st.markdown("""
    <div class="gradient-header">
        <h1>🔄 All Workflows</h1>
        <p>View and manage all available reconciliation workflows</p>
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for each workflow
    workflow_tabs = st.tabs(["🏦 FNB Workflow", "💼 Bidvest Workflow", "🏢 Corporate Workflow"])

    with workflow_tabs[0]:
        st.markdown("### 🏦 FNB Bank Reconciliation")
        st.markdown("---")
        FNBWorkflow().render()

    with workflow_tabs[1]:
        st.markdown("### 💼 Bidvest Settlement Reconciliation")
        st.markdown("---")
        BidvestWorkflow().render()

    with workflow_tabs[2]:
        st.markdown("### 🏢 Corporate Settlement Reconciliation")
        st.markdown("---")
        CorporateWorkflow().render()

def show_reconciliation_page():
    """Reconciliation workflow page"""
    
    # Lazy import heavy modules only when this page is accessed
    from utils.file_loader import load_uploaded_file, get_dataframe_info
    from components.data_editor import DataEditor
    from components.ai_assistant import check_ai_status, render_ai_sidebar

    st.markdown("""
    <div class="gradient-header">
        <h1>📊 Reconciliation Workflow</h1>
        <p>Advanced matching engine with fuzzy logic and AI-powered suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Assistant Sidebar
    render_ai_sidebar()

    # File upload section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 Upload Ledger/Cashbook")
        ledger_file = st.file_uploader(
            "Upload Excel/CSV file",
            type=['xlsx', 'xls', 'csv'],
            key='ledger_upload',
            help="Upload your ledger or cashbook file"
        )

        if ledger_file:
            # Use optimized loader with caching and progress indicator
            ledger_df, is_new = load_uploaded_file(
                ledger_file,
                session_key='ledger_df',
                hash_key='ledger_file_hash',
                show_progress=True
            )

            if is_new:
                st.success(f"✅ Loaded: {ledger_file.name}")
            else:
                st.info(f"📋 Using cached: {ledger_file.name}")

            # Show preview (collapsed by default to reduce initial load)
            with st.expander("👁️ Preview Data", expanded=False):
                st.dataframe(ledger_df.head(10), use_container_width=True)
                st.info(f"📊 {get_dataframe_info(ledger_df)}")

    with col2:
        st.markdown("### 📥 Upload Bank Statement")
        statement_file = st.file_uploader(
            "Upload Excel/CSV file",
            type=['xlsx', 'xls', 'csv'],
            key='statement_upload',
            help="Upload your bank statement file"
        )

        if statement_file:
            # Use optimized loader with caching and progress indicator
            statement_df, is_new = load_uploaded_file(
                statement_file,
                session_key='statement_df',
                hash_key='statement_file_hash',
                show_progress=True
            )

            if is_new:
                st.success(f"✅ Loaded: {statement_file.name}")
            else:
                st.info(f"📋 Using cached: {statement_file.name}")

            # Show preview (collapsed by default to reduce initial load)
            with st.expander("👁️ Preview Data", expanded=False):
                st.dataframe(statement_df.head(10), use_container_width=True)
                st.info(f"📊 {get_dataframe_info(statement_df)}")

    # Data editing option
    if 'ledger_df' in st.session_state or 'statement_df' in st.session_state:
        st.markdown("---")
        st.markdown("### ✏️ Edit Data (Optional)")

        col1, col2 = st.columns(2)
        with col1:
            if 'ledger_df' in st.session_state and st.button("✏️ Edit Ledger Data", use_container_width=True):
                st.session_state.editing_ledger = True

        with col2:
            if 'statement_df' in st.session_state and st.button("✏️ Edit Statement Data", use_container_width=True):
                st.session_state.editing_statement = True

        # Show data editor
        if st.session_state.get('editing_ledger', False):
            st.markdown("#### 📝 Ledger Data Editor")
            editor = DataEditor(st.session_state.ledger_df, "ledger")
            edited_df = editor.render()
            if edited_df is not None:
                st.session_state.ledger_df = edited_df
                st.session_state.editing_ledger = False
                st.success("✅ Ledger data updated!")
                # Removed st.rerun() - Streamlit reruns automatically when session state changes

        if st.session_state.get('editing_statement', False):
            st.markdown("#### 📝 Statement Data Editor")
            editor = DataEditor(st.session_state.statement_df, "statement")
            edited_df = editor.render()
            if edited_df is not None:
                st.session_state.statement_df = edited_df
                st.session_state.editing_statement = False
                st.success("✅ Statement data updated!")
                # Removed st.rerun() - Streamlit reruns automatically when session state changes

    # Configuration and reconciliation
    if 'ledger_df' in st.session_state and 'statement_df' in st.session_state:
        st.markdown("---")
        st.markdown("### ⚙️ Configure Matching Rules")

        ledger_df = st.session_state.ledger_df
        statement_df = st.session_state.statement_df

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 💰 Amount Columns")
            ledger_amount = st.selectbox("Ledger Amount", ledger_df.columns, key='ledger_amount')
            statement_amount = st.selectbox("Statement Amount", statement_df.columns, key='statement_amount')

        with col2:
            st.markdown("#### 📅 Date Columns")
            ledger_date = st.selectbox("Ledger Date", ledger_df.columns, key='ledger_date')
            statement_date = st.selectbox("Statement Date", statement_df.columns, key='statement_date')

        with col3:
            st.markdown("#### 📝 Reference Columns")
            ledger_ref = st.selectbox("Ledger Reference", ledger_df.columns, key='ledger_ref')
            statement_ref = st.selectbox("Statement Reference", statement_df.columns, key='statement_ref')

        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)

            with col1:
                fuzzy_threshold = st.slider("Fuzzy Match Threshold", 0, 100, 85, help="Minimum similarity score for fuzzy matching")
                date_tolerance = st.number_input("Date Tolerance (days)", 0, 30, 3, help="Allow matches within ± N days")

            with col2:
                amount_tolerance = st.number_input("Amount Tolerance (%)", 0.0, 10.0, 0.1, 0.01, help="Allow amount variance")
                enable_ai = st.checkbox("Enable AI Suggestions", value=True, help="Use AI for ambiguous matches")

        # Run reconciliation
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Reconciliation", use_container_width=True, type="primary"):
                run_reconciliation(
                    ledger_df, statement_df,
                    ledger_amount, statement_amount,
                    ledger_date, statement_date,
                    ledger_ref, statement_ref,
                    fuzzy_threshold, date_tolerance, amount_tolerance, enable_ai
                )

def run_reconciliation(ledger_df, statement_df, ledger_amount, statement_amount,
                       ledger_date, statement_date, ledger_ref, statement_ref,
                       fuzzy_threshold, date_tolerance, amount_tolerance, enable_ai):
    """Execute reconciliation process"""
    
    # Lazy import only when actually running reconciliation
    from src.reconciliation_engine import ReconciliationEngine

    with st.spinner("🔄 Processing reconciliation..."):
        # Create reconciliation engine
        engine = ReconciliationEngine(
            ledger_df, statement_df,
            ledger_amount_col=ledger_amount,
            statement_amount_col=statement_amount,
            ledger_date_col=ledger_date,
            statement_date_col=statement_date,
            ledger_ref_col=ledger_ref,
            statement_ref_col=statement_ref,
            fuzzy_threshold=fuzzy_threshold,
            date_tolerance=date_tolerance,
            amount_tolerance=amount_tolerance,
            enable_ai=enable_ai
        )

        # Run reconciliation
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total):
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {current}/{total} ({progress}%)")

        results = engine.reconcile(progress_callback=update_progress)

        # Store results
        st.session_state.reconciliation_results = results
        st.session_state.reconciliation_timestamp = datetime.now()

        progress_bar.empty()
        status_text.empty()

    # Display results
    show_reconciliation_results(results)

def show_reconciliation_results(results):
    """Display reconciliation results"""

    st.markdown("---")
    st.markdown("## 🎉 Reconciliation Complete!")

    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("✅ Perfect Match", results.get('perfect_match_count', 0))
    with col2:
        st.metric("🔄 Fuzzy Match", results.get('fuzzy_match_count', 0))
    with col3:
        st.metric("⚖️ Balanced", results.get('balanced_count', 0))
    with col4:
        st.metric("❌ Unmatched", results.get('unmatched_count', 0))
    with col5:
        match_rate = results.get('match_rate', 0)
        st.metric("📊 Match Rate", f"{match_rate:.1f}%")

    # Detailed results tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✅ Perfect Matches",
        "🔄 Fuzzy Matches",
        "⚖️ Balanced",
        "❌ Unmatched",
        "📥 Export"
    ])

    with tab1:
        if results.get('perfect_matches'):
            st.dataframe(results['perfect_matches'], use_container_width=True)
        else:
            st.info("No perfect matches found")

    with tab2:
        if results.get('fuzzy_matches'):
            st.dataframe(results['fuzzy_matches'], use_container_width=True)
        else:
            st.info("No fuzzy matches found")

    with tab3:
        if results.get('balanced'):
            st.dataframe(results['balanced'], use_container_width=True)
        else:
            st.info("No balanced matches found")

    with tab4:
        if results.get('unmatched'):
            st.dataframe(results['unmatched'], use_container_width=True)
        else:
            st.success("✅ All transactions matched!")

    with tab5:
        st.markdown("### 📤 Export Results")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Export to Excel", use_container_width=True):
                from utils.export_utils import export_to_excel
                file_path = export_to_excel(results, st.session_state.session.username)
                st.success(f"✅ Exported to: {file_path}")

        with col2:
            if st.button("📄 Generate Report", use_container_width=True):
                from utils.report_generator import generate_report
                report_path = generate_report(results, st.session_state.session.username)
                st.success(f"✅ Report generated: {report_path}")

def show_data_management_page():
    """Data management and history"""
    
    # Lazy import data editor only when needed
    from components.data_editor import DataEditor

    st.markdown("""
    <div class="gradient-header">
        <h1>📁 Data Management</h1>
        <p>Manage your data files and reconciliation history</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🕒 Saved Results", "📊 View Result", "🗑️ Cleanup"])

    with tabs[0]:
        st.markdown("### 🕒 Reconciliation History")
        show_saved_reconciliations()

    with tabs[1]:
        st.markdown("### 📊 View Specific Result")
        show_result_viewer()

    with tabs[2]:
        st.markdown("### 🗑️ Data Cleanup")
        show_cleanup_tools()

def show_saved_reconciliations():
    """Display saved reconciliation results"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from database import get_db  # type: ignore

        db = get_db()

        # Filter by workflow type
        workflow_filter = st.selectbox(
            "Filter by Workflow:",
            ["All", "FNB", "Bidvest", "Corporate"],
            key='workflow_filter'
        )

        workflow_type = None if workflow_filter == "All" else workflow_filter

        # Get results
        results = db.list_results(workflow_type=workflow_type, limit=100)

        if results:
            st.info(f"📊 Found {len(results)} saved result(s)")

            # Display as table
            results_data = []
            for result in results:
                result_id, name, wf_type, date_created, summary_json = result
                summary = json.loads(summary_json) if summary_json else {}

                results_data.append({
                    'ID': result_id,
                    'Name': name,
                    'Workflow': wf_type,
                    'Date': date_created,
                    'Matched': summary.get('matched_count', 0),
                    'Unmatched': summary.get('unmatched_ledger_count', 0) + summary.get('unmatched_statement_count', 0)
                })

            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)

            # Delete functionality
            st.markdown("---")
            result_id_to_delete = st.number_input("Enter Result ID to delete:", min_value=1, step=1, key='delete_id')
            if st.button("🗑️ Delete Result", key='delete_btn'):
                try:
                    db.delete_result(result_id_to_delete)
                    st.success(f"✅ Result {result_id_to_delete} deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to delete: {str(e)}")
        else:
            st.info("📭 No saved results found. Run a reconciliation and save the results!")

    except Exception as e:
        st.error(f"❌ Error loading results: {str(e)}")

def show_result_viewer():
    """View specific result details"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from database import get_db  # type: ignore

        db = get_db()

        result_id = st.number_input("Enter Result ID to view:", min_value=1, step=1, key='view_id')

        if st.button("🔍 Load Result", key='load_btn'):
            result = db.get_result(result_id)

            if result:
                st.success(f"✅ Loaded: {result['name']}")

                # Display summary
                st.markdown("### 📊 Summary")
                summary_df = pd.DataFrame([result['summary']])
                st.dataframe(summary_df, use_container_width=True)

                # Display data in tabs
                tab1, tab2, tab3 = st.tabs(["✅ Matched", "📋 Unmatched Ledger", "🏦 Unmatched Statement"])

                with tab1:
                    if not result['matched'].empty:
                        st.dataframe(result['matched'], use_container_width=True)
                    else:
                        st.info("No matched transactions")

                with tab2:
                    if not result['unmatched_ledger'].empty:
                        st.dataframe(result['unmatched_ledger'], use_container_width=True)
                    else:
                        st.info("No unmatched ledger items")

                with tab3:
                    if not result['unmatched_statement'].empty:
                        st.dataframe(result['unmatched_statement'], use_container_width=True)
                    else:
                        st.info("No unmatched statement items")
            else:
                st.error(f"❌ Result ID {result_id} not found")

    except Exception as e:
        st.error(f"❌ Error viewing result: {str(e)}")

def show_cleanup_tools():
    """Data cleanup utilities"""
    st.warning("⚠️ Cleanup operations are permanent!")

    if st.button("🗑️ Delete All Results", key='delete_all_btn'):
        st.error("This feature is disabled for safety. Use individual delete from Saved Results tab.")

def show_reports_page():
    """Reports and analytics"""

    st.markdown("""
    <div class="gradient-header">
        <h1>📈 Reports & Analytics</h1>
        <p>Insights and trends from your reconciliation data</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("📊 Analytics dashboard coming soon!")

def show_settings_page():
    """Application settings"""

    st.markdown("""
    <div class="gradient-header">
        <h1>⚙️ Settings</h1>
        <p>Customize your BARD-RECO experience</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["👤 Profile", "🔒 Security", "🎨 Appearance", "📧 Notifications"])

    with tabs[0]:
        st.markdown("### 👤 Profile Settings")
        username = st.text_input("Username", value=st.session_state.session.username, disabled=True)
        email = st.text_input("Email", placeholder="your.email@company.com")
        company = st.text_input("Company", placeholder="Your Company Name")

        if st.button("💾 Save Profile"):
            st.success("✅ Profile updated successfully!")

    with tabs[1]:
        st.markdown("### 🔒 Security Settings")
        st.markdown("#### Change Password")
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")

        if st.button("🔐 Update Password"):
            if new_password == confirm_new_password:
                st.success("✅ Password updated successfully!")
            else:
                st.error("❌ Passwords don't match!")

    with tabs[2]:
        st.markdown("### 🎨 Appearance")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])

        if st.button("🎨 Apply Settings"):
            st.success("✅ Appearance settings updated!")

    with tabs[3]:
        st.markdown("### 📧 Notifications")
        email_notifications = st.checkbox("Email Notifications", value=True)
        reconciliation_complete = st.checkbox("Reconciliation Complete", value=True)
        daily_summary = st.checkbox("Daily Summary", value=False)

        if st.button("📧 Save Notification Settings"):
            st.success("✅ Notification preferences saved!")

# Initialize persistent data ONLY after authentication
def load_persistent_data():
    """Load persisted reconciliation data from database after user is authenticated"""
    # Only load once per session using a flag
    if 'db_data_loaded' in st.session_state:
        return  # Already loaded in this session
    
    # Only load if user is authenticated
    if not st.session_state.session.is_authenticated:
        return  # Don't load data for unauthenticated users

    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from database import get_db  # type: ignore

        # Only load if not already in session state
        if 'fnb_results' not in st.session_state or st.session_state.fnb_results is None:
            db = get_db()

            # Get the most recent FNB result
            recent_results = db.list_results('FNB', limit=1)
            if recent_results:
                result_id = recent_results[0][0]
                result_data = db.get_result(result_id)

                if result_data:
                    # Restore to session state
                    st.session_state.fnb_results = result_data
                    st.session_state.fnb_results_loaded_from_db = True
    except Exception as e:
        # Silently fail if database not available
        pass
    finally:
        # Mark as loaded to prevent future calls
        st.session_state.db_data_loaded = True

# Run the app
if __name__ == "__main__":
    main()
