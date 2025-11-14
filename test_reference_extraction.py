"""
Test Reference Extraction Logic
"""
import re

def extract_reference_name(description):
    """Extract reference names from banking transaction descriptions"""
    desc = str(description).strip()

    # Pattern-based extraction for common transaction types
    patterns = [
        # Phone number only (10 digits) - High priority
        (r'^\d{10}$', lambda m: m.group(0)),
        
        # FNB APP PAYMENT FROM [NAME]
        (r'FNB APP PAYMENT FROM\s+(.+)', lambda m: m.group(1).strip()),

        # ADT CASH DEPO variations - Extract phone/ref at the END
        (r'ADT CASH DEPO[A-Z\d]+\s+(\d{10})\s*$', lambda m: m.group(1)),  # DEPO + alphanumeric code + 10-digit phone
        (r'ADT CASH DEPO[A-Z\d]+\s+([A-Z]+)\s*$', lambda m: m.group(1)),  # DEPO + alphanumeric code + name  
        (r'ADT CASH DEPO00882112\s+(.+)', lambda m: m.group(1).strip()),
        (r'ADT CASH DEPOSIT\s+(.+)', lambda m: m.group(1).strip()),
        (r'ADT CASH DEPO\s+(.+)', lambda m: m.group(1).strip()),  # Generic fallback

        # CAPITEC [NAME]
        (r'CAPITEC\s+(.+)', lambda m: m.group(1).strip()),

        # ABSA BANK [NAME]
        (r'ABSA BANK\s+(.+)', lambda m: m.group(1).strip()),

        # NEDBANK [NAME]
        (r'NEDBANK\s+(.+)', lambda m: m.group(1).strip()),

        # Standard Bank [NAME]
        (r'STANDARD BANK\s+(.+)', lambda m: m.group(1).strip()),

        # Direct names (capitalized words)
        (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[a-z]+)$', lambda m: m.group(1).strip()),
    ]

    # Try each pattern
    for pattern, extractor in patterns:
        match = re.search(pattern, desc, re.IGNORECASE)
        if match:
            try:
                result = extractor(match)
                if result:
                    # Clean up the reference name
                    result = result.strip()
                    # Only remove trailing long numbers if there's a name before them
                    # This preserves phone-only references like "0849667217"
                    if re.match(r'^[A-Za-z\s]+\s+\d{10,}$', result):
                        result = re.sub(r'\s*\d{10,}$', '', result)
                    return result
            except Exception as e:
                print(f"  ⚠️ Pattern failed: {pattern} - {e}")
                continue

    # Fallback: extract capitalized words that look like names
    words = desc.split()
    name_words = []
    for word in words:
        # Look for capitalized words that could be names
        if re.match(r'^[A-Z][a-z]+$', word) or re.match(r'^[A-Z]+$', word):
            name_words.append(word)

    if name_words:
        return ' '.join(name_words[-2:]) if len(name_words) >= 2 else name_words[-1]

    return "UNKNOWN"


# Test cases from your data
test_cases = [
    "ADT CASH DEPO00486104 EMSON",
    "ADT CASH DEPO01156102 SIZAPHIWA",
    "ADT CASH DEPO02487003 GOODMAN",
    "ADT CASH DEPOSSDNCR  BARBARA",
    "FNB APP PAYMENT FROM  NOCY",
    "ADT CASH DEPO01156103 SKHU",
    "ADT CASH DEPO01156103 BELINDA",
    "ADT CASH DEPO02113002 0849667217",  # THE PROBLEM ROW
    "FNB APP PAYMENT FROM  NCENGIWE MOYO",
    "ADT CASH DEPO01156101 SKHU",
    "COLLIN GUMEDE",
    "FNB APP PAYMENT FROM  ZENZO MLALAZI",
    "ADT CASH DEPO01156102 VALE",
    "ADT CASH DEPO00637002 NDEX",
]

print("=" * 80)
print("REFERENCE EXTRACTION TEST")
print("=" * 80)

for i, desc in enumerate(test_cases, 1):
    result = extract_reference_name(desc)
    print(f"\n{i:2d}. Description: {desc}")
    print(f"    → Reference: {result}")
    
    # Highlight the problem case
    if "0849667217" in desc:
        if result == "0849667217":
            print("    ✅ CORRECT - Phone number extracted!")
        else:
            print(f"    ❌ WRONG - Expected '0849667217', got '{result}'")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
