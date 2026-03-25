"""
Tests for the unified reference extraction module.
"""

import pytest
from utils.extraction import (
    ReferenceExtractor,
    extract_rj_number,
    extract_payment_ref,
    extract_rj_and_ref,
    clean_name,
    extract_from_description,
)


class TestExtractRJNumber:
    """Test RJ/reference number extraction from text."""

    # --- RJ pattern: RJ followed by 11 digits ---

    def test_rj_basic(self):
        assert ReferenceExtractor.extract_rj_number("RJ58822828410 - Gugu") == "RJ58822828410"

    def test_rj_embedded_in_text(self):
        assert ReferenceExtractor.extract_rj_number("Payment ref RJ12345678901 received") == "RJ12345678901"

    def test_rj_with_dash_separator(self):
        """ALL_PATTERNS allows an optional dash between prefix and digits."""
        result = ReferenceExtractor.extract_rj_number("RJ-12345678901")
        assert result == "RJ12345678901"

    # --- TX pattern: TX followed by 11 digits ---

    def test_tx_basic(self):
        assert ReferenceExtractor.extract_rj_number("TX12345678901") == "TX12345678901"

    def test_tx_in_sentence(self):
        assert ReferenceExtractor.extract_rj_number("Ref TX99988877766 processed") == "TX99988877766"

    # --- CSH pattern: CSH followed by 9+ digits ---

    def test_csh_nine_digits(self):
        assert ReferenceExtractor.extract_rj_number("Ref CSH891089488 - (Jenet)") == "CSH891089488"

    def test_csh_in_reversal(self):
        assert ReferenceExtractor.extract_rj_number("Reversal: (#Ref CSH613695391)") == "CSH613695391"

    def test_csh_more_than_nine_digits(self):
        """CSH pattern allows 9 or more digits."""
        result = ReferenceExtractor.extract_rj_number("CSH1234567890")
        assert result == "CSH1234567890"

    # --- ZVC pattern: ZVC followed by 9 digits ---

    def test_zvc_basic(self):
        assert ReferenceExtractor.extract_rj_number("Ref ZVC128809565 - (Test)") == "ZVC128809565"

    def test_zvc_standalone(self):
        assert ReferenceExtractor.extract_rj_number("ZVC999888777") == "ZVC999888777"

    # --- ECO pattern: ECO followed by 9 digits ---

    def test_eco_basic(self):
        assert ReferenceExtractor.extract_rj_number("Ref ECO904183634") == "ECO904183634"

    def test_eco_in_reversal_with_colon(self):
        assert ReferenceExtractor.extract_rj_number("Reversal: ECO149260320: 6505166670") == "ECO149260320"

    # --- INN pattern: INN followed by 9 digits ---

    def test_inn_basic(self):
        assert ReferenceExtractor.extract_rj_number("Ref INN757797206 - (Themba)") == "INN757797206"

    # --- Case insensitivity ---

    def test_lowercase_prefix(self):
        result = ReferenceExtractor.extract_rj_number("ref csh891089488 - name")
        assert result == "CSH891089488"

    def test_mixed_case(self):
        result = ReferenceExtractor.extract_rj_number("Csh123456789")
        assert result == "CSH123456789"

    # --- Edge cases ---

    def test_empty_string(self):
        assert ReferenceExtractor.extract_rj_number("") == ""

    def test_none_input(self):
        assert ReferenceExtractor.extract_rj_number(None) == ""

    def test_non_string_input(self):
        assert ReferenceExtractor.extract_rj_number(12345) == ""

    def test_no_match(self):
        assert ReferenceExtractor.extract_rj_number("No reference here") == ""

    def test_insufficient_digits(self):
        """Patterns require a minimum number of digits (6+ via ALL_PATTERNS)."""
        result = ReferenceExtractor.extract_rj_number("CSH12345")
        # ALL_PATTERNS requires 6+ digits after prefix
        assert result == ""


class TestExtractAllReferences:
    """Test extracting all reference numbers from text."""

    def test_single_reference(self):
        refs = ReferenceExtractor.extract_all_references("Ref CSH891089488")
        assert "CSH891089488" in refs

    def test_multiple_references(self):
        refs = ReferenceExtractor.extract_all_references("CSH891089488 and ZVC128809565")
        assert "CSH891089488" in refs
        assert "ZVC128809565" in refs

    def test_duplicate_references_deduplicated(self):
        refs = ReferenceExtractor.extract_all_references("CSH891089488 CSH891089488")
        assert len([r for r in refs if r == "CSH891089488"]) == 1

    def test_empty_input(self):
        assert ReferenceExtractor.extract_all_references("") == []

    def test_none_input(self):
        assert ReferenceExtractor.extract_all_references(None) == []

    def test_no_references(self):
        assert ReferenceExtractor.extract_all_references("Just some text") == []


