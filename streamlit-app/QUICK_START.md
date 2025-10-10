# 🚀 Quick Start Guide

Get BARD-RECO running in 5 minutes!

## For Users (No Installation Method)

### Someone Already Deployed It?

If your organization already deployed BARD-RECO:

1. **Get the Link**
   - Ask your admin for the application URL
   - Example: `https://your-company-bard-reco.streamlit.app`

2. **Get Credentials**
   - Ask your admin for username and password
   - Or register for a new account

3. **Access**
   - Open the link in any web browser
   - Login with your credentials
   - Start reconciling!

**That's it! No Python, no installation, no setup!** 🎉

---

## For Administrators (Deployment)

### Option 1: Streamlit Cloud (Recommended - FREE)

**Time: 5 minutes**

1. **Fork this repository** on GitHub

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"

3. **Deploy**
   - Repository: `your-username/bard-reco`
   - Branch: `main`
   - Main file path: `streamlit-app/app.py`
   - Click "Deploy"!

4. **Share**
   - Copy your app URL: `https://your-username-bard-reco.streamlit.app`
   - Share with users
   - Default login: `admin` / `admin123`
   - **⚠️ Change default password immediately!**

---

### Option 2: Run Locally

**Time: 3 minutes**

#### Windows

1. **Double-click** `run.bat`
2. Wait for installation
3. Open browser to http://localhost:8501
4. Login: `admin` / `admin123`

#### Mac/Linux

1. Open terminal in `streamlit-app` folder
2. Run:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. Open browser to http://localhost:8501
4. Login: `admin` / `admin123`

#### Manual Method

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

---

### Option 3: Docker

**Time: 2 minutes**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down
```

Access at http://localhost:8501

---

## First Steps After Deployment

### 1. Change Default Password

**IMPORTANT: Do this immediately!**

1. Login with `admin` / `admin123`
2. Go to Settings → Security
3. Change password
4. Or delete `data/users.json` and create new admin account

### 2. Create User Accounts

1. Click "📝 Register" on login page
2. Create accounts for your team
3. Share credentials securely

### 3. Test the System

1. Upload sample Excel files
2. Run a test reconciliation
3. Verify export functionality

---

## Common Questions

### Q: Do users need Python installed?

**A: No!** If you deploy to cloud (Streamlit Cloud, AWS, etc.), users only need:
- Web browser
- Internet connection
- Login credentials

### Q: How much does it cost?

**A: FREE!**
- Streamlit Cloud free tier: Unlimited
- Open source: $0
- AWS/Cloud: Pay only for hosting (can be < $10/month)

### Q: Can it handle large files?

**A: Yes!**
- Tested with 100,000+ rows
- Streamlit Cloud free tier: Up to 1 GB RAM
- For larger: Upgrade plan or use AWS/Azure

### Q: Is it secure?

**A: Yes!**
- Password hashing (SHA-256)
- Session management
- HTTPS on Streamlit Cloud
- User-specific data isolation

### Q: Can I customize it?

**A: Absolutely!**
- Open source - modify anything
- See `README.md` for customization guide
- All code is well-documented

---

## Need Help?

### Documentation
- **Full Guide**: [README.md](README.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **User Manual**: See Dashboard → Help

### Support
- **GitHub Issues**: Report bugs
- **Email**: support@bard-reco.com
- **Community**: Discussions tab

---

## What's Next?

1. ✅ Deploy application
2. ✅ Change default password
3. ✅ Create user accounts
4. ✅ Test reconciliation
5. 📖 Read full [README.md](README.md)
6. 🚀 Share with your team!

---

**Enjoy BARD-RECO! 💼**
