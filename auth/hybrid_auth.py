"""
Hybrid Authentication System
=============================
Automatically uses Supabase if configured, falls back to local file storage

This allows:
1. Testing locally without Supabase
2. Production deployment with Supabase
3. No code changes needed - just configure secrets
"""

import streamlit as st
from typing import Optional, Dict, Tuple

class HybridAuthentication:
    """Hybrid authentication - Supabase first, local file fallback"""

    def __init__(self):
        """Initialize authentication system"""
        self.backend = None
        self.backend_type = "unknown"
        
        # Try Supabase first
        try:
            from auth.supabase_auth import SupabaseAuthentication
            supabase_auth = SupabaseAuthentication()
            
            if supabase_auth.enabled:
                self.backend = supabase_auth
                self.backend_type = "supabase"
                st.success("✅ Using Supabase cloud database - Users persist permanently!")
                return
        except Exception as e:
            st.warning(f"Supabase not available: {e}")
        
        # Fall back to local file storage
        try:
            from auth.authentication import Authentication
            self.backend = Authentication()
            self.backend_type = "local"
            st.warning("""
            ⚠️ **Using local file storage**
            
            User data is stored in `data/users.json` and will be lost when the app restarts.
            
            **To enable permanent storage:**
            1. Create a free Supabase account at https://supabase.com
            2. Follow setup instructions in `auth/supabase_auth.py`
            3. Add credentials to `.streamlit/secrets.toml`
            """)
        except Exception as e:
            st.error(f"❌ Could not initialize authentication: {e}")
            raise

    def register(self, username: str, password: str, email: str = '') -> Tuple[bool, str]:
        """Register new user"""
        if self.backend:
            return self.backend.register(username, password, email)
        return False, "Authentication system not initialized"

    def login(self, username: str, password: str) -> bool:
        """Authenticate user"""
        if self.backend:
            return self.backend.login(username, password)
        return False

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        if self.backend:
            return self.backend.get_user_info(username)
        return None

    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information"""
        if self.backend:
            return self.backend.update_user(username, **kwargs)
        return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if self.backend:
            return self.backend.change_password(username, old_password, new_password)
        return False

    def delete_user(self, username: str) -> bool:
        """Delete user account"""
        if self.backend:
            return self.backend.delete_user(username)
        return False

    def get_backend_info(self) -> Dict[str, str]:
        """Get information about active backend"""
        return {
            'type': self.backend_type,
            'description': 'Cloud database (permanent)' if self.backend_type == 'supabase' else 'Local file (temporary)',
            'persistent': self.backend_type == 'supabase'
        }
