# 🚀 Supabase Setup Guide - Prevent User Data Loss

## Why Supabase?

Your app currently stores users in `data/users.json`. When Streamlit Cloud restarts (after inactivity), this file is deleted and all registered users are lost. **Supabase provides permanent cloud storage** so users persist forever.

## ✅ Benefits

- **100% FREE** - Generous free tier (50,000 rows, 500 MB database, 1 GB file storage)
- **Permanent Storage** - Users never lost, even after app restarts
- **Professional** - Cloud PostgreSQL database (same as big companies use)
- **Instant** - Setup takes 10 minutes
- **Secure** - Built-in authentication, Row Level Security (RLS)

---

## 📋 Step-by-Step Setup (10 Minutes)

### Step 1: Create Supabase Account (2 minutes)

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with **GitHub** or **Google** (instant, no credit card needed)
4. Verify your email if prompted

### Step 2: Create New Project (3 minutes)

1. Click **"New Project"** (green button)
2. Fill in project details:
   - **Organization**: Select your organization (auto-created)
   - **Name**: `bard-reco-users` (or any name you prefer)
   - **Database Password**: Create a STRONG password
     - ⚠️ **SAVE THIS PASSWORD** - You'll need it later
     - Example: `MySecure2025Pass!@#`
   - **Region**: Choose closest to your users
     - If in South Africa: `Cape Town (af-south-1)`
     - If in Europe: `Ireland (eu-west-1)`
     - If in USA: `East US (us-east-1)`
   - **Pricing Plan**: **Free** (selected by default)
3. Click **"Create new project"**
4. Wait ~2 minutes while project is created ☕

### Step 3: Run SQL Setup Script (2 minutes)

1. In Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New Query"** button
3. Open the file `supabase_setup.sql` from your project
4. **Copy ALL the SQL code** from that file
5. **Paste** into the Supabase SQL Editor
6. Click **"Run"** (or press `Ctrl+Enter`)
7. ✅ You should see: **"Success. No rows returned"**
8. Click **"Table Editor"** (left sidebar) → You should see a **"users"** table

### Step 4: Get Your API Credentials (1 minute)

