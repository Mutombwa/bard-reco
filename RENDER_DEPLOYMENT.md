# 🚀 Render Deployment Guide for BARD-RECO

## Why Deploy to Render?

### Render vs Streamlit Cloud Comparison

| Feature | Render (Free) | Streamlit Cloud (Free) |
|---------|---------------|------------------------|
| **App Sleep** | ❌ Never sleeps | ✅ Sleeps after 7 days inactivity |
| **Cold Start** | ~30 seconds | ~5 seconds |
| **RAM** | 512 MB | 1 GB |
| **Build Time** | ~2-3 minutes | ~1-2 minutes |
| **Custom Domain** | ✅ Yes | ✅ Yes |
| **Database Support** | ✅ Built-in PostgreSQL | ⚠️ Requires external DB |
| **Environment Variables** | ✅ Easy | ✅ Easy |
| **Logs** | ✅ Full access | ✅ Full access |
| **Price (Paid)** | $7/month (starter) | $20/month (teams) |
| **Best For** | Production apps | Quick prototypes |

**Verdict:** 
- **Render** = Better for production (no sleep, database included)
- **Streamlit Cloud** = Better for demos/sharing

---

## 📋 Prerequisites

- GitHub account with your code pushed
- Render account (free): https://render.com
- Supabase account (optional, for cloud database)

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Repository

Your repo already has everything needed:
- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Render configuration
- ✅ `.streamlit/secrets.toml` - Secrets template
- ✅ All source code

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. **Dashboard** → Click **"New +"** → Select **"Web Service"**

2. **Connect Repository:**
   - Find and select: `Mutombwa/bard-reco`
   - Click **"Connect"**

3. **Configure Service:**
   ```
   Name: bard-reco
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave blank)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

4. **Select Plan:**
   - Choose **"Free"** plan
   - Note: Free services spin down after 15 min of inactivity
   - Upgrade to **$7/month Starter** for always-on

5. **Environment Variables:**
   Click **"Advanced"** → **"Add Environment Variable"**
   
   Add these:
   ```
   PYTHON_VERSION = 3.11.0
   STREAMLIT_SERVER_ENABLE_CORS = false
   STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = true
   ```

6. **Add Supabase Secrets (if using cloud database):**
   ```
   SUPABASE_URL = https://cmlbornqaojclzrtqffh.supabase.co
   SUPABASE_KEY = eyJhbGci... (your anon key)
   ```

7. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- ⏳ First build takes 2-3 minutes
- 📊 Watch the build logs in real-time
- ✅ When complete, you'll see "Live" status
- 🌐 Your app URL: `https://bard-reco.onrender.com`

### Step 5: Configure Secrets (if needed)

If using Supabase, update your `auth/supabase_auth.py` to read from environment:

```python
import os

SUPABASE_URL = os.getenv('SUPABASE_URL', st.secrets.get('supabase', {}).get('url'))
SUPABASE_KEY = os.getenv('SUPABASE_KEY', st.secrets.get('supabase', {}).get('key'))
```

---

## 🎯 Alternative: Use Render Blueprint

If you have `render.yaml` in your repo, Render can auto-configure:

1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Select your GitHub repo: `Mutombwa/bard-reco`
4. Click **"Apply"**
5. Render reads `render.yaml` and sets everything up automatically!

---

## 🔒 Adding Secrets to Render

### Method 1: Environment Variables (Recommended)

1. Go to your service dashboard
2. Click **"Environment"** in left sidebar
3. Click **"Add Environment Variable"**
4. Add each secret:
   ```
   SUPABASE_URL = your_url
   SUPABASE_KEY = your_key
   ```
5. Click **"Save Changes"**
6. Service will auto-redeploy

### Method 2: Secret Files

1. Create a `.streamlit` directory in Render:
   - Add to `render.yaml`:
   ```yaml
   buildCommand: |
     pip install -r requirements.txt
     mkdir -p .streamlit
     echo "[supabase]" > .streamlit/secrets.toml
     echo "url = \"$SUPABASE_URL\"" >> .streamlit/secrets.toml
     echo "key = \"$SUPABASE_KEY\"" >> .streamlit/secrets.toml
   ```

