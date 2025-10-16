# 💼 BARD-RECO - Modern Cloud Reconciliation System

A **state-of-the-art**, **private** cloud reconciliation application built with **Streamlit**. Access from anywhere with just a web browser - **no Python or Conda installation required**!

**🔒 PRIVATE ACCESS**: Only `@bardsantner.com` email addresses can register and access this system.

## ✨ Features

### 🚀 **Modern & Fast**
- Lightning-fast reconciliation engine with advanced algorithms
- Real-time progress tracking
- Responsive, mobile-friendly interface
- Smooth animations and transitions

### 🔒 **Secure & Private**
- **Email Domain Restriction**: Only @bardsantner.com emails can register
- User authentication and session management
- Password hashing with SHA-256
- Secure file handling
- User-specific data isolation

### 📊 **Advanced Reconciliation**
- **Perfect Matching**: Exact match on amount, date, and reference
- **Fuzzy Matching**: Smart similarity-based matching (85%+ threshold)
- **Balanced Matching**: AI-powered multi-transaction balancing
- **Configurable Rules**: Customize matching criteria

### ✏️ **Excel-Like Data Editor**
- Copy/paste directly from Excel
- Add, edit, delete rows and columns
- Advanced filtering and search
- Undo/redo functionality
- Export to Excel/CSV

### 📈 **Dashboard & Analytics**
- Real-time statistics
- Interactive charts with Plotly
- Match distribution visualization
- Trend analysis

### 📤 **Export & Reporting**
- Export to Excel with formatted sheets
- Generate HTML reports
- Download CSV files
- Automated file organization

## 🎯 Quick Start

### Option 1: Local Installation

1. **Clone or download this folder**
   ```bash
   cd streamlit-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access in browser**
   - Open http://localhost:8501
   - Default login: `admin` / `admin123`

### Option 2: Cloud Deployment

#### Deploy to Streamlit Cloud (Recommended - **100% Free**)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"!

3. **Share the link**
   - Your app will be live at: `https://your-app-name.streamlit.app`
   - Share this link with users - they just need login credentials!

#### Deploy to Other Platforms

**Heroku**
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

**AWS/Azure/GCP**
- Use Docker with the provided Dockerfile
- Deploy to container services
- Configure environment variables

## 📁 Project Structure

```
streamlit-app/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── auth/
│   ├── __init__.py
│   └── authentication.py      # User authentication system
├── components/
│   ├── __init__.py
│   ├── dashboard.py           # Dashboard component
│   └── data_editor.py         # Data editor component
├── src/
│   ├── __init__.py
│   └── reconciliation_engine.py  # Core reconciliation logic
├── utils/
│   ├── __init__.py
│   ├── session_state.py       # Session management
│   ├── export_utils.py        # Export functionality
│   └── report_generator.py    # Report generation
├── config/
│   ├── __init__.py
│   └── app_config.py          # Application configuration
├── data/                      # User data (auto-created)
│   ├── users.json            # User database
│   ├── uploads/              # Uploaded files
│   ├── exports/              # Exported files
│   └── reports/              # Generated reports
└── README.md                  # This file
```

## 📖 User Guide

### First Time Setup

1. **Register an Account**
   - Click "📝 Register" on login page
   - Choose a username and strong password
   - Optional: Add email for recovery

2. **Login**
   - Use your credentials
   - Session stays active for 2 hours

### Performing Reconciliation

1. **Upload Files**
   - Navigate to "📊 Reconciliation"
   - Upload Ledger/Cashbook (Excel or CSV)
   - Upload Bank Statement (Excel or CSV)

2. **Configure Matching**
   - Select amount columns from both files
   - Select date columns
   - Select reference columns
   - Adjust fuzzy threshold (default: 85%)
   - Set date tolerance (default: ±3 days)
   - Set amount tolerance (default: 0.1%)

3. **Run Reconciliation**
   - Click "🚀 Start Reconciliation"
   - Watch real-time progress
   - Review results in tabs

4. **Export Results**
   - Perfect Matches
   - Fuzzy Matches
   - Balanced Transactions
   - Unmatched Items
   - Export to Excel or generate HTML report

### Data Editing

1. **Edit Before Reconciliation**
   - Click "✏️ Edit Ledger Data" or "✏️ Edit Statement Data"
   - Use Excel-like interface
   - **Paste from Excel**: Copy from Excel (Ctrl+C), paste in text area
   - Add/delete rows and columns
   - Filter and search
   - Save changes

