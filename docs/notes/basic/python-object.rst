.. meta::
    :description lang=zh_CN: Python class 速查表涵盖了魔法 methods、property decorators、inheritance、context managers 和 OOP 设计模式以及代码示例
    :keywords: Python, Python3, Python class, Python OOP cheat sheet, magic methods, property decorator, context manager, singleton, abstract class, descriptor, inheritance

================
类（Class）
================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Python 是一种面向 object 的编程语言。本速查表涵盖了 class 定义、inheritance、魔术 methods、property、decorators、context managers 和常见设计模式。理解这些概念对于编写干净、可维护的 Python 代码至关重要。

使用 dir() 列出属性（List Attributes with dir()）
----------------------------------------------------------------------------------

``dir()`` function 返回 object 的所有 attributes 和 methods 的 list。这对于内省和发现可用的操作很有用。

.. code-block:: python

    >>> dir(list)  # 检查list的所有属性
    ['__add__', '__class__', ...]

使用 isinstance() 检查类型（Check Type with isinstance()）
----------------------------------------------------------------------------------------------------

使用 ``isinstance()`` 检查 object 是否是 class 或其 subclasses 的 instance。这优于 ``type()`` 比较，因为它支持 inheritance。

.. code-block:: python

    >>> ex = 10
    >>> isinstance(ex, int)
    True
    >>> isinstance(ex, (int, float))  # 检查多个types
    True

使用 issubclass() 检查继承（Check Inheritance with issubclass()）
------------------------------------------------------------------------------------------------------------------

使用 ``issubclass()`` 检查 class 是否是另一个 class 的 subclass。

.. code-block:: python

    >>> class Animal: pass
    >>> class Dog(Animal): pass
    >>> issubclass(Dog, Animal)
    True
    >>> issubclass(Dog, object)
    True

获取类名（Get Class Name）
----------------------------------------

通过 ``__class__.__name__`` attribute 访问 class 名称。

.. code-block:: python

    >>> class ExampleClass:
    ...     pass
    ...
    >>> ex = ExampleClass()
    >>> ex.__class__.__name__
    'ExampleClass'

检查、获取和设置属性（Has / Get / Set Attributes）
----------------------------------------------------------------------------

Python 提供内置的 functions 来在运行时动态访问和修改 object attributes。

.. code-block:: python

    >>> class Example:
    ...     def __init__(self):
    ...         self.name = "ex"
    ...
    >>> ex = Example()
    >>> hasattr(ex, "name")
    True
    >>> getattr(ex, 'name')
    'ex'
    >>> setattr(ex, 'name', 'example')
    >>> ex.name
    'example'
    >>> getattr(ex, 'missing', 'default')  # 默认情况下
    'default'

使用 type() 声明类（Declare Class with type()）
--------------------------------------------------------------------------------

可以使用 ``type()`` 动态创建 Classes。这对于元编程和在运行时创建 classes 非常有用。

.. code-block:: python

    >>> def greet(self):
    ...     return f"Hello, I'm {self.name}"
    ...
    >>> Person = type('Person', (object,), {
    ...     'name': 'Anonymous',
    ...     'greet': greet
    ... })
    >>> p = Person()
    >>> p.greet()
    "Hello, I'm Anonymous"

这相当于：

.. code-block:: python

    >>> class Person:
    ...     name = 'Anonymous'
    ...     def greet(self):
    ...         return f"Hello, I'm {self.name}"

__new__ 与 __init__ 对比（__new__ vs __init__）
------------------------------------------------------------------------------------

``__new__`` 创建 instance， ``__init__`` 初始化它。仅当 ``__new__`` 返回 class 的 instance 时，才调用 ``__init__`` 。

.. code-block:: python

    >>> class Example:
    ...     def __new__(cls, arg):
    ...         print(f'__new__ {arg}')
    ...         return super().__new__(cls)
    ...     def __init__(self, arg):
    ...         print(f'__init__ {arg}')
    ...
    >>> o = Example("Hello")
    __new__ Hello
    __init__ Hello

__str__ 和 __repr__（__str__ and __repr__）
--------------------------------------------------------------------------------

``__str__`` 返回人类可读的 string， ``__repr__`` 返回 debugging 的明确表示。当未定义 ``__str__`` 时，使用 ``__repr__`` 。

.. code-block:: python

    >>> class Vector:
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...     def __repr__(self):
    ...         return f"Vector({self.x}, {self.y})"
    ...     def __str__(self):
    ...         return f"({self.x}, {self.y})"
    ...
    >>> v = Vector(1, 2)
    >>> repr(v)
    'Vector(1, 2)'
    >>> str(v)
    '(1, 2)'
    >>> print(v)
    (1, 2)

