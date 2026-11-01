"""Python Unicode Examples

Source code for docs/notes/basic/python-unicode.rst
"""

import pytest
import unicodedata


# Encoding 和 Decoding
def encode_utf8(s: str) -> bytes:
    """Encode string to UTF-8 bytes."""
    return s.encode("utf-8")


def decode_utf8(b: bytes) -> str:
    """Decode UTF-8 bytes to string."""
    return b.decode("utf-8")


def encode_with_errors(s: str, encoding: str, errors: str) -> bytes:
    """Encode with error handling."""
    return s.encode(encoding, errors=errors)


# 代码点
def get_code_point(char: str) -> int:
    """Get Unicode code point of character."""
    return ord(char)


def get_char(code_point: int) -> str:
    """Get character from code point."""
    return chr(code_point)


def format_code_points(s: str) -> list[str]:
    """Format string as list of code points."""
    return [f"U+{ord(c):04X}" for c in s]


# 正常化
def normalize_nfc(s: str) -> str:
    """Normalize to NFC (composed) form."""
    return unicodedata.normalize("NFC", s)


def normalize_nfd(s: str) -> str:
    """Normalize to NFD (decomposed) form."""
    return unicodedata.normalize("NFD", s)


# 角色信息
def get_char_name(char: str) -> str:
    """Get Unicode name of character."""
    return unicodedata.name(char)


def get_char_category(char: str) -> str:
    """Get Unicode category of character."""
    return unicodedata.category(char)


def lookup_char(name: str) -> str:
    """Lookup character by Unicode name."""
    return unicodedata.lookup(name)


# String 操作
def case_insensitive_equal(s1: str, s2: str) -> bool:
    """Case-insensitive comparison using casefold."""
    return s1.casefold() == s2.casefold()


# 测试
class TestEncodingDecoding:
    def test_encode_utf8(self):
        assert encode_utf8("Café") == b"Caf\xc3\xa9"

    def test_decode_utf8(self):
        assert decode_utf8(b"Caf\xc3\xa9") == "Café"

    def test_roundtrip(self):
        s = "Hello, 世界!"
        assert decode_utf8(encode_utf8(s)) == s

    def test_encode_errors_ignore(self):
        assert encode_with_errors("Café", "ascii", "ignore") == b"Caf"

    def test_encode_errors_replace(self):
        assert encode_with_errors("Café", "ascii", "replace") == b"Caf?"


class TestCodePoints:
    def test_get_code_point(self):
        assert get_code_point("A") == 65
        assert get_code_point("é") == 233
        assert get_code_point("中") == 20013

    def test_get_char(self):
        assert get_char(65) == "A"
        assert get_char(233) == "é"
        assert get_char(20013) == "中"

    def test_format_code_points(self):
        assert format_code_points("AB") == ["U+0041", "U+0042"]


class TestNormalization:
    def test_nfc(self):
        # e + 组合重音 -> 单 é
        composed = normalize_nfc("e\u0301")
        assert composed == "é"
        assert len(composed) == 1

    def test_nfd(self):
        # 单 é -> e + 组合重音
        decomposed = normalize_nfd("é")
        assert len(decomposed) == 2

    def test_normalization_equality(self):
        s1 = "é"
        s2 = "e\u0301"
        assert s1 != s2
        assert normalize_nfc(s1) == normalize_nfc(s2)


class TestCharInfo:
    def test_get_char_name(self):
        assert get_char_name("A") == "LATIN CAPITAL LETTER A"
        assert "ACUTE" in get_char_name("é")

    def test_get_char_category(self):
        assert get_char_category("A") == "Lu"  # 字母，大写
        assert get_char_category("a") == "Ll"  # 字母，小写
        assert get_char_category("1") == "Nd"  # 数字、数字

    def test_lookup_char(self):
        assert lookup_char("LATIN CAPITAL LETTER A") == "A"
        assert lookup_char("GREEK SMALL LETTER ALPHA") == "α"


class TestStringOperations:
    def test_case_insensitive(self):
        assert case_insensitive_equal("CAFÉ", "café")
        assert case_insensitive_equal("Straße", "strasse")

    def test_unicode_upper_lower(self):
        assert "café".upper() == "CAFÉ"
        assert "CAFÉ".lower() == "café"

    def test_unicode_isalpha(self):
        assert "中文".isalpha()
        assert "αβγ".isalpha()
