"""
Test Extended Reference Patterns (ZVC, ECO, INN, Reversal)
===========================================================
"""

import re

def extract_rj_and_ref(comment):
    """Test extraction with all patterns"""
    if not isinstance(comment, str):
        return '', ''

    # RJ-Number: look for RJ, TX, CSH, ZVC, ECO, INN followed by digits
    rj_match = re.search(r'(RJ|TX|CSH|ZVC|ECO|INN)[-]?(\d{6,})', comment, re.IGNORECASE)
    rj = rj_match.group(0).replace('-', '').replace('#', '').upper() if rj_match else ''

    payref = ''
    # Pattern 1: Explicit "Payment Ref #:" label
    payref_match = re.search(r'Payment\s+Ref\s*[#:]+\s*([\w\s\-\.,&]+)', comment, re.IGNORECASE)
    if payref_match:
        payref = payref_match.group(1).strip()
    # Pattern 2: Parentheses format (but not if it's just the reference itself like "#Ref CSH...")
    elif re.search(r'\(\s*([^)]+)\s*\)', comment):
        paren_match = re.search(r'\(\s*([^)]+)\s*\)', comment)
        paren_content = paren_match.group(1).strip()
        # Only use if it doesn't look like a reference (doesn't start with #Ref or Ref)
        if not re.match(r'#?Ref\s+(RJ|TX|CSH|ZVC|ECO|INN)', paren_content, re.IGNORECASE):
            payref = paren_content
    # Pattern 3: After RJ/TX/CSH/ZVC/ECO/INN number
    elif rj_match:
        after = comment[rj_match.end():]
        after = after.lstrip(' .:-#')
        dash_match = re.search(r'-\s*(.+)', after)
        if dash_match:
            text_after_dash = dash_match.group(1).strip()
            paren_in_dash = re.search(r'\(\s*([^)]+)\s*\)', text_after_dash)
            if paren_in_dash:
                payref = paren_in_dash.group(1).strip()
            else:
                payref = re.split(r'[,\n\r]', text_after_dash)[0].strip()
        else:
            payref = re.split(r'[,\n\r]', after)[0].strip()
        payref = payref.rstrip('. ')
    else:
        payref = comment.strip()

    return rj, payref


# Test cases with new patterns
test_cases = [
    # New patterns
    ("Ref ZVC128809565", "ZVC128809565", ""),
    ("Ref ECO904183634", "ECO904183634", ""),
    ("Reversal: (#Ref CSH767209773)", "CSH767209773", ""),
    ("Ref ECO944594422 - (Phuthani mabhena)", "ECO944594422", "Phuthani mabhena"),
    ("Ref INN757797206 - (Themba)", "INN757797206", "Themba"),

    # Existing CSH patterns (should still work)
    ("Ref CSH764074250 - (Phuthani mabhena)", "CSH764074250", "Phuthani mabhena"),
    ("Ref CSH293299862 - (Mlamuli)", "CSH293299862", "Mlamuli"),

    # Existing RJ/TX patterns (should still work)
    ("RJ123456 - K.kwiyo", "RJ123456", "K.kwiyo"),
    ("TX987654 - John Doe", "TX987654", "John Doe"),
]

print("=" * 70)
print("EXTENDED PATTERN EXTRACTION TEST")
print("=" * 70)
print("\nTesting new reference types: ZVC, ECO, INN, and Reversal format")
print()

passed = 0
failed = 0

for comment, expected_rj, expected_ref in test_cases:
    rj, ref = extract_rj_and_ref(comment)

    rj_match = rj == expected_rj
    ref_match = ref == expected_ref

    status = "[PASS]" if (rj_match and ref_match) else "[FAIL]"

    print(f"\n{status}")
    print(f"  Input:        {comment}")
    print(f"  Expected RJ:  {expected_rj if expected_rj else '(none)'}")
    print(f"  Got RJ:       {rj if rj else '(none)'} {'[OK]' if rj_match else '[X]'}")
    print(f"  Expected Ref: {expected_ref if expected_ref else '(none)'}")
    print(f"  Got Ref:      {ref if ref else '(none)'} {'[OK]' if ref_match else '[X]'}")

    if rj_match and ref_match:
        passed += 1
    else:
        failed += 1

print(f"\n{'=' * 70}")
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print(f"{'=' * 70}")

if failed == 0:
    print("\nALL TESTS PASSED! Extended patterns working correctly.")
else:
    print(f"\n{failed} test(s) failed. Review failures above.")