比较魔术方法（Comparison Magic Methods）
----------------------------------------------------------------

通过定义magic methods来实现比较operators。使用 ``functools.total_ordering`` 生成 ``__eq__`` 与另一个的所有比较。

.. code-block:: python

    >>> from functools import total_ordering
    >>> @total_ordering
    ... class Number:
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __eq__(self, other):
    ...         return self.val == other.val
    ...     def __lt__(self, other):
    ...         return self.val < other.val
    ...
    >>> Number(1) < Number(2)
    True
    >>> Number(2) >= Number(1)
    True

算术魔术方法（Arithmetic Magic Methods）
----------------------------------------------------------------

实现算法operators，使objects与 ``+`` 、 ``-`` 、 ``*`` 等一起工作。

.. code-block:: python

    >>> class Vector:
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...     def __add__(self, other):
    ...         return Vector(self.x + other.x, self.y + other.y)
    ...     def __mul__(self, scalar):
    ...         return Vector(self.x * scalar, self.y * scalar)
    ...     def __repr__(self):
    ...         return f"Vector({self.x}, {self.y})"
    ...
    >>> Vector(1, 2) + Vector(3, 4)
    Vector(4, 6)
    >>> Vector(1, 2) * 3
    Vector(3, 6)

可使用 __call__ 调用（Callable with __call__）
------------------------------------------------------------------------------

实现 ``__call__`` 以使 instances 像 functions 一样可调用。这对于创建类似于 objects 的维护状态的 function 非常有用。

.. code-block:: python

    >>> class Multiplier:
    ...     def __init__(self, factor):
    ...         self.factor = factor
    ...     def __call__(self, x):
    ...         return x * self.factor
    ...
    >>> double = Multiplier(2)
    >>> double(5)
    10
    >>> callable(double)
    True

@property 装饰器（@property Decorator）
--------------------------------------------------------------------

使用 ``@property`` 为托管 attributes 定义 getter、setter 和 deleters。这允许 attribute 在运行自定义代码时访问语法。

.. code-block:: python

    >>> class Circle:
    ...     def __init__(self, radius):
    ...         self._radius = radius
    ...     @property
    ...     def radius(self):
    ...         return self._radius
    ...     @radius.setter
    ...     def radius(self, value):
    ...         if value < 0:
    ...             raise ValueError("Radius must be positive")
    ...         self._radius = value
    ...     @property
    ...     def area(self):
    ...         return 3.14159 * self._radius ** 2
    ...
    >>> c = Circle(5)
    >>> c.area
    78.53975
    >>> c.radius = 10
    >>> c.radius
    10

描述符协议（Descriptor Protocol）
----------------------------------------------------

描述符控制 class 级别的 attribute 访问。它们实现了 ``__get__`` 、 ``__set__`` 和/或 ``__delete__`` methods。

.. code-block:: python

    >>> class Positive:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __get__(self, obj, objtype=None):
    ...         return obj.__dict__[self.name]
    ...     def __set__(self, obj, value):
    ...         if value < 0:
    ...             raise ValueError("Must be positive")
    ...         obj.__dict__[self.name] = value
    ...
    >>> class Example:
    ...     x = Positive('x')
    ...     def __init__(self, x):
    ...         self.x = x
    ...
    >>> ex = Example(10)
    >>> ex.x
    10

上下文管理器协议（Context Manager Protocol）
--------------------------------------------------------------------

Context managers 实现 ``__enter__`` 和 ``__exit__`` 与 ``with`` statement 一起管理资源。即使出现 exceptions，这也能确保正确的清理。

.. code-block:: python

    class ManagedFile:
        def __init__(self, filename):
            self.filename = filename

        def __enter__(self):
            self.file = open(self.filename, 'r')
            return self.file

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.file.close()
            return False  # 不要压制exceptions

    with ManagedFile('example.txt') as f:
        content = f.read()

使用 contextlib（Using contextlib）
--------------------------------------------------------------

``contextlib`` module 提供了用于创建 context managers 的实用程序，而无需编写完整的 class。

.. code-block:: python

    from contextlib import contextmanager

    @contextmanager
    def managed_file(filename):
        f = open(filename, 'r')
        try:
            yield f
        finally:
            f.close()

    with managed_file('example.txt') as f:
        content = f.read()

@staticmethod 和 @classmethod（@staticmethod and @classmethod）
------------------------------------------------------------------------------------------------------------------------

