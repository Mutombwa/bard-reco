"""
Unified Reference Extraction Module
====================================
Standardized extraction patterns for all BARD-RECO workflows.
Ensures consistent extraction across FNB, ABSA, Kazang, Corporate, and Bidvest.
"""

import re
from typing import Tuple, List, Optional


class ReferenceExtractor:
    """
    Unified reference extraction for all workflows.

    Supports patterns:
    - RJ: RJ followed by 11 digits (e.g., RJ58822828410)
    - TX: TX followed by 11 digits (e.g., TX12345678901)
    - CSH: CSH followed by 9+ digits (e.g., CSH891089488)
    - ZVC: ZVC followed by 9 digits (e.g., ZVC128809565)
    - ECO: ECO followed by 9 digits (e.g., ECO904183634)
    - INN: INN followed by 9 digits (e.g., INN757797206)
    """

    # Pattern definitions
    PATTERNS = {
        'RJ': r'RJ\d{11}',
        'TX': r'TX\d{11}',
        'CSH': r'CSH\d{9,}',
        'ZVC': r'ZVC\d{9}',
        'ECO': r'ECO\d{9}',
        'INN': r'INN\d{9}',
    }

    # Combined pattern for all reference types
    ALL_PATTERNS = r'(RJ|TX|CSH|ZVC|ECO|INN)[-]?(\d{6,})'

    @classmethod
    def extract_rj_number(cls, text: str) -> str:
        """
        Extract RJ/reference number from text.

        Args:
            text: Input text containing reference number

        Returns:
            Extracted reference number (e.g., 'CSH891089488') or empty string

        Examples:
            >>> ReferenceExtractor.extract_rj_number("Ref CSH891089488 - (Jenet)")
            'CSH891089488'
            >>> ReferenceExtractor.extract_rj_number("Reversal: (#Ref CSH613695391)")
            'CSH613695391'
        """
        if not text or not isinstance(text, str):
            return ''

        # Match any of our reference patterns
        match = re.search(cls.ALL_PATTERNS, text, re.IGNORECASE)
        if match:
            prefix = match.group(1).upper()
            digits = match.group(2)
            return f"{prefix}{digits}"

        return ''

    @classmethod
    def extract_all_references(cls, text: str) -> List[str]:
        """
        Extract all reference numbers from text.

        Args:
            text: Input text potentially containing multiple references

        Returns:
            List of extracted reference numbers

        Examples:
            >>> ReferenceExtractor.extract_all_references("RJ123 and CSH456")
            ['RJ12345678901', 'CSH456789012']
        """
        if not text or not isinstance(text, str):
            return []

        all_matches = []

        # Extract each pattern type
        for pattern_name, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_matches.extend([m.upper() for m in matches])

        # Remove duplicates while preserving order
        seen = set()
        unique = [x for x in all_matches if not (x in seen or seen.add(x))]

        return unique

    @classmethod
    def clean_name(cls, name: str) -> str:
        """
        Clean extracted name by removing phone numbers.

        Handles:
        - Trailing phone numbers after space: "Jenet 6452843846" → "Jenet"
        - Phone numbers after slash: "gracious/6453092146" → "gracious"
        - Attached phone numbers: "remember6453463069" → "remember"

        Args:
            name: Raw extracted name

        Returns:
            Cleaned name without phone numbers
        """
        if not name:
            return ''

        name = name.strip()

        # Remove trailing phone number after space: "Jenet 6452843846" → "Jenet"
        name = re.sub(r'\s+\d{10,}$', '', name)

        # Remove phone number after slash: "gracious/6453092146" → "gracious"
        name = re.sub(r'/\d{10,}$', '', name)

        # Remove attached phone number: "remember6453463069" → "remember"
        # Only if it starts with letters followed by 10+ digits at the end
        name = re.sub(r'^([a-zA-Z][a-zA-Z\s]*?)\d{10,}$', r'\1', name)

        return name.strip()

    @classmethod
    def extract_payment_ref(cls, text: str) -> str:
        """
        Extract payment reference (name or phone number) from text.

        Args:
            text: Input text containing payment reference

        Returns:
            Extracted payment reference (name or phone number)

        Examples:
            >>> ReferenceExtractor.extract_payment_ref("Ref CSH891089488 - (Jenet 6452843846)")
            'Jenet'
            >>> ReferenceExtractor.extract_payment_ref("Reversal: (#Ref CSH613695391) - (Doubt Sibanda)")
            'Doubt Sibanda'
            >>> ReferenceExtractor.extract_payment_ref("Ref CSH667941330 - (6503065718)")
            '6503065718'
            >>> ReferenceExtractor.extract_payment_ref("Reversal: CSH564980448: 6505166670")
            '6505166670'
        """
        if not text or not isinstance(text, str):
            return ''

        text = text.strip()

        # Pattern 0: Reversal with colon format - "Reversal: CSH564980448: 6505166670"
        # Extract phone number after the second colon
        match = re.search(r'Reversal:\s*(CSH|ECO|ZVC|INN|RJ|TX)\d+:\s*(\d{10})', text, re.IGNORECASE)
        if match:
            return match.group(2)

        # Pattern 1: Find ALL parentheses and use the one with the name/phone (not #Ref)
        all_parens = re.findall(r'\(\s*([^)]+)\s*\)', text)
        for paren_content in all_parens:
            paren_content = paren_content.strip()
            # Skip if it looks like a reference (starts with #Ref or Ref followed by pattern)
            if re.match(r'#?Ref\s+(RJ|TX|CSH|ZVC|ECO|INN)', paren_content, re.IGNORECASE):
                continue
            # Check if it's a phone number only (10 digits starting with 6)
            if re.match(r'^6\d{9}$', paren_content):
                return paren_content
            # Found a valid name in parentheses
            cleaned = cls.clean_name(paren_content)
            if cleaned:
                return cleaned

        # Pattern 2: Look for ". - Name" format
        match = re.search(r'\.\s*-\s*([A-Za-z][A-Za-z\s]*)', text)
        if match:
            return cls.clean_name(match.group(1))

        # Pattern 3: Look for "- Name" format (dash followed by space and name)
        match = re.search(r'[-–]\s+([A-Za-z][A-Za-z\s]*)', text)
        if match:
            return cls.clean_name(match.group(1))

        # Pattern 4: After reference number with dash
        match = re.search(r'(RJ|TX|CSH|ZVC|ECO|INN)\d+\.?\s*-\s*([A-Za-z][A-Za-z\s]*)', text, re.IGNORECASE)
        if match:
            return cls.clean_name(match.group(2))

        return ''

    @classmethod
    def extract_rj_and_ref(cls, text: str) -> Tuple[str, str]:
        """
        Extract both RJ number and payment reference from text.

        Args:
            text: Input text

        Returns:
            Tuple of (rj_number, payment_ref)

        Examples:
            >>> ReferenceExtractor.extract_rj_and_ref("Ref CSH891089488 - (Jenet 6452843846)")
            ('CSH891089488', 'Jenet')
        """
        rj = cls.extract_rj_number(text)
        ref = cls.extract_payment_ref(text)
        return rj, ref

    @classmethod
    def extract_from_description(cls, description: str) -> str:
        """
        Extract reference name from bank statement description.
        Handles formats like:
        - "ABSA BANK Thenjiwe" → "Thenjiwe"
        - "CAPITEC   G KWENDA" → "G KWENDA"
        - "0795272164mkethwa" → "mkethwa"

        Args:
            description: Bank statement description

        Returns:
            Extracted reference name
        """
        if not description or not isinstance(description, str):
            return ''

        desc = description.strip()

        # Pattern: Phone number (10 digits) followed by name
        match = re.match(r'^0\d{9}\s*([a-zA-Z][a-zA-Z\s]+)$', desc)
        if match:
            return match.group(1).strip()

        # Pattern: Bank name followed by customer name
        bank_patterns = [
            r'ABSA\s+BANK\s+(.+)',
            r'ABSA BANK\s+(.+)',
            r'CAPITEC\s+(.+)',
            r'NEDBANK\s+(.+)',
            r'STANDARD BANK\s+(.+)',
            r'FNB\s+BANK\s+(.+)',
            r'FNB\s+(.+)',
        ]

        for pattern in bank_patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Pattern: FNB specific patterns
        fnb_patterns = [
            r'FNB OB PMT\s+(.+)',
            r'FNB APP PAYMENT FROM\s+(.+)',
            r'CELL PMNT FROM\s+(.+)',
        ]

        for pattern in fnb_patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: return original if short enough
        if len(desc) <= 50:
            return desc

        return ''


