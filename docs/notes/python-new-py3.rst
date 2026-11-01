.. meta::
    :description lang=zh_CN: Python 3 新功能指南，涵盖 f-strings、海象 operator、数据类、异步/等待、type hints 以及 Python 2 的主要改进
    :keywords: Python, Python3, new features, f-strings, walrus operator, dataclasses, async await, type hints, pathlib, migration

==========================================================
Python3 中的新功能（New in Python3）
==========================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

源代码可以在 `py3.py <https://github.com/crazyguitar/pysheeet/blob/master/src/new_py3/py3.py>`_ 上找到。

类型参数语法（Type Parameter Syntax）
----------------------------------------------------------

**Python新品 3.12**

- PEP 695_ - Type Parameter 语法

Python 3.12 引入了一种更清晰、更直观的语法来定义通用 classes 和 functions。您现在可以直接在 class 和 function 定义中使用 ``[]`` 括号表示法，而不是从键入的 module 导入 ``TypeVar`` 和 ``Generic`` 。这使得通用代码更具可读性并显着减少了样板代码。

.. code-block:: python

    # 旧方式（Python 3.12 之前）
    from typing import TypeVar, Generic
    T = TypeVar('T')
    class Box(Generic[T]):
        def __init__(self, item: T) -> None:
            self.item = item

    # 新方式（Python 3.12+）
    class Box[T]:
        def __init__(self, item: T) -> None:
            self.item = item

    # 通用 functions
    def first[T](items: list[T]) -> T:
        return items[0]


f 字符串改进（f-string Improvements）
------------------------------------------------------------

**Python新品 3.12**

- PEP 701_ - f-strings 的语法形式化

F-strings在Python 3.12上有了显着的改进。它们现在支持相同 type 的嵌套引号、反斜杠转义和多行 expressions，没有任何限制。这使得 f-strings 更加灵活，并消除了许多以前需要解决方法的边缘情况。

.. code-block:: python

    >>> songs = ["Take me back to Eden", "&", "Satellite"]
    >>> f"This is the playlist: {", ".join(songs)}"
    'This is the playlist: Take me back to Eden, &, Satellite'

    # 嵌套引号现在可以使用
    >>> f"He said {"hello"}"
    'He said hello'


异常组（Exception Groups）
------------------------------------------

**Python新品 3.11**

- PEP 654_ - Exception 组及除外*

Exception 组允许您同时发起和处理多个不相关的 exceptions。这对于多个任务可能独立失败的并发操作特别有用。新的 ``except*`` 语法允许您处理组中的特定 exception types，同时让其他组传播。

.. code-block:: python

    >>> def raise_multiple():
    ...     raise ExceptionGroup("multiple errors", [
    ...         ValueError("invalid value"),
    ...         TypeError("wrong type"),
    ...     ])
    ...
    >>> try:
    ...     raise_multiple()
    ... except* ValueError as e:
    ...     print(f"ValueError: {e.exceptions}")
    ... except* TypeError as e:
    ...     print(f"TypeError: {e.exceptions}")
    ...
    ValueError: (ValueError('invalid value'),)
    TypeError: (TypeError('wrong type'),)


结构模式匹配（Structural Pattern Matching）
----------------------------------------------------------------------

**Python新品 3.10**

- PEP 634_ - 结构模式匹配：规范
- PEP 635_ - 结构模式匹配：动机和基本原理

模式匹配提供了一种强大的方法来解构和匹配 complex 数据结构。它与其他语言中的 switch statements 类似，但更具表现力，支持序列模式、映射模式、class 模式和防护。通配符 ``_`` 匹配任何内容并用作默认情况。

