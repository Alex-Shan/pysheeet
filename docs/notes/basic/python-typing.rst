.. meta::
    :description lang=zh_CN: Python 打字速查表，涵盖 type hints、注释、泛型、协议、TypeVar 和 mypy type 检查代码示例
    :keywords: Python, Python3, Python typing, Python type hints cheat sheet, type annotations, generics, Protocol, TypeVar, mypy, static typing

========================
类型标注（Typing）
========================

.. contents:: 目录（Table of Contents）
    :backlinks: none

PEP `484 <https://www.python.org/dev/peps/pep-0484/>`_ 提供了关于 type 系统在 Python3 中应该是什么样子的规范，引入了 type hints 的概念。此外，为了更好地理解 type hints 的设计理念，阅读 PEP `483 <https://www.python.org/dev/peps/pep-0483/>`_ 至关重要，这将有助于帮助 Python 工程师理解 Python 引入 type 系统的原因。本速查表的主要目标是展示 Python3 中 type hints 的一些常见用法。


没有类型检查（Without type check）
----------------------------------------------------

.. code-block:: python

    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            yield a
            b, a = a + b, b

    print([n for n in fib(3.6)])


输出：

.. code-block:: bash

    # 直到运行时才会检测到错误

    $ python fib.py
    Traceback (most recent call last):
      File "fib.py", line 8, in <module>
        print([n for n in fib(3.5)])
      File "fib.py", line 8, in <listcomp>
        print([n for n in fib(3.5)])
      File "fib.py", line 3, in fib
        for _ in range(n):
    TypeError: 'float' object cannot be interpreted as an integer


带类型检查（With type check）
--------------------------------------------

.. code-block:: python

    # 给一个 type hint
    from typing import Generator

    def fib(n: int) -> Generator:
        a: int = 0
        b: int = 1
        for _ in range(n):
            yield a
            b, a = a + b, b

    print([n for n in fib(3.6)])

输出：

.. code-block:: bash

    # 运行前会检测到错误

    $ mypy --strict fib.py
    fib.py:12: error: Argument 1 to "fib" has incompatible type "float"; expected "int"

基本类型（Basic types）
----------------------------------

.. code-block:: python

    import io
    import re

    from collections import deque, namedtuple
    from typing import (
        Dict,
        List,
        Tuple,
        Set,
        Deque,
        NamedTuple,
        IO,
        Pattern,
        Match,
        Text,
        Optional,
        Sequence,
        Iterable,
        Mapping,
        MutableMapping,
        Any,
    )

    # 没有初始化
    x: int

    # 任意 type
    y: Any
    y = 1
    y = "1"

    # 内置
    var_int: int = 1
    var_str: str = "Hello Typing"
    var_byte: bytes = b"Hello Typing"
    var_bool: bool = True
    var_float: float = 1.
    var_unicode: Text = u'\u2713'

    # 可能是 none
    var_could_be_none: Optional[int] = None
    var_could_be_none = 1

    # collections
    var_set: Set[int] = {i for i in range(3)}
    var_dict: Dict[str, str] = {"foo": "Foo"}
    var_list: List[int] = [i for i in range(3)]
    var_static_length_Tuple: Tuple[int, int, int] = (1, 2, 3)
    var_dynamic_length_Tuple: Tuple[int, ...] = (i for i in range(10, 3))
    var_deque: Deque = deque([1, 2, 3])
    var_nametuple: NamedTuple = namedtuple('P', ['x', 'y'])

    # io
    var_io_str: IO[str] = io.StringIO("Hello String")
    var_io_byte: IO[bytes] = io.BytesIO(b"Hello Bytes")
    var_io_file_str: IO[str] = open(__file__)
    var_io_file_byte: IO[bytes] = open(__file__, 'rb')

    # 关于
    p: Pattern = re.compile("(https?)://([^/\r\n]+)(/[^\r\n]*)?")
    m: Optional[Match] = p.match("https://www.python.org/")

    # duck types：类似list
    var_seq_list: Sequence[int] = [1, 2, 3]
    var_seq_tuple: Sequence[int] = (1, 2, 3)
    var_iter_list: Iterable[int] = [1, 2, 3]
    var_iter_tuple: Iterable[int] = (1, 2, 3)

    # duck types：类似dict
    var_map_dict: Mapping[str, str] = {"foo": "Foo"}
    var_mutable_dict: MutableMapping[str, str] = {"bar": "Bar"}

函数（Functions）
--------------------------

