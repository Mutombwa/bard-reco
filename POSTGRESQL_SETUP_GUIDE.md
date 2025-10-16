# 🐘 PostgreSQL/Supabase Setup Guide

Quick guide to set up PostgreSQL database that works on **both localhost AND Streamlit Cloud**.

---

## 🎯 Why PostgreSQL/Supabase?

- ✅ Works on Streamlit Cloud (SQL Server doesn't)
- ✅ Free tier available
- ✅ Cloud-hosted (accessible from anywhere)
- ✅ Easy setup (5 minutes)

---

## 🚀 Option 1: Supabase (Recommended - Cloud)

### Step 1: Create Free Supabase Account

1. Go to: **https://supabase.com**
2. Click **"Start your project"**
3. Sign in with GitHub (or email)

### Step 2: Create New Project

1. Click **"New Project"**
2. Fill in:
   - **Name:** `reconciliation-db`
   - **Database Password:** Create a strong password (save it!)
   - **Region:** Choose closest to you
3. Click **"Create new project"**
4. Wait 2 minutes for setup

### Step 3: Get Connection String

1. In your project, click **"Settings"** (⚙️ icon)
2. Click **"Database"**
3. Scroll to **"Connection string"**
4. Select **"URI"** tab
5. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with your actual password

### Step 4: Configure in Streamlit App

**For Local Testing:**
1. In your app, go to **🗄️ Database Config**
2. Select **"PostgreSQL/Supabase"**
3. Paste your connection string
4. Click **Test Connection**

**For Streamlit Cloud:**
1. Go to your app dashboard: https://share.streamlit.io
2. Click your app → **Settings** → **Secrets**
3. Add:
   ```toml
   [postgres]
   host = "db.xxx.supabase.co"
   port = "5432"
   database = "postgres"
   user = "postgres"
   password = "your-password-here"
   ```
4. Click **Save**

---

## 🏠 Option 2: Local PostgreSQL

### For Windows:

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Download installer
   - Run and install (remember your password!)

2. **Connection String:**
   ```
   postgresql://postgres:your-password@localhost:5432/reconciliation_db
   ```

---

## ✅ Test Connection

After setup:
1. Open your Streamlit app
2. Go to **🗄️ Database Config**
3. Select **PostgreSQL/Supabase**
4. Enter connection details
5. Click **🔌 Test Connection**
6. Click **📋 Create Tables**

Done! Your reconciliation data will now save to the cloud! 🎊

---

## 🆚 SQL Server vs PostgreSQL

| Feature | SQL Server (Local) | PostgreSQL (Supabase) |
|---------|-------------------|----------------------|
| Works Locally | ✅ Yes | ✅ Yes |
| Works on Streamlit Cloud | ❌ No | ✅ Yes |
| Cost | Free (Express) | Free tier available |
| Setup Time | 10 min | 5 min |
| Cloud Access | No | Yes |

**Recommendation:** Use PostgreSQL/Supabase for cloud deployment!
