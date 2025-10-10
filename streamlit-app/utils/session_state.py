"""
Session State Management
=======================
Manage user sessions and application state
"""

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