.. code-block:: python

    from typing import Generator, Callable

    # function
    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    # callback
    def fun(cb: Callable[[int, int], int]) -> int:
        return cb(55, 66)

    # lambda
    f: Callable[[int], int] = lambda x: x * 2

类（Classes）
--------------------

.. code-block:: python

    from typing import ClassVar, Dict, List

    class Foo:

        x: int = 1  # instance variable. default = 1
        y: ClassVar[str] = "class var"  # class variable

        def __init__(self) -> None:
            self.i: List[int] = [0]

        def foo(self, a: int, b: str) -> Dict[int, str]:
            return {a: b}

    foo = Foo()
    foo.x = 123

    print(foo.x)
    print(foo.i)
    print(Foo.y)
    print(foo.foo(1, "abc"))

生成器（Generator）
----------------------------

.. code-block:: python

    from typing import Generator

    # Generator[YieldType, SendType, ReturnType]
    def fib(n: int) -> Generator[int, None, None]:
        a: int = 0
        b: int = 1
        while n > 0:
            yield a
            b, a = a + b, b
            n -= 1

    g: Generator = fib(10)
    i: Iterator[int] = (x for x in range(3))

异步生成器（Asynchronous Generator）
----------------------------------------------------------

.. code-block:: python

    import asyncio

    from typing import AsyncGenerator, AsyncIterator

    async def fib(n: int) -> AsyncGenerator:
        a: int = 0
        b: int = 1
        while n > 0:
            await asyncio.sleep(0.1)
            yield a

            b, a = a + b, b
            n -= 1

    async def main() -> None:
        async for f in fib(10):
            print(f)

        ag: AsyncIterator = (f async for f in fib(10))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

上下文管理器（Context Manager）
----------------------------------------------

.. code-block:: python

    from typing import ContextManager, Generator, IO
    from contextlib import contextmanager

    @contextmanager
    def open_file(name: str) -> Generator:
        f = open(name)
        yield f
        f.close()

    cm: ContextManager[IO] = open_file(__file__)
    with cm as f:
        print(f.read())

异步上下文管理器（Asynchronous Context Manager）
----------------------------------------------------------------------------

.. code-block:: python

    import asyncio

    from typing import AsyncContextManager, AsyncGenerator, IO
    from contextlib import asynccontextmanager

    # 需要python 3.7或以上
    @asynccontextmanager
    async def open_file(name: str) -> AsyncGenerator:
        await asyncio.sleep(0.1)
        f = open(name)
        yield f
        await asyncio.sleep(0.1)
        f.close()

    async def main() -> None:
        acm: AsyncContextManager[IO] = open_file(__file__)
        async with acm as f:
            print(f.read())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

避免 ``None`` 访问（Avoid ``None`` access）
--------------------------------------------------------------------------

.. code-block:: python

    import re

    from typing import Pattern, Dict, Optional

    # 像c++
    # std::regex url("(https?)://([^/\r\n]+)(/[^\r\n]*)?");
    # std::regex color("^#?([a-f0-9]{6}|[a-f0-9]{3})$");

    url: Pattern = re.compile("(https?)://([^/\r\n]+)(/[^\r\n]*)?")
    color: Pattern = re.compile("^#?([a-f0-9]{6}|[a-f0-9]{3})$")

    x: Dict[str, Pattern] = {"url": url, "color": color}
    y: Optional[Pattern] = x.get("baz", None)

    print(y.match("https://www.python.org/"))

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:15: error: Item "None" of "Optional[Pattern[Any]]" has no attribute "match"

仅位置参数（Positional-only arguments）
----------------------------------------------------------------

.. code-block:: python

    # define arguments with names beginning with __

    def fib(__n: int) -> int:  # 仅位置 arg
        a, b = 0, 1
        for _ in range(__n):
            b, a = a + b, b
        return a


    def gcd(*, a: int, b: int) -> int:  # 仅关键字参数
        while b:
            a, b = b, a % b
        return a


    print(fib(__n=10))  # 错误
    print(gcd(10, 5))   # 错误

输出：

.. code-block:: bash

    mypy --strict foo.py
    foo.py:1: note: "fib" defined here
    foo.py:14: error: Unexpected keyword argument "__n" for "fib"
    foo.py:15: error: Too many positional arguments for "gcd"

多个返回值（Multiple return values）
----------------------------------------------------------