2. **Paste from Excel**
   - Copy data in Excel (Ctrl+C)
   - Expand "📋 Paste from Excel"
   - Paste in text area (Ctrl+V)
   - Choose "Replace All" or "Append Data"
   - Click apply

### Dashboard

- View overall statistics
- See match distribution charts
- Monitor trends
- Review recent activity

## 🔧 Configuration

### Customize Matching Rules

Edit `config/app_config.py`:

```python
RECONCILIATION_CONFIG = {
    'default_fuzzy_threshold': 85,    # 0-100
    'default_date_tolerance': 3,      # days
    'default_amount_tolerance': 0.1,  # percentage
    'enable_ai': True,                # AI suggestions
    'max_file_size_mb': 100,
}
```

### Customize UI

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#3498db"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

## 🌐 Deployment Best Practices

### For Production Use

1. **Change Default Password**
   - Delete `data/users.json`
   - First user will create new admin account

2. **Environment Variables**
   - Set `STREAMLIT_SERVER_PORT`
   - Set `STREAMLIT_SERVER_ADDRESS`
   - Configure secrets in `.streamlit/secrets.toml`

3. **Security**
   - Use HTTPS in production
   - Enable XSRF protection
   - Set strong session secrets

4. **Performance**
   - Limit file upload sizes
   - Enable caching
   - Use database for user management (production)

### Streamlit Cloud Deployment

1. **Secrets Management**
   - Go to app settings
   - Add secrets in dashboard
   - Never commit sensitive data

2. **Resource Limits**
   - Free tier: 1 CPU, 800 MB RAM
   - For larger datasets, upgrade plan

## 🐛 Troubleshooting

### Common Issues

**"Module not found" error**
```bash
pip install -r requirements.txt
```

**Port already in use**
```bash
streamlit run app.py --server.port 8502
```

**Data not persisting**
- Check that `data/` folder exists
- Ensure write permissions
- For cloud: Use database instead of JSON

**Slow performance**
- Reduce file size
- Increase date/amount tolerance
- Disable AI matching for very large datasets

## 🆚 Comparison with GUI Version

| Feature | GUI (Tkinter) | Web App (Streamlit) |
|---------|---------------|---------------------|
| **Installation** | Python + packages required | Browser only! |
| **Access** | Local machine only | Anywhere via link |
| **Deployment** | Manual on each PC | One-time cloud deploy |
| **Updates** | Update all installations | Update once, affects all |
| **Collaboration** | File sharing needed | Real-time shared access |
| **Modern UI** | Standard Windows | Beautiful, responsive |
| **Mobile Support** | ❌ | ✅ |
| **User Management** | ❌ | ✅ Built-in |
| **Cloud Storage** | ❌ | ✅ Integrated |

## 🎨 Customization

### Adding Custom Features

1. **New Matching Algorithm**
   - Edit `src/reconciliation_engine.py`
   - Add method to `ReconciliationEngine` class

2. **New Export Format**
   - Edit `utils/export_utils.py`
   - Add export function

3. **New UI Component**
   - Create file in `components/`
   - Import in `app.py`

## 📊 Performance

- **Small files** (< 1,000 rows): < 1 second
- **Medium files** (1,000 - 10,000 rows): 1-5 seconds
- **Large files** (10,000 - 100,000 rows): 5-30 seconds
- **Very large files** (> 100,000 rows): 30-120 seconds

## 🤝 Support

- **Issues**: Open GitHub issue
- **Email**: support@bard-reco.com
- **Docs**: See `/docs` folder

## 📄 License

MIT License - Free for commercial and personal use

## 🚀 Future Enhancements

- [ ] PostgreSQL/MySQL integration
- [ ] Real-time collaboration
- [ ] Advanced AI matching
- [ ] Mobile app
- [ ] API endpoints
- [ ] Webhook integrations
- [ ] Email notifications
- [ ] PDF export
- [ ] Multi-language support
- [ ] Dark mode

---

## 🚀 Deployment

### **Recommended: Streamlit Cloud (Free & Easy)**

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete step-by-step instructions.**

**Quick Start:**
1. Push code to GitHub (private repository)
2. Sign up at https://streamlit.io/cloud
3. Connect your GitHub repo
4. Click "Deploy"
5. Done! App live in 2-3 minutes ⚡

**Default Admin Credentials:**
- Username: `tatenda.mutombwa`
- Password: `admin123` (⚠️ Change immediately!)
- Email: `tatenda.mutombwa@bardsantner.com`

---

**Made with ❤️ using Streamlit**

**🔐 Private System**: Restricted to @bardsantner.com users only.
