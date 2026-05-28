"""
Tests for ABSA reference extraction patterns including new patterns:
- DIGITAL PAYMENT DT/CR
- IMDTE DIGITAL PMT (hex codes)
- CREDIT TRANSFER
- PROOF OF PAYMT SMS
"""

import pytest
import re
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pre-compiled patterns from absa_workflow
from components.absa_workflow import (
    _RE_FEE, _RE_PROOF_OF_PAYMT, _RE_PAYSHAP, _RE_IMMEDIATE_TRF,
    _RE_ACB_CREDIT, _RE_IMDTE_DIGITAL, _RE_DIGITAL_PAYMENT,
    _RE_CREDIT_TRANSFER, _RE_DEPOSIT_NO, _RE_ABSA_BANK, _RE_CONTACT,
    _RE_RJ_PATTERN, _RE_RJ_NUMBER, _RE_PAYREF_LABEL,
)


def extract_absa_ref(desc):
    """Replicate the extract_absa_data logic for testing."""
    desc = str(desc).strip()

    # Fee
    fee_match = _RE_FEE.search(desc)
    fee = float(f"{fee_match.group(1)}.{fee_match.group(2)}") if fee_match else 0.0

    # Reference
    reference = "UNKNOWN"
    if 'STAMPED STATEMENT' in desc.upper():
        reference = ""
    elif _RE_PROOF_OF_PAYMT.match(desc):
        reference = ""
    else:
        m = _RE_PAYSHAP.search(desc)
        if m:
            reference = m.group(1).strip()
        else:
            m = _RE_IMMEDIATE_TRF.search(desc)
            if m:
                reference = m.group(1).strip()
            else:
                m = _RE_ACB_CREDIT.search(desc)
                if m:
                    reference = m.group(1).strip().upper()
                else:
                    m = _RE_IMDTE_DIGITAL.search(desc)
                    if m:
                        reference = m.group(1).strip()
                    else:
                        m = _RE_DIGITAL_PAYMENT.search(desc)
                        if m:
                            tokens = m.group(1).strip().split()
                            reference = tokens[-1] if tokens else m.group(1).strip()
                        else:
                            m = _RE_CREDIT_TRANSFER.search(desc)
                            if m:
                                reference = m.group(1).strip()
                            else:
                                m = _RE_DEPOSIT_NO.search(desc)
                                if m:
                                    reference = m.group(1).strip()
                                else:
                                    m = _RE_ABSA_BANK.search(desc)
                                    if m:
                                        tokens = m.group(1).strip().split()
                                        reference = tokens[-1] if tokens else m.group(1).strip()
                                    else:
                                        m = _RE_CONTACT.search(desc)
                                        if m:
                                            reference = m.group(1).strip()

    return reference, fee


class TestABSAFeeExtraction:
    def test_fee_standard(self):
        ref, fee = extract_absa_ref("DIGITAL PAYMENT DT            (      5,50 ) ABSA BANK EFT376180798")
        assert fee == 5.50

    def test_fee_large(self):
        ref, fee = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK EFT553186763 161A9556C7")
        assert fee == 40.0

    def test_fee_small(self):
        ref, fee = extract_absa_ref("PROOF OF PAYMT SMS            (      1,25 )")
        assert fee == 1.25

    def test_no_fee(self):
        ref, fee = extract_absa_ref("CREDIT TRANSFER     CASHFOCUS ESOR CONSTRUCTION")
        assert fee == 0.0


class TestABSADigitalPaymentDT:
    def test_eft_reference(self):
        ref, _ = extract_absa_ref("DIGITAL PAYMENT DT            (      5,50 ) ABSA BANK EFT376180798")
        assert ref == "EFT376180798"

    def test_eft_reference_2(self):
        ref, _ = extract_absa_ref("DIGITAL PAYMENT DT            (      5,50 ) ABSA BANK EFT680898755")
        assert ref == "EFT680898755"


class TestABSADigitalPaymentCR:
    def test_name_after_absa_bank(self):
        ref, _ = extract_absa_ref("DIGITAL PAYMENT CR ABSA BANK Dumi")
        assert ref == "Dumi"


class TestABSAImdteDigitalPMT:
    def test_hex_code_after_eft(self):
        ref, _ = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK EFT553186763 161A9556C7")
        assert ref == "161A9556C7"

    def test_hex_code_after_name(self):
        ref, _ = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK IMAGEMAKERS 161A95A6EA")
        assert ref == "161A95A6EA"

    def test_hex_code_various(self):
        ref, _ = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK EFT325640814 161A9554CA")
        assert ref == "161A9554CA"

    def test_hex_code_another(self):
        ref, _ = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK EFT375209565 161A9554F2")
        assert ref == "161A9554F2"

    def test_hex_code_5570d(self):
        ref, _ = extract_absa_ref("IMDTE DIGITAL PMT             (     40,00 ) ABSA BANK EFT331162507 161A95570D")
        assert ref == "161A95570D"


class TestABSACreditTransfer:
    def test_with_cashfocus(self):
        ref, _ = extract_absa_ref("CREDIT TRANSFER     CASHFOCUS ESOR CONSTRUCTION")
        assert ref == "ESOR CONSTRUCTION"


class TestABSAProofOfPaymt:
    def test_proof_of_paymt_sms(self):
        ref, _ = extract_absa_ref("PROOF OF PAYMT SMS            (      1,25 )")
        assert ref == ""


class TestABSAStampedStatement:
    def test_stamped_statement(self):
        ref, _ = extract_absa_ref("STAMPED STATEMENT ( 13,00 )")
        assert ref == ""


class TestABSAPayShap:
    def test_payshap_single_name(self):
        ref, _ = extract_absa_ref("PayShap Ext Credit Nomatemba")
        assert ref == "Nomatemba"

    def test_payshap_initial_surname(self):
        ref, _ = extract_absa_ref("PayShap Ext Credit P NCUBE")
        assert ref == "P NCUBE"


class TestABSADepositNo:
    def test_deposit_no(self):
        ref, _ = extract_absa_ref("CARDLESS CASH DEP HILLBROW 1( 5,49 ) DEPOSIT NO : linda CONTACT : 0744811776")
        assert ref == "linda"


class TestABSAACBCredit:
    def test_acb_capitec(self):
        ref, _ = extract_absa_ref("ACB CREDIT CAPITEC K KWIYO")
        assert ref == "K KWIYO"


class TestABSAImmediateTRF:
    def test_immediate_trf(self):
        ref, _ = extract_absa_ref("IMMEDIATE TRF CR FIRSTRAND Mehluli Nkomo 05LBW8SRGP")
        assert ref == "Mehluli Nkomo"


class TestPreCompiledPatternsExist:
    """Verify all pre-compiled patterns are valid regex objects."""
    def test_all_patterns_compiled(self):
        patterns = [
            _RE_FEE, _RE_PROOF_OF_PAYMT, _RE_PAYSHAP, _RE_IMMEDIATE_TRF,
            _RE_ACB_CREDIT, _RE_IMDTE_DIGITAL, _RE_DIGITAL_PAYMENT,
            _RE_CREDIT_TRANSFER, _RE_DEPOSIT_NO, _RE_ABSA_BANK, _RE_CONTACT,
            _RE_RJ_PATTERN, _RE_RJ_NUMBER, _RE_PAYREF_LABEL,
        ]
        for p in patterns:
            assert isinstance(p, re.Pattern), f"{p} is not a compiled regex"
