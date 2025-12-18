# Reconciliation Performance Thresholds Update

## Changes Made

### Previous Thresholds (Too Restrictive)
- **Skip split detection if:** > 1000 statement rows OR > 2000 ledger rows
- **Your dataset:** 54 ledger, 2044 statement rows
- **Result:** Split detection was skipped ❌

### New Thresholds (More Flexible)
- **Skip split detection if:** > 5000 statement rows OR > 5000 ledger rows
- **Your dataset:** 54 ledger, 2044 statement rows
- **Result:** Split detection will run ✅

### Performance Expectations

| Dataset Size | Expected Time | Status |
|--------------|---------------|--------|
| < 500 statement | < 5 seconds | Fast |
| 500-1000 statement | 5-15 seconds | Moderate |
| 1000-2500 statement | 15-60 seconds | Large (Your case) |
| 2500-5000 statement | 60-180 seconds | Very Large |
| > 5000 statement | Skipped | Too Large |

## What Will Happen Now

With 2044 statement rows and 54 ledger rows:

1. **Phase 1:** Regular matching - Fast (< 5 seconds)
2. **Phase 1.5:** Foreign credits - Fast (< 1 second)
3. **Phase 2:** Many-to-one splits - **30-60 seconds expected**
4. **Phase 2B:** One-to-many splits - Fast (< 10 seconds)

**Total Expected Time:** ~45-75 seconds for full reconciliation

## Progress Indicators

You'll see these messages during reconciliation:

```
📊 Large dataset (54 ledger, 2044 statement) - Split detection may take 30-60 seconds...
🔄 Processing splits: 100/2044 statements...
🔄 Processing splits: 500/2044 statements...
✅ Many-to-one splits: 15 found
```

## Performance Tips

### If Reconciliation is Too Slow:

1. **Pre-filter your data:**
   - Filter by date range (e.g., only current month)
   - Filter by amount range (e.g., > $100)
   - Remove already matched transactions

2. **Improve matching criteria:**
   - Enable reference matching (reduces unmatched items)
   - Enable date matching (reduces candidates)
   - Use fuzzy matching (catches more matches in Phase 1)

3. **Use batch processing:**
   - Split large files into smaller chunks
   - Process month by month
   - Process by transaction type

### Why Split Detection is Important:

Split detection finds transactions where:
- **Many-to-one:** Multiple statement entries match one ledger entry
  - Example: Customer payment split across 3 installments
- **One-to-many:** One statement entry matches multiple ledger entries
  - Example: Bulk payment covering multiple invoices

**Skipping split detection means missing these matches!**

## Changes Applied

**File:** `components/fnb_workflow_gui_engine.py`

**Lines Changed:**
- Line 817-822: Increased skip threshold from 1000/2000 to 5000/5000
- Line 824-828: Added info message for large datasets (1000-5000 range)

## How to Apply Changes

The changes have been saved. To apply them:

1. **Restart the Streamlit app:**
   - Stop the current app (Ctrl+C in terminal, or close browser)
   - Run: `streamlit run app.py`

2. **Or reload the page:**
   - In some cases, Streamlit will auto-detect changes
   - Click "Rerun" button in the app if prompted

## Testing the Changes

After restarting:

1. Load your 2044-row statement file
2. Load your 54-row ledger file
3. Configure column mappings
4. Click "Reconcile"
5. Watch for the progress message:
   ```
   📊 Large dataset (54 ledger, 2044 statement) - Split detection may take 30-60 seconds...
   ```
6. Wait for split detection to complete (expect 30-60 seconds)
7. Review results - you should now see split matches that were previously missed

## Verification

To verify the changes are working:

```python
# Check if split detection runs
# You should see in the logs:
"Phase 2: Many-to-One Split Transactions..."  # ✅ Should appear
# NOT:
"Skipping split detection for performance"    # ❌ Should NOT appear
```

---

**Updated:** December 18, 2024
**Threshold Change:** 1000/2000 → 5000/5000
**Impact:** Your 2044-row dataset will now process split detection
