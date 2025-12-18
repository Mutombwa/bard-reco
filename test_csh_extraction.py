"""
Test script to verify CSH pattern extraction works correctly
across FNB, ABSA, and Kazang workflows
"""

import re

def test_fnb_absa_extraction():
    """Test FNB/ABSA extraction logic"""

    def extract_rj_and_ref(comment):
        if not isinstance(comment, str):
            return '', ''

        # RJ-Number: look for RJ, TX, or CSH followed by digits
        # Patterns: RJ123456, TX123456, CSH764074250
        rj_match = re.search(r'(RJ|TX|CSH)[-]?(\d{6,})', comment, re.IGNORECASE)
        rj = rj_match.group(0).replace('-', '') if rj_match else ''

        payref = ''
        # Pattern 1: Explicit "Payment Ref #:" label
        payref_match = re.search(r'Payment\s+Ref\s*[#:]+\s*([\w\s\-\.,&]+)', comment, re.IGNORECASE)
        if payref_match:
            payref = payref_match.group(1).strip()
        # Pattern 2: Parentheses format - "Ref CSH764074250 - (Phuthani mabhena)"
        elif re.search(r'\(\s*([^)]+)\s*\)', comment):
            paren_match = re.search(r'\(\s*([^)]+)\s*\)', comment)
            payref = paren_match.group(1).strip()
        # Pattern 3: After RJ/TX/CSH number
        elif rj_match:
            after = comment[rj_match.end():]
            after = after.lstrip(' .:-#')
            # Check if there's a dash followed by text (handle "- Name" format)
            dash_match = re.search(r'-\s*(.+)', after)
            if dash_match:
                # Extract text after dash, handle parentheses if present
                text_after_dash = dash_match.group(1).strip()
                paren_in_dash = re.search(r'\(\s*([^)]+)\s*\)', text_after_dash)
                if paren_in_dash:
                    payref = paren_in_dash.group(1).strip()
                else:
                    # Don't split on dots to preserve names like "K.kwiyo"
                    payref = re.split(r'[,\n\r]', text_after_dash)[0].strip()
            else:
                # Don't split on dots to preserve names like "K.kwiyo"
                payref = re.split(r'[,\n\r]', after)[0].strip()
            # Clean up trailing dots/spaces
            payref = payref.rstrip('. ')
        else:
            # No RJ-Number found, use the whole comment as Payment Ref
            payref = comment.strip()

        return rj, payref

    # Test cases
    test_cases = [
        ("Ref CSH764074250 - (Phuthani mabhena)", "CSH764074250", "Phuthani mabhena"),
        ("Ref CSH293299862 - (Mlamuli)", "CSH293299862", "Mlamuli"),
        ("RJ123456 - K.kwiyo", "RJ123456", "K.kwiyo"),
        ("TX987654 - John Doe", "TX987654", "John Doe"),
        ("Payment Ref #: TestRef123", "", "TestRef123"),
        ("RJ-123456. - Test Name", "RJ123456", "Test Name"),
        ("No reference here", "", "No reference here"),
        ("Ref #RJ58822828410. - Gugu 6408370691", "RJ58822828410", "Gugu 6408370691"),
    ]

    print("=" * 70)
    print("FNB/ABSA EXTRACTION TEST RESULTS")
    print("=" * 70)

    passed = 0
    failed = 0

    for comment, expected_rj, expected_ref in test_cases:
        rj, ref = extract_rj_and_ref(comment)

        rj_match = rj == expected_rj
        ref_match = ref == expected_ref

        status = "[PASS]" if (rj_match and ref_match) else "[FAIL]"

        print(f"\n{status}")
        print(f"  Input:        {comment}")
        print(f"  Expected RJ:  {expected_rj}")
        print(f"  Got RJ:       {rj} {'[OK]' if rj_match else '[X]'}")
        print(f"  Expected Ref: {expected_ref}")
        print(f"  Got Ref:      {ref} {'[OK]' if ref_match else '[X]'}")

        if rj_match and ref_match:
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"FNB/ABSA Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"{'=' * 70}\n")

    return passed, failed