.. code-block:: python

    >>> def http_status(status):
    ...     match status:
    ...         case 200:
    ...             return "OK"
    ...         case 404:
    ...             return "Not Found"
    ...         case 500:
    ...             return "Internal Server Error"
    ...         case _:
    ...             return "Unknown"
    ...
    >>> http_status(200)
    'OK'
    >>> http_status(404)
    'Not Found'

    # 模式匹配与解构
    >>> def describe_point(point):
    ...     match point:
    ...         case (0, 0):
    ...             return "Origin"
    ...         case (x, 0):
    ...             return f"On x-axis at {x}"
    ...         case (0, y):
    ...             return f"On y-axis at {y}"
    ...         case (x, y):
    ...             return f"Point at ({x}, {y})"
    ...
    >>> describe_point((0, 0))
    'Origin'
    >>> describe_point((5, 0))
    'On x-axis at 5'


字典合并（Dictionary Merge）
--------------------------------------------

**Python新品 3.9**

- PEP 584_ - 将联合 Operators 添加到 dict

``|`` operator 提供了一种更清晰、更直观的方式来合并 dictionaries。 ``|=`` operator 就地更新了 dictionary。这比使用 ``{**a, **b}`` 或 ``dict.update()`` 更具可读性，并且遵循 set 操作的模式。

.. code-block:: python

    >>> a = {"foo": "Foo"}
    >>> b = {"bar": "Bar"}

    # 老方法
    >>> {**a, **b}
    {'foo': 'Foo', 'bar': 'Bar'}
    >>> a.update(b)
    >>> a
    {'foo': 'Foo', 'bar': 'Bar'}

    # 新方式
    >>> a = {"foo": "Foo"}
    >>> a | b
    {'foo': 'Foo', 'bar': 'Bar'}
    >>> a |= b
    >>> a
    {'foo': 'Foo', 'bar': 'Bar'}


仅位置参数（Positional-only parameters）
------------------------------------------------------------------

**Python新品 3.8**

- PEP 570_ - Python 仅位置 Parameters

``/`` 标记之前的 Parameters 必须按位置传递，不能用作 keyword arguments。这为 library 作者在 API 设计中提供了更大的灵活性，并允许在不破坏向后兼容性的情况下更改 parameter 名称。

.. code-block:: python

    >>> def f(a, b, /, c, d):
    ...     print(a, b, c, d)
    ...
    >>> f(1, 2, 3, 4)
    1 2 3 4
    >>> f(1, 2, c=3, d=4)
    1 2 3 4
    >>> f(1, b=2, c=3, d=4)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: f() got some positional-only arguments passed as keyword arguments: 'b'


海象运算符（The walrus operator）
----------------------------------------------------

**Python新品 3.8**

- PEP 572_ - 分配 Expressions

海象 operator ``:=`` 允许您将 values 分配给 variables 作为 expression 的一部分。当您需要计算 value 并在条件中使用它时，这可以减少代码重复。在完成PEP 572后，Guido van Rossum（俗称BDFL）决定辞去Python的独裁者职务。

