"""
Test Supabase Registration Flow
"""
import streamlit as st
from auth.supabase_auth import SupabaseAuthentication

def test_registration():
    print("="*60)
    print("TESTING SUPABASE REGISTRATION")
    print("="*60)
    
    auth = SupabaseAuthentication()
    
    if not auth.enabled:
        print("❌ Supabase is NOT enabled!")
        print("   Check .streamlit/secrets.toml file exists")
        return
    
    print("✅ Supabase is enabled")
    print(f"   Connection active\n")
    
    # Test registration
    test_username = "test.user2"
    test_email = "test.user2@bardsantner.com"
    test_password = "Test123!@#"
    
    print(f"📝 Attempting to register:")
    print(f"   Username: {test_username}")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    
    success, message = auth.register(test_username, test_password, test_email)
    
    if success:
        print(f"\n✅ Registration SUCCESSFUL!")
        print(f"   Message: {message}")
        
        # Verify in database
        result = auth.supabase.table('users').select('*').eq('username', test_username).execute()
        if result.data:
            print(f"\n✅ User found in Supabase:")
            user = result.data[0]
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
            print(f"   Hash: {user['password_hash'][:20]}...")
            
            # Test login
            print(f"\n🧪 Testing login...")
            if auth.login(test_username, test_password):
                print(f"✅ Login test PASSED!")
            else:
                print(f"❌ Login test FAILED!")
            
            # Cleanup
            print(f"\n🧹 Cleaning up test user...")
            auth.delete_user(test_username)
            print(f"✅ Test user deleted")
        else:
            print(f"\n❌ User NOT found in Supabase after registration!")
            
    else:
        print(f"\n❌ Registration FAILED!")
        print(f"   Message: {message}")
        
        # Check if user already exists
        result = auth.supabase.table('users').select('*').eq('username', test_username).execute()
        if result.data:
            print(f"\n   User already exists in database")
            print(f"   Deleting existing user for retry...")
            auth.delete_user(test_username)
            print(f"   Try running this script again")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_registration()
