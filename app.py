"""
BARD-RECO Streamlit Application Entry Point
============================================
This file serves as the entry point for Streamlit Cloud deployment.
It imports and runs the main application from the streamlit-app directory.
"""

import sys
from pathlib import Path

# Add streamlit-app directory to path
app_dir = Path(__file__).parent / "streamlit-app"
sys.path.insert(0, str(app_dir))

# Import and run the main app
import streamlit as st
import pandas as pd
from datetime import datetime

# Add project directories to path
sys.path.append(str(app_dir))

from auth.authentication import Authentication
from components.data_editor import DataEditor
from components.dashboard import Dashboard
from src.reconciliation_engine import ReconciliationEngine
from utils.session_state import SessionState
from config.app_config import APP_CONFIG
from pages.database_config import show_database_config

# Page configuration
st.set_page_config(
    page_title="BARD-RECO | Modern Reconciliation System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Mutombwa/bard-reco',
        'Report a bug': 'https://github.com/Mutombwa/bard-reco/issues',
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
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 20px;
        background: #f8f9fa;
    }

    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'


def show_login_page():
    """Display login page"""
    st.markdown('<div class="gradient-header"><h1>🔐 BARD-RECO Login</h1><p>Modern Reconciliation System</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Please Login")
        
        # Use a form to better handle autofill
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="admin", autocomplete="username")
            password = st.text_input("Password", type="password", placeholder="admin123", autocomplete="current-password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_submitted = st.form_submit_button("🔓 Login", use_container_width=True)
            with col_b:
                # Note: Can't have another submit button in the same form
                pass
        
        # Handle login outside the form
        if login_submitted:
            username_val = username.strip() if username else ""
            password_val = password.strip() if password else ""
            
            if username_val and password_val:
                # Simple authentication check
                if (username_val == "admin" and password_val == "admin123") or (username_val == "demo" and password_val == "demo"):
                    st.session_state.authenticated = True
                    st.session_state.username = username_val
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try: admin/admin123 or demo/demo")
            else:
                st.warning("⚠️ Please enter both username and password")
        
        # Demo mode button outside the form
        if st.button("📝 Demo Mode", use_container_width=True, key="demo_mode_btn"):
            st.session_state.authenticated = True
            st.session_state.username = "Demo User"
            st.session_state.current_page = 'dashboard'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.info("💡 **Demo Mode** - Try the system without authentication\n\n🔑 **Login credentials**: admin/admin123 or demo/demo")


def show_dashboard():
    """Display main dashboard"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.username}!")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "📊 FNB Workflow", "🏢 Bidvest Workflow", "🏦 Corporate Settlements", "🗄️ Database Config", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Main content based on navigation
    if "Dashboard" in page:
        show_main_dashboard()
    elif "FNB" in page:
        show_fnb_workflow()
    elif "Bidvest" in page:
        show_bidvest_workflow()
    elif "Corporate" in page:
        show_corporate_workflow()
    elif "Database" in page:
        show_database_config()
    elif "Settings" in page:
        show_settings()


def show_main_dashboard():
    """Show main dashboard with overview"""
    st.markdown('<div class="gradient-header"><h1>💼 BARD-RECO Dashboard</h1><p>Modern Cloud-Based Reconciliation System</p></div>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Transactions", "0", "0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Matched", "0", "0%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Unmatched", "0", "0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Success Rate", "0%", "0%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Start FNB Reconciliation", use_container_width=True):
            st.session_state.current_workflow = 'fnb'
            st.rerun()
    
    with col2:
        if st.button("🏢 Start Bidvest Reconciliation", use_container_width=True):
            st.session_state.current_workflow = 'bidvest'
            st.rerun()
    
    with col3:
        if st.button("🏦 Corporate Settlements", use_container_width=True):
            st.session_state.current_workflow = 'corporate'
            st.rerun()


def show_fnb_workflow():
    """FNB reconciliation workflow"""
    from components.fnb_workflow import FNBWorkflow
    workflow = FNBWorkflow()
    workflow.render()


def show_bidvest_workflow():
    """Bidvest reconciliation workflow"""
    from components.bidvest_workflow import BidvestWorkflow
    workflow = BidvestWorkflow()
    workflow.render()


def show_corporate_workflow():
    """Corporate settlements workflow"""
    from components.corporate_workflow import CorporateWorkflow
    workflow = CorporateWorkflow()
    workflow.render()


def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    st.info("Settings page - Configure your preferences")


def main():
    """Main application entry point"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
