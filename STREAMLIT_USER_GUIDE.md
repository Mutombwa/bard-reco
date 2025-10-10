# 📘 FNB Workflow - Step-by-Step User Guide
## For: https://bard-reco.streamlit.app

---

## ✅ IMPORTANT: How Column Persistence Works

The app now uses **file content hashing** to preserve added columns. Here's what you need to know:

### **Key Behavior:**
1. When you upload a file **for the first time**, it's loaded into memory
2. When you add columns (RJ-Number, Payment Ref, Reference), they're stored in session state
3. **The file uploader only reloads if you upload a DIFFERENT file** (different content hash)
4. Added columns **persist** across page interactions (dropdowns, buttons, etc.)
5. Refreshing the page **clears everything** (this is normal Streamlit behavior)

---

## 📋 Step-by-Step Instructions

### **Step 1: Upload Your Files** 📁

1. Go to: **🔄 Workflows** → **🏦 FNB Workflow** tab
2. Under "Step 1: Import Files":
   - Upload your **Ledger file** (Excel or CSV)
   - Upload your **Statement file** (Excel or CSV)
3. ✅ You'll see: `📊 Ledger: X rows × Y columns`

**💡 TIP:** Click the "📋 View Columns" expander to see all column names

---

### **Step 2: Add Columns Using Data Tools** 🛠️

#### **For Statement - Add Reference Column:**

1. Find "Step 2: Data Processing Tools"
2. Under "**📝 Add Reference**":
   - Click **🚀 Launch**
3. ✅ The app will:
   - Extract names from Statement Description column
   - Add a "Reference" column after Description
   - Show sample extractions
   - **Auto-refresh** the page

4. ✅ Status will show: `✅ Reference added to Statement`
5. ✅ Column count increases: `📊 Statement: X rows × (Y+1) columns`

**Examples of extraction:**
```
"FNB APP PAYMENT FROM JOHN SMITH" → "JOHN SMITH"
"ADT CASH DEPO JAMES DOE" → "JAMES DOE"
"CAPITEC JANE WILLIAMS" → "JANE WILLIAMS"
```

#### **For Ledger - Add RJ-Number & Payment Ref:**

1. Under "**🔢 RJ & Payment Ref**":
   - Click **🚀 Launch**
2. ✅ The app will:
   - Extract RJ numbers and payment references
   - Add "RJ-Number" and "Payment Ref" columns
   - Show sample results
   - **Auto-refresh** the page

3. ✅ Status shows: `✅ RJ-Number & Payment Ref added`
4. ✅ Column count increases: `📊 Ledger: X rows × (Y+2) columns`

---

### **Step 3: Verify Columns Persist** ✅

**DO THIS TEST:**

