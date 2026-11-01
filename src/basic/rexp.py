"""Python Regular Expression Examples

Source code for docs/notes/basic/python-rexp.rst
"""

import re
from collections import namedtuple

import pytest


# 基本搭配
def search_pattern(pattern: str, text: str) -> str | None:
    """Find first match of pattern in text."""
    m = re.search(pattern, text)
    return m.group() if m else None


def match_start(pattern: str, text: str) -> bool:
    """Check if text starts with pattern."""
    return re.match(pattern, text) is not None


def fullmatch(pattern: str, text: str) -> bool:
    """Check if entire text matches pattern."""
    return re.fullmatch(pattern, text) is not None


# 查找全部
def find_all(pattern: str, text: str) -> list:
    """Find all matches of pattern."""
    return re.findall(pattern, text)


def find_all_groups(pattern: str, text: str) -> list:
    """Find all matches with groups."""
    return re.findall(pattern, text)


# 分裂
def split_pattern(pattern: str, text: str) -> list:
    """Split text by pattern."""
    return re.split(pattern, text)


# 团体
def parse_date(text: str) -> dict | None:
    """Parse date string into components."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return {"year": m.group(1), "month": m.group(2), "day": m.group(3)}
    return None


def parse_date_named(text: str) -> dict | None:
    """Parse date using named groups."""
    pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    m = re.search(pattern, text)
    return m.groupdict() if m else None


# 非捕获组
def parse_url(url: str) -> tuple | None:
    """Parse URL with non-capturing group for protocol."""
    m = re.search(r"(?:https?|ftp)://([^/\r\n]+)(/[^\r\n]*)?", url)
    return m.groups() if m else None


# 向后参考
def has_repeated_char(text: str) -> bool:
    """Check if text has repeated adjacent characters."""
    return re.search(r"(\w)\1", text) is not None


def match_html_tag(text: str) -> str | None:
    """Match HTML tag with matching close tag."""
    m = re.search(r"<(\w+)>[^<]*</\1>", text)
    return m.group() if m else None


# 前瞻/后瞻
def find_before_at(text: str) -> list:
    """Find words before @ symbol (positive lookahead)."""
    return re.findall(r"\w+(?=@)", text)


def find_after_dollar(text: str) -> list:
    """Find numbers after $ symbol (positive lookbehind)."""
    return re.findall(r"(?<=\$)\d+", text)


def find_not_followed_by(text: str, suffix: str) -> list:
    """Find digits not followed by suffix (negative lookahead)."""
    return re.findall(rf"\d+(?!{suffix})", text)


# 替代
def replace_pattern(pattern: str, repl: str, text: str) -> str:
    """Replace pattern with replacement."""
    return re.sub(pattern, repl, text)


def double_numbers(text: str) -> str:
    """Double all numbers in text using function replacement."""
    return re.sub(r"\d+", lambda m: str(int(m.group()) * 2), text)


def camel_to_snake(s: str) -> str:
    """Convert CamelCase to snake_case."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", s).lower()


# 编译模式
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
MAC_PATTERN = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", re.I)
URL_PATTERN = re.compile(
    r"^(https?://)?([\da-z.-]+)\.([a-z.]{2,6})([/\w.-]*)*/?$", re.I
)
HEX_COLOR_PATTERN = re.compile(r"^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$")
PHONE_PATTERN = re.compile(
    r"^(\+1)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
)
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


def is_valid_email(text: str) -> bool:
    """Validate email address."""
    return EMAIL_PATTERN.match(text) is not None


def is_valid_ip(text: str) -> bool:
    """Validate IPv4 address."""
    return IP_PATTERN.match(text) is not None


def is_valid_mac(text: str) -> bool:
    """Validate MAC address."""
    return MAC_PATTERN.match(text) is not None


def is_valid_url(text: str) -> bool:
    """Validate URL."""
    return URL_PATTERN.match(text) is not None


def is_valid_hex_color(text: str) -> bool:
    """Validate hex color code."""
    return HEX_COLOR_PATTERN.match(text) is not None


def is_valid_phone(text: str) -> bool:
    """Validate US phone number."""
    return PHONE_PATTERN.match(text) is not None


def is_strong_password(text: str) -> bool:
    """Validate password strength."""
    return PASSWORD_PATTERN.match(text) is not None


# HTML标签
def find_open_tags(html: str) -> list:
    """Find all open tags."""
    return re.findall(r"<[^/>][^>]*>", html)


def find_close_tags(html: str) -> list:
    """Find all close tags."""
    return re.findall(r"</[^>]+>", html)


def strip_html_tags(html: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r"<[^>]+>", "", html)


# 词法分析器
Token = namedtuple("Token", ["type", "value"])


def tokenize(text: str) -> list:
    """Tokenize arithmetic expression."""
    tokens = [
        r"(?P<NUMBER>\d+)",
        r"(?P<PLUS>\+)",
        r"(?P<MINUS>-)",
        r"(?P<TIMES>\*)",
        r"(?P<DIVIDE>/)",
        r"(?P<WS>\s+)",
    ]
    lex = re.compile("|".join(tokens))
    scan = lex.scanner(text)
    return [
        Token(m.lastgroup, m.group())
        for m in iter(scan.match, None)
        if m.lastgroup != "WS"
    ]


