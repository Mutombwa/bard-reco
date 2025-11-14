"""
AI Assistant Component for Streamlit Reconciliation App
Provides chat interface and intelligent suggestions
"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_reconciliation_engine import LocalReconciliationAI


def render_ai_assistant():
    """Render AI chat assistant in sidebar or main area"""
    
    # Initialize AI engine in session state
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = LocalReconciliationAI()
    
    if 'ai_conversation' not in st.session_state:
        st.session_state.ai_conversation = []
    
    st.markdown("### 🤖 AI Reconciliation Assistant")
    st.caption("Powered by Local AI (Free & Private)")
    
    # Display conversation history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.ai_conversation:
            role = message['role']
            content = message['content']
            
            if role == 'user':
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**AI:** {content}")
    
    # Chat input
    user_input = st.text_input(
        "Ask me anything about reconciliation:",
        placeholder="e.g., How do I match transactions? What are outstanding items?",
        key="ai_chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("Send", type="primary")
    with col2:
        if st.button("Clear Chat"):
            st.session_state.ai_conversation = []
            st.rerun()
    
    if send_button and user_input:
        # Add user message to conversation
        st.session_state.ai_conversation.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        with st.spinner("AI thinking..."):
            response = st.session_state.ai_engine.chat(
                user_input, 
                st.session_state.ai_conversation
            )
        
        # Add AI response to conversation
        st.session_state.ai_conversation.append({
            'role': 'assistant',
            'content': response
        })
        
        st.rerun()


def render_ai_suggestions(df1=None, df2=None):
    """Render AI-powered suggestions for reconciliation settings"""
    
    if df1 is None or df2 is None:
        st.info("📊 Upload both files to get AI-powered suggestions")
        return None
    
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = LocalReconciliationAI()
    
    with st.expander("🔮 AI Recommendations", expanded=True):
        if st.button("Get AI Suggestions", type="primary"):
            with st.spinner("AI analyzing your data..."):
                suggestions = st.session_state.ai_engine.suggest_settings(df1, df2)
            
            st.success("✅ AI Analysis Complete")
            
            # Display suggestions
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Recommended Amount Tolerance",
                    f"±R{suggestions.get('amount_tolerance', 0.01)}"
                )
            
            with col2:
                st.metric(
                    "Recommended Date Tolerance",
                    f"{suggestions.get('date_tolerance_days', 3)} days"
                )
            
            if suggestions.get('use_fuzzy_matching'):
                st.info("💡 AI suggests enabling fuzzy text matching for descriptions")
            
            # Warnings
            if suggestions.get('warnings'):
                st.warning("⚠️ **Data Quality Warnings:**")
                for warning in suggestions['warnings']:
                    st.markdown(f"- {warning}")
            
            # Recommendations
            if suggestions.get('recommendations'):
                st.success("💡 **AI Recommendations:**")
                for rec in suggestions['recommendations']:
                    st.markdown(f"- {rec}")
            
            return suggestions
    
    return None


def render_column_mapper(df, expected_columns):
    """
    AI-powered column mapping interface
    
    Args:
        df: Uploaded DataFrame
        expected_columns: List of expected column names
    
    Returns:
        Dictionary of column mappings
    """
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = LocalReconciliationAI()
    
    st.markdown("### 🎯 Smart Column Mapping")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption("Let AI detect the correct columns automatically")
    
    with col2:
        if st.button("🤖 Auto-Detect", type="primary"):
            with st.spinner("AI detecting columns..."):
                mappings = st.session_state.ai_engine.detect_column_mappings(
                    df, 
                    expected_columns
                )
            
            if mappings:
                st.session_state['ai_column_mappings'] = mappings
                st.success("✅ Columns detected!")
                st.rerun()
    
    # Show AI-detected mappings or manual selection
    mappings = st.session_state.get('ai_column_mappings', {})
    
    result_mappings = {}
    
    for expected_col in expected_columns:
        detected = mappings.get(expected_col, '')
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"**{expected_col}:**")
        
        with col2:
            # Get the index of detected column, or 0 if not found
            available_columns = [''] + list(df.columns)
            default_index = 0
            if detected and detected in available_columns:
                default_index = available_columns.index(detected)
            
            selected = st.selectbox(
                f"Map to column",
                options=available_columns,
                index=default_index,
                key=f"map_{expected_col}",
                label_visibility="collapsed"
            )
            
            if selected:
                result_mappings[expected_col] = selected
    
    return result_mappings


def render_anomaly_detector(df):
    """Detect and display anomalies in transaction data"""
    
    if df is None or df.empty:
        return
    
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = LocalReconciliationAI()
    
    with st.expander("🔍 AI Anomaly Detection"):
        if st.button("Scan for Anomalies", type="secondary"):
            with st.spinner("AI scanning for issues..."):
                anomalies = st.session_state.ai_engine.detect_anomalies(df)
            
            if not anomalies:
                st.success("✅ No anomalies detected! Data looks clean.")
            else:
                st.warning(f"⚠️ Found {len(anomalies)} potential issues:")
                
                for anomaly in anomalies:
                    severity = anomaly.get('severity', 'low')
                    icon = "🔴" if severity == 'high' else "🟡" if severity == 'medium' else "🟢"
                    
                    st.markdown(f"{icon} **{anomaly.get('type', 'Issue').title()}** "
                               f"(Row {anomaly.get('transaction_index', 'N/A')})")
                    st.markdown(f"   ↳ {anomaly.get('description', 'No description')}")


def render_ai_sidebar():
    """Render compact AI assistant in sidebar"""
    
    with st.sidebar:
        st.divider()
        
        if st.button("💬 Ask AI Assistant", use_container_width=True):
            st.session_state['show_ai_chat'] = True
        
        # Show AI status
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                st.success("🤖 AI Online")
            else:
                st.error("🤖 AI Offline")
        except:
            st.warning("🤖 AI Starting...")
            st.caption("Start Ollama to enable AI features")


def check_ai_status():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False
