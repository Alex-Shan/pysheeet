"""Python List Examples

Source code for docs/notes/basic/python-list.rst
"""

import bisect
import copy
import itertools
from collections import defaultdict, deque
from functools import reduce

import pytest


# 初始化
def init_immutable(n: int) -> list:
    """Initialize list with immutable objects."""
    return [0] * n


def init_mutable(n: int) -> list:
    """Initialize list with mutable objects (correct way)."""
    return [[] for _ in range(n)]


# 复制
def shallow_copy(lst: list) -> list:
    """Create shallow copy of list."""
    return lst.copy()


def deep_copy(lst: list) -> list:
    """Create deep copy of nested list."""
    return copy.deepcopy(lst)


# List Comprehensions
def squares(n: int) -> list:
    """List of squares."""
    return [x**2 for x in range(n)]


def filter_even(nums: list) -> list:
    """Filter even numbers."""
    return [x for x in nums if x % 2 == 0]


def flatten(nested: list) -> list:
    """Flatten nested list."""
    return [x for sublist in nested for x in sublist]


# 开箱
def extended_unpack(lst: list) -> tuple:
    """Extended unpacking with *."""
    first, *middle, last = lst
    return first, middle, last


# Enumerate 和 Zip
def enumerate_example(items: list) -> list:
    """Enumerate with index."""
    return [(i, v) for i, v in enumerate(items)]


def zip_to_dict(keys: list, values: list) -> dict:
    """Create dict from two lists."""
    return dict(zip(keys, values))


def unzip(pairs: list) -> tuple:
    """Unzip list of pairs."""
    return tuple(zip(*pairs))


# 排序
def sort_by_key(items: list, key_func) -> list:
    """Sort by custom key."""
    return sorted(items, key=key_func)


def sort_dicts(dicts: list, key: str) -> list:
    """Sort list of dicts by key."""
    return sorted(dicts, key=lambda x: x[key])


