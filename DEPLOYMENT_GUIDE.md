# 🚀 Deployment Guide: Streamlit Cloud

## Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)
- Your code in a GitHub repository

---

## 📋 Step-by-Step Deployment

### 1️⃣ **Prepare Your GitHub Repository**

1. Create a new **private** GitHub repository (to keep it secure)
2. Push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit - Bank Reconciliation App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streamlit-reconciliation-app.git
git push -u origin main
```

### 2️⃣ **Sign Up for Streamlit Cloud**

1. Go to https://streamlit.io/cloud
2. Click "Sign up" and connect your GitHub account
3. Authorize Streamlit Cloud to access your repositories

### 3️⃣ **Deploy Your App**

1. Click "New app" in Streamlit Cloud dashboard
2. Select your repository: `YOUR_USERNAME/streamlit-reconciliation-app`
3. Set the main file path: `app.py`
4. Choose branch: `main`
5. Click "Deploy!"

The app will deploy in 2-3 minutes ⏱️

### 4️⃣ **Configure Privacy Settings**

1. In your app dashboard, click "Settings"
2. Go to "Sharing" section
3. Set visibility to **"Restricted"** or **"Private"**
4. Add allowed email addresses (all @bardsantner.com users)

---

## 🔐 Security Features Already Implemented

✅ **Email Domain Restriction**
- Only `@bardsantner.com` emails can register
- Enforced at application level

✅ **Password Protection**
- SHA-256 hashed passwords
- Minimum 6 characters required

✅ **Session Management**
- Secure session handling
- Auto-logout on browser close

---

## 🌐 Access Your Deployed App

After deployment, your app will be available at:
```
https://your-app-name.streamlit.app
```

**Default Admin Account:**
- Username: `tatenda.mutombwa`
- Password: `admin123` (⚠️ **Change this immediately after first login!**)
- Email: `tatenda.mutombwa@bardsantner.com`

---

## 📝 Post-Deployment Tasks

1. **Change Admin Password**
   - Login with default credentials
   - Change password immediately

2. **Test Email Registration**
   - Try registering with @bardsantner.com email ✅
   - Verify non-bardsantner emails are rejected ❌

3. **Share with Team**
   - Send app URL to your team
   - They can register with their @bardsantner.com emails

---

## 🛠️ Updating Your App

Any push to the `main` branch will auto-deploy:

```bash
git add .
git commit -m "Update reconciliation logic"
git push origin main
```

The app will automatically redeploy in ~2 minutes! 🚀

---

## 💰 Cost

**Streamlit Cloud Free Tier:**
- ✅ Unlimited private apps
- ✅ Up to 1 GB RAM per app
- ✅ Community support
- ✅ Perfect for your use case!

**Upgrade if needed:**
- $20/month for more resources
- Priority support

---

## 🆘 Troubleshooting

**Issue: App shows "Build Failed"**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility

**Issue: Data not persisting**
- Streamlit Cloud uses ephemeral storage
- User accounts are stored in `data/users.json` (will reset on redeploy)
- Consider upgrading to PostgreSQL for persistent storage

**Issue: Large file uploads failing**
- Check `maxUploadSize` in `.streamlit/config.toml`
- Default is 200MB

---

## 📞 Support

Need help? Contact:
- Streamlit Community: https://discuss.streamlit.io
- GitHub Issues: Your repository issues page

---

**🎉 Your private, domain-restricted reconciliation app is now live!**
