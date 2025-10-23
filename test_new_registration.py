"""
Test complete registration flow:
1. Register new user
2. Verify it appears in Supabase with hashed password
3. Test login works
"""
from auth.supabase_auth import SupabaseAuthentication
import hashlib
from datetime import datetime

def test_registration_flow():
    print("\n" + "="*60)
    print("🧪 TESTING NEW USER REGISTRATION FLOW")
    print("="*60)
    
    # Test credentials
    test_username = f"test.user.{datetime.now().strftime('%H%M%S')}"
    test_email = f"{test_username}@bardsantner.com"
    test_password = "TestPass123!"
    
    print(f"\n📝 Registering new user:")
    print(f"   Username: {test_username}")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    
    # Initialize auth
    auth = SupabaseAuthentication()
    
    # STEP 1: Register the user
    print("\n🔹 STEP 1: Registering user...")
    try:
        success, message = auth.register(test_username, test_password, test_email)
        if success:
            print(f"   ✅ Registration successful! {message}")
        else:
            print(f"   ❌ Registration failed: {message}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    # STEP 2: Verify in database with correct hash
    print("\n🔹 STEP 2: Checking Supabase database...")
    try:
        response = auth.supabase.table('users').select('*').eq('username', test_username).execute()
        
        if response.data:
            user_data = response.data[0]
            stored_hash = user_data['password_hash']
            expected_hash = hashlib.sha256(test_password.encode()).hexdigest()
            
            print(f"   ✅ User found in Supabase!")
            print(f"   📊 User details:")
            print(f"      Email: {user_data['email']}")
            print(f"      Role: {user_data['role']}")
            print(f"      Created: {user_data['created_at']}")
            print(f"\n   🔐 Password Hash Verification:")
            print(f"      Stored:   {stored_hash[:40]}...")
            print(f"      Expected: {expected_hash[:40]}...")
            
            if stored_hash == expected_hash:
                print(f"      ✅ HASH MATCHES - Password was hashed correctly!")
            else:
                print(f"      ❌ HASH MISMATCH - Password hashing failed!")
                return False
        else:
            print("   ❌ User not found in database!")
            return False
    except Exception as e:
        print(f"   ❌ Database check error: {e}")
        return False
    
    # STEP 3: Test login
    print("\n🔹 STEP 3: Testing login with credentials...")
    try:
        login_result = auth.login(test_username, test_password)
        
        if login_result:
            print(f"   ✅ LOGIN SUCCESSFUL!")
            print(f"   🎉 Complete flow working perfectly!")
            
            # Get user details from database to display
            response = auth.supabase.table('users').select('*').eq('username', test_username).execute()
            if response.data:
                user = response.data[0]
                print(f"\n   📊 Logged in user details:")
                print(f"      Username: {user['username']}")
                print(f"      Email: {user['email']}")
                print(f"      Role: {user['role']}")
        else:
            print(f"   ❌ LOGIN FAILED - Check password hashing!")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Final summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n📋 Summary:")
    print("   ✅ User registered successfully")
    print("   ✅ Saved to Supabase with SHA-256 hash")
    print("   ✅ Login works immediately")
    print("   ✅ User persists permanently in cloud")
    print("\n🎯 Result: Registration system working perfectly!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_registration_flow()
    exit(0 if success else 1)
