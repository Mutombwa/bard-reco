"""
Quick test to verify which backend the app is using
"""
from auth.hybrid_auth import HybridAuthentication

auth = HybridAuthentication()

print("="*60)
print("AUTHENTICATION BACKEND TEST")
print("="*60)

backend_info = auth.get_backend_info()

print(f"\n✅ Backend Type: {backend_info['backend']}")
print(f"   Message: {backend_info['message']}")
print(f"   Persistent: {backend_info['persistent']}")

if backend_info['backend'] == 'supabase':
    print("\n✅ SUPABASE IS ACTIVE!")
    print("   - Registrations will be saved to cloud")
    print("   - Logins will check cloud database")
    print("   - Users persist forever")
else:
    print("\n⚠️  LOCAL FILES ACTIVE")
    print("   - Registrations saved to data/users.json")
    print("   - Will be lost on app restart")
    print("\n   To enable Supabase:")
    print("   1. Check .streamlit/secrets.toml exists")
    print("   2. Verify credentials are correct")

print("\n" + "="*60)
