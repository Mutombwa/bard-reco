"""
Quick script to hash a password and update it in Supabase
Run this to fix the password for the user you created manually
"""
import hashlib
import streamlit as st
from auth.supabase_auth import SupabaseAuthentication

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_user_password(username: str, new_password: str):
    """Update user password in Supabase with hashed version"""
    print(f"\n🔧 Updating password for user: {username}")
    
    # Hash the password
    password_hash = hash_password(new_password)
    print(f"✅ Password hashed: {password_hash[:20]}...")
    
    try:
        # Initialize Supabase
        auth = SupabaseAuthentication()
        
        if not auth.enabled:
            print("❌ Supabase not configured!")
            return
        
        # Update the password
        result = auth.supabase.table('users').update({
            'password_hash': password_hash
        }).eq('username', username).execute()
        
        print(f"✅ Password updated successfully!")
        print(f"📊 Updated records: {len(result.data)}")
        
        # Verify the update
        verify = auth.supabase.table('users').select('username, email, password_hash').eq('username', username).execute()
        if verify.data:
            user = verify.data[0]
            print(f"\n✅ Verification:")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Hash: {user['password_hash'][:20]}...")
        
        # Test login
        print(f"\n🧪 Testing login...")
        if auth.login(username, new_password):
            print(f"✅ Login test PASSED! User can now login with the password.")
        else:
            print(f"❌ Login test FAILED! Something is wrong.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("SUPABASE PASSWORD HASHER & UPDATER")
    print("="*60)
    
    # The user you created in Supabase
    username = "Rosebud Mpofu"  # Change this to match your Supabase user
    password = "Talith@17"  # The password you want to set
    
    print(f"\n📝 Configuration:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    # Update the password
    update_user_password(username, password)
    
    print("\n" + "="*60)
    print("✅ DONE! You can now login to the app with these credentials.")
    print("="*60)
