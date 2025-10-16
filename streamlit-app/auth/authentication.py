"""
Authentication System
====================
User authentication and session management
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

class Authentication:
    """Simple authentication system with file-based storage"""

    def __init__(self):
        self.users_file = Path(__file__).parent.parent / 'data' / 'users.json'
        self.users_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._init_users_file()

    def _init_users_file(self):
        """Initialize users file with default admin account"""

        default_users = {
            'admin': {
                'password_hash': self._hash_password('admin123'),
                'email': 'admin@bard-reco.com',
                'created_at': datetime.now().isoformat(),
                'role': 'admin'
            }
        }

        self._save_users(default_users)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""

        return hashlib.sha256(password.encode()).hexdigest()

    def _load_users(self) -> Dict:
        """Load users from file"""

        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_users(self, users: Dict):
        """Save users to file"""

        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def register(self, username: str, password: str, email: str = '') -> bool:
        """
        Register new user

        Args:
            username: Username
            password: Password
            email: Email (optional)

        Returns:
            True if registration successful, False if username exists
        """

        users = self._load_users()

        if username in users:
            return False

        users[username] = {
            'password_hash': self._hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'role': 'user'
        }

        self._save_users(users)
        return True

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful, False otherwise
        """

        users = self._load_users()

        if username not in users:
            return False

        stored_hash = users[username]['password_hash']
        provided_hash = self._hash_password(password)

        return stored_hash == provided_hash

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""

        users = self._load_users()
        return users.get(username)

    def update_user(self, username: str, **kwargs):
        """Update user information"""

        users = self._load_users()

        if username in users:
            users[username].update(kwargs)
            self._save_users(users)
            return True

        return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""

        if not self.login(username, old_password):
            return False

        users = self._load_users()
        users[username]['password_hash'] = self._hash_password(new_password)
        self._save_users(users)

        return True

    def delete_user(self, username: str) -> bool:
        """Delete user account"""

        users = self._load_users()

        if username in users:
            del users[username]
            self._save_users(users)
            return True

        return False
