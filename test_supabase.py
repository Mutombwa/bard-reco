"""
Quick test script to verify Supabase connection and setup
Run this to check if everything is configured correctly
"""
import streamlit as st
from auth.supabase_auth import SupabaseAuthentication

def test_supabase():
    print("🧪 Testing Supabase Connection...\n")
    
    try:
        # Initialize Supabase
        print("1️⃣ Initializing Supabase client...")
        auth = SupabaseAuthentication()
        print("   ✅ Client initialized successfully!")
        
        # Test database connection
        print("\n2️⃣ Testing database connection...")
        result = auth.supabase.table('users').select('*').limit(1).execute()
        print("   ✅ Database connection successful!")
        
        # Check if users table exists and has data
        print("\n3️⃣ Checking users table...")
        all_users = auth.supabase.table('users').select('username, email, role').execute()
        user_count = len(all_users.data)
        print(f"   ✅ Found {user_count} users in database")
        
        if user_count > 0:
            print("\n   Existing users:")
            for user in all_users.data:
                print(f"   - {user['username']} ({user['email']}) - Role: {user['role']}")
        else:
            print("\n   ⚠️ No users found. The default admin might not have been created.")
            print("   💡 Try running: supabase_setup.sql in your Supabase SQL Editor")
        
        # Test create user (then delete it)
        print("\n4️⃣ Testing user creation...")
        test_username = "test_user_temp"
        test_email = "test@bardsantner.com"
        test_password = "Test123!@#"
        
        try:
            # Try to create test user
            auth.register(test_username, test_password, test_email)
            print(f"   ✅ Successfully created test user: {test_username}")
            
            # Clean up - delete test user
            auth.delete_user(test_username)
            print(f"   ✅ Successfully deleted test user (cleanup)")
            
        except Exception as e:
            if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                print(f"   ℹ️ Test user already exists (that's ok)")
                # Clean up if it exists
                try:
                    auth.delete_user(test_username)
                    print(f"   ✅ Cleaned up existing test user")
                except:
                    pass
            else:
                raise e
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        print("\nYour Supabase integration is working correctly! 🎉")
        print("\nNext steps:")
        print("1. Open your app: http://localhost:8501")
        print("2. Look for green message: 'Using Supabase cloud database'")
        print("3. Register a new user - it will persist forever!")
        
        return True
        
    except Exception as e:
        print("\n" + "="*50)
        print("❌ TEST FAILED!")
        print("="*50)
        print(f"\nError: {str(e)}\n")
        
        if "relation \"users\" does not exist" in str(e):
            print("🔧 FIX: You need to run the SQL setup script!")
            print("\nSteps:")
            print("1. Go to https://supabase.com/dashboard")
            print("2. Open your project: cmlbornqaojclzrtqffh")
            print("3. Click 'SQL Editor' in left sidebar")
            print("4. Click 'New Query'")
            print("5. Copy & paste contents of: supabase_setup.sql")
            print("6. Click 'Run' (or press Ctrl+Enter)")
            print("7. Run this test again!")
            
        elif "Invalid API key" in str(e) or "JWT" in str(e):
            print("🔧 FIX: API key issue!")
            print("\nSteps:")
            print("1. Check .streamlit/secrets.toml")
            print("2. Verify the 'key' is the 'anon public' key")
            print("3. Make sure there are no extra spaces or line breaks")
            
        elif "Supabase configuration not found" in str(e):
            print("🔧 FIX: Secrets file missing!")
            print("\nSteps:")
            print("1. Create file: .streamlit/secrets.toml")
            print("2. Add your credentials (see secrets.toml.template)")
            
        else:
            print("🔧 TROUBLESHOOTING:")
            print("1. Check your internet connection")
            print("2. Verify Supabase project is not paused")
            print("3. Check .streamlit/secrets.toml has correct URL and key")
            print("4. See SUPABASE_SETUP_GUIDE.md for detailed help")
        
        return False

if __name__ == "__main__":
    test_supabase()
