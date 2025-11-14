import re

def extract_reference_name(description):
    """Extract reference names from banking transaction descriptions"""
    desc = str(description).strip()
    print(f"\n{'='*60}")
    print(f"Testing: {desc}")
    print(f"{'='*60}")

    # Pattern-based extraction for common transaction types
    patterns = [
        # Phone number only (10 digits) - High priority
        (r'^\d{10}$', lambda m: m.group(0), "Phone only"),
        
        # FNB APP PAYMENT FROM [NAME]
        (r'FNB APP PAYMENT FROM\s+(.+)', lambda m: m.group(1).strip(), "FNB Payment"),

        # ADT CASH DEPO variations - Extract phone/ref at the END
        (r'ADT CASH DEPO[A-Z\d]+\s+(\d{10})\s*$', lambda m: m.group(1), "ADT + Code + 10-digit phone"),
        (r'ADT CASH DEPO[A-Z\d]+\s+([A-Z]+)\s*$', lambda m: m.group(1), "ADT + Code + Name"),  
        (r'ADT CASH DEPO00882112\s+(.+)', lambda m: m.group(1).strip(), "ADT specific code"),
        (r'ADT CASH DEPOSIT\s+(.+)', lambda m: m.group(1).strip(), "ADT DEPOSIT"),
        (r'ADT CASH DEPO\s+(.+)', lambda m: m.group(1).strip(), "ADT generic"),

        # CAPITEC [NAME]
        (r'CAPITEC\s+(.+)', lambda m: m.group(1).strip(), "Capitec"),

        # ABSA BANK [NAME]
        (r'ABSA BANK\s+(.+)', lambda m: m.group(1).strip(), "ABSA"),

        # NEDBANK [NAME]
        (r'NEDBANK\s+(.+)', lambda m: m.group(1).strip(), "Nedbank"),

        # Standard Bank [NAME]
        (r'STANDARD BANK\s+(.+)', lambda m: m.group(1).strip(), "Standard Bank"),

        # Direct names (capitalized words)
        (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[a-z]+)$', lambda m: m.group(1).strip(), "Capitalized name"),
    ]

    # Try each pattern
    for i, (pattern, extractor, description_text) in enumerate(patterns, 1):
        match = re.search(pattern, desc, re.IGNORECASE)
        if match:
            print(f"  Pattern {i} ({description_text}): MATCH ✓")
            print(f"    Regex: {pattern}")
            print(f"    Captured groups: {match.groups()}")
            try:
                result = extractor(match)
                if result:
                    result = result.strip()
                    print(f"    Extracted: '{result}'")
                    
                    # Check cleanup
                    if re.match(r'^[A-Za-z\s]+\s+\d{10,}$', result):
                        cleaned = re.sub(r'\s*\d{10,}$', '', result)
                        print(f"    After cleanup: '{cleaned}'")
                        return cleaned
                    else:
                        print(f"    No cleanup needed (not 'Name + 10-digit')")
                    return result
            except Exception as e:
                print(f"    ERROR: {e}")
        else:
            print(f"  Pattern {i} ({description_text}): no match")

    # Fallback
    print("\n  No patterns matched - using fallback...")
    words = desc.split()
    name_words = []
    for word in words:
        if re.match(r'^[A-Z][a-z]+$', word) or re.match(r'^[A-Z]+$', word):
            name_words.append(word)

    if name_words:
        result = ' '.join(name_words[-2:]) if len(name_words) >= 2 else name_words[-1]
        print(f"  Fallback result: '{result}'")
        return result

    print(f"  Fallback result: 'UNKNOWN'")
    return "UNKNOWN"


# THE PROBLEM ROW
print("\n" + "="*60)
print("TESTING THE PROBLEM CASE")
print("="*60)

test_input = "ADT CASH DEPO02113002 0849667217"
result = extract_reference_name(test_input)

print("\n" + "="*60)
print(f"FINAL RESULT: '{result}'")
print("="*60)

if result == "0849667217":
    print("✅ SUCCESS! Phone number extracted correctly!")
else:
    print(f"❌ FAILED! Expected '0849667217', got '{result}'")
