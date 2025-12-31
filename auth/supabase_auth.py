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
import os
from datetime import datetime
from typing import Optional, Dict, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

class SupabaseAuthentication:
    """Supabase-backed authentication system"""

    ALLOWED_EMAIL_DOMAIN = "@bardsantner.com"

    def __init__(self):
        """Initialize Supabase connection"""
        try:
            from supabase import create_client, Client
            
            # Get credentials from environment variables (Render) OR Streamlit secrets (local/Streamlit Cloud)
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            # Fallback to Streamlit secrets if environment variables not set
            if not url or not key:
                if "supabase" in st.secrets:
                    url = st.secrets["supabase"]["url"]
                    key = st.secrets["supabase"]["key"]
            
            if url and key:
                self.supabase: Client = create_client(url, key)
                self.enabled = True
                
                # Create default admin if not exists (silently)
                self._create_default_admin()
            else:
                self.enabled = False
                # Don't show warning here - handled by hybrid_auth
                
        except ImportError:
            self.enabled = False
            # Don't show error here - handled by hybrid_auth
        except Exception:
            self.enabled = False
            # Don't show error here - handled by hybrid_auth

    def _hash_password(self, password: str) -> str:
        """Hash password using Werkzeug (compatible with ROSEBUD Flask app)"""
        # Use pbkdf2:sha256 method which is memory-efficient for cloud deployment
        return generate_password_hash(password, method='pbkdf2:sha256')

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash (supports multiple formats)"""
        try:
            # Try Werkzeug verification first (handles scrypt, pbkdf2, etc.)
            if stored_hash.startswith(('scrypt:', 'pbkdf2:', 'sha256:')):
                return check_password_hash(stored_hash, password)

            # Fallback: SHA-256 hex comparison (legacy BARD-RECO format)
            if len(stored_hash) == 64:  # SHA-256 produces 64 char hex
                sha256_hash = hashlib.sha256(password.encode()).hexdigest()
                if stored_hash.lower() == sha256_hash.lower():
                    return True

            # Try Werkzeug as final fallback
            return check_password_hash(stored_hash, password)

        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def _is_email_allowed(self, email: str) -> bool:
        """Check if email domain is allowed"""
        if not email:
            return False
        return email.lower().endswith(self.ALLOWED_EMAIL_DOMAIN.lower())

    def _create_default_admin(self):
        """Create default admin account if it doesn't exist"""
        try:
            # Check if admin exists (use 'tatenda' as that's in the existing table)
            result = self.supabase.table('users').select('*').eq('username', 'tatenda').execute()

            if not result.data:
                # Create admin with existing table structure
                self.supabase.table('users').insert({
                    'username': 'tatenda',
                    'password_hash': self._hash_password('admin123'),
                    'email': 'tatenda.mutombwa@bardsantner.com',
                    'full_name': 'Tatenda Mutombwa',
                    'role': 'admin'
                }).execute()

        except Exception:
            pass  # Silently fail - admin may already exist or table not ready

    def register(self, username: str, password: str, email: str = '', full_name: str = '') -> Tuple[bool, str]:
        """
        Register new user in Supabase

        Args:
            username: Username
            password: Password
            email: Email (required, must end with @bardsantner.com)
            full_name: Full name (optional)

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

            # Generate full_name from email if not provided
            if not full_name:
                # Extract name from email: tatenda.mutombwa@bardsantner.com -> Tatenda Mutombwa
                name_part = email.split('@')[0]
                full_name = ' '.join(word.capitalize() for word in name_part.replace('.', ' ').replace('_', ' ').split())

            # Insert new user (compatible with existing table structure)
            self.supabase.table('users').insert({
                'username': username,
                'password_hash': self._hash_password(password),
                'email': email.lower(),
                'full_name': full_name,
                'role': 'poster'  # Default role for new users
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
            stored_hash = user.get('password_hash', '')

            # Use the new password verification that supports scrypt
            if self._verify_password(password, stored_hash):
                # Update last login (only if column exists)
                try:
                    self.supabase.table('users').update({
                        'last_login': datetime.now().isoformat()
                    }).eq('username', username).execute()
                except:
                    pass  # Column may not exist

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