# =============================================
# CONVENIENCE FUNCTIONS
# =============================================

def extract_rj_number(text: str) -> str:
    """Extract RJ/reference number from text"""
    return ReferenceExtractor.extract_rj_number(text)


def extract_payment_ref(text: str) -> str:
    """Extract payment reference (name) from text"""
    return ReferenceExtractor.extract_payment_ref(text)


def extract_rj_and_ref(text: str) -> Tuple[str, str]:
    """Extract both RJ number and payment reference"""
    return ReferenceExtractor.extract_rj_and_ref(text)


def clean_name(name: str) -> str:
    """Clean extracted name by removing phone numbers"""
    return ReferenceExtractor.clean_name(name)


def extract_from_description(description: str) -> str:
    """Extract reference name from bank statement description"""
    return ReferenceExtractor.extract_from_description(description)


# =============================================
# TESTING
# =============================================

if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Ref CSH891089488 - (Jenet 6452843846)", "CSH891089488", "Jenet"),
        ("Ref CSH031515152 - (Elisha 6452973196)", "CSH031515152", "Elisha"),
        ("Ref CSH759506112 - (gracious/6453092146)", "CSH759506112", "gracious"),
        ("Ref CSH332138014 - (mahunga/6450105265)", "CSH332138014", "mahunga"),
        ("Ref CSH654176053 - (remember6453463069)", "CSH654176053", "remember"),
        ("Ref CSH438032426 - (Charity6452970770)", "CSH438032426", "Charity"),
        ("Reversal: (#Ref CSH613695391)  - (Doubt Sibanda)", "CSH613695391", "Doubt Sibanda"),
        ("Reversal: (#Ref CSH043126323)  - (Orison)", "CSH043126323", "Orison"),
        ("Ref CSH432046285 - (Sobukhosi Dube)", "CSH432046285", "Sobukhosi Dube"),
        ("Ref CSH857542137 - (Slyvia)", "CSH857542137", "Slyvia"),
        ("Ref ZVC128809565 - (Test)", "ZVC128809565", "Test"),
        ("Ref ECO904183634", "ECO904183634", ""),
        ("Ref INN757797206 - (Themba)", "INN757797206", "Themba"),
        ("RJ58822828410 - Gugu", "RJ58822828410", "Gugu"),
        # New patterns: phone numbers as payment refs
        ("Ref CSH667941330 - (6503065718)", "CSH667941330", "6503065718"),
        ("Reversal: CSH564980448: 6505166670", "CSH564980448", "6505166670"),
        ("Ref ECO149260320 - (6507067253)", "ECO149260320", "6507067253"),
        ("Reversal: ECO149260320: 6505166670", "ECO149260320", "6505166670"),
    ]

    print("=" * 70)
    print("UNIFIED EXTRACTION MODULE TEST")
    print("=" * 70)

    passed = 0
    for text, expected_rj, expected_ref in test_cases:
        rj, ref = extract_rj_and_ref(text)

        rj_ok = rj == expected_rj
        ref_ok = ref == expected_ref

        if rj_ok and ref_ok:
            passed += 1
            status = "[PASS]"
        else:
            status = "[FAIL]"

        print(f"{status}")
        print(f"  Input: {text[:60]}...")
        print(f"  RJ:  Expected '{expected_rj}' | Got '{rj}' {'[OK]' if rj_ok else '[X]'}")
        print(f"  Ref: Expected '{expected_ref}' | Got '{ref}' {'[OK]' if ref_ok else '[X]'}")
        print()

    print("=" * 70)
    print(f"Results: {passed}/{len(test_cases)} tests passed")
    print("=" * 70)
