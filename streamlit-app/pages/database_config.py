"""
Database Configuration Page
===========================
Configure SQL Server connection and manage database schema
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.sql_database import ReconciliationDatabase


def show_database_config():
    """Show database configuration page"""
    st.title("🗄️ SQL Server Configuration")
    
    # Check if pyodbc is available
    from utils.sql_database import PYODBC_AVAILABLE
    
    if not PYODBC_AVAILABLE:
        st.error("❌ SQL Server features are not available on Streamlit Cloud")
        st.info("""
        💡 **SQL Server integration is only available when running locally**
        
        To use SQL Server features:
        1. Run the app locally: `streamlit run app.py`
        2. Ensure SQL Server and ODBC Driver 17 are installed
        3. Follow the setup guide: `SQL_SERVER_SETUP_GUIDE.md`
        
        For cloud deployment, consider using:
        - PostgreSQL (Supabase)
        - MySQL (PlanetScale)
        - SQLite (local storage)
        - Cloud-native databases
        """)
        return
    
    st.markdown("""
    Configure your SQL Server connection to save reconciliation results.
    """)
    
    # Connection Configuration
    st.subheader("Connection Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server = st.text_input(
            "Server Address",
            value=st.session_state.get('sql_server', 'localhost'),
            help="SQL Server address (e.g., localhost or server.database.windows.net)"
        )
        
        database = st.text_input(
            "Database Name",
            value=st.session_state.get('sql_database', 'ReconciliationDB'),
            help="Name of the database to use"
        )
    
    with col2:
        auth_type = st.radio(
            "Authentication Type",
            ["Windows Authentication", "SQL Server Authentication"],
            index=0 if st.session_state.get('sql_auth_type', 'Windows') == 'Windows' else 1
        )
        
        if auth_type == "SQL Server Authentication":
            username = st.text_input(
                "Username",
                value=st.session_state.get('sql_username', '')
            )
            password = st.text_input(
                "Password",
                type="password",
                value=st.session_state.get('sql_password', '')
            )
    
    # Test Connection Button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔌 Test Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                # Build connection string
                if auth_type == "Windows Authentication":
                    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
                else:
                    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                
                db = ReconciliationDatabase(conn_str)
                
                if db.connect():
                    st.success("✅ Connection successful!")
                    
                    # Save to session state
                    st.session_state['sql_server'] = server
                    st.session_state['sql_database'] = database
                    st.session_state['sql_auth_type'] = 'Windows' if auth_type == "Windows Authentication" else 'SQL'
                    if auth_type == "SQL Server Authentication":
                        st.session_state['sql_username'] = username
                        st.session_state['sql_password'] = password
                    st.session_state['sql_connection_string'] = conn_str
                    
                    db.disconnect()
                else:
                    st.error("❌ Connection failed. Please check your settings.")
    
    with col2:
        if st.button("📋 Create Tables", use_container_width=True):
            if 'sql_connection_string' not in st.session_state:
                st.error("Please test connection first!")
            else:
                with st.spinner("Creating database tables..."):
                    db = ReconciliationDatabase(st.session_state['sql_connection_string'])
                    
                    if db.create_tables():
                        st.success("✅ Database tables created successfully!")
                    else:
                        st.error("❌ Failed to create tables. Check permissions.")
    
    # Database Schema Documentation
    st.divider()
    st.subheader("📊 Database Schema")
    
    with st.expander("View Database Structure", expanded=False):
        st.markdown("""
        ### Tables Created:
        
        **1. ReconciliationSessions**
        - SessionID (Primary Key)
        - WorkflowType (FNB, Corporate, etc.)
        - Username
        - StartTime, EndTime
        - Status (In Progress/Completed/Failed)
        - TotalMatched, TotalUnmatched, MatchRate
        
        **2. MatchedTransactions**
        - TransactionID (Primary Key)
        - SessionID (Foreign Key)
        - MatchType (Perfect/Fuzzy/Amount/Split)
        - Ledger fields (Date, Reference, Debit, Credit, Description)
        - Statement fields (Date, Reference, Amount, Description)
        - MatchScore, Currency
        
        **3. SplitTransactions**
        - SplitID (Primary Key)
        - SessionID (Foreign Key)
        - SplitType (Many-to-One/One-to-Many)
        - TotalAmount, ComponentCount
        
        **4. SplitComponents**
        - ComponentID (Primary Key)
        - SplitID (Foreign Key)
        - TransactionSource (Ledger/Statement)
        - Transaction details
        
        **5. UnmatchedTransactions**
        - UnmatchedID (Primary Key)
        - SessionID (Foreign Key)
        - Source (Ledger/Statement)
        - Transaction details
        
        **6. ForeignCredits**
        - ForeignCreditID (Primary Key)
        - SessionID (Foreign Key)
        - Ledger and Statement transaction details
        """)
    
    # View Saved Data
    st.divider()
    st.subheader("📈 Session History")
    
    if 'sql_connection_string' in st.session_state:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🔄 Refresh History", use_container_width=True):
                st.rerun()
        
        db = ReconciliationDatabase(st.session_state['sql_connection_string'])
        
        username_filter = st.session_state.get('current_user', None)
        history_df = db.get_session_history(username=username_filter, limit=50)
        
        if not history_df.empty:
            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SessionID": "Session ID",
                    "WorkflowType": "Workflow",
                    "StartTime": st.column_config.DatetimeColumn("Start Time", format="DD/MM/YYYY HH:mm"),
                    "EndTime": st.column_config.DatetimeColumn("End Time", format="DD/MM/YYYY HH:mm"),
                    "MatchRate": st.column_config.NumberColumn("Match Rate", format="%.2f%%")
                }
            )
            
            # View session details
            st.subheader("View Session Details")
            session_id = st.number_input("Enter Session ID", min_value=1, step=1)
            
            if st.button("📊 Load Session Details"):
                details = db.get_session_details(session_id)
                
                if details:
                    st.success(f"Session {session_id} loaded")
                    
                    # Show session info
                    if 'session' in details:
                        st.json(details['session'])
                    
                    # Show matched transactions
                    if 'matched' in details and not details['matched'].empty:
                        st.subheader("Matched Transactions")
                        st.dataframe(details['matched'], use_container_width=True)
                    
                    # Show unmatched transactions
                    if 'unmatched' in details and not details['unmatched'].empty:
                        st.subheader("Unmatched Transactions")
                        st.dataframe(details['unmatched'], use_container_width=True)
                    
                    # Show splits
                    if 'splits' in details and not details['splits'].empty:
                        st.subheader("Split Transactions")
                        st.dataframe(details['splits'], use_container_width=True)
                else:
                    st.error("Session not found")
        else:
            st.info("No reconciliation sessions found in database")
    else:
        st.info("👆 Please configure and test database connection first")


if __name__ == "__main__":
    show_database_config()