.. code-block:: python

    from typing import Tuple, Iterable, Union

    def foo(x: int, y: int) -> Tuple[int, int]:
        return x, y

    # 或者

    def bar(x: int, y: str) -> Iterable[Union[int, str]]:
        # XXX：不建议这样声明
        return x, y

    a: int
    b: int
    a, b = foo(1, 2)      # 好的
    c, d = bar(3, "bar")  # 好的

可选类型（Optional Type）
--------------------------------------

.. code-block:: python

    from typing import List, Union

    def first(l: List[Union[int, None]]) -> Union[int, None]:
        return None if len(l) == 0 else l[0]

    first([None])

    # 等于

    from typing import List, Optional

    def first(l: List[Optional[int]]) -> Optional[int]:
        return None if len(l) == 0 else l[0]

    first([None])

小心 ``Optional`` （Be careful of ``Optional`` ）
------------------------------------------------------------------------------------------

.. code-block:: python

    from typing import cast, Optional

    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            b, a = a + b, b
        return a

    def cal(n: Optional[int]) -> None:
        print(fib(n))

    cal(None)

输出：

.. code-block:: bash

    # mypy 不会检测错误
    $ mypy foo.py

明确声明

.. code-block:: python

    from typing import Optional

    def fib(n: int) -> int:  # 声明 n 为 int
        a, b = 0, 1
        for _ in range(n):
            b, a = a + b, b
        return a

    def cal(n: Optional[int]) -> None:
        print(fib(n))

输出：

.. code-block:: bash

    # 即使我们不检查 None，mypy 也可以检测到错误
    $ mypy --strict foo.py
    foo.py:11: error: Argument 1 to "fib" has incompatible type "Optional[int]"; expected "int"

谨慎使用类型转换（Be careful of casting）
--------------------------------------------------------------

.. code-block:: python

    from typing import cast, Optional

    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def cal(a: Optional[int], b: Optional[int]) -> None:
        # XXX：避免铸造
        ca, cb = cast(int, a), cast(int, b)
        print(gcd(ca, cb))

    cal(None, None)

输出：

.. code-block:: bash

    # mypy 将不会检测到 type 错误
    $ mypy --strict foo.py


前向引用（Forward references）
------------------------------------------------

基于 PEP 484，如果我们想在声明之前引用 type，则必须使用 **字符串文字** 来暗示文件中稍后存在该名称的 type。

.. code-block:: python

    from typing import Optional


    class Tree:
        def __init__(
            self, data: int,
            left: Optional["Tree"],  # 转发参考文献。
            right: Optional["Tree"]
        ) -> None:
            self.data = data
            self.left = left
            self.right = right

.. note::

    mypy 不会抱怨前向引用的一些问题。从 `Issue#948`_ 获取更多信息。

.. _Issue\#948: https://github.com/python/mypy/issues/948

.. code-block:: python

    class A:
        def __init__(self, a: A) -> None:  # 应该失败
            self.a = a

输出：

.. code-block:: bash

    $ mypy --strict type.py
    $ echo $?
    0
    $ python type.py   # 获取运行时失败
    Traceback (most recent call last):
      File "type.py", line 1, in <module>
        class A:
      File "type.py", line 2, in A
        def __init__(self, a: A) -> None:  # 应该失败
    NameError: name 'A' is not defined

延迟求值标注（Postponed Evaluation of Annotations）
--------------------------------------------------------------------------------------

**Python新品 3.7**

- PEP 563_ - 推迟注释评估

.. _563: https://www.python.org/dev/peps/pep-0563/

之前 Python 3.7

.. code-block:: python

    >>> class A:
    ...     def __init__(self, a: A) -> None:
    ...         self._a = a
    ...
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in A
    NameError: name 'A' is not defined

Python 3.7之后（包括3.7）

.. code-block:: python

    >>> from __future__ import annotations
    >>> class A:
    ...     def __init__(self, a: A) -> None:
    ...         self._a = a
    ...

.. note::

    注释只能在名称已经存在的 scope 内使用。因此， **前向参考** 不支持当前scope中没有名称的情况。 **推迟评估注释** 将成为Python 4.0中的默认行为。

类型别名（Type Alias）
--------------------------------

像 c/c++ 中的 ``typedef`` 或 ``using``

