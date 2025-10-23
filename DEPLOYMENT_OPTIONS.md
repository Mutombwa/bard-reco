# Preventing App Sleep & User Data Loss

## The Problem
On Streamlit Cloud **free tier**, your app will:
- ✅ Go to sleep after **7 days of inactivity**
- ❌ Lose all file-based data (including `data/users.json`)
- ❌ Force users to re-register

## Solutions

### **Option 1: Upgrade to Streamlit Cloud Paid Plan (Easiest)**
**Cost:** $20/month per app
**Benefits:**
- ✅ App never sleeps
- ✅ Persistent file storage
- ✅ Better performance
- ✅ No data loss

**How to upgrade:**
1. Go to https://streamlit.io/cloud
2. Click "Upgrade" on your app
3. Choose a paid plan

---

### **Option 2: Use a Cloud Database (Recommended for Production)**
Store users in a database instead of `users.json`:

#### **A. Supabase (FREE tier available)**
1. Create account at https://supabase.com
2. Create a new project
3. Get your connection details
4. Add to Streamlit secrets:
   ```toml
   # .streamlit/secrets.toml
   [supabase]
   url = "https://xxxxx.supabase.co"
   key = "your-anon-key"
   ```
5. Update authentication to use Supabase

#### **B. PostgreSQL on Railway/Render (FREE tier)**
1. Deploy free PostgreSQL at https://railway.app or https://render.com
2. Get connection string
3. Add to Streamlit secrets
4. Update authentication

---

### **Option 3: Deploy Elsewhere (Free alternatives)**

#### **A. Render.com**
- ✅ Free tier available
- ✅ Persistent disk storage
- ✅ No sleep (on paid plan)
```bash
# Deploy on Render
1. Push to GitHub
2. Connect Render to your repo
3. Select "Web Service"
4. Build command: pip install -r requirements.txt
5. Start command: streamlit run app.py --server.port $PORT
```

#### **B. Hugging Face Spaces**
- ✅ Free
- ✅ Always on
- ✅ Persistent storage
```bash
# Create a Spaces app
1. Go to https://huggingface.co/spaces
2. Create new Space
3. Choose "Streamlit" 
4. Push your code
```

#### **C. Self-Host on VPS**
- Use DigitalOcean ($5/month) or AWS/Azure
- Full control, no sleep
- Persistent storage

---

### **Option 4: Workaround for Free Tier (Temporary)**
Keep app awake by pinging it regularly:

1. **Create a GitHub Action** to ping your app:
```yaml
# .github/workflows/keep-alive.yml
name: Keep Streamlit App Awake
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping app
        run: curl https://your-app-name.streamlit.app
```

2. **Use UptimeRobot** (free):
   - Visit https://uptimerobot.com
   - Add your app URL
   - Set to ping every 5 minutes
   - This keeps the app awake but **data will still be lost on restart**

---

## **Recommended Solution for Your App**

For a **professional production app**, I recommend:

1. **Immediate Fix (Today):**
   - Add UptimeRobot to keep app awake
   - Add a warning message to users about data persistence

2. **Permanent Fix (This Week):**
   - Integrate Supabase (FREE) for user authentication
   - Store user data in cloud database
   - Data persists even if app sleeps

3. **Long-term (Production):**
   - Upgrade to Streamlit Cloud paid plan ($20/month)
   - OR deploy on Railway/Render with persistent storage
   - Add automated backups

---

## Quick Fix: Add Warning to Users

Add this to your login/register page:
```python
st.warning("""
⚠️ **Note:** This app is on free hosting. User accounts may be reset if the app 
restarts. For permanent accounts, please contact your administrator.
""")
```

Would you like me to implement the **Supabase integration** for permanent user storage?