class TestCleanName:
    """Test name cleaning (phone number removal)."""

    def test_trailing_phone_number(self):
        assert ReferenceExtractor.clean_name("Jenet 6452843846") == "Jenet"

    def test_phone_after_slash(self):
        assert ReferenceExtractor.clean_name("gracious/6453092146") == "gracious"

    def test_attached_phone_number(self):
        assert ReferenceExtractor.clean_name("remember6453463069") == "remember"

    def test_name_without_phone(self):
        assert ReferenceExtractor.clean_name("Doubt Sibanda") == "Doubt Sibanda"

    def test_empty_input(self):
        assert ReferenceExtractor.clean_name("") == ""

    def test_none_input(self):
        assert ReferenceExtractor.clean_name(None) == ""

    def test_whitespace_stripping(self):
        assert ReferenceExtractor.clean_name("  Jenet  ") == "Jenet"

    def test_charity_with_phone(self):
        assert ReferenceExtractor.clean_name("Charity6452970770") == "Charity"

    def test_name_with_slash_phone(self):
        assert ReferenceExtractor.clean_name("mahunga/6450105265") == "mahunga"


class TestExtractPaymentRef:
    """Test payment reference (name or phone number) extraction."""

    # --- Names in parentheses ---

    def test_name_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH891089488 - (Jenet 6452843846)")
        assert result == "Jenet"

    def test_full_name_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH432046285 - (Sobukhosi Dube)")
        assert result == "Sobukhosi Dube"

    def test_single_name_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH857542137 - (Slyvia)")
        assert result == "Slyvia"

    def test_name_with_phone_slash_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH759506112 - (gracious/6453092146)")
        assert result == "gracious"

    def test_name_with_attached_phone_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH654176053 - (remember6453463069)")
        assert result == "remember"

    # --- Phone numbers as payment refs ---

    def test_phone_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH667941330 - (6503065718)")
        assert result == "6503065718"

    def test_eco_phone_in_parentheses(self):
        result = ReferenceExtractor.extract_payment_ref("Ref ECO149260320 - (6507067253)")
        assert result == "6507067253"

    # --- Reversal patterns ---

    def test_reversal_with_hash_ref(self):
        result = ReferenceExtractor.extract_payment_ref("Reversal: (#Ref CSH613695391)  - (Doubt Sibanda)")
        assert result == "Doubt Sibanda"

    def test_reversal_with_hash_ref_single_name(self):
        result = ReferenceExtractor.extract_payment_ref("Reversal: (#Ref CSH043126323)  - (Orison)")
        assert result == "Orison"

    def test_reversal_colon_format_csh(self):
        """Reversal with colon format: 'Reversal: CSH564980448: 6505166670'."""
        result = ReferenceExtractor.extract_payment_ref("Reversal: CSH564980448: 6505166670")
        assert result == "6505166670"

    def test_reversal_colon_format_eco(self):
        result = ReferenceExtractor.extract_payment_ref("Reversal: ECO149260320: 6505166670")
        assert result == "6505166670"

    # --- Other patterns ---

    def test_rj_dash_name(self):
        result = ReferenceExtractor.extract_payment_ref("RJ58822828410 - Gugu")
        assert result == "Gugu"

    def test_zvc_with_name(self):
        result = ReferenceExtractor.extract_payment_ref("Ref ZVC128809565 - (Test)")
        assert result == "Test"

    def test_inn_with_name(self):
        result = ReferenceExtractor.extract_payment_ref("Ref INN757797206 - (Themba)")
        assert result == "Themba"

    def test_eco_no_name(self):
        """ECO reference with no name should return empty string."""
        result = ReferenceExtractor.extract_payment_ref("Ref ECO904183634")
        assert result == ""

    # --- Edge cases ---

    def test_empty_string(self):
        assert ReferenceExtractor.extract_payment_ref("") == ""

    def test_none_input(self):
        assert ReferenceExtractor.extract_payment_ref(None) == ""

    def test_non_string_input(self):
        assert ReferenceExtractor.extract_payment_ref(12345) == ""

    def test_elisha_with_phone(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH031515152 - (Elisha 6452973196)")
        assert result == "Elisha"

    def test_mahunga_with_slash_phone(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH332138014 - (mahunga/6450105265)")
        assert result == "mahunga"

    def test_charity_with_attached_phone(self):
        result = ReferenceExtractor.extract_payment_ref("Ref CSH438032426 - (Charity6452970770)")
        assert result == "Charity"


class TestExtractRJAndRef:
    """Test combined extraction of RJ number and payment reference."""

    def test_csh_with_name(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("Ref CSH891089488 - (Jenet 6452843846)")
        assert rj == "CSH891089488"
        assert ref == "Jenet"

    def test_reversal_with_name(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("Reversal: (#Ref CSH613695391)  - (Doubt Sibanda)")
        assert rj == "CSH613695391"
        assert ref == "Doubt Sibanda"

    def test_reversal_colon_format(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("Reversal: CSH564980448: 6505166670")
        assert rj == "CSH564980448"
        assert ref == "6505166670"

    def test_rj_with_name(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("RJ58822828410 - Gugu")
        assert rj == "RJ58822828410"
        assert ref == "Gugu"

    def test_eco_no_name(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("Ref ECO904183634")
        assert rj == "ECO904183634"
        assert ref == ""

    def test_empty_input(self):
        rj, ref = ReferenceExtractor.extract_rj_and_ref("")
        assert rj == ""
        assert ref == ""


class TestExtractFromDescription:
    """Test bank statement description extraction."""

    def test_absa_bank_name(self):
        result = ReferenceExtractor.extract_from_description("ABSA BANK Thenjiwe")
        assert result == "Thenjiwe"

    def test_capitec_name(self):
        result = ReferenceExtractor.extract_from_description("CAPITEC   G KWENDA")
        assert result == "G KWENDA"

    def test_phone_followed_by_name(self):
        result = ReferenceExtractor.extract_from_description("0795272164mkethwa")
        # Pattern: phone (10 digits starting with 0) + name
        # The regex expects space between phone and name, so this may or may not match
        # Based on the regex: r'^0\d{9}\s*([a-zA-Z][a-zA-Z\s]+)$'
        # "0795272164mkethwa" has no space so \s* matches zero spaces
        assert result == "mkethwa"

    def test_phone_with_space_then_name(self):
        result = ReferenceExtractor.extract_from_description("0795272164 mkethwa")
        assert result == "mkethwa"

    def test_fnb_ob_pmt(self):
        result = ReferenceExtractor.extract_from_description("FNB OB PMT John Smith")
        # Extractor strips FNB prefix but keeps OB PMT as part of the description
        assert "John Smith" in result

    def test_fnb_app_payment_from(self):
        result = ReferenceExtractor.extract_from_description("FNB APP PAYMENT FROM Jane Doe")
        # Extractor strips FNB prefix but keeps APP PAYMENT FROM as part of the description
        assert "Jane Doe" in result

    def test_cell_pmnt_from(self):
        result = ReferenceExtractor.extract_from_description("CELL PMNT FROM Mike")
        assert result == "Mike"

    def test_nedbank_name(self):
        result = ReferenceExtractor.extract_from_description("NEDBANK Sipho Nkosi")
        assert result == "Sipho Nkosi"

    def test_standard_bank_name(self):
        result = ReferenceExtractor.extract_from_description("STANDARD BANK Tendai")
        assert result == "Tendai"

    def test_fnb_generic(self):
        result = ReferenceExtractor.extract_from_description("FNB Customer Name")
        assert result == "Customer Name"

    def test_short_description_fallback(self):
        """Short descriptions (<=50 chars) are returned as-is."""
        result = ReferenceExtractor.extract_from_description("Short desc")
        assert result == "Short desc"

    def test_long_description_no_match(self):
        """Long descriptions (>50 chars) with no pattern match return empty."""
        long_text = "A" * 51
        result = ReferenceExtractor.extract_from_description(long_text)
        assert result == ""

    def test_empty_input(self):
        assert ReferenceExtractor.extract_from_description("") == ""

    def test_none_input(self):
        assert ReferenceExtractor.extract_from_description(None) == ""

    def test_non_string_input(self):
        assert ReferenceExtractor.extract_from_description(12345) == ""


class TestConvenienceFunctions:
    """Test the module-level convenience functions match the class methods."""

    def test_extract_rj_number_function(self):
        assert extract_rj_number("Ref CSH891089488 - (Jenet)") == "CSH891089488"

    def test_extract_payment_ref_function(self):
        assert extract_payment_ref("Ref CSH891089488 - (Jenet 6452843846)") == "Jenet"

    def test_extract_rj_and_ref_function(self):
        rj, ref = extract_rj_and_ref("Ref CSH891089488 - (Jenet 6452843846)")
        assert rj == "CSH891089488"
        assert ref == "Jenet"

    def test_clean_name_function(self):
        assert clean_name("Jenet 6452843846") == "Jenet"

    def test_extract_from_description_function(self):
        assert extract_from_description("ABSA BANK Thenjiwe") == "Thenjiwe"
