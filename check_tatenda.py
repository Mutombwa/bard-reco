"""Check tatenda's password hash in Supabase"""
from auth.supabase_auth import SupabaseAuthentication
import hashlib

# Initialize auth
auth = SupabaseAuthentication()

# Get tatenda's current hash
response = auth.supabase.table('users').select('username, password_hash').eq('username', 'tatenda.mutombwa').execute()

if response.data:
    current_hash = response.data[0]['password_hash']
    print(f"Current hash in DB: {current_hash}")
    
    # Calculate what it should be
    correct_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    print(f"Expected hash:      {correct_hash}")
    
    # Check match
    if current_hash == correct_hash:
        print("✅ Hash is CORRECT!")
    else:
        print("❌ Hash is WRONG - needs fix_all_passwords.sql")
else:
    print("❌ User not found in database")