# 实用程序 functions
def find_hashtags(text: str) -> list:
    """Find all hashtags in text."""
    return re.findall(r"#\w+", text)


def find_mentions(text: str) -> list:
    """Find all @mentions in text."""
    return re.findall(r"@\w+", text)


def extract_domain(url: str) -> str | None:
    """Extract domain from URL."""
    m = re.search(r"https?://([^/]+)", url)
    return m.group(1) if m else None


# 测试
class TestBasicMatching:
    def test_search(self):
        assert search_pattern(r"\d+", "abc123def") == "123"
        assert search_pattern(r"\d+", "no digits") is None

    def test_match_start(self):
        assert match_start(r"\d+", "123abc")
        assert not match_start(r"\d+", "abc123")

    def test_fullmatch(self):
        assert fullmatch(r"\d+", "123")
        assert not fullmatch(r"\d+", "123abc")


class TestFindAll:
    def test_find_all(self):
        assert find_all(r"\d+", "a1b22c333") == ["1", "22", "333"]

    def test_find_all_groups(self):
        assert find_all_groups(r"(\w+)=(\d+)", "a=1 b=2") == [
            ("a", "1"),
            ("b", "2"),
        ]


class TestSplit:
    def test_split(self):
        assert split_pattern(r"\s+", "a  b   c") == ["a", "b", "c"]
        assert split_pattern(r"[,;]", "a,b;c") == ["a", "b", "c"]


class TestGroups:
    def test_parse_date(self):
        result = parse_date("2024-01-15")
        assert result == {"year": "2024", "month": "01", "day": "15"}

    def test_parse_date_named(self):
        result = parse_date_named("2024-01-15")
        assert result == {"year": "2024", "month": "01", "day": "15"}

    def test_parse_url(self):
        assert parse_url("http://example.com/path") == ("example.com", "/path")


class TestBackReference:
    def test_repeated_char(self):
        assert has_repeated_char("hello")  # 二
        assert not has_repeated_char("world")

    def test_html_tag(self):
        assert match_html_tag("<b>bold</b>") == "<b>bold</b>"
        assert match_html_tag("<b>text</i>") is None


class TestLookaround:
    def test_lookahead(self):
        assert find_before_at("user@example.com") == ["user"]

    def test_lookbehind(self):
        assert find_after_dollar("$100 $200") == ["100", "200"]

    def test_negative_lookahead(self):
        assert find_not_followed_by("12px 34em 56", "px") == ["1", "34", "56"]


class TestSubstitution:
    def test_replace(self):
        assert replace_pattern(r"\d+", "X", "a1b2c3") == "aXbXcX"

    def test_double_numbers(self):
        assert double_numbers("a1b2c3") == "a2b4c6"

    def test_camel_to_snake(self):
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("SimpleHTTPServer") == "simple_http_server"


class TestValidation:
    def test_email(self):
        assert is_valid_email("user@example.com")
        assert is_valid_email("user+tag@sub.domain.org")
        assert not is_valid_email("invalid@")

    def test_ip(self):
        assert is_valid_ip("192.168.1.1")
        assert is_valid_ip("255.255.255.0")
        assert not is_valid_ip("256.0.0.0")

    def test_mac(self):
        assert is_valid_mac("3c:38:51:05:03:1e")
        assert is_valid_mac("AA:BB:CC:DD:EE:FF")

    def test_url(self):
        assert is_valid_url("https://www.example.com/path")
        assert is_valid_url("example.com")

    def test_hex_color(self):
        assert is_valid_hex_color("#ffffff")
        assert is_valid_hex_color("fff")
        assert not is_valid_hex_color("#gggggg")

    def test_phone(self):
        assert is_valid_phone("123-456-7890")
        assert is_valid_phone("(123) 456-7890")

    def test_password(self):
        assert is_strong_password("Passw0rd!")
        assert not is_strong_password("weakpass")


class TestHtmlTags:
    def test_open_tags(self):
        assert "<table>" in find_open_tags("<table><tr></tr></table>")

    def test_close_tags(self):
        assert "</table>" in find_close_tags("<table></table>")

    def test_strip_tags(self):
        assert strip_html_tags("<p>Hello</p>") == "Hello"


class TestLexer:
    def test_tokenize(self):
        tokens = tokenize("9 + 5 * 2")
        assert tokens[0] == Token("NUMBER", "9")
        assert tokens[1] == Token("PLUS", "+")
        assert tokens[2] == Token("NUMBER", "5")


class TestUtility:
    def test_hashtags(self):
        assert find_hashtags("Hello #world #python") == ["#world", "#python"]

    def test_mentions(self):
        assert find_mentions("Hello @user @admin") == ["@user", "@admin"]

    def test_extract_domain(self):
        assert (
            extract_domain("https://www.example.com/path") == "www.example.com"
        )