1. After adding columns, scroll down to "Step 3: Configure Column Mapping"
2. Click the **"ℹ️ View Available Columns"** expander (it's expanded by default)
3. ✅ **You should see:**
   ```
   Ledger Columns (7 total):
   Date, Description, RJ-Number, Payment Ref, Debit, Credit, Balance
   ✨ Added columns: RJ-Number, Payment Ref

   Statement Columns (5 total):
   Date, Description, Reference, Amount, Balance
   ✨ Added columns: Reference
   ```

4. Click any dropdown (Date Column, Reference Column, etc.)
5. ✅ **The added columns should STILL BE THERE**
6. The page might refresh, but check the "View Available Columns" again
7. ✅ **Columns should persist!**

---

### **Step 4: Configure Column Mapping** ⚙️

1. Under "Step 3: Configure Column Mapping":
2. **Ledger Columns:**
   - Date Column: Select your date column
   - Reference Column: Select "RJ-Number" or "Payment Ref"
   - Debit Column: Select debit column
   - Credit Column: Select credit column

3. **Statement Columns:**
   - Date Column: Select date column
   - Reference Column: Select "Reference" (the one you just added!)
   - Amount Column: Select amount column

4. ✅ Selections will persist as you configure

---

### **Step 5: Set Matching Settings** 🎯

1. Under "Step 4: Matching Settings":
2. Check/uncheck:
   - ✅ Match by Dates
   - ✅ Match by References
   - ✅ Match by Amounts
3. Set fuzzy matching threshold (default 85%)
4. Choose amount mode (Both Debits/Credits, Debits Only, or Credits Only)

---

### **Step 6: Run Reconciliation** ⚡

1. Under "Step 5: Execute Reconciliation"
2. Click **"🚀 Start Reconciliation"**
3. Wait for processing...
4. ✅ Results will appear with:
   - Summary metrics
   - Matched pairs count
   - Unmatched counts

---

### **Step 7: View Results** 📊

Results appear in three tabs:

#### **Tab 1: ✅ Matched Pairs**
- Shows all successfully matched transactions
- Includes Match_Score
- Shows Ledger_ and Statement_ columns side by side
- **ALL COLUMNS ARE INCLUDED** (including RJ-Number, Payment Ref, Reference)

#### **Tab 2: 📋 Unmatched Ledger**
- Ledger transactions with no match
- All columns preserved

#### **Tab 3: 🏦 Unmatched Statement**
- Statement transactions with no match
- All columns preserved

---

### **Step 8: Save Results** 💾

1. At the bottom of results, click **"💾 Save Results to Database"**
2. Enter a name (or use auto-generated one):
   ```
   Example: "March_2024_FNB_Reconciliation"
   ```
3. Click **"✅ Confirm Save"**
4. ✅ You'll see: `✅ Results saved successfully! (ID: 1)`

---

### **Step 9: View Saved Results** 🕒

1. Go to **"📁 Data Management"** in sidebar
2. Click **"🕒 Saved Results"** tab
3. See table with all your saved reconciliations:
   ```
   ID | Name | Workflow | Date | Matched | Unmatched
   1  | March_2024... | FNB | 2024-03-15 | 250 | 10
   ```

4. To view details:
   - Go to **"📊 View Result"** tab
   - Enter the Result ID
   - Click **"🔍 Load Result"**
   - View all data in tabs

---

### **Step 10: Export Results** 📥

**Option 1: CSV Download**
- In each tab (Matched/Unmatched), click **"📥 Download"**
- Gets single CSV file for that category

**Option 2: Complete Excel Report**
- Click **"📊 Export All to Excel"**
- Click **"📥 Download Complete Excel Report"**
- Gets Excel workbook with all sheets:
  - Summary
  - Matched Pairs
  - Unmatched Ledger
  - Unmatched Statement

✅ **ALL COLUMNS INCLUDED IN EXPORT** (RJ-Number, Payment Ref, Reference)

---

## 🚨 Troubleshooting

### **Problem: Columns disappear after clicking dropdown**

**Solution:**
1. Check "ℹ️ View Available Columns" expander
2. If columns are NOT there, they were lost
3. **Root Cause:** You uploaded a new file after adding columns
4. **Fix:**
   - **DO NOT** re-upload the same file after adding columns
   - Once file is uploaded and columns added, **don't touch the file uploader**
   - If you need to restart, refresh the whole page and start over

---

### **Problem: Getting error when saving results**

**Solution:**
1. Make sure the `streamlit-app/data/` directory exists
2. Check write permissions
3. Try a shorter result name (no special characters)

---

### **Problem: Results don't show all columns**

**Verify:**
1. Before running reconciliation, check "View Available Columns"
2. All added columns should be listed there
3. If they're there before reconciliation, they'll be in results
4. If they're not there, redo Step 2 (add columns)

---

## 💡 Best Practices

### **✅ DO:**
1. Upload files ONCE at the beginning
2. Add all columns you need (Reference, RJ-Number, Payment Ref)
3. Verify columns persist using the "View Available Columns" expander
4. Configure mappings
5. Run reconciliation
6. Save results with descriptive names
7. Export to Excel for reporting

### **❌ DON'T:**
1. Don't re-upload the same file after adding columns
2. Don't refresh the page while working (you'll lose everything)
3. Don't click the file uploader after columns are added
4. Don't use special characters in result names

---

## 📞 Still Having Issues?

If columns are still not persisting:

1. **Check browser console** for errors (F12 → Console tab)
2. **Clear browser cache** and try again
3. **Use incognito/private mode** to test
4. **Try a different browser** (Chrome recommended)
5. **Ensure you're on latest deployment** - wait 1-2 minutes after code push

---

## 🎯 Quick Reference Card

```
UPLOAD → ADD COLUMNS → VERIFY → CONFIGURE → RUN → SAVE → EXPORT
  📁        🛠️          ✅         ⚙️        ⚡      💾      📥

Column Tools:
- Add Reference (Statement): Extracts names from Description
- RJ & Payment Ref (Ledger): Extracts RJ numbers and refs
- Nedbank Processing (Statement): Cleans Nedbank data

Remember:
✅ Upload files ONCE
✅ Add all columns before configuring
✅ Verify columns in "View Available Columns"
✅ Don't re-upload after adding columns
✅ Save results with descriptive names
```

---

## 🎉 You're All Set!

Follow these steps exactly and your columns will persist throughout the entire workflow!

**Need Help?** Contact support with:
- Screenshot of "View Available Columns"
- Description of which step failed
- Browser console errors (if any)
