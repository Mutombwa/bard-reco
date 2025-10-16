# 🚀 Streamlit Cloud Deployment Steps

## To Deploy Your Changes to https://bard-reco.streamlit.app

---

## ✅ Step 1: Commit Your Changes

Open your terminal in the project folder and run:

```bash
# Check what files changed
git status

# Add all changed files
git add .

# Commit with a descriptive message
git commit -m "Fix: File uploader now uses content hashing for cloud deployment - columns persist correctly"

# Push to GitHub
git push origin main
```

**Note:** Replace `main` with your branch name if different (could be `master`)

---

## ✅ Step 2: Wait for Streamlit Cloud to Deploy

1. Go to https://share.streamlit.io (Streamlit Cloud dashboard)
2. Find your app "bard-reco"
3. You'll see **"Deploying..."** or **"Building..."** status
4. **Wait 2-5 minutes** for deployment to complete
5. Status will change to **"Running"** when ready

---

## ✅ Step 3: Verify the Fix Works

### **Test 1: File Upload & Column Persistence**

1. Go to https://bard-reco.streamlit.app/#fnb-workflow
2. Upload a test **Ledger file**
3. Upload a test **Statement file**
4. ✅ Verify you see: `📊 Ledger: X rows × Y columns`

### **Test 2: Add Reference Column (Statement)**

1. Scroll to "Step 2: Data Processing Tools"
2. Click **"🚀 Launch"** under "📝 Add Reference"
3. ✅ Wait for page to auto-refresh
4. ✅ Verify status shows: `✅ Reference added to Statement`
5. ✅ Check column count increased: `📊 Statement: X rows × (Y+1) columns`

### **Test 3: Add RJ & Payment Ref (Ledger)**

1. Click **"🚀 Launch"** under "🔢 RJ & Payment Ref"
2. ✅ Wait for page to auto-refresh
3. ✅ Verify status shows: `✅ RJ-Number & Payment Ref added`
4. ✅ Check column count increased: `📊 Ledger: X rows × (Y+2) columns`

### **Test 4: Verify Column Persistence**

1. Scroll to "Step 3: Configure Column Mapping"
2. Click the **"ℹ️ View Available Columns"** expander
3. ✅ **CRITICAL CHECK:** You should see:
   ```
   Ledger Columns (X total):
   ..., RJ-Number, Payment Ref, ...
   ✨ Added columns: RJ-Number, Payment Ref

   Statement Columns (Y total):
   ..., Reference, ...
   ✨ Added columns: Reference
   ```

4. Click any dropdown (e.g., "Date Column" for Ledger)
5. Select a column
6. Click another dropdown
7. ✅ **CRITICAL:** Check "View Available Columns" again
8. ✅ **The added columns (RJ-Number, Payment Ref, Reference) should STILL BE THERE**

### **Test 5: Full Reconciliation Flow**

1. Configure all column mappings
2. Set matching settings
3. Click **"🚀 Start Reconciliation"**
4. ✅ Verify results appear
5. Check the "Matched Pairs" tab
6. ✅ **VERIFY:** All columns appear including:
   - `Ledger_RJ-Number`
   - `Ledger_Payment Ref`
   - `Statement_Reference`

### **Test 6: Save & Export**

1. Click **"💾 Save Results to Database"**
2. Enter a name and click **"✅ Confirm Save"**
3. ✅ Verify success message
4. Click **"📊 Export All to Excel"**
5. Download and open the Excel file
6. ✅ **VERIFY:** All added columns are in the export

---

## 🔧 If Tests Fail

### **Problem: Changes not showing up**

**Solution:**
1. Hard refresh the browser: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Clear browser cache
3. Open in incognito/private mode
4. Wait another 2 minutes (deployment might be slow)

### **Problem: Columns still disappearing**

**Check:**
1. Did you push ALL changes to GitHub?
   ```bash
   git status
   # Should show "nothing to commit, working tree clean"
   ```

2. Is deployment complete on Streamlit Cloud?
   - Dashboard should show "Running" not "Building"

3. Are you testing with NEW files?
   - Don't use browser back button
   - Start fresh each test

### **Problem: Import errors or app crashes**

