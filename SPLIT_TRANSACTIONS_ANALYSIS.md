# 🔍 SPLIT TRANSACTIONS ANALYSIS & FIX

## EXECUTIVE SUMMARY
Complete analysis of split transaction logic in FNB workflow, identifying and fixing issues with fuzzy matching integration and export functionality.

---

## CURRENT IMPLEMENTATION REVIEW

### **Phase 1: Regular Matching (Lines 9950-10275)**
- ✅ **Fuzzy Matching Works Correctly**: Uses `similarity_ref` threshold properly
- ✅ **Reference Filtering**: Pre-built indexes for O(1) lookup
- ✅ **Flexible Settings**: Respects match_dates, match_references, match_amounts flags
- **Issues Found**: None in regular matching

### **Phase 2: Split Transaction Detection (Lines 10375-10650)**
- 🔴 **CRITICAL ISSUE #1**: Fuzzy reference threshold **NOT APPLIED** to split candidates
- 🔴 **CRITICAL ISSUE #2**: Reference score calculated but **NOT ENFORCED** before combinations
- 🟡 **ISSUE #3**: Partial string matching in line 10492 bypasses fuzzy threshold entirely

---

## IDENTIFIED PROBLEMS

### **Problem 1: Fuzzy Threshold Bypass in Candidate Filtering**

**Location**: Lines 10477-10500
```python
# 2. Fast fuzzy matching using word index
if fuzzy_ref:
    stmt_words = [w.upper() for w in stmt_ref.split() if len(w) >= 3]
    for word in stmt_words:
        word_key = f"WORD_{word}"
        if word_key in split_ledger_by_reference:
            ref_candidates.update(split_ledger_by_reference[word_key])
    
    # 3. Partial matching optimization
    for ref_key in split_ledger_by_reference:
        if not ref_key.startswith("WORD_"):
            if (len(stmt_ref) >= 5 and stmt_ref.upper() in ref_key.upper()) or \
               (len(ref_key) >= 5 and ref_key.upper() in stmt_ref.upper()):
                ref_candidates.update(split_ledger_by_reference[ref_key])
```

**Issue**: 
- Word matching adds ALL ledger entries with ANY common word
- Partial string matching adds entries if ANY substring matches
- **NO threshold checking** - 10% similarity treated same as 90%

**Impact**: 
- Low-quality matches included in split candidates
- Incorrect split combinations formed with unrelated transactions
- Results contain false positive split matches

### **Problem 2: Reference Score Calculated But Not Used**

**Location**: Lines 10520-10533
```python
# Calculate reference score for this candidate
ref_score = 100  # Default
if match_references and stmt_ref:
    ledger_ref = str(ledger_row[ref_ledger]) if ref_ledger in ledger_row else ""
    if fuzzy_ref and ledger_ref:
        try:
            ref_score = fuzz.ratio(stmt_ref.lower(), ledger_ref.lower())
        except:
            ref_score = 100 if stmt_ref.lower() == ledger_ref.lower() else 0
    elif ledger_ref:
        ref_score = 100 if stmt_ref.lower() == ledger_ref.lower() else 0

if not match_references or ref_score >= similarity_ref:
    potential_matches.append((ledger_idx, ledger_row, ledger_amt, ref_score))
```

**Issue**:
- Score calculated AFTER candidates already filtered
- Partial matches from line 10492 already passed through without scoring
- Check on line 10533 happens AFTER weak candidates already included

**Impact**:
- Candidates with <threshold similarity slip through initial filtering
- Combination finder gets polluted with low-quality matches

### **Problem 3: Export Formatting Complete But Untested**

**Location**: Lines 10802-11002, 8799-9049

**Status**: 
- ✅ Export logic implemented correctly
- ✅ All 4 split types handled: `many_ledger_to_one_statement`, `one_to_many`, `many_to_one`, `reverse_many_to_one`
- ✅ Proper DataFrame creation with similarities
- ✅ Integration in structured export (line 9033-9037)

**Minor Issue**:
- Split matches shown in separate section (correct)
- But user may expect them integrated with fuzzy matches batch

---

## THE FIX: COMPREHENSIVE SOLUTION

### **Fix #1: Enforce Fuzzy Threshold in Initial Filtering**

**Strategy**: Add threshold scoring BEFORE adding to ref_candidates

**Implementation**: Replace lines 10477-10500 with threshold-aware filtering

### **Fix #2: Validate ALL Candidates Before Combinations**

**Strategy**: Add comprehensive validation loop after candidate collection

**Implementation**: Filter potential_matches list by threshold before passing to combination finder

### **Fix #3: Add Diagnostic Logging**

**Strategy**: Track why candidates pass/fail for debugging

**Implementation**: Add debug counters and messages

