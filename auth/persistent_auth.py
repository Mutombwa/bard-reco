"""
Persistent Authentication System with SQLite
=============================================
Ensures user data survives app restarts on Streamlit Cloud
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import streamlit as st

class PersistentAuthentication:
    """Authentication system with persistent SQLite storage"""

    # Domain restriction for user registration
    ALLOWED_EMAIL_DOMAIN = "@bardsantner.com"

    def __init__(self):
        """Initialize authentication with persistent database"""

        # Use Streamlit's data directory which persists on Cloud
        # This directory is part of the GitHub repo and persists
        self.db_path = Path(__file__).parent.parent / 'data' / 'users.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _init_database(self):
        """Initialize database with users table"""

        conn = self._get_connection()
        cursor = conn.cursor()

        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                last_login TEXT
            )
        ''')

        # Create index on email for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email ON users(email)
        ''')

        conn.commit()

        # Check if admin exists, if not create default admin
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            self._create_default_admin(cursor)
            conn.commit()

        conn.close()

    def _create_default_admin(self, cursor):
        """Create default admin account"""

        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, email, created_at, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'tatenda.mutombwa',
            self._hash_password('admin123'),
            'tatenda.mutombwa@bardsantner.com',
            datetime.now().isoformat(),
            'admin'
        ))

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _is_email_allowed(self, email: str) -> bool:
        """
        Check if email domain is allowed.

        IMPORTANT: Does NOT show the domain to prevent fake registrations

        Args:
            email: Email address to validate

        Returns:
            True if email ends with allowed domain, False otherwise
        """
        if not email:
            return False
        return email.lower().endswith(self.ALLOWED_EMAIL_DOMAIN.lower())

    def register(self, username: str, password: str, email: str = '') -> Tuple[bool, str]:
        """
        Register new user with email domain restriction

        Security: Does not reveal the required domain in error messages

        Args:
            username: Username
            password: Password
            email: Email (required, must end with company domain)

        Returns:
            Tuple of (success: bool, message: str)
        """

        # Validate inputs
        if not username or not password or not email:
            return False, "All fields are required"

        # Validate email domain (silently - don't reveal the domain)
        if not self._is_email_allowed(email):
            return False, "Invalid email address. Please use your official company email."

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists"

            # Check if email is already registered
            cursor.execute("SELECT email FROM users WHERE email=?", (email.lower(),))
            if cursor.fetchone():
                conn.close()
                return False, "Email already registered"

            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, created_at, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                self._hash_password(password),
                email.lower(),
                datetime.now().isoformat(),
                'user'
            ))

            conn.commit()
            conn.close()
            return True, "Registration successful"

        except sqlite3.Error as e:
            conn.close()
            return False, f"Registration failed: {str(e)}"

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful, False otherwise
        """

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT password_hash FROM users WHERE username=?",
                (username,)
            )

            row = cursor.fetchone()

            if not row:
                conn.close()
                return False

            stored_hash = row[0]
            provided_hash = self._hash_password(password)

            if stored_hash == provided_hash:
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login=? WHERE username=?",
                    (datetime.now().isoformat(), username)
                )
                conn.commit()
                conn.close()
                return True

            conn.close()
            return False

        except sqlite3.Error:
            conn.close()
            return False

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT username, email, created_at, role, last_login FROM users WHERE username=?",
                (username,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'username': row[0],
                    'email': row[1],
                    'created_at': row[2],
                    'role': row[3],
                    'last_login': row[4]
                }

            return None

        except sqlite3.Error:
            conn.close()
            return None

    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information"""

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build update query dynamically
            allowed_fields = ['email', 'role']
            updates = []
            values = []

            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key}=?")
                    values.append(value)

            if not updates:
                conn.close()
                return False

            values.append(username)
            query = f"UPDATE users SET {', '.join(updates)} WHERE username=?"

            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()

            return success

        except sqlite3.Error:
            conn.close()
            return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""

        if not self.login(username, old_password):
            return False

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET password_hash=? WHERE username=?",
                (self._hash_password(new_password), username)
            )
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()

            return success

        except sqlite3.Error:
            conn.close()
            return False

    def delete_user(self, username: str) -> bool:
        """Delete user account"""

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()

            return success

        except sqlite3.Error:
            conn.close()
            return False

    def get_all_users(self) -> list:
        """Get list of all users (admin only)"""

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT username, email, created_at, role, last_login FROM users ORDER BY created_at DESC"
            )

            rows = cursor.fetchall()
            conn.close()

            users = []
            for row in rows:
                users.append({
                    'username': row[0],
                    'email': row[1],
                    'created_at': row[2],
                    'role': row[3],
                    'last_login': row[4]
                })

            return users

        except sqlite3.Error:
            conn.close()
            return []
