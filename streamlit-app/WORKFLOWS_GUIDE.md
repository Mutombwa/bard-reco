# 🔄 Workflows Guide

## Overview

Your BARD-RECO Streamlit app now includes **3 specialized workflows** that replicate the functionality from your GUI application:

1. **🏦 FNB Workflow** - Bank reconciliation with FNB-specific logic
2. **🏢 Bidvest Workflow** - Bidvest settlement reconciliation
3. **💼 Corporate Settlements** - Ultra-fast 5-tier settlement matching

---

## How to Access Workflows

### Step 1: Login
- Go to: https://bard-reco.streamlit.app
- Login: `admin` / `admin123` (change this!)

### Step 2: Navigate to Workflows
- Click **"🔄 Workflows"** in the sidebar

### Step 3: Select Workflow
- Choose from 3 workflow cards:
  - FNB Workflow
  - Bidvest Workflow
  - Corporate Settlements

---

## 🏦 FNB Workflow

### Purpose
Bank statement reconciliation with FNB-specific matching algorithms.

### Features
- ✅ Date matching (with tolerance)
- ✅ Reference matching (fuzzy)
- ✅ Amount matching (debits/credits)
- ✅ Advanced filtering

### How to Use

1. **Upload Files**:
   - Upload Ledger/Cashbook (Excel/CSV)
   - Upload Bank Statement (Excel/CSV)

2. **Map Columns**:
   - Ledger: Date, Reference, Debit, Credit
   - Statement: Date, Reference, Amount

3. **Configure Matching**:
   - Date Tolerance: ± days (default: 3)
   - Amount Tolerance: % variance (default: 0.1%)
   - Fuzzy Threshold: similarity score (default: 85%)

4. **Run Reconciliation**:
   - Click "🚀 Start FNB Reconciliation"
   - Wait for processing
   - View results in tabs

5. **Export Results**:
   - Perfect Matches
   - Fuzzy Matches
   - Unmatched Ledger
   - Unmatched Statement
   - Export to Excel

### Example Use Case
**Scenario**: Monthly bank reconciliation for FNB corporate account

- Upload: General Ledger export + FNB statement
- Match: Transactions by date, reference, and amount
- Result: Categorized matches with unmatched items highlighted

---

## 🏢 Bidvest Workflow

### Purpose
Settlement reconciliation with batch processing for Bidvest transactions.

### Features
- ✅ Batch matching
- ✅ Foreign currency support
- ✅ Settlement tracking
- ✅ Advanced reporting

### How to Use

1. **Upload File**:
   - Upload Bidvest settlement file (Excel/CSV)

2. **Map Columns**:
   - Foreign Debits
   - Foreign Credits
   - Reference

3. **Run Reconciliation**:
   - Click "🚀 Run Bidvest Reconciliation"
   - Automatic batch matching

4. **View Results**:
   - Matched settlements (balanced)
   - Unmatched settlements (requires review)

### Example Use Case
**Scenario**: Bidvest settlement file with foreign currency transactions

- Upload: Bidvest_Settlement_Jan2025.xlsx
- Match: Find balanced debits/credits
- Result: Separated matched and unmatched settlements

---

## 💼 Corporate Settlements Workflow

### Purpose
Ultra-fast settlement matching with 5-tier batch processing for large corporate files.

### Features
- ✅ **5-Tier Matching System**:
  - **Tier 1**: Perfect balance (debit + credit = 0)
  - **Tier 2**: Within tolerance
  - **Tier 3**: Within percentage threshold
  - **Tier 4**: Grouped matches
  - **Tier 5**: Unmatched
- ✅ Ultra-fast processing
- ✅ Handles large files (100K+ rows)
- ✅ Professional batch separation

### How to Use

1. **Upload File**:
   - Upload corporate settlement file (Excel/CSV)

2. **Map Columns**:
   - Foreign Debits
   - Foreign Credits
   - Reference

3. **Configure Parameters**:
   - Tolerance: absolute value (default: 0.5)
   - Percentage Threshold: % variance (default: 7%)

4. **Run 5-Tier Matching**:
   - Click "🚀 Run Corporate Reconciliation"
   - Watch 5-tier algorithm process

5. **Review Tiers**:
   - **Tier 1**: Perfect matches - ready to process
   - **Tier 2**: Close matches - minor review
   - **Tier 3**: Threshold matches - needs review
   - **Tier 4**: Grouped matches - manual verification
   - **Tier 5**: Unmatched - investigate