def test_kazang_extraction():
    """Test Kazang extraction logic"""

    def extract_payment_ref_from_comment(comment):
        if not isinstance(comment, str):
            return ''

        comment = comment.strip()

        # Pattern 1: Parentheses format - "Ref CSH764074250 - (Phuthani mabhena)"
        paren_match = re.search(r'\(\s*([^)]+)\s*\)', comment)
        if paren_match:
            return paren_match.group(1).strip()

        # Pattern 2: Look for "- " followed by name (with dot before)
        pattern2 = r'\.\s*-\s*([A-Za-z]+)'
        match2 = re.search(pattern2, comment)
        if match2:
            return match2.group(1).strip()

        # Pattern 3: Alternative format without dot
        pattern3 = r'-\s+([A-Za-z]+)'
        match3 = re.search(pattern3, comment)
        if match3:
            return match3.group(1).strip()

        # Pattern 4: If there's text after RJ/CSH number, try to extract name
        pattern4 = r'#?(RJ|CSH)\d+\.?\s*-?\s*([A-Za-z]+)'
        match4 = re.search(pattern4, comment, re.IGNORECASE)
        if match4:
            return match4.group(2).strip()

        return ''

    def extract_rj(comment):
        if not isinstance(comment, str):
            return ''
        # Patterns: RJ123456, CSH764074250, TX123456
        rj_match = re.search(r'#?(RJ|CSH|TX)[-]?(\d{6,})', comment, re.IGNORECASE)
        return rj_match.group(0).replace('#', '').replace('-', '').upper() if rj_match else ''

    # Test cases
    test_cases = [
        ("Ref CSH764074250 - (Phuthani mabhena)", "CSH764074250", "Phuthani mabhena"),
        ("Ref CSH293299862 - (Mlamuli)", "CSH293299862", "Mlamuli"),
        ("Ref #RJ58822828410. - Gugu 6408370691", "RJ58822828410", "Gugu"),
        ("Ref #RJ58953541109. - Lucy6410281493", "RJ58953541109", "Lucy"),
        ("RJ123456 - TestName", "RJ123456", "TestName"),
        ("TX987654 - John", "TX987654", "John"),
    ]

    print("=" * 70)
    print("KAZANG EXTRACTION TEST RESULTS")
    print("=" * 70)

    passed = 0
    failed = 0

    for comment, expected_rj, expected_ref in test_cases:
        rj = extract_rj(comment)
        ref = extract_payment_ref_from_comment(comment)

        rj_match = rj == expected_rj
        ref_match = ref == expected_ref

        status = "[PASS]" if (rj_match and ref_match) else "[FAIL]"

        print(f"\n{status}")
        print(f"  Input:        {comment}")
        print(f"  Expected RJ:  {expected_rj}")
        print(f"  Got RJ:       {rj} {'[OK]' if rj_match else '[X]'}")
        print(f"  Expected Ref: {expected_ref}")
        print(f"  Got Ref:      {ref} {'[OK]' if ref_match else '[X]'}")

        if rj_match and ref_match:
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"Kazang Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"{'=' * 70}\n")

    return passed, failed


if __name__ == "__main__":
    print("\nTESTING CSH PATTERN EXTRACTION")
    print("=" * 70)
    print("Testing new patterns:")
    print("  - 'Ref CSH764074250 - (Phuthani mabhena)' => RJ: CSH764074250, Ref: Phuthani mabhena")
    print("  - 'Ref CSH293299862 - (Mlamuli)' => RJ: CSH293299862, Ref: Mlamuli")
    print("=" * 70)
    print()

    fnb_passed, fnb_failed = test_fnb_absa_extraction()
    kazang_passed, kazang_failed = test_kazang_extraction()

    total_passed = fnb_passed + kazang_passed
    total_failed = fnb_failed + kazang_failed
    total_tests = total_passed + total_failed

    print("\n" + "=" * 70)
    print("OVERALL TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {total_passed}")
    print(f"Failed:       {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    print("=" * 70)

    if total_failed == 0:
        print("\nALL TESTS PASSED! CSH extraction is working correctly.")
    else:
        print(f"\n{total_failed} test(s) failed. Please review the failures above.")