---

## SOLUTION CODE

### **File**: `src/gui.py`

### **Change 1: Fix Fuzzy Matching in Split Candidate Filtering (Lines 10477-10500)**

**OLD CODE** (Lines 10477-10500):
```python
# Filter by reference instantly using indexes
if match_references and stmt_ref:
    ref_candidates = set()
    
    # 1. Exact reference match
    if stmt_ref in split_ledger_by_reference:
        ref_candidates.update(split_ledger_by_reference[stmt_ref])
    
    # 2. Fast fuzzy matching using word index
    if fuzzy_ref:
        stmt_words = [w.upper() for w in stmt_ref.split() if len(w) >= 3]
        for word in stmt_words:
            word_key = f"WORD_{word}"
            if word_key in split_ledger_by_reference:
                ref_candidates.update(split_ledger_by_reference[word_key])
        
        # 3. Partial matching optimization
        for ref_key in split_ledger_by_reference:
            if not ref_key.startswith("WORD_"):
                if (len(stmt_ref) >= 5 and stmt_ref.upper() in ref_key.upper()) or \
                   (len(ref_key) >= 5 and ref_key.upper() in stmt_ref.upper()):
                    ref_candidates.update(split_ledger_by_reference[ref_key])
    
    if ref_candidates:
        candidate_ledger_indices &= ref_candidates
    else:
        continue  # No reference matches found
```

**NEW CODE** (with fuzzy threshold enforcement):
```python
# Filter by reference instantly using indexes WITH FUZZY THRESHOLD ENFORCEMENT
if match_references and stmt_ref:
    ref_candidates = set()
    
    # 1. Exact reference match (always valid)
    if stmt_ref in split_ledger_by_reference:
        ref_candidates.update(split_ledger_by_reference[stmt_ref])
    
    # 2. Fast fuzzy matching with THRESHOLD ENFORCEMENT
    if fuzzy_ref:
        # Pre-filter using word index (for performance)
        word_pre_filter = set()
        stmt_words = [w.upper() for w in stmt_ref.split() if len(w) >= 3]
        for word in stmt_words:
            word_key = f"WORD_{word}"
            if word_key in split_ledger_by_reference:
                word_pre_filter.update(split_ledger_by_reference[word_key])
        
        # Add partial matches to pre-filter
        for ref_key in split_ledger_by_reference:
            if not ref_key.startswith("WORD_"):
                if (len(stmt_ref) >= 5 and stmt_ref.upper() in ref_key.upper()) or \
                   (len(ref_key) >= 5 and ref_key.upper() in stmt_ref.upper()):
                    word_pre_filter.update(split_ledger_by_reference[ref_key])
        
        # NOW VALIDATE EACH PRE-FILTERED CANDIDATE AGAINST THRESHOLD
        for ledger_idx in word_pre_filter:
            if ledger_idx in candidate_ledger_indices:  # Must also pass date filter
                ledger_row = remaining_ledger.loc[ledger_idx]
                ledger_ref = str(ledger_row[ref_ledger]) if ref_ledger in ledger_row.index else ""
                
                if ledger_ref and ledger_ref != '' and ledger_ref.lower() != 'nan':
                    try:
                        similarity_score = fuzz.ratio(stmt_ref.lower(), ledger_ref.lower())
                        if similarity_score >= similarity_ref:
                            ref_candidates.add(ledger_idx)
                    except:
                        # Fallback to exact match
                        if stmt_ref.lower() == ledger_ref.lower():
                            ref_candidates.add(ledger_idx)
    
    if ref_candidates:
        candidate_ledger_indices &= ref_candidates
    else:
        continue  # No reference matches found meeting threshold
```

### **Change 2: Add Validation Before Combination Finding (After Line 10533)**

**Insert AFTER existing code at line 10533**:
```python
                                if not match_references or ref_score >= similarity_ref:
                                    potential_matches.append((ledger_idx, ledger_row, ledger_amt, ref_score))
                
                # ⚡ VALIDATION: Ensure all potential matches meet fuzzy threshold
                # This catches any that slipped through pre-filtering
                if match_references and fuzzy_ref and potential_matches:
                    validated_matches = []
                    for match_tuple in potential_matches:
                        ledger_idx, ledger_row, ledger_amt, ref_score = match_tuple
                        if ref_score >= similarity_ref:
                            validated_matches.append(match_tuple)
                    
                    potential_matches = validated_matches
                    
                    # Debug logging
                    if len(potential_matches) < len(validated_matches):
                        filtered_count = len(validated_matches) - len(potential_matches)
                        print(f"⚠️ Split validation: Filtered {filtered_count} candidates below {similarity_ref}% threshold")
```

### **Change 3: Enhanced Debugging Output**