### Example Use Case
**Scenario**: Monthly corporate settlement file with 50,000 transactions

- Upload: Corporate_Settlements_Jan2025.xlsx
- Configure: Tolerance=0.5, Threshold=7%
- Process: 5-tier algorithm categorizes all transactions
- Result:
  - Tier 1: 35,000 perfect matches
  - Tier 2: 8,000 tolerance matches
  - Tier 3: 4,000 threshold matches
  - Tier 4: 2,000 grouped
  - Tier 5: 1,000 unmatched

---

## 📊 Workflow Comparison

| Feature | FNB | Bidvest | Corporate |
|---------|-----|---------|-----------|
| **Best For** | Bank Statements | Settlements | Bulk Settlements |
| **Speed** | Fast | Fast | Ultra-Fast |
| **File Types** | 2 files (ledger + statement) | 1 file | 1 file |
| **Matching** | 3-way (date, ref, amount) | Balance matching | 5-tier algorithm |
| **Complexity** | Medium | Medium | Low |
| **Batch Support** | No | Yes | Yes (5-tier) |
| **Currency** | ZAR | Multi-currency | Multi-currency |
| **Max Records** | 50K | 100K | 200K+ |

---

## 🆚 General Reconciliation vs Workflows

### Use **General Reconciliation** (📊 Reconciliation page) when:
- Simple two-file reconciliation
- Custom matching rules
- Ad-hoc reconciliation
- Learning the system

### Use **Workflows** (🔄 Workflows page) when:
- Specific bank (FNB, Bidvest)
- Regular monthly reconciliation
- Large settlement files
- Need specialized matching logic

---

## 💡 Tips & Best Practices

### FNB Workflow
- ✅ Use consistent date formats
- ✅ Clean reference fields before upload
- ✅ Start with higher fuzzy threshold (90%), lower if needed
- ✅ Review fuzzy matches manually

### Bidvest Workflow
- ✅ Ensure foreign currency columns are numeric
- ✅ Check for hidden characters in amounts
- ✅ Review unmatched for data entry errors

### Corporate Settlements
- ✅ Use for files > 10,000 rows
- ✅ Start with Tier 1 (perfect matches)
- ✅ Review Tier 5 (unmatched) for patterns
- ✅ Adjust tolerance based on Tier 2/3 results

---

## 🔧 Troubleshooting

### Issue: "No matches found"
**Cause**: Column mapping or data format issue

**Solution**:
1. Check column mappings are correct
2. Preview data to verify formats
3. Check for:
   - Hidden spaces in text
   - Date format inconsistencies
   - Amount formatting (commas, decimals)

### Issue: "Too many unmatched"
**Cause**: Thresholds too strict

**Solution**:
1. FNB: Increase date tolerance (try 5-7 days)
2. FNB: Lower fuzzy threshold (try 80%)
3. Corporate: Increase tolerance or threshold

### Issue: "Slow processing"
**Cause**: Large file or complex matching

**Solution**:
1. Split large files into smaller chunks
2. Use Corporate workflow for bulk files
3. Close other browser tabs
4. Refresh page and try again

---

## 📈 Performance

### Expected Processing Times

| Workflow | Rows | Time |
|----------|------|------|
| FNB | 1,000 | 5-10 sec |
| FNB | 10,000 | 30-60 sec |
| FNB | 50,000 | 2-5 min |
| Bidvest | 10,000 | 10-20 sec |
| Bidvest | 50,000 | 1-2 min |
| Corporate | 10,000 | 5-10 sec |
| Corporate | 100,000 | 30-90 sec |
| Corporate | 200,000 | 2-3 min |

---

## 🎯 What's Next?

### Coming Soon
- [ ] Email notifications when reconciliation completes
- [ ] Scheduled automatic reconciliations
- [ ] API integration with accounting systems
- [ ] Advanced AI matching suggestions
- [ ] Mobile app version

### Request Features
Have a feature request? Contact your administrator or open an issue on GitHub.

---

## 📞 Support

### Need Help?
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Check [README.md](README.md)
3. Contact support

### Report Issues
- Email: support@bard-reco.com
- GitHub Issues: https://github.com/Mutombwa/bard-reco/issues

---

**Happy Reconciling! 🎉**
