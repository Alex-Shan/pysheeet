"""Python Future Examples

Source code for docs/notes/basic/python-future.rst
"""

from __future__ import annotations
import __future__
import sys
import pytest


# List 未来特性
def get_all_features() -> list[str]:
    """Get all available future features."""
    return __future__.all_feature_names


def get_feature_info(name: str) -> tuple:
    """Get feature info (optional, mandatory versions)."""
    feature = getattr(__future__, name, None)
    if feature:
        return (feature.optional, feature.mandatory)
    return None


# 注释示例
class Node:
    """Example using forward reference with annotations."""

    def __init__(self, value: int, next: Node | None = None):
        self.value = value
        self.next = next

    def append(self, value: int) -> Node:
        """Append value and return new node."""
        new_node = Node(value)
        self.next = new_node
        return new_node


def get_annotations(func) -> dict:
    """Get function annotations as strings."""
    return func.__annotations__


# 分配
def true_division(a: int, b: int) -> float:
    """True division (/)."""
    return a / b


def floor_division(a: int, b: int) -> int:
    """Floor division (//)."""
    return a // b


# 版本检查
def check_version(major: int, minor: int) -> bool:
    """Check if Python version is at least major.minor."""
    return sys.version_info >= (major, minor)


def get_version_string() -> str:
    """Get Python version as string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


# 测试
class TestFutureFeatures:
    def test_get_all_features(self):
        features = get_all_features()
        assert "annotations" in features
        assert "division" in features
        assert "print_function" in features

    def test_get_feature_info(self):
        info = get_feature_info("annotations")
        assert info is not None
        assert len(info) == 2


class TestAnnotations:
    def test_node_creation(self):
        node = Node(1)
        assert node.value == 1
        assert node.next is None

    def test_node_append(self):
        node = Node(1)
        node2 = node.append(2)
        assert node.next is node2
        assert node2.value == 2

    def test_annotations_are_strings(self):
        # 通过 from __future__ 导入注释，
        # 注释存储为 strings
        annotations = get_annotations(Node.__init__)
        assert "value" in annotations
        assert "next" in annotations


class TestDivision:
    def test_true_division(self):
        assert true_division(5, 2) == 2.5
        assert true_division(4, 2) == 2.0

    def test_floor_division(self):
        assert floor_division(5, 2) == 2
        assert floor_division(7, 3) == 2


class TestVersionCheck:
    def test_check_version(self):
        # 我们正在运行 Python 3.x
        assert check_version(3, 0)
        # 未来版本应该是False
        assert not check_version(99, 0)

    def test_get_version_string(self):
        version = get_version_string()
        assert version.startswith("3.")
        parts = version.split(".")
        assert len(parts) == 3
