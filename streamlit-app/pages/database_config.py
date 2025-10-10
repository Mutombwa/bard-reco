"""
Database Configuration Page
===========================
Configure database connection and manage database schema
Supports: SQL Server (local) and PostgreSQL/Supabase (cloud)
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.sql_database import ReconciliationDatabase, PYODBC_AVAILABLE
from utils.postgres_database import PostgreSQLDatabase, PSYCOPG2_AVAILABLE


def show_database_config():
    """Show database configuration page"""
    st.title("🗄️ Database Configuration")
    
    st.markdown("""
    Configure your database connection to save reconciliation results permanently.
    """)
    
    # Database Type Selection
    st.subheader("Select Database Type")
    
    db_type = st.radio(
        "Database",
        ["PostgreSQL/Supabase (Cloud Compatible ✅)", "SQL Server (Local Only 🖥️)"],
        help="PostgreSQL works on Streamlit Cloud. SQL Server only works locally."
    )
    
    if "SQL Server" in db_type:
        show_sql_server_config()
    else:
        show_postgres_config()


def show_postgres_config():
    """Configure PostgreSQL/Supabase connection"""
    
    if not PSYCOPG2_AVAILABLE:
        st.error("❌ PostgreSQL driver not installed")
        st.info("💡 Add to requirements.txt: `psycopg2-binary>=2.9.0`")
        return
    
    st.markdown("### 🐘 PostgreSQL/Supabase Connection")
    
    # Connection string or individual fields
    connection_method = st.radio(
        "Connection Method",
        ["Connection String", "Individual Fields"],
        horizontal=True
    )
    
    if connection_method == "Connection String":
        conn_string = st.text_input(
            "Connection String",
            value=st.session_state.get('postgres_conn_string', ''),
            type="password",
            help="postgresql://user:password@host:port/database",
            placeholder="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input(
                "Host",
                value=st.session_state.get('postgres_host', 'db.cmlbornqaojclzrtqffh.supabase.co'),
                help="Database host address"
            )
            database = st.text_input(
                "Database",
                value=st.session_state.get('postgres_database', 'postgres'),
                help="Database name"
            )
        
        with col2:
            user = st.text_input(
                "Username",
                value=st.session_state.get('postgres_user', 'postgres'),
                help="Database username"
            )
            password = st.text_input(
                "Password",
                type="password",
                value=st.session_state.get('postgres_password', ''),
                help="Database password"
            )
            port = st.text_input(
                "Port",
                value=st.session_state.get('postgres_port', '5432'),
                help="Database port"
            )
        
        # Build connection string from individual fields
        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Test Connection Button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔌 Test Connection", use_container_width=True, key="pg_test"):
            with st.spinner("Testing PostgreSQL connection..."):
                # Rebuild connection string with current values
                if connection_method == "Connection String":
                    test_conn_string = conn_string
                else:
                    # Use the text input values directly
                    test_conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                
                # Show connection string for debugging (without password)
                debug_string = test_conn_string.replace(password, "****")
                st.info(f"Connecting to: {debug_string}")
                
                db = PostgreSQLDatabase(test_conn_string)
                
                if db.connect():
                    st.success("✅ Connection successful!")
                    
                    # Save to session state
                    st.session_state['postgres_conn_string'] = test_conn_string
                    if connection_method == "Individual Fields":
                        st.session_state['postgres_host'] = host
                        st.session_state['postgres_database'] = database
                        st.session_state['postgres_user'] = user
                        st.session_state['postgres_password'] = password
                        st.session_state['postgres_port'] = port
                    
                    db.disconnect()
                else:
                    st.error("❌ Connection failed. Please check your settings.")
    
    with col2:
        if st.button("📋 Create Tables", use_container_width=True, key="pg_create"):
            if 'postgres_conn_string' not in st.session_state:
                st.error("Please test connection first!")
            else:
                with st.spinner("Creating database tables..."):
                    db = PostgreSQLDatabase(st.session_state['postgres_conn_string'])
                    
                    if db.create_tables():
                        st.success("✅ Database tables created successfully!")
                    else:
                        st.error("❌ Failed to create tables. Check permissions.")
    
    # Supabase Quick Setup Guide
    with st.expander("📖 Supabase Setup Guide", expanded=False):
        st.markdown("""
        ### Quick Setup Steps:
        
        1. **Create Supabase Account:** https://supabase.com
        2. **Create New Project** (takes 2 minutes)
        3. **Get Connection Details:**
           - Host: `db.xxxxx.supabase.co`
           - Database: `postgres`
           - User: `postgres`
           - Password: (from project creation)
        4. **Run SQL Script** in Supabase SQL Editor (see below)
        5. **Add to Streamlit Cloud Secrets:**
           ```toml
           [postgres]
           host = "db.xxxxx.supabase.co"
           port = "5432"
           database = "postgres"
           user = "postgres"
           password = "your-password"
           ```
        
        See `POSTGRESQL_SETUP_GUIDE.md` for detailed instructions!
        """)


def show_sql_server_config():
    """Configure SQL Server connection"""
    
    if not PYODBC_AVAILABLE:
        st.error("❌ SQL Server features are not available on Streamlit Cloud")
        st.info("""
        💡 **SQL Server integration is only available when running locally**
        
        To use SQL Server features:
        1. Run the app locally: `streamlit run app.py`
        2. Ensure SQL Server and ODBC Driver 17 are installed
        3. Follow the setup guide: `SQL_SERVER_SETUP_GUIDE.md`
        """)
        return
    
    st.markdown("### 🖥️ SQL Server Connection (Local)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server = st.text_input(
            "Server Address",
            value=st.session_state.get('sql_server', 'localhost\\SQLEXPRESS'),
            help="SQL Server address (e.g., localhost\\SQLEXPRESS)"
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
    
    # Show username/password fields if SQL Server Authentication is selected
    if auth_type == "SQL Server Authentication":
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input(
                "Username",
                value=st.session_state.get('sql_username', 'ReconciliationApp'),
                help="SQL Server login username"
            )
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                value=st.session_state.get('sql_password', ''),
                help="SQL Server login password"
            )
    else:
        username = None
        password = None
    
    # Test Connection Button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔌 Test Connection", use_container_width=True, key="sql_test"):
            with st.spinner("Testing SQL Server connection..."):
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
        if st.button("📋 Create Tables", use_container_width=True, key="sql_create"):
            if 'sql_connection_string' not in st.session_state:
                st.error("Please test connection first!")
            else:
                with st.spinner("Creating database tables..."):
                    db = ReconciliationDatabase(st.session_state['sql_connection_string'])
                    
                    if db.create_tables():
                        st.success("✅ Database tables created successfully!")
                    else:
                        st.error("❌ Failed to create tables. Check permissions.")


if __name__ == "__main__":
    show_database_config()
