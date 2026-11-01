"""Python Basics Examples

Source code for docs/notes/basic/python-basic.rst
"""

import sys
import platform
import pytest


# Python版本
def get_version_info() -> tuple:
    """Get Python version info."""
    return sys.version_info[:3]


def get_version_string() -> str:
    """Get Python version as string."""
    return platform.python_version()


def check_version(major: int, minor: int) -> bool:
    """Check if Python version is at least major.minor."""
    return sys.version_info >= (major, minor)


# 控制流程
def classify_number(x: int) -> str:
    """Classify number as negative, zero, or positive."""
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    else:
        return "positive"


def is_even(x: int) -> bool:
    """Check if number is even using ternary."""
    return True if x % 2 == 0 else False


# Loops
def sum_range(n: int) -> int:
    """Sum numbers from 0 to n-1."""
    total = 0
    for i in range(n):
        total += i
    return total


def find_first_even(numbers: list) -> int | None:
    """Find first even number, demonstrating break."""
    for n in numbers:
        if n % 2 == 0:
            return n
    return None


def sum_odd_only(numbers: list) -> int:
    """Sum only odd numbers, demonstrating continue."""
    total = 0
    for n in numbers:
        if n % 2 == 0:
            continue
        total += n
    return total


def loop_completed(items: list, target) -> bool:
    """Check if loop completed without finding target (for-else)."""
    for item in items:
        if item == target:
            return False
    return True


# Exception 搬运
def safe_divide(a: float, b: float) -> float | None:
    """Divide with exception handling."""
    try:
        return a / b
    except ZeroDivisionError:
        return None


def parse_int(s: str) -> int | None:
    """Parse string to int with error handling."""
    try:
        return int(s)
    except ValueError:
        return None


def divide_or_raise(a: float, b: float) -> float:
    """Divide or raise ValueError."""
    if b == 0:
        raise ValueError("divisor cannot be zero")
    return a / b


# Comprehensions
def squares(n: int) -> list:
    """List of squares using comprehension."""
    return [x**2 for x in range(n)]


def even_numbers(n: int) -> list:
    """Even numbers using comprehension with filter."""
    return [x for x in range(n) if x % 2 == 0]


def square_dict(n: int) -> dict:
    """Dict comprehension."""
    return {x: x**2 for x in range(n)}


# 真实性
def is_truthy(value) -> bool:
    """Check if value is truthy."""
    return bool(value)


# 多重作业
def swap(a, b) -> tuple:
    """Swap two values."""
    return b, a


def first_and_rest(items: list) -> tuple:
    """Split into first and rest."""
    first, *rest = items
    return first, rest


# 测试
class TestVersion:
    def test_get_version_info(self):
        info = get_version_info()
        assert len(info) == 3
        assert info[0] >= 3

    def test_check_version(self):
        assert check_version(3, 0)
        assert not check_version(99, 0)


class TestControlFlow:
    def test_classify_number(self):
        assert classify_number(-5) == "negative"
        assert classify_number(0) == "zero"
        assert classify_number(5) == "positive"

    def test_is_even(self):
        assert is_even(4)
        assert not is_even(3)


class TestLoops:
    def test_sum_range(self):
        assert sum_range(5) == 10  # 0+1+2+3+4

    def test_find_first_even(self):
        assert find_first_even([1, 3, 4, 6]) == 4
        assert find_first_even([1, 3, 5]) is None

    def test_sum_odd_only(self):
        assert sum_odd_only([1, 2, 3, 4, 5]) == 9  # 1+3+5

    def test_loop_completed(self):
        assert loop_completed([1, 2, 3], 5)
        assert not loop_completed([1, 2, 3], 2)


class TestExceptions:
    def test_safe_divide(self):
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) is None

    def test_parse_int(self):
        assert parse_int("42") == 42
        assert parse_int("abc") is None

    def test_divide_or_raise(self):
        assert divide_or_raise(10, 2) == 5.0
        with pytest.raises(ValueError):
            divide_or_raise(10, 0)


class TestComprehensions:
    def test_squares(self):
        assert squares(5) == [0, 1, 4, 9, 16]

    def test_even_numbers(self):
        assert even_numbers(10) == [0, 2, 4, 6, 8]

    def test_square_dict(self):
        assert square_dict(3) == {0: 0, 1: 1, 2: 4}


class TestTruthiness:
    def test_falsy(self):
        assert not is_truthy(None)
        assert not is_truthy(0)
        assert not is_truthy("")
        assert not is_truthy([])

    def test_truthy(self):
        assert is_truthy(1)
        assert is_truthy("text")
        assert is_truthy([1])


class TestAssignment:
    def test_swap(self):
        assert swap(1, 2) == (2, 1)

    def test_first_and_rest(self):
        first, rest = first_and_rest([1, 2, 3, 4])
        assert first == 1
        assert rest == [2, 3, 4]