.. code-block:: cpp

    #include <iostream>
    #include <string>
    #include <regex>
    #include <vector>

    typedef std::string Url;
    template<typename T> using Vector = std::vector<T>;

    int main(int argc, char *argv[])
    {
        Url url = "https://python.org";
        std::regex p("(https?)://([^/\r\n]+)(/[^\r\n]*)?");
        bool m = std::regex_match(url, p);
        Vector<int> v = {1, 2};

        std::cout << m << std::endl;
        for (auto it : v) std::cout << it << std::endl;
        return 0;
    }

Type 别名由简单的 variable 赋值定义

.. code-block:: python

    import re

    from typing import Pattern, List

    # 与typedef一样，在c/c++中使用

    # PEP 484 建议别名大写
    Url = str

    url: Url = "https://www.python.org/"

    p: Pattern = re.compile("(https?)://([^/\r\n]+)(/[^\r\n]*)?")
    m = p.match(url)

    Vector = List[int]
    v: Vector = [1., 2.]

使用 NewType（Using NewType）
--------------------------------------------------

与别名不同， ``NewType`` 返回一个单独的 type，但在运行时与原始 type 相同。

.. code-block:: python

    from sqlalchemy import Column, String, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from typing import NewType, Any

    # 检查 mypy #2477
    Base: Any = declarative_base()

    # 创建一个新的type
    Id = NewType('Id', int) # 不等于别名，它是 'new type'

    class User(Base):
        __tablename__ = 'User'
        id = Column(Integer, primary_key=True)
        age = Column(Integer, nullable=False)
        name = Column(String, nullable=False)

        def __init__(self, id: Id, age: int, name: str) -> None:
            self.id = id
            self.age = age
            self.name = name

    # 创建用户
    user1 = User(Id(1), 62, "Guido van Rossum") # 好的
    user2 = User(2, 48, "David M. Beazley")     # 错误

输出：

.. code-block:: bash

    $ python foo.py
    $ mypy --ignore-missing-imports foo.py
    foo.py:24: error: Argument 1 to "User" has incompatible type "int"; expected "Id"

进一步阅读：

- `Issue\#1284`_

.. _`Issue\#1284`: https://github.com/python/mypy/issues/1284


使用 ``TypeVar`` 作为模板（Using ``TypeVar`` as template）
----------------------------------------------------------------------------------------------------

喜欢 c++ ``template <typename T>``

.. code-block:: cpp

    #include <iostream>

    template <typename T>
    T add(T x, T y) {
        return x + y;
    }

    int main(int argc, char *argv[])
    {
        std::cout << add(1, 2) << std::endl;
        std::cout << add(1., 2.) << std::endl;
        return 0;
    }

Python 使用 ``TypeVar``

.. code-block:: python

    from typing import TypeVar

    T = TypeVar("T")

    def add(x: T, y: T) -> T:
        return x + y

    add(1, 2)
    add(1., 2.)

使用 ``TypeVar`` 和 ``Generic`` 作为类模板（Using ``TypeVar`` and ``Generic`` as class template）
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

喜欢 c++ ``template <typename T> class``

.. code-block:: cpp

    #include <iostream>

    template<typename T>
    class Foo {
    public:
        Foo(T foo) {
            foo_ = foo;
        }
        T Get() {
            return foo_;
        }
    private:
        T foo_;
    };

    int main(int argc, char *argv[])
    {
        Foo<int> f(123);
        std::cout << f.Get() << std::endl;
        return 0;
    }

在Python中定义通用class

.. code-block:: python

    from typing import Generic, TypeVar

    T = TypeVar("T")

    class Foo(Generic[T]):
        def __init__(self, foo: T) -> None:
            self.foo = foo

        def get(self) -> T:
            return self.foo

    f: Foo[str] = Foo("Foo")
    v: int = f.get()

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:13: error: Incompatible types in assignment (expression has type "str", variable has type "int")

``TypeVar`` 的作用域规则（Scoping rules for ``TypeVar`` ）
----------------------------------------------------------------------------------------------------

- 不同通用function中使用的 ``TypeVar`` 将被推断为不同的types。

.. code-block:: python

    from typing import TypeVar

    T = TypeVar("T")

    def foo(x: T) -> T:
        return x

    def bar(y: T) -> T:
        return y

    a: int = foo(1)    # ok：T 被推断为 int
    b: int = bar("2")  # 错误：T 被推断为 str

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:12: error: Incompatible types in assignment (expression has type "str", variable has type "int")

- 通用 class 中使用的 ``TypeVar`` 将被推断为相同的 types。

