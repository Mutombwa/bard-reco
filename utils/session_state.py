"""
Session State Management
=======================
Manage user sessions and application state
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Optional

class SessionState:
    """Manage application session state"""

    def __init__(self):
        self.is_authenticated = False
        self.username = None
        self.login_time = None
        self.user_data = {}
        self.stats = {}

    def authenticate(self, username: str):
        """Authenticate user and start session"""

        self.is_authenticated = True
        self.username = username
        self.login_time = datetime.now()

    def logout(self):
        """Logout user and clear session"""

        self.is_authenticated = False
        self.username = None
        self.login_time = None
        self.user_data = {}

    def set_user_data(self, key: str, value: Any):
        """Set user-specific data"""

        self.user_data[key] = value

    def get_user_data(self, key: str, default: Any = None) -> Any:
        """Get user-specific data"""

        return self.user_data.get(key, default)

    def set_stat(self, key: str, value: Any):
        """Set statistic"""

        self.stats[key] = value

    def get_stat(self, key: str, default: Any = None) -> Any:
        """Get statistic"""

        return self.stats.get(key, default)

    def increment_stat(self, key: str, amount: int = 1):
        """Increment statistic"""

        current = self.stats.get(key, 0)
        self.stats[key] = current + amount


def cleanup_workflow_state(prefix: str):
    """
    Remove all session state keys for a given workflow prefix.
    Call this when switching between workflows to free memory.

    Args:
        prefix: Workflow prefix (e.g. 'fnb', 'absa', 'kazang')
    """
    keys_to_remove = [k for k in st.session_state if k.startswith(f"{prefix}_")]
    for k in keys_to_remove:
        del st.session_state[k]
    return len(keys_to_remove)


def get_session_memory_usage() -> dict:
    """
    Get approximate memory usage of session state.
    Returns dict with key counts and total estimated size.
    """
    import sys
    total_size = 0
    df_count = 0
    key_count = len(st.session_state)

    for key, value in st.session_state.items():
        if isinstance(value, pd.DataFrame):
            total_size += value.memory_usage(deep=True).sum()
            df_count += 1
        else:
            try:
                total_size += sys.getsizeof(value)
            except (TypeError, ValueError):
                total_size += 100  # estimate

    return {
        'total_keys': key_count,
        'dataframe_count': df_count,
        'estimated_mb': total_size / (1024 * 1024)
    }