``@staticmethod`` 定义了不访问 instance 或 class 的 method。 ``@classmethod`` 接收 class 作为第一个 argument，对于替代构造函数很有用。

.. code-block:: python

    >>> class Date:
    ...     def __init__(self, year, month, day):
    ...         self.year, self.month, self.day = year, month, day
    ...     @classmethod
    ...     def from_string(cls, date_string):
    ...         year, month, day = map(int, date_string.split('-'))
    ...         return cls(year, month, day)
    ...     @staticmethod
    ...     def is_valid(date_string):
    ...         try:
    ...             y, m, d = map(int, date_string.split('-'))
    ...             return 1 <= m <= 12 and 1 <= d <= 31
    ...         except:
    ...             return False
    ...
    >>> d = Date.from_string('2024-01-15')
    >>> d.year
    2024
    >>> Date.is_valid('2024-13-01')
    False

带有 abc 的抽象基类（Abstract Base Classes with abc）
----------------------------------------------------------------------------------------

使用 ``abc`` module定义无法实例化的abstract base classes，并要求subclasses实现某些methods。

.. code-block:: python

    >>> from abc import ABC, abstractmethod
    >>> class Shape(ABC):
    ...     @abstractmethod
    ...     def area(self):
    ...         pass
    ...
    >>> class Rectangle(Shape):
    ...     def __init__(self, width, height):
    ...         self.width, self.height = width, height
    ...     def area(self):
    ...         return self.width * self.height
    ...
    >>> r = Rectangle(3, 4)
    >>> r.area()
    12
    >>> Shape()  # 引发类型错误

菱形继承问题（MRO）（The Diamond Problem (MRO)）
----------------------------------------------------------------------------

Python使用Method解析顺序（MRO）来解决多个inheritance中的菱形问题。使用 ``ClassName.mro()`` 查看解析顺序。

.. code-block:: python

    >>> class A:
    ...     def method(self):
    ...         return "A"
    ...
    >>> class B(A):
    ...     def method(self):
    ...         return "B"
    ...
    >>> class C(A):
    ...     def method(self):
    ...         return "C"
    ...
    >>> class D(B, C):
    ...     pass
    ...
    >>> D().method()
    'B'
    >>> D.mro()
    [<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>]

单例模式（Singleton Pattern）
----------------------------------------------

Singleton 确保 class 中仅存在一个 instance。使用 ``__new__`` 或 decorator 实施。

.. code-block:: python

    class Singleton:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    a = Singleton()
    b = Singleton()
    print(a is b)  # True

使用__slots__（Using __slots__）
--------------------------------------------------------

``__slots__`` 限制 instance attributes 并通过避免每个 instance 出现 ``__dict__`` 来减少内存使用量。

.. code-block:: python

    >>> class Point:
    ...     __slots__ = ['x', 'y']
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    >>> p = Point(1, 2)
    >>> p.x
    1
    >>> p.z = 3  # 引发属性错误

常用魔术方法参考（Common Magic Methods Reference）
--------------------------------------------------------------------------------

.. code-block:: python

    # Object 的创作与表现
    __new__(cls, ...)        # 创建instance
    __init__(self, ...)      # 初始化instance
    __del__(self)            # 析构函数
    __repr__(self)           # repr(obj)
    __str__(self)            # str(obj)

    # 比较
    __eq__(self, other)      # ==
    __ne__(self, other)      # !=
    __lt__(self, other)      # <
    __le__(self, other)      # <=
    __gt__(self, other)      # >
    __ge__(self, other)      # >=

    # 算术
    __add__(self, other)     # +
    __sub__(self, other)     # -
    __mul__(self, other)     # *
    __truediv__(self, other) # /
    __floordiv__(self, other)# //
    __mod__(self, other)     # %
    __pow__(self, other)     # **

    # 容器
    __len__(self)            # len(obj)
    __getitem__(self, key)   # 对象[key]
    __setitem__(self, k, v)  # obj[key] = value
    __delitem__(self, key)   # 删除 obj[key]
    __contains__(self, item) # item 在 obj 中
    __iter__(self)           # iter(obj)

    # Attribute 访问
    __getattr__(self, name)  # obj.name（未找到时）
    __setattr__(self, n, v)  # obj.name = value
    __delattr__(self, name)  # 删除obj.name

    # 可调用
    __call__(self, ...)      # obj()

    # Context Manager
    __enter__(self)          # 与对象
    __exit__(self, ...)      # 退出并阻止

    # 描述符
    __get__(self, obj, type) # 描述符访问
    __set__(self, obj, val)  # 描述符分配
    __delete__(self, obj)    # 描述符删除
