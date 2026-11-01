"""Python Dictionary Examples

Source code for docs/notes/basic/python-dict.rst
"""

import pytest
from collections import defaultdict, OrderedDict
from functools import lru_cache


# 创建 Dictionary
def create_dict_literal():
    """Create dict using literal syntax."""
    return {"key": "value", "num": 42}


def create_dict_constructor():
    """Create dict using constructor."""
    return dict(key="value", num=42)


def create_dict_comprehension(n: int) -> dict:
    """Create dict using comprehension."""
    return {x: x**2 for x in range(n)}


# 获取 Keys、Values、Items
def get_keys(d: dict) -> list:
    """Get all keys from dictionary."""
    return list(d.keys())


def get_values(d: dict) -> list:
    """Get all values from dictionary."""
    return list(d.values())


def get_items(d: dict) -> list:
    """Get all key-value pairs."""
    return list(d.items())


# 查找常见的 Keys
def find_common_keys(a: dict, b: dict) -> set:
    """Find keys that exist in both dictionaries."""
    return a.keys() & b.keys()


# Set 默认 Value
def setdefault_example():
    """Use setdefault to initialize missing keys."""
    d = {}
    d.setdefault("key", []).append("value")
    return d


def defaultdict_example():
    """Use defaultdict for automatic default values."""
    d = defaultdict(list)
    d["key"].append("value")
    return dict(d)


# 合并Dictionaries
def merge_dicts_operator(a: dict, b: dict) -> dict:
    """Merge dicts using | operator (Python 3.9+)."""
    return a | b


def merge_dicts_unpack(a: dict, b: dict) -> dict:
    """Merge dicts using unpacking (Python 3.5+)."""
    return {**a, **b}


# Dictionary Comprehension
def dict_comprehension_filter(n: int) -> dict:
    """Dict comprehension with filter."""
    return {x: x**2 for x in range(n) if x % 2 == 0}


def swap_keys_values(d: dict) -> dict:
    """Swap dictionary keys and values."""
    return {v: k for k, v in d.items()}


# 模拟 Dictionary
class EmuDict:
    """Custom dictionary-like class."""

    def __init__(self, data=None):
        self._dict = data or {}

    def __repr__(self):
        return f"EmuDict({self._dict})"

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, val):
        self._dict[key] = val

    def __delitem__(self, key):
        del self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)


# LRU Cache
class LRUCache:
    """LRU Cache implementation using OrderedDict."""

    def __init__(self, maxsize=128):
        self._maxsize = maxsize
        self._cache = OrderedDict()

    def get(self, key):
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Fibonacci with LRU cache decorator."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 测试
class TestDictCreation:
    def test_literal(self):
        assert create_dict_literal() == {"key": "value", "num": 42}

    def test_constructor(self):
        assert create_dict_constructor() == {"key": "value", "num": 42}

    def test_comprehension(self):
        assert create_dict_comprehension(3) == {0: 0, 1: 1, 2: 4}


class TestDictAccess:
    def test_get_keys(self):
        assert get_keys({"a": 1, "b": 2}) == ["a", "b"]

    def test_get_values(self):
        assert get_values({"a": 1, "b": 2}) == [1, 2]

    def test_get_items(self):
        assert get_items({"a": 1}) == [("a", 1)]


class TestDictOperations:
    def test_find_common_keys(self):
        assert find_common_keys({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {"b"}

    def test_setdefault(self):
        assert setdefault_example() == {"key": ["value"]}

    def test_defaultdict(self):
        assert defaultdict_example() == {"key": ["value"]}

    def test_merge_operator(self):
        assert merge_dicts_operator({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_merge_unpack(self):
        assert merge_dicts_unpack({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


class TestDictComprehension:
    def test_filter(self):
        assert dict_comprehension_filter(6) == {0: 0, 2: 4, 4: 16}

    def test_swap(self):
        assert swap_keys_values({"a": 1, "b": 2}) == {1: "a", 2: "b"}


class TestEmuDict:
    def test_getitem(self):
        d = EmuDict({"a": 1})
        assert d["a"] == 1

    def test_setitem(self):
        d = EmuDict()
        d["a"] = 1
        assert d["a"] == 1

    def test_contains(self):
        d = EmuDict({"a": 1})
        assert "a" in d
        assert "b" not in d

    def test_len(self):
        assert len(EmuDict({"a": 1, "b": 2})) == 2


class TestLRUCache:
    def test_get_put(self):
        cache = LRUCache(maxsize=2)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") == 1

    def test_eviction(self):
        cache = LRUCache(maxsize=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # 驱逐 "a"
        assert cache.get("a") is None

    def test_fibonacci(self):
        assert fibonacci(10) == 55
        assert fibonacci(20) == 6765
