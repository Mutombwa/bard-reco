"""
Supabase Authentication System
===============================
Cloud-based user authentication with persistent storage

Benefits:
- Users persist even when app sleeps/restarts
- Free tier: 500MB database, 50,000 monthly active users
- Automatic backups
- No data loss

Setup Instructions:
1. Create account at https://supabase.com
2. Create a new project
3. Go to Settings > API
4. Copy your project URL and anon key
5. Add to .streamlit/secrets.toml:
   [supabase]
   url = "https://xxxxx.supabase.co"
   key = "your-anon-key"

6. Create users table in Supabase SQL Editor:
   CREATE TABLE users (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       username TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       email TEXT UNIQUE NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       role TEXT DEFAULT 'user',
       last_login TIMESTAMP WITH TIME ZONE
   );
   
   CREATE INDEX idx_username ON users(username);
   CREATE INDEX idx_email ON users(email);
"""

import streamlit as st
import hashlib
from datetime import datetime
from typing import Optional, Dict, Tuple

class SupabaseAuthentication:
    """Supabase-backed authentication system"""

    ALLOWED_EMAIL_DOMAIN = "@bardsantner.com"

    def __init__(self):
        """Initialize Supabase connection"""
        try:
            from supabase import create_client, Client
            
            # Get credentials from Streamlit secrets
            if "supabase" in st.secrets:
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["key"]
                self.supabase: Client = create_client(url, key)
                self.enabled = True
                
                # Create default admin if not exists
                self._create_default_admin()
            else:
                self.enabled = False
                st.warning("⚠️ Supabase not configured. Using local file storage (data may be lost on app restart).")
                
        except ImportError:
            self.enabled = False
            st.error("❌ Supabase package not installed. Run: pip install supabase")
        except Exception as e:
            self.enabled = False
            st.error(f"❌ Supabase connection failed: {e}")

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _is_email_allowed(self, email: str) -> bool:
        """Check if email domain is allowed"""
        if not email:
            return False
        return email.lower().endswith(self.ALLOWED_EMAIL_DOMAIN.lower())

    def _create_default_admin(self):
        """Create default admin account if it doesn't exist"""
        try:
            # Check if admin exists
            result = self.supabase.table('users').select('*').eq('username', 'tatenda.mutombwa').execute()
            
            if not result.data:
                # Create admin
                self.supabase.table('users').insert({
                    'username': 'tatenda.mutombwa',
                    'password_hash': self._hash_password('admin123'),
                    'email': 'tatenda.mutombwa@bardsantner.com',
                    'role': 'admin'
                }).execute()
                
        except Exception as e:
            st.warning(f"Could not create default admin: {e}")

    def register(self, username: str, password: str, email: str = '') -> Tuple[bool, str]:
        """
        Register new user in Supabase

        Args:
            username: Username
            password: Password
            email: Email (required, must end with @bardsantner.com)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            return False, "Supabase not configured"

        # Validate email domain
        if not self._is_email_allowed(email):
            return False, f"Registration failed: Email must end with {self.ALLOWED_EMAIL_DOMAIN}"

        try:
            # Check if username exists
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            if result.data:
                return False, "Username already exists"

            # Check if email exists
            result = self.supabase.table('users').select('*').eq('email', email.lower()).execute()
            if result.data:
                return False, "Email already registered"

            # Insert new user
            self.supabase.table('users').insert({
                'username': username,
                'password_hash': self._hash_password(password),
                'email': email.lower(),
                'role': 'user'
            }).execute()

            return True, "Registration successful! Your account is now permanently stored in the cloud."

        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user against Supabase

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Get user from Supabase
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            
            if not result.data:
                return False

            user = result.data[0]
            stored_hash = user['password_hash']
            provided_hash = self._hash_password(password)

            if stored_hash == provided_hash:
                # Update last login
                self.supabase.table('users').update({
                    'last_login': datetime.now().isoformat()
                }).eq('username', username).execute()
                
                return True

            return False

        except Exception as e:
            st.error(f"Login failed: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information from Supabase"""
        if not self.enabled:
            return None

        try:
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            return None

    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information in Supabase"""
        if not self.enabled:
            return False

        try:
            self.supabase.table('users').update(kwargs).eq('username', username).execute()
            return True
        except Exception as e:
            st.error(f"Error updating user: {e}")
            return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password in Supabase"""
        if not self.enabled:
            return False

        if not self.login(username, old_password):
            return False

        try:
            self.supabase.table('users').update({
                'password_hash': self._hash_password(new_password)
            }).eq('username', username).execute()
            return True
        except Exception as e:
            st.error(f"Error changing password: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """Delete user from Supabase"""
        if not self.enabled:
            return False

        try:
            self.supabase.table('users').delete().eq('username', username).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False

    def get_all_users(self) -> list:
        """Get all users (admin only)"""
        if not self.enabled:
            return []

        try:
            result = self.supabase.table('users').select('username, email, created_at, role, last_login').execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
