"""Python Set Examples

Source code for docs/notes/basic/python-set.rst
"""

import pytest


# 创建 Set
def create_set_literal():
    """Create set using literal syntax."""
    return {1, 2, 3}


def create_set_from_list(items: list) -> set:
    """Create set from list, removing duplicates."""
    return set(items)


def create_empty_set() -> set:
    """Create empty set."""
    return set()


# Set Comprehension
def set_comprehension_basic(items: list) -> set:
    """Basic set comprehension."""
    return {x for x in items}


def set_comprehension_filter(items: list, threshold: int) -> set:
    """Set comprehension with filter."""
    return {x for x in items if x > threshold}


def set_comprehension_squares(n: int) -> set:
    """Set of squares."""
    return {x**2 for x in range(n)}


# 统一
def uniquify_list(items: list) -> list:
    """Remove duplicates from list."""
    return list(set(items))


def uniquify_preserve_order(items: list) -> list:
    """Remove duplicates preserving order (Python 3.7+)."""
    return list(dict.fromkeys(items))


# 添加Items
def add_single(s: set, item) -> set:
    """Add single item to set."""
    s.add(item)
    return s


def add_multiple(s: set, items) -> set:
    """Add multiple items to set."""
    s.update(items)
    return s


# 删除 Items
def remove_item(s: set, item) -> set:
    """Remove item from set (raises KeyError if missing)."""
    s.remove(item)
    return s


def discard_item(s: set, item) -> set:
    """Remove item from set (no error if missing)."""
    s.discard(item)
    return s


def pop_item(s: set):
    """Remove and return arbitrary item."""
    return s.pop()


# Set 操作
def union(a: set, b: set) -> set:
    """Union of two sets."""
    return a | b


def intersection(a: set, b: set) -> set:
    """Intersection of two sets."""
    return a & b


def difference(a: set, b: set) -> set:
    """Difference of two sets (a - b)."""
    return a - b


def symmetric_difference(a: set, b: set) -> set:
    """Symmetric difference of two sets."""
    return a ^ b


def is_subset(a: set, b: set) -> bool:
    """Check if a is subset of b."""
    return a <= b


def is_proper_subset(a: set, b: set) -> bool:
    """Check if a is proper subset of b."""
    return a < b


def is_superset(a: set, b: set) -> bool:
    """Check if a is superset of b."""
    return a >= b


def is_disjoint(a: set, b: set) -> bool:
    """Check if sets have no common elements."""
    return a.isdisjoint(b)


# 会员资格
def membership_test(s: set, item) -> bool:
    """Test if item is in set."""
    return item in s


# Frozenset
def create_frozenset(items: list) -> frozenset:
    """Create immutable frozenset."""
    return frozenset(items)


def frozenset_as_dict_key():
    """Use frozenset as dictionary key."""
    return {frozenset([1, 2]): "a", frozenset([3, 4]): "b"}


def frozenset_in_set():
    """Use frozenset as set element."""
    return {frozenset([1, 2]), frozenset([3, 4])}


# 测试
class TestSetCreation:
    def test_literal(self):
        assert create_set_literal() == {1, 2, 3}

    def test_from_list(self):
        assert create_set_from_list([1, 2, 2, 3]) == {1, 2, 3}

    def test_empty(self):
        assert create_empty_set() == set()
        assert len(create_empty_set()) == 0


class TestSetComprehension:
    def test_basic(self):
        assert set_comprehension_basic([1, 2, 2, 3]) == {1, 2, 3}

    def test_filter(self):
        assert set_comprehension_filter([1, 2, 3, 4, 5], 3) == {4, 5}

    def test_squares(self):
        assert set_comprehension_squares(5) == {0, 1, 4, 9, 16}


class TestUniquify:
    def test_uniquify(self):
        result = uniquify_list([1, 2, 2, 3, 3, 3])
        assert set(result) == {1, 2, 3}

    def test_preserve_order(self):
        assert uniquify_preserve_order([3, 1, 2, 1, 3]) == [3, 1, 2]


class TestAddRemove:
    def test_add_single(self):
        s = {1, 2}
        assert add_single(s, 3) == {1, 2, 3}

    def test_add_multiple(self):
        s = {1, 2}
        assert add_multiple(s, [3, 4]) == {1, 2, 3, 4}

    def test_remove(self):
        s = {1, 2, 3}
        assert remove_item(s, 2) == {1, 3}

    def test_remove_missing(self):
        s = {1, 2, 3}
        with pytest.raises(KeyError):
            remove_item(s, 10)

    def test_discard(self):
        s = {1, 2, 3}
        assert discard_item(s, 2) == {1, 3}
        assert discard_item(s, 10) == {1, 3}  # 没有错误

    def test_pop(self):
        s = {1, 2, 3}
        item = pop_item(s)
        assert item in {1, 2, 3}
        assert len(s) == 2


class TestSetOperations:
    def test_union(self):
        assert union({1, 2}, {2, 3}) == {1, 2, 3}

    def test_intersection(self):
        assert intersection({1, 2, 3}, {2, 3, 4}) == {2, 3}

    def test_difference(self):
        assert difference({1, 2, 3}, {2, 3, 4}) == {1}

    def test_symmetric_difference(self):
        assert symmetric_difference({1, 2, 3}, {2, 3, 4}) == {1, 4}

    def test_subset(self):
        assert is_subset({1, 2}, {1, 2, 3})
        assert is_subset({1, 2}, {1, 2})  # 相等是子集
        assert not is_subset({1, 2, 3}, {1, 2})

    def test_proper_subset(self):
        assert is_proper_subset({1, 2}, {1, 2, 3})
        assert not is_proper_subset({1, 2}, {1, 2})  # 平等是不恰当的

    def test_superset(self):
        assert is_superset({1, 2, 3}, {1, 2})
        assert not is_superset({1, 2}, {1, 2, 3})

    def test_disjoint(self):
        assert is_disjoint({1, 2}, {3, 4})
        assert not is_disjoint({1, 2}, {2, 3})


class TestMembership:
    def test_in(self):
        assert membership_test({1, 2, 3}, 2)
        assert not membership_test({1, 2, 3}, 10)


class TestFrozenset:
    def test_create(self):
        fs = create_frozenset([1, 2, 2, 3])
        assert fs == frozenset({1, 2, 3})

    def test_immutable(self):
        fs = create_frozenset([1, 2, 3])
        assert not hasattr(fs, "add")

    def test_as_dict_key(self):
        d = frozenset_as_dict_key()
        assert d[frozenset([1, 2])] == "a"

    def test_in_set(self):
        s = frozenset_in_set()
        assert frozenset([1, 2]) in s
        assert frozenset([5, 6]) not in s
