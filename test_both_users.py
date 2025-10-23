"""
Test login for both users after password fix
"""
from auth.supabase_auth import SupabaseAuthentication

def test_login(username, password):
    auth = SupabaseAuthentication()
    
    print(f"\n🧪 Testing login for: {username}")
    print(f"   Password: {password}")
    
    if auth.login(username, password):
        print(f"   ✅ LOGIN SUCCESSFUL!")
        
        # Get user info
        result = auth.supabase.table('users').select('*').eq('username', username).execute()
        if result.data:
            user = result.data[0]
            print(f"   📊 User Details:")
            print(f"      Email: {user['email']}")
            print(f"      Role: {user['role']}")
            print(f"      Hash: {user['password_hash'][:20]}...")
    else:
        print(f"   ❌ LOGIN FAILED!")
        print(f"   💡 Make sure you ran: fix_all_passwords.sql")

print("="*60)
print("TESTING USER LOGINS")
print("="*60)

# Test tatenda.mutombwa
test_login("tatenda.mutombwa", "admin123")

# Test Rosebud Mpofu
test_login("Rosebud Mpofu", "Talith@17")

print("\n" + "="*60)
print("✅ If both logins successful, you're ready to go!")
print("="*60)