---

## 🐛 Troubleshooting

### Issue: Build Failed

**Solution:**
- Check `requirements.txt` has all dependencies
- Check Python version (3.11.0 recommended)
- View build logs for specific errors

### Issue: App Doesn't Start

**Solution:**
- Check start command:
  ```bash
  streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
  ```
- Make sure `app.py` is in root directory
- Check runtime logs

### Issue: "Address already in use"

**Solution:**
- Make sure start command uses `$PORT` (not hardcoded 8501)
- Render assigns port dynamically

### Issue: Database Connection Failed

**Solution:**
- Verify Supabase environment variables
- Check Supabase URL and key are correct
- Test connection from Render shell

---

## 📊 Monitoring Your App

### View Logs

1. Go to service dashboard
2. Click **"Logs"** tab
3. See real-time application logs
4. Filter by error/warning

### Check Metrics

1. Click **"Metrics"** tab
2. View:
   - CPU usage
   - Memory usage
   - Response times
   - Request counts

### Set Up Alerts

1. Click **"Settings"**
2. Scroll to **"Alerts"**
3. Add email for:
   - Deploy failures
   - Service crashes
   - High memory usage

---

## 💰 Upgrade Options

### Free Plan Limits
- ✅ 750 hours/month compute
- ✅ 512 MB RAM
- ✅ 100 GB bandwidth
- ❌ Spins down after 15 min inactivity
- ❌ Cold starts (~30 sec)

### Starter Plan ($7/month)
- ✅ Always on (no sleep!)
- ✅ 512 MB RAM
- ✅ Faster cold starts
- ✅ Custom domain
- ✅ Priority support

### Pro Plan ($25/month)
- ✅ 2 GB RAM
- ✅ Auto-scaling
- ✅ Zero-downtime deploys
- ✅ Advanced metrics

---

## 🔄 Auto-Deploy from GitHub

### Enable Automatic Deployments

1. Go to service **"Settings"**
2. Under **"Build & Deploy"**
3. Enable **"Auto-Deploy"**
4. Select branch: `main`
5. Now every push to `main` auto-deploys!

### Manual Deploy

1. Go to service dashboard
2. Click **"Manual Deploy"**
3. Select **"Deploy latest commit"**
4. Click **"Deploy"**

---

## 🌐 Custom Domain

### Add Your Domain

1. Go to service **"Settings"**
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter: `reconciliation.yourdomain.com`
5. Follow DNS setup instructions
6. Add CNAME record to your DNS:
   ```
   reconciliation.yourdomain.com → bard-reco.onrender.com
   ```

### SSL Certificate

- ✅ Render provides free SSL automatically
- 🔒 HTTPS enabled by default
- 🔄 Auto-renewal

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] App loads at Render URL
- [ ] Login/Register works
- [ ] Supabase connection active (if using)
- [ ] File uploads work
- [ ] Reconciliation runs successfully
- [ ] Downloads work
- [ ] No errors in logs

---

## 📞 Support

### Render Support
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### BARD-RECO Issues
- GitHub: https://github.com/Mutombwa/bard-reco/issues

---

## 🆚 Final Comparison

### Choose Render If:
- ✅ You need production-ready hosting
- ✅ You want app always available (no sleep)
- ✅ You need built-in PostgreSQL
- ✅ Budget is $7/month or free

### Choose Streamlit Cloud If:
- ✅ Quick prototypes/demos
- ✅ Sharing with team quickly
- ✅ Streamlit-native features
- ✅ You're okay with app sleeping

**Recommendation:** Deploy to BOTH!
- **Render** for production users
- **Streamlit Cloud** for testing/demos

---

## 🚀 Quick Deploy Button

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Mutombwa/bard-reco)

---

*Last Updated: October 23, 2025*