# Stack
class Stack:
    """Stack implementation using list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1] if self._items else None

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


# 测试
class TestInitialize:
    def test_immutable(self):
        a = init_immutable(3)
        a[0] = 1
        assert a == [1, 0, 0]

    def test_mutable(self):
        a = init_mutable(3)
        a[0].append(1)
        assert a == [[1], [], []]


class TestCopy:
    def test_shallow(self):
        a = [1, 2, 3]
        b = shallow_copy(a)
        b[0] = 99
        assert a == [1, 2, 3]

    def test_deep(self):
        a = [[1, 2], [3, 4]]
        b = deep_copy(a)
        b[0][0] = 99
        assert a == [[1, 2], [3, 4]]


class TestComprehensions:
    def test_squares(self):
        assert squares(5) == [0, 1, 4, 9, 16]

    def test_filter_even(self):
        assert filter_even([1, 2, 3, 4, 5, 6]) == [2, 4, 6]

    def test_flatten(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]


class TestUnpacking:
    def test_extended(self):
        first, middle, last = extended_unpack([1, 2, 3, 4, 5])
        assert first == 1
        assert middle == [2, 3, 4]
        assert last == 5


class TestEnumerateZip:
    def test_enumerate(self):
        assert enumerate_example(["a", "b"]) == [(0, "a"), (1, "b")]

    def test_zip_to_dict(self):
        assert zip_to_dict(["a", "b"], [1, 2]) == {"a": 1, "b": 2}

    def test_unzip(self):
        nums, chars = unzip([(1, "a"), (2, "b")])
        assert nums == (1, 2)
        assert chars == ("a", "b")


class TestSorting:
    def test_sort_by_key(self):
        assert sort_by_key(["bb", "a", "ccc"], len) == ["a", "bb", "ccc"]

    def test_sort_dicts(self):
        data = [{"n": 2}, {"n": 1}]
        assert sort_dicts(data, "n") == [{"n": 1}, {"n": 2}]


class TestStack:
    def test_push_pop(self):
        s = Stack()
        s.push(1)
        s.push(2)
        assert s.pop() == 2
        assert s.pop() == 1

    def test_peek(self):
        s = Stack()
        s.push(1)
        assert s.peek() == 1
        assert len(s) == 1

    def test_is_empty(self):
        s = Stack()
        assert s.is_empty()
        s.push(1)
        assert not s.is_empty()


# 二等分 - 维护排序 List
def bisect_insort(items: list) -> list:
    """Insert items maintaining sorted order."""
    result = []
    for x in items:
        bisect.insort(result, x)
    return result


def bisect_left_example(lst: list, x) -> int:
    """Find lower bound position."""
    return bisect.bisect_left(lst, x)


def bisect_right_example(lst: list, x) -> int:
    """Find upper bound position."""
    return bisect.bisect_right(lst, x)


def binary_search(arr: list, x, lo: int = 0, hi: int = None) -> int:
    """Binary search in sorted list."""
    if hi is None:
        hi = len(arr)
    pos = bisect.bisect_left(arr, x, lo, hi)
    return pos if pos != hi and arr[pos] == x else -1


# 嵌套 Lists
def create_2d_list(rows: int, cols: int) -> list:
    """Create 2D list correctly."""
    return [[0] * cols for _ in range(rows)]


# Deque - 圆形 Buffer
def circular_buffer(items: list, maxlen: int) -> deque:
    """Create circular buffer with deque."""
    d = deque(maxlen=maxlen)
    for x in items:
        d.append(x)
    return d


# 块 List
def chunk(lst: list, n: int) -> list:
    """Split list into chunks of size n."""
    return [lst[i : i + n] for i in range(0, len(lst), n)]


# Groupby
def groupby_example(s: str) -> list:
    """Group consecutive elements."""
    return [(k, list(v)) for k, v in itertools.groupby(s)]


# 特里树
def create_trie(words: list) -> dict:
    """Create trie from list of words."""
    Trie = lambda: defaultdict(Trie)
    trie = Trie()
    end = True
    for word in words:
        reduce(dict.__getitem__, word, trie)[end] = word
    return trie


def trie_has_prefix(trie: dict, prefix: str) -> bool:
    """Check if trie has prefix."""
    curr = trie
    for c in prefix:
        if c not in curr:
            return False
        curr = curr[c]
    return True


class TestBisect:
    def test_insort(self):
        assert bisect_insort([3, 1, 2, 0]) == [0, 1, 2, 3]

    def test_bisect_left(self):
        a = [1, 2, 3, 3, 4, 5]
        assert bisect_left_example(a, 3) == 2

    def test_bisect_right(self):
        a = [1, 2, 3, 3, 4, 5]
        assert bisect_right_example(a, 3) == 4

    def test_binary_search(self):
        a = [1, 1, 1, 2, 3]
        assert binary_search(a, 1) == 0
        assert binary_search(a, 2) == 3
        assert binary_search(a, 99) == -1


class TestNestedLists:
    def test_create_2d(self):
        grid = create_2d_list(2, 3)
        grid[0][0] = 1
        assert grid == [[1, 0, 0], [0, 0, 0]]


class TestDeque:
    def test_circular_buffer(self):
        d = circular_buffer(range(5), 3)
        assert list(d) == [2, 3, 4]


class TestChunk:
    def test_chunk(self):
        assert chunk([1, 2, 3, 4, 5, 6, 7, 8], 3) == [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8],
        ]


class TestGroupby:
    def test_groupby(self):
        result = groupby_example("AAABBC")
        assert result == [
            ("A", ["A", "A", "A"]),
            ("B", ["B", "B"]),
            ("C", ["C"]),
        ]


class TestTrie:
    def test_create_and_search(self):
        trie = create_trie(["abc", "de", "g"])
        assert trie_has_prefix(trie, "ab")
        assert trie_has_prefix(trie, "abc")
        assert not trie_has_prefix(trie, "xyz")
