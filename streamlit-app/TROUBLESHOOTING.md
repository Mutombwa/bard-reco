# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: XSRF Protection Error (FIXED!)

**Error:**
```
SystemError: PY_SSIZE_T_CLEAN macro must be defined for '#' formats
Warning: the config option 'server.enableCORS=false' is not compatible with 'server.enableXsrfProtection=true'
```

**Solution:** ✅ Already fixed in `.streamlit/config.toml`

The configuration has been updated to disable XSRF protection for local development.

If you still see this error:
1. Stop the server (Ctrl+C)
2. Delete `.streamlit/secrets.toml` if it exists
3. Restart: `streamlit run app.py`

---

### Issue 2: Config Option Not Valid Warnings

**Warning:**
```
"runner.installTracer" is not a valid config option
"runner.fixMatplotlib" is not a valid config option
```

**Solution:** ✅ Already fixed!

These options have been removed from the config file as they're not supported in newer Streamlit versions.

**Impact:** None - these warnings don't affect functionality.

---

### Issue 3: Module Not Found Errors

**Error:**
```
ModuleNotFoundError: No module named 'streamlit'
ModuleNotFoundError: No module named 'plotly'
```

**Solution:**

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install streamlit==1.31.0
pip install plotly==5.18.0
pip install pandas==2.2.0
pip install rapidfuzz==3.6.1
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9
```

---

### Issue 4: Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**

**Option A: Use a different port**
```bash
streamlit run app.py --server.port 8502
```

**Option B: Kill the process using port 8501**

Windows:
```powershell
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

Linux/Mac:
```bash
lsof -ti:8501 | xargs kill -9
```

---

### Issue 5: Data Not Persisting

**Problem:** User data disappears after restart

**Cause:** The `data/` folder is being deleted or not writable

**Solution:**

1. **Check folder exists:**
   ```bash
   # Should create automatically, but you can create manually
   mkdir -p data/uploads data/exports data/reports
   ```

2. **Check permissions:**
   ```bash
   # Linux/Mac
   chmod -R 755 data/

   # Windows: Right-click data folder → Properties → Security → Ensure write permissions
   ```

3. **For production:** Use a database instead of JSON files
   - PostgreSQL
   - MySQL
   - MongoDB

---

### Issue 6: File Upload Fails

**Error:**
```
File size exceeds maximum allowed
```

**Solution:**

Edit `config/app_config.py`:

```python
RECONCILIATION_CONFIG = {
    'max_file_size_mb': 200,  # Increase from 100 to 200 MB
    # ...
}
```

Or in Streamlit Cloud:
- Go to App Settings
- Advanced Settings
- Increase upload limit

---

### Issue 7: Slow Performance

**Problem:** App is slow with large files

**Solutions:**

1. **Increase tolerance to reduce comparisons:**
   ```python
   # In reconciliation page
   amount_tolerance = 1.0  # Instead of 0.1
   date_tolerance = 7      # Instead of 3 days
   ```

2. **Disable AI matching for large datasets:**
   ```python
   enable_ai = False  # For files > 50,000 rows
   ```

3. **Use sampling for preview:**
   ```python
   # Preview only first 1000 rows
   df.head(1000)
   ```

4. **Upgrade hosting:**
   - Streamlit Cloud: Upgrade plan
   - Self-hosted: Increase RAM/CPU

---

### Issue 8: Excel Export Not Working

**Error:**
```
ModuleNotFoundError: No module named 'xlsxwriter'
```

**Solution:**

```bash
pip install xlsxwriter openpyxl
```

**Alternative:** Export as CSV instead of Excel

---

### Issue 9: Authentication Not Working

**Problem:** Can't login with admin/admin123

**Solution:**

1. **Check `data/users.json` exists:**
   ```bash
   # If missing, delete it and restart app
   rm data/users.json
   streamlit run app.py
   ```

2. **Manually create users file:**
   Create `data/users.json`:
   ```json
   {
     "admin": {
       "password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
       "email": "admin@bard-reco.com",
       "created_at": "2025-10-08T00:00:00",
       "role": "admin"
     }
   }
   ```
   (This is the hash for "admin123")

3. **Reset password:**
   - Delete `data/users.json`
   - Register new account
   - Use that account

---

### Issue 10: Browser Shows "Connection Error"

**Problem:** Can't connect to http://localhost:8501

**Checks:**

1. **Is Streamlit running?**
   - Check terminal/console for "You can now view your Streamlit app"

2. **Firewall blocking?**
   - Windows: Allow Python through firewall
   - Mac: System Preferences → Security → Allow

3. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

4. **Try different URL:**
   ```
   http://localhost:8501
   http://127.0.0.1:8501
   http://[your-local-ip]:8501
   ```

---

### Issue 11: Paste from Excel Not Working

**Problem:** Copy/paste from Excel doesn't work

**Solutions:**

1. **Check clipboard format:**
   - Copy from Excel (Ctrl+C)
   - Paste in text area (Ctrl+V)
   - Should be tab-separated values