.. code-block:: python

    from typing import TypeVar, Generic

    T = TypeVar("T")

    class Foo(Generic[T]):

        def foo(self, x: T) -> T:
            return x

        def bar(self, y: T) -> T:
            return y

    f: Foo[int] = Foo()
    a: int = f.foo(1)    # ok：T 被推断为 int
    b: str = f.bar("2")  # 错误：T 预计为 int

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:15: error: Incompatible types in assignment (expression has type "int", variable has type "str")
    foo.py:15: error: Argument 1 to "bar" of "Foo" has incompatible type "str"; expected "int"

- ``TypeVar`` 在 method 中使用，但与 ``Generic`` 中声明的任何 parameters 不匹配，可以推断为不同的 types。

.. code-block:: python

    from typing import TypeVar, Generic

    T = TypeVar("T")
    S = TypeVar("S")

    class Foo(Generic[T]):    # S 与参数不匹配

        def foo(self, x: T, y: S) -> S:
            return y

        def bar(self, z: S) -> S:
            return z

    f: Foo[int] = Foo()
    a: str = f.foo(1, "foo")  # S 被推断为 str
    b: int = f.bar(12345678)  # S 被推断为 int

输出：

.. code-block:: bash

    $  mypy --strict foo.py

- 未绑定的 ``TypeVar`` 不应出现在 method/function 的主体中。

.. code-block:: python

    from typing import TypeVar, Generic

    T = TypeVar("T")
    S = TypeVar("S")

    def foo(x: T) -> None:
        a: T = x    # 好的
        b: S = 123  # 错误：无效 type

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:8: error: Invalid type "foo.S"

限制为一组固定的可能类型（Restricting to a fixed set of possible types）
--------------------------------------------------------------------------------------------------------------------

``T = TypeVar('T', ClassA, ...)`` 意味着我们创建一个 **类型 variable ，并带有 value 限制** 。

.. code-block:: python

    from typing import TypeVar

    # restrict T = int or T = float
    T = TypeVar("T", int, float)

    def add(x: T, y: T) -> T:
        return x + y

    add(1, 2)
    add(1., 2.)
    add("1", 2)
    add("hello", "world")

输出：

.. code-block:: bash

    # mypy 可以检测到错误的 type
    $ mypy --strict foo.py
    foo.py:10: error: Value of type variable "T" of "add" cannot be "object"
    foo.py:11: error: Value of type variable "T" of "add" cannot be "str"

带上界的 ``TypeVar`` （ ``TypeVar`` with an upper bound）
------------------------------------------------------------------------------------------------------

``T = TypeVar('T', bound=BaseClass)`` 意味着我们创建一个 **类型 variable，其上限为** 。概念与c++中的 **多态性** 类似。

.. code-block:: cpp

    #include <iostream>

    class Shape {
    public:
        Shape(double width, double height) {
            width_ = width;
            height_ = height;
        };
        virtual double Area() = 0;
    protected:
        double width_;
        double height_;
    };

    class Rectangle: public Shape {
    public:
        Rectangle(double width, double height)
        :Shape(width, height)
        {};

        double Area() {
            return width_ * height_;
        };
    };

    class Triangle: public Shape {
    public:
        Triangle(double width, double height)
        :Shape(width, height)
        {};

        double Area() {
            return width_ * height_ / 2;
        };
    };

    double Area(Shape &s) {
        return s.Area();
    }

    int main(int argc, char *argv[])
    {
        Rectangle r(1., 2.);
        Triangle t(3., 4.);

        std::cout << Area(r) << std::endl;
        std::cout << Area(t) << std::endl;
        return 0;
    }

与 c++ 一样，创建绑定到 base class 的 base class 和 ``TypeVar`` 。然后，静态type检查器将把每个subclass作为base class的type。

.. code-block:: python

    from typing import TypeVar


    class Shape:
        def __init__(self, width: float, height: float) -> None:
            self.width = width
            self.height = height

        def area(self) -> float:
            return 0


    class Rectangle(Shape):
        def area(self) -> float:
            width: float = self.width
            height: float = self.height
            return width * height


    class Triangle(Shape):
        def area(self) -> float:
            width: float = self.width
            height: float = self.height
            return width * height / 2


    S = TypeVar("S", bound=Shape)


    def area(s: S) -> float:
        return s.area()


    r: Rectangle = Rectangle(1, 2)
    t: Triangle = Triangle(3, 4)
    i: int = 5566

    print(area(r))
    print(area(t))
    print(area(i))

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:40: error: Value of type variable "S" of "area" cannot be "int"

