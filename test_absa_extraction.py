"""
Test script for ABSA reference and fee extraction
"""
import re

def extract_absa_data(description):
    """
    Extract Reference and Fee from ABSA description
    
    Returns: (reference, fee)
    """
    desc = str(description).strip()
    
    # Extract Fee - Format: ( 5,49 ) where comma is decimal separator
    fee_pattern = r'\(\s*(\d+),(\d+)\s*\)'
    fee_match = re.search(fee_pattern, desc)
    
    if fee_match:
        rand = fee_match.group(1)
        cents = fee_match.group(2)
        fee = float(f"{rand}.{cents}")
    else:
        fee = 0.0
    
    # Extract Reference
    reference = "UNKNOWN"
    
    # Check if it's STAMPED STATEMENT (no reference, only fee)
    if 'STAMPED STATEMENT' in desc.upper():
        reference = ""
    else:
        # Try pattern 1: PayShap Ext Credit followed by name
        payshap_pattern = r'PayShap\s+Ext\s+Credit\s+([A-Z]+\s+[A-Z]+)'
        payshap_match = re.search(payshap_pattern, desc, re.IGNORECASE)
        
        if payshap_match:
            reference = payshap_match.group(1).strip().upper()
        else:
            # Try pattern 2: ACB CREDIT CAPITEC followed by name
            acb_pattern = r'ACB\s+CREDIT\s+CAPITE[C]?\s+([A-Z]+\s+[A-Z]+)'
            acb_match = re.search(acb_pattern, desc, re.IGNORECASE)
            
            if acb_match:
                reference = acb_match.group(1).strip().upper()
            else:
                # Try pattern 3: DIGITAL PAYMENT CR ABSA BANK followed by name
                digital_pattern = r'DIGITAL\s+PAYMENT\s+CR\s+ABSA\s+BANK\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)'
                digital_match = re.search(digital_pattern, desc, re.IGNORECASE)
                
                if digital_match:
                    reference = digital_match.group(1).strip()
                else:
                    # Try pattern 4: DEPOSIT NO
                    ref_pattern = r'DEPOSIT\s+NO\s*:\s*([a-zA-Z0-9]+)'
                    ref_match = re.search(ref_pattern, desc, re.IGNORECASE)
                    
                    if ref_match:
                        reference = ref_match.group(1).strip()
                    else:
                        # Try pattern 5: ABSA BANK followed by name
                        absa_pattern = r'ABSA\s+BANK\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)'
                        absa_match = re.search(absa_pattern, desc, re.IGNORECASE)
                        
                        if absa_match:
                            reference = absa_match.group(1).strip()
                        else:
                            # Fallback: try CONTACT pattern
                            contact_pattern = r'CONTACT\s*:\s*(\d+)'
                            contact_match = re.search(contact_pattern, desc, re.IGNORECASE)
                            if contact_match:
                                reference = contact_match.group(1).strip()
    
    return reference, fee


# Test cases from the user's data
test_cases = [
    "ACB CREDIT CAPITEC K KWIYO",
    "PayShap Ext Credit P NCUBE",
    "PayShap Ext Credit S MOYO",
    "DIGITAL PAYMENT CR ABSA BANK Dumi",
    "DIGITAL PAYMENT CR ABSA BANK Concilia Mabhena",
    "CARDLESS CASH DEP   HILLBROW 1(   24,66 ) DEPOSIT NO : lulu CO",
    "STAMPED STATEMENT             (     13,00 )",
    "CARDLESS CASH DEP   HILLBROW 1(   30,78 ) DEPOSIT NO : brenda",
]

print("=" * 80)
print("ABSA REFERENCE AND FEE EXTRACTION TEST")
print("=" * 80)
print()

for i, desc in enumerate(test_cases, 1):
    ref, fee = extract_absa_data(desc)
    print(f"Test {i}:")
    print(f"  Description: {desc}")
    print(f"  Reference:   {ref}")
    print(f"  Fee:         {fee}")
    print()

print("=" * 80)
print("EXPECTED RESULTS:")
print("=" * 80)
print("Test 1: Reference = 'K KWIYO', Fee = 0.0")
print("Test 2: Reference = 'P NCUBE', Fee = 0.0")
print("Test 3: Reference = 'S MOYO', Fee = 0.0")
print("Test 4: Reference = 'Dumi', Fee = 0.0")
print("Test 5: Reference = 'Concilia Mabhena', Fee = 0.0")
print("Test 6: Reference = 'lulu', Fee = 24.66")
print("Test 7: Reference = '', Fee = 13.0")
print("Test 8: Reference = 'brenda', Fee = 30.78")