2. **Alternative method:**
   - Save Excel as CSV
   - Upload CSV file instead

3. **Browser clipboard permissions:**
   - Chrome: Allow clipboard access when prompted
   - Firefox: about:config → dom.events.asyncClipboard.read → true

---

### Issue 12: Reconciliation Taking Too Long

**Problem:** Reconciliation never finishes

**Causes & Solutions:**

1. **File too large:**
   - Split into smaller chunks
   - Process in batches

2. **Too many comparisons:**
   - Increase fuzzy threshold (85 → 90)
   - Increase date tolerance
   - Disable balanced matching

3. **Stuck in loop:**
   - Refresh page (F5)
   - Restart app

---

### Issue 13: Docker Issues

**Error:**
```
docker-compose: command not found
```

**Solution:**

```bash
# Install Docker Desktop (includes Docker Compose)
# Windows/Mac: https://www.docker.com/products/docker-desktop

# Linux:
sudo apt-get install docker-compose
```

**Error:**
```
Cannot connect to Docker daemon
```

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Or start Docker Desktop application
```

---

### Issue 14: Streamlit Cloud Deployment Fails

**Problem:** App won't deploy on Streamlit Cloud

**Solutions:**

1. **Check requirements.txt:**
   - Must be in root of repository
   - All dependencies listed
   - Correct versions

2. **Check main file path:**
   - Should be `streamlit-app/app.py`
   - Or move app.py to repository root

3. **Check Python version:**
   - Streamlit Cloud uses Python 3.9-3.11
   - Update requirements if needed

4. **Check logs:**
   - Streamlit Cloud dashboard → View logs
   - Fix errors shown

---

### Issue 15: Memory Errors

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Reduce data size:**
   - Process in chunks
   - Use sampling

2. **Increase memory:**
   - Local: Close other applications
   - Cloud: Upgrade plan
   - Docker: Increase container memory

3. **Optimize code:**
   - Use generators instead of lists
   - Delete unused DataFrames
   - Use `del` to free memory

---

## Quick Fixes Checklist

Before reporting an issue, try these:

- [ ] Restart the app (Ctrl+C, then `streamlit run app.py`)
- [ ] Clear browser cache (Ctrl+Shift+Delete)
- [ ] Update dependencies (`pip install -r requirements.txt --upgrade`)
- [ ] Check all files exist (auth/, components/, src/, utils/)
- [ ] Check file permissions (can write to data/)
- [ ] Try different browser
- [ ] Check antivirus/firewall
- [ ] Restart computer (really!)

---

## Still Having Issues?

### Get Help

1. **Check Documentation:**
   - [README.md](README.md)
   - [QUICK_START.md](QUICK_START.md)
   - [DEPLOYMENT.md](DEPLOYMENT.md)

2. **Check Logs:**
   ```bash
   # Terminal output shows errors
   # Look for:
   # - Traceback (most recent call last)
   # - Error messages
   # - Warning messages
   ```

3. **Enable Debug Mode:**

   In `app.py`, add at top:
   ```python
   import streamlit as st
   st.set_option('client.showErrorDetails', True)
   ```

4. **Report Issue:**
   - GitHub Issues
   - Include error message
   - Include steps to reproduce
   - Include Python version (`python --version`)
   - Include Streamlit version (`streamlit version`)

---

## Environment Debugging

**Check Your Environment:**

```bash
# Python version (should be 3.9-3.11)
python --version

# Streamlit version
streamlit version

# List installed packages
pip list | grep -E "streamlit|pandas|plotly|rapidfuzz"

# Check config
streamlit config show

# Test import
python -c "import streamlit; import pandas; import plotly; print('All imports OK')"
```

---

## Performance Optimization

If app is slow:

1. **Use caching:**
   ```python
   @st.cache_data
   def load_data(file):
       return pd.read_excel(file)
   ```

2. **Limit preview:**
   ```python
   st.dataframe(df.head(100))  # Instead of full DF
   ```

3. **Use st.session_state:**
   ```python
   if 'data' not in st.session_state:
       st.session_state.data = load_data()
   ```

4. **Profile performance:**
   ```bash
   streamlit run app.py --server.enableCORS=false --logger.level=debug
   ```

---

## System Requirements

**Minimum:**
- Python 3.9+
- 2 GB RAM
- 500 MB disk space

**Recommended:**
- Python 3.10+
- 4 GB RAM
- 1 GB disk space
- Modern browser (Chrome, Firefox, Edge)

**For Large Files (>50K rows):**
- 8 GB+ RAM
- 4 CPU cores
- SSD storage

---

## Contact Support

If nothing works:

📧 Email: support@bard-reco.com
🐛 GitHub Issues: [Your repo]/issues
💬 Discussions: [Your repo]/discussions

**Include in your report:**
- Operating System
- Python version
- Error message (full traceback)
- Steps to reproduce
- File sizes being processed
- Screenshots if applicable

---

**Most issues are fixed by:**
1. Restarting the app
2. Reinstalling dependencies
3. Checking file permissions

**Good luck! 🚀**
