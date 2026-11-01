"""New features in Python 3 (3.12 → 3.0)

Source code examples for docs/notes/python-new-py3.rst
"""

import sys
import asyncio
import pytest
from dataclasses import dataclass, FrozenInstanceError

PY_VERSION = sys.version_info[:2]


# Python 3.9 - Dictionary 合并 (PEP 584)
def dict_merge(a: dict, b: dict) -> dict:
    """Merge dicts with | operator."""
    return a | b


def dict_update(a: dict, b: dict) -> dict:
    """Update dict in place with |= operator."""
    a |= b
    return a


# Python 3.8 - 仅位置 parameters (PEP 570)
def positional_only(a, b, /, c, d):
    """a and b must be positional, c and d can be keyword."""
    return a + b + c + d


# Python 3.8 - 海象 operator (PEP 572)
def walrus_example(data: list):
    """Assignment expression in condition."""
    if (n := len(data)) > 3:
        return n
    return None


def walrus_fib(count: int) -> list:
    """Fibonacci using walrus operator."""
    f = (0, 1)
    return [(f := (f[1], sum(f)))[0] for _ in range(count)]


# Python 3.7 - 数据 Classes (PEP 557)
@dataclass
class Point:
    """Mutable dataclass."""

    x: int
    y: int


@dataclass(frozen=True)
class FrozenPoint:
    """Immutable dataclass."""

    x: int
    y: int


# Python 3.6 - f-string (PEP 498)
def fstring_basic(name: str) -> str:
    """Basic f-string interpolation."""
    return f"Hello, {name}!"


def fstring_format(value: float) -> str:
    """F-string with format spec."""
    return f"{value:1.3}"


# Python 3.5 - 异步/等待 (PEP 492)
async def async_greet() -> str:
    """Native coroutine syntax."""
    await asyncio.sleep(0.01)
    return "Hello"


# Python 3.5 - 一般拆箱 (PEP 448)
def general_unpacking() -> list:
    """Multiple unpacking in literals."""
    return [*range(3), 3, *range(4, 6)]


# Python 3.3 - (PEP 380) 的产量
def fib_gen(n: int):
    """Generator for fibonacci."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        b, a = a + b, b


def delegate_fib(n: int):
    """Delegate to subgenerator."""
    yield from fib_gen(n)


# Python 3.0 - 扩展拆包 (PEP 3132)
def extended_unpacking() -> tuple:
    """Star operator captures remaining items."""
    a, *b, c = range(5)
    return a, b, c


# Python 3.0 - 仅关键字 arguments (PEP 3102)
def keyword_only(a, b, *, kw):
    """kw must be passed as keyword argument."""
    return a, b, kw


# Python 3.0 - 非本地关键字 (PEP 3104)
def nonlocal_example() -> str:
    """Modify variable in enclosing scope."""
    outer = "original"

    def inner():
        nonlocal outer
        outer = "modified"

    inner()
    return outer


# 测试
@pytest.mark.skipif(PY_VERSION < (3, 12), reason="Requires Python 3.12+")
class TestPython312:
    def test_box_int(self):
        exec(
            "class Box[T]:\n    def __init__(self, item: T): self.item = item\nassert Box(42).item == 42"
        )

    def test_first(self):
        exec(
            "def first[T](items: list[T]) -> T: return items[0]\nassert first([1, 2, 3]) == 1"
        )

    def test_fstring_nested(self):
        songs = ["Take me back to Eden", "&", "Satellite"]
        result = eval('f"Playlist: {", ".join(songs)}"')
        assert "Playlist:" in result


@pytest.mark.skipif(PY_VERSION < (3, 11), reason="Requires Python 3.11+")
class TestPython311:
    def test_exception_group(self):
        code = """
caught_value = caught_type = False
try:
    raise ExceptionGroup("errors", [ValueError("invalid"), TypeError("wrong")])
except* ValueError:
    caught_value = True
except* TypeError:
    caught_type = True
assert caught_value and caught_type
"""
        exec(code)


@pytest.mark.skipif(PY_VERSION < (3, 10), reason="Requires Python 3.10+")
class TestPython310:
    def test_http_status(self):
        code = """
def http_status(status: int) -> str:
    match status:
        case 200: return "OK"
        case 404: return "Not Found"
        case 500: return "Internal Server Error"
        case _: return "Unknown"
assert http_status(200) == "OK"
assert http_status(404) == "Not Found"
assert http_status(999) == "Unknown"
"""
        exec(code)

    def test_describe_point(self):
        code = """
def describe_point(point: tuple) -> str:
    match point:
        case (0, 0): return "Origin"
        case (x, 0): return f"On x-axis at {x}"
        case (0, y): return f"On y-axis at {y}"
        case (x, y): return f"Point at ({x}, {y})"
assert describe_point((0, 0)) == "Origin"
assert describe_point((5, 0)) == "On x-axis at 5"
"""
        exec(code)


class TestPython39:
    def test_dict_merge(self):
        assert dict_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_dict_update(self):
        assert dict_update({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


class TestPython38:
    def test_positional_only(self):
        assert positional_only(1, 2, 3, 4) == 10
        assert positional_only(1, 2, c=3, d=4) == 10

    def test_walrus(self):
        assert walrus_example([1, 2, 3, 4, 5]) == 5
        assert walrus_example([1, 2]) is None

    def test_walrus_fib(self):
        assert walrus_fib(10) == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]


class TestPython37:
    def test_dataclass(self):
        assert Point(1, 2) == Point(1, 2)

    def test_frozen_dataclass(self):
        with pytest.raises(FrozenInstanceError):
            FrozenPoint(1, 2).x = 3


class TestPython36:
    def test_fstring_basic(self):
        assert fstring_basic("World") == "Hello, World!"

    def test_fstring_format(self):
        assert fstring_format(123.567) == "1.24e+02"


class TestPython35:
    def test_async_greet(self):
        assert asyncio.run(async_greet()) == "Hello"

    def test_general_unpacking(self):
        assert general_unpacking() == [0, 1, 2, 3, 4, 5]


class TestPython33:
    def test_delegate_fib(self):
        assert list(delegate_fib(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


class TestPython30:
    def test_extended_unpacking(self):
        assert extended_unpacking() == (0, [1, 2, 3], 4)

    def test_keyword_only(self):
        assert keyword_only(1, 2, kw=3) == (1, 2, 3)

    def test_nonlocal(self):
        assert nonlocal_example() == "modified"