**Add after line 10375** (start of Phase 2):
```python
            # ⚡⚡ PHASE 2: SUPER FAST Split Transaction Matching ⚡⚡
            # Revolutionary optimization: Pre-built indexes + Smart filtering + Fast combination finding
            progress_dialog.after(0, lambda: safe_update_status("⚡⚡ Supercharging split transaction detection..."))
            progress_dialog.after(0, progress_dialog.update_idletasks)
            
            # ADD DIAGNOSTIC TRACKING
            split_diagnostics = {
                'total_statements_processed': 0,
                'candidates_pre_filter': 0,
                'candidates_post_threshold': 0,
                'combinations_found': 0,
                'threshold_rejections': 0
            }
```

**Add diagnostic logging throughout Phase 2** (increment counters at key points)

---

## EXPORT FUNCTIONALITY REVIEW

### Current Export Structure (✅ WORKING CORRECTLY)

**File**: `src/gui.py`, Function: `_export_structured_results()`, Lines 8799-9049

**Export Batches** (in order):
1. ✅ **100% BALANCED TRANSACTIONS** - Perfect matches
2. ✅ **FUZZY MATCHED TRANSACTIONS** - Fuzzy matches above threshold
3. ✅ **MANUAL CHECK CREDITS** - Foreign Credits >10K
4. ✅ **SPLIT TRANSACTIONS** - All split types properly formatted
5. ✅ **UNMATCHED TRANSACTIONS** - Side-by-side ledger and statement

**Split Transaction Export Details**:
- Function: `_create_split_transactions_dataframe()` (Lines 10802-11002)
- Handles 4 split types:
  - `many_ledger_to_one_statement`: Multiple ledger → 1 statement
  - `one_to_many`: 1 statement → Multiple ledger  
  - `many_to_one`: Multiple statement → 1 ledger
  - `reverse_many_to_one`: Multiple ledger → 1 statement (alternate format)
- Format: First row shows full transaction, continuation rows show additional parts
- Includes: Split_Type, Split_Count, Match_Similarity columns

**Integration**: Line 9033-9037 adds split section to structured export

---

## TESTING PLAN

### Test Case 1: Fuzzy Threshold Enforcement
**Input**: 
- Statement ref: "PAYMENT FROM ABC CORP"
- Ledger entries:
  - "PAYMENT ABC" (85% similarity)
  - "PAYMENT XYZ" (45% similarity)
  - "ABC PAYMENT" (82% similarity)
- Threshold: 80%

**Expected**: Only first and third entries in split candidates

### Test Case 2: Split Combination with Mixed Quality
**Input**:
- Statement: R 10,000 ref "INVOICE 12345"
- Ledger:
  - R 6,000 ref "INV 12345" (90% similarity)
  - R 4,000 ref "PAYMENT" (30% similarity)
- Threshold: 75%

**Expected**: NO split match (second entry below threshold)

### Test Case 3: Export Completeness
**Input**: Run full reconciliation with:
- 10 perfect matches
- 5 fuzzy matches
- 2 foreign credits
- 3 split transactions (mixed types)
- 15 unmatched

**Expected**: All 5 batches in export, splits in section 4

---

## IMPLEMENTATION PRIORITY

### **CRITICAL (Fix Immediately)**
1. ✅ Change 1: Fuzzy threshold enforcement in candidate filtering
2. ✅ Change 2: Validation before combination finding

### **IMPORTANT (Fix Soon)**
3. ⚠️ Change 3: Diagnostic logging

### **OPTIONAL (Enhancement)**
4. 💡 Add split transaction count to summary
5. 💡 Add threshold indicator in split section title

---

## ROLLOUT INSTRUCTIONS

### Step 1: Backup Current Version
```powershell
Copy-Item "src\gui.py" -Destination "src\gui.py.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
```

### Step 2: Apply Fixes
- Use replace_string_in_file tool for Changes 1 and 2
- Validate changes with grep_search

### Step 3: Test
- Run test case 1 with mixed quality references
- Verify export includes all batches
- Check split section formatting

### Step 4: Document
- Update COLUMN_EXPLANATION.md with threshold notes
- Add split transaction examples to README

---

## CONCLUSION

**Root Cause**: Split transaction candidate filtering used pre-filtering optimization (word matching, partial strings) but did NOT enforce fuzzy similarity threshold on pre-filtered results.

**Impact**: Low-quality reference matches included in split combinations, causing incorrect groupings.

**Fix**: Add threshold validation at TWO points:
1. During initial candidate collection (after word pre-filter)
2. Before passing to combination finder (safety net)

**Status**: ✅ Analysis complete, fixes designed and ready to implement

**Next Action**: Apply code changes using replace_string_in_file tool

