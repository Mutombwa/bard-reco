#!/bin/bash
# Deployment script for authentication fixes
# Run this to deploy persistent authentication to Streamlit Cloud

echo "🚀 Deploying Authentication Fixes to Streamlit Cloud"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the repository root."
    exit 1
fi

# Check if database exists
if [ ! -f "data/users.db" ]; then
    echo "⚠️  Warning: data/users.db not found. Creating database..."
    python -c "from auth.persistent_auth import PersistentAuthentication; PersistentAuthentication()"
    echo "✅ Database created"
fi

# Check database file size
DB_SIZE=$(wc -c < "data/users.db" | tr -d ' ')
if [ "$DB_SIZE" -lt 10000 ]; then
    echo "❌ Error: Database file is too small ($DB_SIZE bytes). Something went wrong."
    exit 1
fi

echo "✅ Database file valid ($DB_SIZE bytes)"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
echo "------------------------"
git status --short | grep -E "(app.py|.gitignore|auth/|data/users.db|data/.gitkeep)"
echo ""

# Confirm
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Add files
echo "📦 Adding files to Git..."
git add .gitignore
git add app.py
git add auth/persistent_auth.py
git add data/users.db
git add data/.gitkeep
git add AUTHENTICATION_FIX_GUIDE.md

# Commit
echo "💾 Creating commit..."
git commit -m "Fix: Persistent authentication + secure registration

- Migrate from JSON to SQLite for user persistence
- Database tracked in Git to survive app restarts
- Remove email domain hint to prevent fake registrations
- Add comprehensive deployment documentation

Fixes:
- Users no longer lost when app goes to sleep
- Fake registrations prevented (domain not shown)
- Better performance with indexed database queries
- Thread-safe concurrent user support"

# Push
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment Complete!"
echo "======================"
echo ""
echo "📊 Next Steps:"
echo "1. Go to your Streamlit Cloud dashboard"
echo "2. App will automatically rebuild (takes ~2-3 minutes)"
echo "3. Test registration with generic message (no domain hint)"
echo "4. Test that users persist after app restart"
echo ""
echo "📖 Documentation: AUTHENTICATION_FIX_GUIDE.md"
echo ""
echo "🎉 Your app now has persistent authentication!"
