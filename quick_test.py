import re

def extract_reference(description):
    """Test extraction patterns"""
    desc = str(description).strip()
    
    print(f"  Testing: '{desc}'")
    print(f"  Length: {len(desc)}")
    print(f"  Repr: {repr(desc)}")
    
    # Pattern 1: PayShap Ext Credit
    payshap_pattern = r'PayShap\s+Ext\s+Credit\s+([A-Z]+\s+[A-Z]+)'
    payshap_match = re.search(payshap_pattern, desc, re.IGNORECASE)
    print(f"  PayShap pattern match: {payshap_match is not None}")
    if payshap_match:
        result = payshap_match.group(1).strip().upper()
        print(f"  PayShap extracted: '{result}'")
        return result
    
    # Pattern 2: ACB CREDIT CAPITEC
    acb_pattern = r'ACB\s+CREDIT\s+CAPITE[C]?\s+([A-Z]+\s+[A-Z]+)'
    acb_match = re.search(acb_pattern, desc, re.IGNORECASE)
    print(f"  ACB pattern match: {acb_match is not None}")
    if acb_match:
        result = acb_match.group(1).strip().upper()
        print(f"  ACB extracted: '{result}'")
        return result
    
    print(f"  No match - returning UNKNOWN")
    return 'UNKNOWN'

# Test cases
tests = [
    ('ACB CREDIT CAPITEC K KWIYO', 'K KWIYO'),
    ('PayShap Ext Credit P NCUBE', 'P NCUBE'),
    ('PayShap Ext Credit S MOYO', 'S MOYO'),
]

print('TESTING ABSA EXTRACTION PATTERNS')
print('=' * 70)
print()

for test_input, expected in tests:
    print(f"Test: {test_input}")
    print(f"Expected: {expected}")
    result = extract_reference(test_input)
    status = "PASS ✓" if result == expected else f"FAIL ✗ (got '{result}')"
    print(f"Status: {status}")
    print('-' * 70)
    print()