@overload 重载（@overload）
----------------------------------------------

有时，我们用 ``Union`` 来推断一个function的返回有多个不同的types。然而，type检查器无法区分我们想要哪个type。因此，以下代码片段显示 type 检查器无法确定哪个 type 是正确的。

.. code-block:: python

    from typing import List, Union


    class Array(object):
        def __init__(self, arr: List[int]) -> None:
            self.arr = arr

        def __getitem__(self, i: Union[int, str]) -> Union[int, str]:
            if isinstance(i, int):
                return self.arr[i]
            if isinstance(i, str):
                return str(self.arr[int(i)])


    arr = Array([1, 2, 3, 4, 5])
    x:int = arr[1]
    y:str = arr["2"]

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    foo.py:16: error: Incompatible types in assignment (expression has type "Union[int, str]", variable has type "int")
    foo.py:17: error: Incompatible types in assignment (expression has type "Union[int, str]", variable has type "str")

虽然我们可以使用 ``cast`` 来解决问题， 它无法避免拼写错误，并且 ``cast`` 不安全。

.. code-block:: python

    from typing import  List, Union, cast


    class Array(object):
        def __init__(self, arr: List[int]) -> None:
            self.arr = arr

        def __getitem__(self, i: Union[int, str]) -> Union[int, str]:
            if isinstance(i, int):
                return self.arr[i]
            if isinstance(i, str):
                return str(self.arr[int(i)])


    arr = Array([1, 2, 3, 4, 5])
    x: int = cast(int, arr[1])
    y: str = cast(str, arr[2])  # 错字。我们要分配 arr["2"]

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    $ echo $?
    0

使用 ``@overload`` 可以解决该问题。我们可以显式声明返回 type。

.. code-block:: python

    from typing import Generic, List, Union, overload


    class Array(object):
        def __init__(self, arr: List[int]) -> None:
            self.arr = arr

        @overload
        def __getitem__(self, i: str) -> str:
            ...

        @overload
        def __getitem__(self, i: int) -> int:
            ...

        def __getitem__(self, i: Union[int, str]) -> Union[int, str]:
            if isinstance(i, int):
                return self.arr[i]
            if isinstance(i, str):
                return str(self.arr[int(i)])


    arr = Array([1, 2, 3, 4, 5])
    x: int = arr[1]
    y: str = arr["2"]

输出：

.. code-block:: bash

    $ mypy --strict foo.py
    $ echo $?
    0

.. warning::

    基于PEP 484， ``@overload`` decorator只是 **，仅用于type检查器** ，它没有像c++/java那样实现真正的重载。因此，我们必须实现一个完全非 ``@overload`` 的 function。在运行时，调用 ``@overload`` function 将引发 ``NotImplementedError`` 。

.. code-block:: python

    from typing import List, Union, overload


    class Array(object):
        def __init__(self, arr: List[int]) -> None:
            self.arr = arr

        @overload
        def __getitem__(self, i: Union[int, str]) -> Union[int, str]:
            if isinstance(i, int):
                return self.arr[i]
            if isinstance(i, str):
                return str(self.arr[int(i)])


    arr = Array([1, 2, 3, 4, 5])
    try:
        x: int = arr[1]
    except NotImplementedError as e:
        print("NotImplementedError")

输出：

.. code-block:: bash

    $ python foo.py
    NotImplementedError

存根文件（Stub Files）
--------------------------------

存根文件就像我们通常用来在 c/c++ 中定义接口的头文件一样。在python中，我们可以在同一个module目录或 ``export MYPYPATH=${stubs}`` 中定义我们的接口

首先，我们需要为module创建一个存根文件（接口文件）。

.. code-block:: bash

    $ mkdir fib
    $ touch fib/__init__.py fib/__init__.pyi

然后，在 ``__init__.pyi`` 中定义function的接口并实现module。

.. code-block:: python

    # 纤维/__init__.pyi
    def fib(n: int) -> int: ...

    # 纤维/__init__.py

    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            b, a = a + b, b
        return a

然后，编写一个test.py用于测试 ``fib`` module。

.. code-block:: python

    # 触摸test.py
    import sys

    from pathlib import Path

    p = Path(__file__).parent / "fib"
    sys.path.append(str(p))

    from fib import fib

    print(fib(10.0))

输出：

.. code-block:: bash

    $ mypy --strict test.py
    test.py:10: error: Argument 1 to "fib" has incompatible type "float"; expected "int"
