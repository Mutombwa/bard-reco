# 🚀 Quick Deployment Reference Card

## ✅ What's Been Set Up

### 🔐 Security Features
- ✅ Email domain restriction: `@bardsantner.com` only
- ✅ Password hashing (SHA-256)
- ✅ Session management
- ✅ User registration validation

### 👤 Default Admin Account
```
Username: tatenda.mutombwa
Password: admin123
Email: tatenda.mutombwa@bardsantner.com
```
⚠️ **IMPORTANT**: Change password after first login!

---

## 🎯 Recommended: Streamlit Cloud

### Why Streamlit Cloud?
✅ **FREE** for private apps
✅ **2-3 minutes** to deploy
✅ **Auto-deploys** on git push
✅ **Zero configuration** needed
✅ **Perfect** for Streamlit apps

### Cost Comparison
| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| **Streamlit Cloud** | **FREE** ⭐ | **2-3 min** | Streamlit apps (Private) |
| Render | $7/month | 10-15 min | General apps |
| Heroku | $7/month | 10-15 min | General apps |
| AWS/Azure | $10+/month | 30+ min | Enterprise |

---

## 📋 5-Minute Deployment Checklist

### Step 1: GitHub Setup (2 min)
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Bank reconciliation app - ready for deployment"

# Create GitHub repo (via web: https://github.com/new)
# Make it PRIVATE for security

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/bard-reco-app.git
git push -u origin main
```

### Step 2: Streamlit Cloud (3 min)
1. Go to https://streamlit.io/cloud
2. Click "Sign up" → Connect GitHub
3. Click "New app"
4. Select your repo: `YOUR_USERNAME/bard-reco-app`
5. Main file: `app.py`
6. Branch: `main`
7. Click "Deploy!" 🚀

### Step 3: Configure Privacy
1. App settings → "Sharing"
2. Set to "Private" or "Restricted"
3. Done! ✅

---

## 🔑 First Login Steps

1. Open your deployed app URL: `https://your-app.streamlit.app`
2. Login with default admin credentials (see above)
3. **Immediately change password!**
4. Share URL with your team (@bardsantner.com users)

---

## 👥 User Registration

Users can self-register with these requirements:
- ✅ Must use `@bardsantner.com` email
- ✅ Password minimum 6 characters
- ✅ Email must be unique
- ❌ Other email domains will be rejected

Example valid emails:
- `john.doe@bardsantner.com` ✅
- `jane.smith@bardsantner.com` ✅
- `admin@gmail.com` ❌ (rejected)

---

## 🔄 Updating Your App

After initial deployment, updates are automatic:

```bash
# Make your code changes
# Then:
git add .
git commit -m "Updated reconciliation logic"
git push origin main
```

Streamlit Cloud will automatically redeploy in ~2 minutes! 🎉

---

## 📊 App Features Ready

✅ FNB Workflow (with split detection)
✅ Bidvest Workflow  
✅ Corporate Workflow
✅ User authentication with email restriction
✅ Export to Excel/CSV
✅ Real-time reconciliation progress
✅ Dashboard analytics

---

## 🆘 Troubleshooting

### "Email domain not allowed"
- Only @bardsantner.com emails can register
- Check spelling of email address

### "Build failed" on Streamlit Cloud
- Verify `requirements.txt` is committed
- Check Python version compatibility

### Users can't register
- Confirm they're using @bardsantner.com email
- Check username isn't already taken

---

## 📞 Support

- **Full Guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Community**: https://discuss.streamlit.io

---

**🎉 You're ready to deploy! It takes just 5 minutes!**