1. Click the **⚙️ Settings** icon (bottom left)
2. Click **"API"** in the Settings menu
3. Find the **"Project URL"** section:
   - Copy the URL (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
   - 📋 Save this as `SUPABASE_URL`
4. Find the **"Project API keys"** section:
   - Copy the **"anon public"** key (starts with: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - ⚠️ **DO NOT** copy the `service_role` key (keep that secret!)
   - 📋 Save this as `SUPABASE_KEY`

### Step 5: Configure Local Secrets (2 minutes)

#### For Local Development:

1. In your project folder, create: `.streamlit/secrets.toml`
2. Add this content (replace with YOUR credentials):

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

3. **Save the file**
4. ⚠️ **IMPORTANT**: Add to `.gitignore` so secrets aren't committed:

```bash
# Add this line to .gitignore
.streamlit/secrets.toml
```

#### For Streamlit Cloud Deployment:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Open your deployed app settings
3. Click **"⚙️ Settings"** → **"Secrets"**
4. Paste the same content:

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

5. Click **"Save"**
6. Your app will automatically restart with Supabase enabled!

---

## 🧪 Test Your Setup

### Test 1: Check Connection Status

1. Run your app locally: `streamlit run app.py`
2. Look at the **sidebar** - you should see:
   - ✅ **"Using Supabase cloud database (permanent storage)"** ← Success!
   - ⚠️ **"Using local file storage (temporary)"** ← Supabase not configured

### Test 2: Create a Test User

1. Register a new user (use @bardsantner.com email)
2. Go to Supabase dashboard → **Table Editor** → **users** table
3. ✅ You should see your new user in the database!

### Test 3: Verify Persistence

1. **Stop** your Streamlit app (`Ctrl+C`)
2. **Delete** `data/users.json` (simulate app restart)
3. **Restart** your app: `streamlit run app.py`
4. ✅ You should still be able to login! (User persisted in cloud)

---

## 🔧 Troubleshooting

### ❌ Error: "Supabase configuration not found"

**Solution**: Make sure `.streamlit/secrets.toml` exists with correct format:

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "eyJhbGci..."
```

### ❌ Error: "Invalid API key"

**Solution**: 
- Make sure you copied the **"anon public"** key (NOT service_role)
- Check for extra spaces or missing characters
- Regenerate the key in Supabase → Settings → API

### ❌ Error: "Failed to create default admin user"

**Solution**: 
- The default admin might already exist
- Try logging in with: `admin` / `admin@bardsantner.com` / `admin123`
- Check Supabase Table Editor → users → look for admin user

### ⚠️ Warning: "Using local file storage"

**Cause**: Supabase secrets not configured or connection failed

**Solution**:
1. Check `.streamlit/secrets.toml` exists and has correct format
2. Verify URL and key are correct (no typos)
3. Check internet connection
4. Verify Supabase project is active (not paused)

---

## 🔐 Security Best Practices

### ✅ DO:

- ✅ Use the **anon/public** key in your app
- ✅ Keep `.streamlit/secrets.toml` in `.gitignore`
- ✅ Use different projects for development/production
- ✅ Enable Row Level Security (RLS) - already configured in setup script
- ✅ Regularly backup your database (Supabase has automatic backups)

### ❌ DON'T:

- ❌ Commit secrets to GitHub
- ❌ Share your `service_role` key (has full database access)
- ❌ Use production database for testing
- ❌ Disable Row Level Security (RLS)
- ❌ Share your database password publicly

---

## 📊 Monitoring Your Database

### View Users:

1. Go to Supabase Dashboard
2. Click **"Table Editor"** → **"users"**
3. See all registered users with creation dates, last login, etc.

### Run Queries:

1. Click **"SQL Editor"**
2. Run queries like:

```sql
-- Count total users
SELECT COUNT(*) FROM users;

-- See recent registrations
SELECT username, email, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;

-- Find inactive users
SELECT username, email, last_login 
FROM users 
WHERE last_login < NOW() - INTERVAL '30 days'
ORDER BY last_login;
```

---

## 🎉 Success!

Once configured, you'll see:

- ✅ **Sidebar shows**: "Using Supabase cloud database (permanent storage)"
- ✅ **Users persist** after app restarts
- ✅ **Professional setup** - no more data loss!
- ✅ **Scalable** - supports unlimited users (within free tier limits)

---

## 📞 Need Help?

- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Community**: [https://github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
- **Your setup files**:
  - `auth/supabase_auth.py` - Cloud authentication
  - `auth/hybrid_auth.py` - Smart fallback system
  - `supabase_setup.sql` - Database schema
  - `.streamlit/secrets.toml.template` - Example config

---

## 🔄 Migration from Local Files (Optional)

If you have existing users in `data/users.json` you want to keep:

### Option 1: Manual Migration

1. Have existing users re-register (they'll go to Supabase automatically)
2. Manually add important users via SQL Editor:

```sql
INSERT INTO users (id, username, email, password_hash, role)
VALUES (
    gen_random_uuid(),
    'existing_user',
    'user@bardsantner.com',
    'their_password_hash',
    'user'
);
```

### Option 2: Bulk Import Script

Create a Python script to bulk import:

```python
import json
from auth.supabase_auth import SupabaseAuthentication

# Load existing users
with open('data/users.json', 'r') as f:
    users = json.load(f)

# Initialize Supabase
auth = SupabaseAuthentication()

# Import users
for username, data in users.items():
    try:
        # Insert directly (password already hashed)
        auth.supabase.table('users').insert({
            'username': username,
            'email': data['email'],
            'password_hash': data['password'],
            'role': data.get('role', 'user')
        }).execute()
        print(f"✅ Imported: {username}")
    except Exception as e:
        print(f"❌ Failed: {username} - {e}")
```

---

**🎯 You're all set! Your users will now persist permanently in the cloud. No more data loss!**
