"""Python OOP Examples

Source code for docs/notes/basic/python-object.rst
"""

from abc import ABC, abstractmethod
from functools import total_ordering

import pytest


# 基本型 Class
class Person:
    """Basic class with __init__."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"


# Class 和 Instance Attributes
class Counter:
    """Class with class and instance attributes."""

    count = 0

    def __init__(self):
        Counter.count += 1
        self.id = Counter.count


# Inheritance
class Animal:
    """Base class for inheritance."""

    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says Meow!"


# Magic Methods - 再现和 str
class Vector:
    """Class with magic methods."""

    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# 与total_ordering的比较
@total_ordering
class Number:
    """Class with comparison methods."""

    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        return self.val == other.val

    def __lt__(self, other):
        return self.val < other.val


# 可调用
class Multiplier:
    """Callable class."""

    def __init__(self, factor: int):
        self.factor = factor

    def __call__(self, x: int) -> int:
        return x * self.factor


# Property
class Circle:
    """Class with property."""

    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value

    @property
    def area(self) -> float:
        return 3.14159 * self._radius**2


# 描述符
class Positive:
    """Descriptor that enforces positive values."""

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError("Must be positive")
        obj.__dict__[self.name] = value


class DescriptorExample:
    x = Positive("x")

    def __init__(self, x):
        self.x = x


# Context Manager
class ManagedResource:
    """Context manager class."""

    def __init__(self):
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False


# 辛格尔顿
class Singleton:
    """Singleton pattern."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


# Class Methods 和 Static Methods
class Date:
    """Class with classmethod and staticmethod."""

    def __init__(self, year: int, month: int, day: int):
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, date_string: str):
        year, month, day = map(int, date_string.split("-"))
        return cls(year, month, day)

    @staticmethod
    def is_valid(date_string: str) -> bool:
        try:
            year, month, day = map(int, date_string.split("-"))
            return 1 <= month <= 12 and 1 <= day <= 31
        except Exception:
            return False


# Abstract Base Class
class Shape(ABC):
    """Abstract base class."""

    @abstractmethod
    def area(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width, self.height = width, height

    def area(self) -> float:
        return self.width * self.height


# MRO - 钻石问题
class A:
    def method(self):
        return "A"


class B(A):
    def method(self):
        return "B"


class C(A):
    def method(self):
        return "C"


class D(B, C):
    pass


# 老虎机
class PointWithSlots:
    """Class with __slots__ for memory efficiency."""

    __slots__ = ["x", "y"]

    def __init__(self, x, y):
        self.x, self.y = x, y


# 测试
class TestBasicClass:
    def test_person(self):
        p = Person("Alice", 30)
        assert p.name == "Alice"
        assert p.greet() == "Hello, I'm Alice"


class TestClassAttributes:
    def test_counter(self):
        Counter.count = 0
        a, b = Counter(), Counter()
        assert a.id == 1
        assert b.id == 2
        assert Counter.count == 2


class TestInheritance:
    def test_dog(self):
        assert Dog("Buddy").speak() == "Buddy says Woof!"

    def test_cat(self):
        assert Cat("Whiskers").speak() == "Whiskers says Meow!"


class TestMagicMethods:
    def test_vector_add(self):
        v1 = Vector(1, 2)
        v2 = Vector(3, 4)
        assert v1 + v2 == Vector(4, 6)

    def test_vector_mul(self):
        v = Vector(1, 2)
        assert v * 3 == Vector(3, 6)

    def test_vector_repr(self):
        assert repr(Vector(1, 2)) == "Vector(1, 2)"

    def test_vector_str(self):
        assert str(Vector(1, 2)) == "(1, 2)"


class TestComparison:
    def test_total_ordering(self):
        assert Number(1) < Number(2)
        assert Number(2) > Number(1)
        assert Number(2) >= Number(1)
        assert Number(1) <= Number(2)
        assert Number(1) == Number(1)


class TestCallable:
    def test_multiplier(self):
        double = Multiplier(2)
        assert double(5) == 10
        assert callable(double)


class TestProperty:
    def test_circle_area(self):
        c = Circle(5)
        assert abs(c.area - 78.53975) < 0.001

    def test_circle_setter(self):
        c = Circle(5)
        c.radius = 10
        assert c.radius == 10

    def test_circle_invalid(self):
        c = Circle(5)
        with pytest.raises(ValueError):
            c.radius = -1


class TestDescriptor:
    def test_positive(self):
        ex = DescriptorExample(10)
        assert ex.x == 10

    def test_positive_invalid(self):
        with pytest.raises(ValueError):
            DescriptorExample(-1)


class TestContextManager:
    def test_managed_resource(self):
        with ManagedResource() as r:
            assert r.entered
        assert r.exited


class TestSingleton:
    def test_singleton(self):
        Singleton._instance = None  # 重置
        a = Singleton()
        b = Singleton()
        assert a is b


class TestClassMethods:
    def test_from_string(self):
        d = Date.from_string("2024-01-15")
        assert d.year == 2024
        assert d.month == 1

    def test_is_valid(self):
        assert Date.is_valid("2024-01-15")
        assert not Date.is_valid("2024-13-01")


class TestABC:
    def test_rectangle(self):
        r = Rectangle(3, 4)
        assert r.area() == 12

    def test_abstract_instantiation(self):
        with pytest.raises(TypeError):
            Shape()


class TestMRO:
    def test_diamond(self):
        assert D().method() == "B"

    def test_mro(self):
        assert D.mro() == [D, B, C, A, object]


class TestSlots:
    def test_slots(self):
        p = PointWithSlots(1, 2)
        assert p.x == 1
        assert p.y == 2

    def test_slots_no_dict(self):
        p = PointWithSlots(1, 2)
        assert not hasattr(p, "__dict__")