**Check:**
1. Look at Streamlit Cloud logs:
   - Go to app dashboard
   - Click "Manage app"
   - Check logs for errors

2. Common fixes:
   ```bash
   # Make sure requirements.txt has all dependencies
   cat streamlit-app/requirements.txt

   # Should include:
   # streamlit
   # pandas
   # numpy
   # openpyxl  ← Important for Excel
   # fuzzywuzzy
   # python-Levenshtein
   ```

---

## 📊 What Was Changed

### **Files Modified:**

1. **streamlit-app/components/fnb_workflow.py**
   - Line 127-209: `render_file_upload()` - Uses MD5 hash of file content
   - Line 224-345: `add_reference_tool()` - Fixed to process Statement not Ledger
   - Line 1048-1128: Added `save_results_to_db()` method

2. **streamlit-app/utils/database.py** (NEW FILE)
   - Complete database system for saving results
   - SQLite-based with 4 tables

3. **streamlit-app/app.py**
   - Line 603-740: Enhanced Data Management page
   - Added saved results viewing

4. **streamlit-app/components/bidvest_workflow.py**
   - Line 73: Removed duplicate back button

5. **streamlit-app/components/corporate_workflow.py**
   - Line 35: Removed duplicate back button

### **Key Technical Changes:**

**Before (BROKEN):**
```python
# File ID tracking - doesn't work on Cloud
file_id = f"{ledger_file.name}_{ledger_file.size}"
if st.session_state.file_id != file_id:
    st.session_state.fnb_ledger = pd.read_csv(ledger_file)
```

**After (FIXED):**
```python
# Content hash - works everywhere
import hashlib
file_bytes = ledger_file.getvalue()
file_hash = hashlib.md5(file_bytes).hexdigest()

if st.session_state.fnb_ledger_hash != file_hash:
    st.session_state.fnb_ledger = pd.read_csv(ledger_file)
    st.session_state.fnb_ledger_hash = file_hash
```

**Why this works:**
- `getvalue()` reads actual file bytes
- MD5 hash is unique per file content
- Hash persists in session state
- Only reloads if different file uploaded
- Added columns stay in session state DataFrame

---

## 📋 Post-Deployment Checklist

After successful deployment, verify:

- [ ] App loads without errors
- [ ] File upload works for both Ledger and Statement
- [ ] "Add Reference" adds column to Statement (not Ledger)
- [ ] "RJ & Payment Ref" adds columns to Ledger
- [ ] Column count shows correctly after adding
- [ ] "View Available Columns" shows added columns
- [ ] Clicking dropdowns doesn't lose columns
- [ ] Reconciliation runs successfully
- [ ] Results include all added columns
- [ ] Export includes all added columns
- [ ] Save to database works
- [ ] Data Management page shows saved results
- [ ] Loading saved results works

---

## 🎉 Success Criteria

✅ **The fix is working if:**

1. You can add columns (Reference, RJ-Number, Payment Ref)
2. After adding, the column count increases
3. Clicking any dropdown/button preserves the columns
4. "View Available Columns" consistently shows added columns
5. Reconciliation results include all columns
6. Exports include all columns

---

## 🆘 Emergency Rollback

If deployment breaks everything:

```bash
# Revert to previous commit
git log --oneline -5  # Find previous commit hash
git revert <commit-hash>
git push origin main

# Or reset hard (DANGER: loses changes)
git reset --hard HEAD~1
git push origin main --force
```

---

## 📞 Need Help?

**Check:**
1. Streamlit Cloud logs (Manage app → Logs)
2. Browser console (F12 → Console)
3. GitHub Actions (if you have CI/CD)

**Debug Mode:**
Add this temporarily to see what's happening:
```python
# In fnb_workflow.py, add at top of render_file_upload()
st.write("DEBUG - Ledger hash:", st.session_state.get('fnb_ledger_hash', 'None'))
st.write("DEBUG - Ledger columns:", len(st.session_state.fnb_ledger.columns) if st.session_state.fnb_ledger is not None else 0)
```

---

## ✅ You're Done!

Follow these steps and the column persistence issue will be fixed on Streamlit Cloud! 🎉
