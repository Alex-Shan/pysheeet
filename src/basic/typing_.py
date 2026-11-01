"""Python Typing Examples

Source code for docs/notes/basic/python-typing.rst
"""

import pytest
from typing import (
    Optional,
    Union,
    Callable,
    TypeVar,
    Generic,
    Protocol,
    TypedDict,
    Literal,
    Final,
    ClassVar,
)


# 基本型 Types
def greet(name: str) -> str:
    """Function with type annotations."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


# Collection Types
def sum_list(numbers: list[int]) -> int:
    """Sum a list of integers."""
    return sum(numbers)


def get_value(data: dict[str, int], key: str) -> int | None:
    """Get value from dict."""
    return data.get(key)


# 可选和联合
def find_user(user_id: int) -> Optional[str]:
    """Return username or None."""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)


def process(value: int | str) -> str:
    """Process int or str."""
    return str(value)


# 可调用
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    """Apply function to arguments."""
    return func(a, b)


double: Callable[[int], int] = lambda x: x * 2


# TypeVar 和泛型
T = TypeVar("T")


def first(items: list[T]) -> T:
    """Return first item."""
    return items[0]


Number = TypeVar("Number", int, float)


def double_num(x: Number) -> Number:
    """Double a number."""
    return x * 2


# 通用 Class
class Stack(Generic[T]):
    """Generic stack class."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


# 协议
class Drawable(Protocol):
    """Protocol for drawable objects."""

    def draw(self) -> str: ...


class Circle:
    """Circle that implements Drawable."""

    def draw(self) -> str:
        return "Circle"


class Square:
    """Square that implements Drawable."""

    def draw(self) -> str:
        return "Square"


def render(shape: Drawable) -> str:
    """Render any drawable."""
    return shape.draw()


# 类型字典
class UserDict(TypedDict):
    """Typed dictionary for user data."""

    name: str
    age: int


# Literal
def set_status(status: Literal["active", "inactive"]) -> str:
    """Set status with literal type."""
    return f"Status: {status}"


# 最终的
MAX_SIZE: Final = 100


# 类变量
class Config:
    """Class with ClassVar."""

    debug: ClassVar[bool] = False
    name: str

    def __init__(self, name: str) -> None:
        self.name = name


# 测试
class TestBasicTypes:
    def test_greet(self):
        assert greet("World") == "Hello, World!"

    def test_add(self):
        assert add(2, 3) == 5


class TestCollections:
    def test_sum_list(self):
        assert sum_list([1, 2, 3, 4, 5]) == 15

    def test_get_value(self):
        assert get_value({"a": 1, "b": 2}, "a") == 1
        assert get_value({"a": 1}, "x") is None


class TestOptionalUnion:
    def test_find_user(self):
        assert find_user(1) == "Alice"
        assert find_user(999) is None

    def test_process(self):
        assert process(42) == "42"
        assert process("hello") == "hello"


class TestCallable:
    def test_apply(self):
        assert apply(lambda a, b: a + b, 2, 3) == 5

    def test_double(self):
        assert double(5) == 10


class TestGenerics:
    def test_first(self):
        assert first([1, 2, 3]) == 1
        assert first(["a", "b"]) == "a"

    def test_double_num(self):
        assert double_num(5) == 10
        assert double_num(2.5) == 5.0


class TestGenericClass:
    def test_stack(self):
        s: Stack[int] = Stack()
        s.push(1)
        s.push(2)
        assert s.pop() == 2
        assert s.pop() == 1
        assert s.is_empty()


class TestProtocol:
    def test_render(self):
        assert render(Circle()) == "Circle"
        assert render(Square()) == "Square"


class TestTypedDict:
    def test_user_dict(self):
        user: UserDict = {"name": "Alice", "age": 30}
        assert user["name"] == "Alice"
        assert user["age"] == 30


class TestLiteral:
    def test_set_status(self):
        assert set_status("active") == "Status: active"


class TestClassVar:
    def test_config(self):
        c = Config("test")
        assert c.name == "test"
        assert Config.debug is False