.. code-block:: python

    >>> f = (0, 1)
    >>> [(f := (f[1], sum(f)))[0] for i in range(10)]
    [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

    # 在 loops 中有用
    >>> while (line := input("Enter: ")) != "quit":
    ...     print(f"You entered: {line}")

    # 在 if statements 中有用
    >>> if (n := len("hello")) > 3:
    ...     print(f"Length {n} is greater than 3")


数据类（Data Classes）
----------------------------------

**Python新品 3.7**

- PEP 557_ - 数据 Classes

数据类自动生成主要存储数据的样板代码，例如 ``__init__`` 、 ``__repr__`` 、 ``__eq__`` 以及可选的 ``__hash__`` （对于 classes）。这减少了重复代码，并使数据保存 classes 更加简洁和可读。

Mutable 数据 Class

.. code-block:: python

    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class DCls(object):
    ...     x: str
    ...     y: str
    ...
    >>> d = DCls("foo", "bar")
    >>> d
    DCls(x='foo', y='bar')
    >>> d = DCls(x="foo", y="baz")
    >>> d
    DCls(x='foo', y='baz')
    >>> d.z = "bar"

Immutable 数据 Class

.. code-block:: python

    >>> from dataclasses import dataclass
    >>> from dataclasses import FrozenInstanceError
    >>> @dataclass(frozen=True)
    ... class DCls(object):
    ...     x: str
    ...     y: str
    ...
    >>> try:
    ...     d.x = "baz"
    ... except FrozenInstanceError as e:
    ...     print(e)
    ...
    cannot assign to field 'x'
    >>> try:
    ...     d.z = "baz"
    ... except FrozenInstanceError as e:
    ...     print(e)
    ...
    cannot assign to field 'z'


内置 ``breakpoint()`` （Built-in ``breakpoint()`` ）
------------------------------------------------------------------------------------------------

**Python新品 3.7**

- PEP 553_ - 内置breakpoint()

``breakpoint()`` function 提供了一种便捷的方式进入 debugger。它尊重 ``PYTHONBREAKPOINT`` 环境 variable，允许您自定义或禁用 debugging 行为，而无需修改代码。

.. code-block:: python

    >>> for x in range(3):
    ...     print(x)
    ...     breakpoint()
    ...
    0
    > <stdin>(1)<module>()->None
    (Pdb) c
    1
    > <stdin>(1)<module>()->None
    (Pdb) c
    2
    > <stdin>(1)<module>()->None
    (Pdb) c


typing 模块与泛型类型的核心支持（Core support for typing module and generic types）
------------------------------------------------------------------------------------------------------------------------------------------

**Python新品 3.7**

- PEP 560_ - 对键入 module 和通用 types 的核心支持

Python 3.7 添加了对 module 类型的核心支持，使通用 types 更快，并使 classes 能够自定义通过 ``__class_getitem__`` 下标的方式。

之前 Python 3.7

.. code-block:: python

    >>> from typing import Generic, TypeVar
    >>> from typing import Iterable
    >>> T = TypeVar('T')
    >>> class C(Generic[T]): ...
    ...
    >>> def func(l: Iterable[C[int]]) -> None:
    ...     for i in l:
    ...         print(i)
    ...
    >>> func([1,2,3])
    1
    2
    3

Python 3.7 或以上

.. code-block:: python

    >>> from typing import Iterable
    >>> class C:
    ...     def __class_getitem__(cls, item):
    ...         return f"{cls.__name__}[{item.__name__}]"
    ...
    >>> def func(l: Iterable[C[int]]) -> None:
    ...     for i in l:
    ...         print(i)
    ...
    >>> func([1,2,3])
    1
    2
    3


变量标注（Variable annotations）
----------------------------------------------------

**Python新品 3.6**

- PEP 526_ - Variable 注释的语法

现在可以使用 ``:`` 语法用 types 注释 Variables，即使没有立即赋值。这可以实现更好的静态分析和 IDE 支持。

.. code-block:: python

    >>> from typing import List
    >>> x: List[int] = [1, 2, 3]
    >>> x
    [1, 2, 3]

    >>> from typing import List, Dict
    >>> class Cls(object):
    ...     x: List[int] = [1, 2, 3]
    ...     y: Dict[str, str] = {"foo": "bar"}
    ...
    >>> o = Cls()
    >>> o.x
    [1, 2, 3]
    >>> o.y
    {'foo': 'bar'}


f 字符串（f-string）
------------------------------

**Python新品 3.6**

- PEP 498_ - Literal String 插补

F-strings（格式为 string literals）提供了一种简洁易读的方式将 expressions 嵌入到 string literals 中。它们比 ``%`` 格式化和 ``str.format()`` 更快，因为它们是在运行时评估的。

.. code-block:: python

    >>> py = "Python3"
    >>> f'Awesome {py}'
    'Awesome Python3'
    >>> x = [1, 2, 3, 4, 5]
    >>> f'{x}'
    '[1, 2, 3, 4, 5]'
    >>> def foo(x:int) -> int:
    ...     return x + 1
    ...
    >>> f'{foo(0)}'
    '1'
    >>> f'{123.567:1.3}'
    '1.24e+02'


异步生成器（Asynchronous generators）
------------------------------------------------------------

**Python新品 3.6**

- PEP 525_ - Asynchronous Generators

Asynchronous generators 将 generators 的强大功能与异步/等待语法相结合，允许您异步生成 values。这对于来自异步源的流数据很有用。

.. code-block:: python

    >>> import asyncio
    >>> async def fib(n: int):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         await asyncio.sleep(1)
    ...         yield a
    ...         b, a = a + b , b
    ...
    >>> async def coro(n: int):
    ...     ag = fib(n)
    ...     f = await ag.asend(None)
    ...     print(f)
    ...     f = await ag.asend(None)
    ...     print(f)
    ...
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(coro(5))
    0
    1


异步推导式（Asynchronous comprehensions）
--------------------------------------------------------------------

**Python新品 3.6**

- PEP 530_ - Asynchronous Comprehensions

异步 comprehensions 允许在 list、set、dict、comprehensions 和 generator expressions 中使用 ``async for`` 。您还可以在 comprehensions 中使用 ``await`` expressions。

.. code-block:: python

    >>> import asyncio
    >>> async def fib(n: int):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         await asyncio.sleep(1)
    ...         yield a
    ...         b, a = a + b , b
    ...

    # 异步...其他

    >>> async def coro(n: int):
    ...     async for f in fib(n):
    ...         print(f, end=" ")
    ...     else:
    ...         print()
    ...
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(coro(5))
    0 1 1 2 3

    # list 中的异步

    >>> async def coro(n: int):
    ...     return [f async for f in fib(n)]
    ...
    >>> loop.run_until_complete(coro(5))
    [0, 1, 1, 2, 3]

    # 等待list

    >>> async def slowfmt(n: int) -> str:
    ...     await asyncio.sleep(0.5)
    ...     return f'{n}'
    ...
    >>> async def coro(n: int):
    ...     return [await slowfmt(f) async for f in fib(n)]
    ...
    >>> loop.run_until_complete(coro(5))
    ['0', '1', '1', '2', '3']


新的 dict 实现（New dict implementation）
----------------------------------------------------------------------

**Python新品 3.6**

- PEP 468_ - 保留 function 中 \*\*kwargs 的顺序
- PEP 520_ - 保留 Class Attribute 定义顺序
- bpo 27350_ - 更紧凑的 dictionaries 和更快的 iteration

Python 3.6 引入了新的 dictionary 实现，该实现减少了 20-25% 的内存使用并保留插入顺序。这是 3.6 中的实现细节，但在 Python 3.7 中成为语言保证。

之前 Python 3.5

.. code-block:: python

    >>> import sys
    >>> sys.getsizeof({str(i):i for i in range(1000)})
    49248

    >>> d = {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}
    >>> d   # 不保序
    {'barry': 'green', 'timmy': 'red', 'guido': 'blue'}

Python 3.6

- 内存占用小于Python 3.5
- 保留插入顺序

.. code-block:: python

    >>> import sys
    >>> sys.getsizeof({str(i):i for i in range(1000)})
    36968

    >>> d = {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}
    >>> d   # 保留插入顺序
    {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}


``async`` 和 ``await`` 语法（ ``async`` and ``await`` syntax）
------------------------------------------------------------------------------------------------------------------

**Python新品 3.5**

- PEP 492_ - Coroutines 具有异步和等待语法

``async`` 和 ``await`` 关键字提供了用于编写 coroutines 的本机语法，使 asynchronous 代码比之前基于 generator 的方法更具可读性。这是现代 Python 异步编程的基础。

之前 Python 3.5

.. code-block:: python

    >>> import asyncio
    >>> @asyncio.coroutine
    ... def fib(n: int):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         b, a = a + b, b
    ...     return a
    ...
    >>> @asyncio.coroutine
    ... def coro(n: int):
    ...     for x in range(n):
    ...         yield from asyncio.sleep(1)
    ...         f = yield from fib(x)
    ...         print(f)
    ...
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(coro(3))
    0
    1
    1

Python 3.5 或以上

.. code-block:: python

    >>> import asyncio
    >>> async def fib(n: int):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         b, a = a + b, b
    ...     return a
    ...
    >>> async def coro(n: int):
    ...     for x in range(n):
    ...         await asyncio.sleep(1)
    ...         f = await fib(x)
    ...         print(f)
    ...
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(coro(3))
    0
    1
    1


通用解包（General unpacking）
----------------------------------------------

**Python新品 3.5**

- PEP 448_ - 附加拆包概括

Python 3.5 扩展了 ``*`` 和 ``**`` 解包 operators 以在更多上下文中工作，包括具有多个解包操作的 function 调用以及 list/dict literals 中的调用。

Python 2

.. code-block:: python

    >>> def func(*a, **k):
    ...     print(a)
    ...     print(k)
    ...
    >>> func(*[1,2,3,4,5], **{"foo": "bar"})
    (1, 2, 3, 4, 5)
    {'foo': 'bar'}

Python 3

.. code-block:: python

    >>> print(*[1, 2, 3], 4, *[5, 6])
    1 2 3 4 5 6
    >>> [*range(4), 4]
    [0, 1, 2, 3, 4]
    >>> {"foo": "Foo", "bar": "Bar", **{"baz": "baz"}}
    {'foo': 'Foo', 'bar': 'Bar', 'baz': 'baz'}
    >>> def func(*a, **k):
    ...     print(a)
    ...     print(k)
    ...
    >>> func(*[1], *[4,5], **{"foo": "FOO"}, **{"bar": "BAR"})
    (1, 4, 5)
    {'foo': 'FOO', 'bar': 'BAR'}


矩阵乘法（Matrix multiplication）
------------------------------------------------------

**Python新品 3.5**

- PEP 465_ - 用于矩阵乘法的专用中缀 operator

添加 ``@`` operator用于矩阵乘法，主要有利于像NumPy一样的科学计算libraries。 Classes 可以实现 ``__matmul__`` 和 ``__imatmul__`` 来支持此 operator。

.. code-block:: python

    >>> # "@" 表示矩阵乘法
    >>> class Arr:
    ...     def __init__(self, *arg):
    ...         self._arr = arg
    ...     def __matmul__(self, other):
    ...         if not isinstance(other, Arr):
    ...             raise TypeError
    ...         if len(self) != len(other):
    ...             raise ValueError
    ...         return sum([x*y for x, y in zip(self._arr, other._arr)])
    ...     def __imatmul__(self, other):
    ...         if not isinstance(other, Arr):
    ...             raise TypeError
    ...         if len(self) != len(other):
    ...             raise ValueError
    ...         res = sum([x*y for x, y in zip(self._arr, other._arr)])
    ...         self._arr = [res]
    ...         return self
    ...     def __len__(self):
    ...         return len(self._arr)
    ...     def __str__(self):
    ...         return self.__repr__()
    ...     def __repr__(self):
    ...         return "Arr({})".format(repr(self._arr))
    ...
    >>> a = Arr(9, 5, 2, 7)
    >>> b = Arr(5, 5, 6, 6)
    >>> a @ b  # __matmul__
    124
    >>> a @= b  # __imatmul__
    >>> a
    Arr([124])


格式化字节字符串（Format byte string）
--------------------------------------------------------

**Python新品 3.5**

- PEP 461_ - 将 ``%`` 格式添加到 bytes 和 bytearray

``%`` 格式 operator 现在可与 bytes 和 bytearray objects 配合使用，从而更轻松地使用二进制协议和格式。

.. code-block:: python

    >>> b'abc %b %b' % (b'foo', b'bar')
    b'abc foo bar'
    >>> b'%d %f' % (1, 3.14)
    b'1 3.140000'
    >>> class Cls(object):
    ...     def __repr__(self):
    ...         return "repr"
    ...     def __str__(self):
    ...         return "str"
    ...
    'repr'
    >>> b'%a' % Cls()
    b'repr'


抑制异常（Suppressing exception）
------------------------------------------------------

**Python新品 3.3**

- PEP 409_ - 抑制 exception 上下文

当重新加注 exceptions 时，Python 默认显示 exceptions 的链。使用 ``raise ... from None`` 会抑制上下文，仅显示新的 exception。

不带 ``raise Exception from None``

.. code-block:: python

    >>> def func():
    ...     try:
    ...         1 / 0
    ...     except ZeroDivisionError:
    ...         raise ArithmeticError
    ...
    >>> func()
    Traceback (most recent call last):
      File "<stdin>", line 3, in func
    ZeroDivisionError: division by zero

    During handling of the above exception, another exception occurred:

    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 5, in func
    ArithmeticError

配 ``raise Exception from None``

.. code-block:: python

    >>> def func():
    ...     try:
    ...         1 / 0
    ...     except ZeroDivisionError:
    ...         raise ArithmeticError from None
    ...
    >>> func()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 5, in func
    ArithmeticError

    # 调试

    >>> try:
    ...     func()
    ... except ArithmeticError as e:
    ...     print(e.__context__)
    ...
    division by zero


生成器委托（Generator delegation）
------------------------------------------------------

**Python新品 3.3**

- PEP 380_ - 委托给子生成器的语法

``yield from`` expression 允许 generator 将其部分操作委托给另一个 generator。这简化了消耗其他 generators 的 generators 的编写。

.. code-block:: python

    >>> def fib(n: int):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         yield a
    ...         b, a = a + b, b
    ...
    >>> def delegate(n: int):
    ...     yield from fib(n)
    ...
    >>> list(delegate(10))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


BDFL 退休（BDFL retirement）
------------------------------------------------

**Python新品 3.1**

- PEP 401_ - BDFL 退休

愚人节笑话 PEP，添加了幽默的复活节彩蛋。当您从 ``__future__`` 导入 ``barry_as_FLUFL`` 时， ``!=`` operator 将替换为 ``<>`` 。

.. code-block:: python

    >>> from __future__ import barry_as_FLUFL
    >>> 1 != 2
      File "<stdin>", line 1
        1 != 2
           ^
    SyntaxError: with Barry as BDFL, use '<>' instead of '!='
    >>> 1 <> 2
    True


函数标注（Function annotations）
----------------------------------------------------

**Python新品 3.0**

- PEP 3107_ - Function 注释
- PEP 484_ - Type Hints
- PEP 483_ - Type Hints 的理论

Function 注释允许将元数据附加到 function、parameters 和 return values。虽然 Python 不会在运行时强制执行这些操作，但它们启用静态 type 检查工具和更好的 IDE 支持。

.. code-block:: python

    >>> import types
    >>> generator = types.GeneratorType
    >>> def fib(n: int) -> generator:
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         yield a
    ...         b, a = a + b, b
    ...
    >>> [f for f in fib(10)]
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


扩展的可迭代拆包（Extended iterable unpacking）
--------------------------------------------------------------------------

**Python新品 3.0**

- PEP 3132_ - 扩展Iterable开箱

解包中的 ``*`` operator 将剩余的 items 捕获到 list 中。这适用于作业和 loops，可以轻松分割序列。

.. code-block:: python

    >>> a, *b, c = range(5)
    >>> a, b, c
    (0, [1, 2, 3], 4)
    >>> for a, *b in [(1, 2, 3), (4, 5, 6, 7)]:
    ...     print(a, b)
    ...
    1 [2, 3]
    4 [5, 6, 7]


仅关键字参数（Keyword-Only Arguments）
------------------------------------------------------------

**Python新品 3.0**

- PEP 3102_ - 仅限关键字 Arguments

function 签名中 ``*`` 之后定义的 Parameters 必须作为 keyword arguments 传递。这提高了 API 的清晰度并防止意外的位置使用。

.. code-block:: python

    >>> def f(a, b, *, kw):
    ...     print(a, b, kw)
    ...
    >>> f(1, 2, 3)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: f() takes 2 positional arguments but 3 were given
    >>> f(1, 2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: f() missing 1 required keyword-only argument: 'kw'
    >>> f(1, 2, kw=3)
    1 2 3


新的 super 用法（New Super）
--------------------------------------------

**Python新品 3.0**

- PEP 3135_-新超级

Python 3 简化了 ``super()`` 调用，使其在大多数情况下无需 arguments 即可工作。 interpreter 自动确定 class 和 instance。

Python 2

.. code-block:: python

    >>> class ParentCls(object):
    ...     def foo(self):
    ...         print "call parent"
    ...
    >>> class ChildCls(ParentCls):
    ...     def foo(self):
    ...         super(ChildCls, self).foo()
    ...         print "call child"
    ...
    >>> p = ParentCls()
    >>> c = ChildCls()
    >>> p.foo()
    call parent
    >>> c.foo()
    call parent
    call child

Python 3

.. code-block:: python

    >>> class ParentCls(object):
    ...     def foo(self):
    ...         print("call parent")
    ...
    >>> class ChildCls(ParentCls):
    ...     def foo(self):
    ...         super().foo()
    ...         print("call child")
    ...
    >>> p = ParentCls()
    >>> c = ChildCls()
    >>> p.foo()
    call parent
    >>> c.foo()
    call parent
    call child


添加 ``nonlocal`` 关键字（Add ``nonlocal`` keyword）
------------------------------------------------------------------------------------------

**Python新品 3.0**

- PEP 3104_ - 访问外部 Scopes 中的名称

``nonlocal`` 关键字允许在封闭（但非全局）scope 中分配给 variables。这对于需要修改外部 variables 的 closures 很有用。

.. code-block:: python

    >>> def outf():
    ...     o = "out"
    ...     def inf():
    ...         nonlocal o
    ...         o = "change out"
    ...     inf()
    ...     print(o)
    ...
    >>> outf()
    change out


禁止在函数内部使用 ``from module import *`` （Not allow ``from module import *`` inside function）
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Python新品 3.0**

现在仅允许在 module 级别导入星星。这可以防止 namespace 污染并使代码更具可预测性。

.. code-block:: python

    >>> def f():
    ...     from os import *
    ...
      File "<stdin>", line 1
    SyntaxError: import * only allowed at module level


删除 ``<>`` （Remove ``<>`` ）
----------------------------------------------------

**Python新品 3.0**

``<>`` operator（ ``!=`` 的替代）在 Python 3 中被删除以简化语言。使用 ``!=`` 进行不等式比较。

Python 2

.. code-block:: python

    >>> a = "Python2"
    >>> a <> "Python3"
    True

    # 等于！=
    >>> a != "Python3"
    True

Python 3

.. code-block:: python

    >>> a = "Python3"
    >>> a != "Python2"
    True


``print`` 是一个函数（ ``print`` is a function）
----------------------------------------------------------------------------------

**Python新品 3.0**

- PEP 3105_ - 打印 function

在Python 3中， ``print`` 变成了function而不是statement。这使得 keyword arguments（如 ``end`` 、 ``sep`` 和 ``file`` ）具有更大的灵活性。

Python 2

.. code-block:: python

    >>> print "print is a statement"
    print is a statement
    >>> for x in range(3):
    ...     print x,
    ...
    0 1 2

Python 3

.. code-block:: python

    >>> print("print is a function")
    print is a function
    >>> print()
    >>> for x in range(3):
    ...     print(x, end=' ')
    ... else:
    ...     print()
    ...
    0 1 2


字符串是unicode（String is unicode）
------------------------------------------------------------

**Python新品 3.0**

- PEP 3138_ - Python 3000 中的 String 表示
- PEP 3120_ - 使用 UTF-8 作为默认源 encoding
- PEP 3131_ - 支持非 ASCII 标识符

在Python 3中，所有strings默认都是Unicode。 ``str`` type 表示 Unicode 文本，而 ``bytes`` 表示二进制数据。这消除了 Python 2 中常见的许多与 encoding 相关的错误。

Python 2

.. code-block:: python

    >>> s = 'Café'  # byte string
    >>> s
    'Caf\xc3\xa9'
    >>> type(s)
    <type 'str'>
    >>> u = u'Café' # unicode string
    >>> u
    u'Caf\xe9'
    >>> type(u)
    <type 'unicode'>
    >>> len([_c for _c in 'Café'])
    5

Python 3

.. code-block:: python

    >>> s = 'Café'
    >>> s
    'Café'
    >>> type(s)
    <class 'str'>
    >>> s.encode('utf-8')
    b'Caf\xc3\xa9'
    >>> s.encode('utf-8').decode('utf-8')
    'Café'
    >>> len([_c for _c in 'Café'])
    4


除法运算符（Division Operator）
------------------------------------------------

**Python新品 3.0**

- PEP 238_ - 更改分区 Operator

在Python 3中， ``/`` operator始终执行true除法（返回float），而 ``//`` 执行楼层除法。这消除了错误的常见来源。

Python 2

.. code-block:: python

    >>> 1 / 2
    0
    >>> 1 // 2
    0
    >>> 1. / 2
    0.5

    # 将 "true division" 向后移植到 python2

    >>> from __future__ import division
    >>> 1 / 2
    0.5
    >>> 1 // 2
    0

Python 3

.. code-block:: python

    >>> 1 / 2
    0.5
    >>> 1 // 2
    0


.. _695: https://www.python.org/dev/peps/pep-0695/
.. _701: https://www.python.org/dev/peps/pep-0701/
.. _654: https://www.python.org/dev/peps/pep-0654/
.. _634: https://www.python.org/dev/peps/pep-0634/
.. _635: https://www.python.org/dev/peps/pep-0635/
.. _584: https://www.python.org/dev/peps/pep-0584/
.. _570: https://www.python.org/dev/peps/pep-0570/
.. _572: https://www.python.org/dev/peps/pep-0572/
.. _557: https://www.python.org/dev/peps/pep-0557/
.. _553: https://www.python.org/dev/peps/pep-0553/
.. _560: https://www.python.org/dev/peps/pep-0560/
.. _526: https://www.python.org/dev/peps/pep-0526/
.. _498: https://www.python.org/dev/peps/pep-0498/
.. _525: https://www.python.org/dev/peps/pep-0525/
.. _530: https://www.python.org/dev/peps/pep-0530/
.. _468: https://www.python.org/dev/peps/pep-0468/
.. _520: https://www.python.org/dev/peps/pep-0520/
.. _27350: https://bugs.python.org/issue27350
.. _492: https://www.python.org/dev/peps/pep-0492/
.. _448: https://www.python.org/dev/peps/pep-0448/
.. _465: https://www.python.org/dev/peps/pep-0465/
.. _461: https://www.python.org/dev/peps/pep-0461/
.. _409: https://www.python.org/dev/peps/pep-0409/
.. _380: https://www.python.org/dev/peps/pep-0380/
.. _401: https://www.python.org/dev/peps/pep-0401/
.. _3107: https://www.python.org/dev/peps/pep-3107/
.. _484: https://www.python.org/dev/peps/pep-0484/
.. _483: https://www.python.org/dev/peps/pep-0483/
.. _3132: https://www.python.org/dev/peps/pep-3132/
.. _3102: https://www.python.org/dev/peps/pep-3102/
.. _3135: https://www.python.org/dev/peps/pep-3135/
.. _3104: https://www.python.org/dev/peps/pep-3104/
.. _3105: https://www.python.org/dev/peps/pep-3105/
.. _3138: https://www.python.org/dev/peps/pep-3138/
.. _3120: https://www.python.org/dev/peps/pep-3120/
.. _3131: https://www.python.org/dev/peps/pep-3131/
.. _238: https://www.python.org/dev/peps/pep-0238/
