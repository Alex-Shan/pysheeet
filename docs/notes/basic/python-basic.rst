.. meta::
    :description lang=zh_CN: Python 基础教程涵盖基本语法、data types、控制流、string 格式化和基本 Python 编程概念
    :keywords: Python, Python3, basics, syntax, data types, control flow, string formatting, variables, operators, conditionals

====================================
从头开始（From Scratch）
====================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

本速查表的主要目标是收集一些常见且基本的语义或片段。速查表包括一些我们已经知道但在我们脑海中仍然模糊的语法，或者一些我们一次又一次谷歌搜索的片段。此外，由于 **Python 2** 的生命周期结束日期即将到来。大多数代码片段主要基于 **Python 3** 的语法。


你好世界！（Hello world!）
--------------------------------------

当我们开始学习一门新语言时，我们通常是通过打印 **Hello world!** 来学习的。在Python中，我们可以使用另一种方式来打印消息，即导入 ``__hello__`` module。源代码可以在 `frozen.c <https://github.com/python/cpython/blob/master/Python/frozen.c>`_ 上找到。

.. code-block:: python

    >>> print("Hello world!")
    Hello world!
    >>> import __hello__
    Hello world!
    >>> import __phello__
    Hello world!
    >>> import __phello__.spam
    Hello world!


Python版本（Python Version）
------------------------------------------------

对于程序员来说，了解当前的 Python 版本非常重要，因为并非所有语法都适用于当前版本。在这种情况下，我们可以通过 ``python -V`` 或使用module、 ``sys`` 来获取Python版本。

.. code-block:: python

    >>> import sys
    >>> print(sys.version)
    3.7.1 (default, Nov  6 2018, 18:46:03)
    [Clang 10.0.0 (clang-1000.11.45.5)]

我们还可以使用 ``platform.python_version`` 来获取 Python 版本。

.. code-block:: python

    >>> import platform
    >>> platform.python_version()
    '3.7.1'

有时，检查当前的 Python 版本很重要，因为我们可能希望在某些特定版本中启用某些功能。 ``sys.version_info`` 提供了有关 interpreter 的更多详细信息。我们可以用它来和我们想要的版本进行比较。

.. code-block:: python

    >>> import sys
    >>> sys.version_info >= (3, 6)
    True
    >>> sys.version_info >= (3, 7)
    False

省略号（Ellipsis）
--------------------------

`省略号（Ellipsis） <https://docs.python.org/3/library/constants.html#Ellipsis>`_ 是内置 constant。在Python 3.0之后，我们使用 ``...`` 作为 ``Ellipsis`` 。可能是Python中最神秘的constant。根据官方文档，我们可以用它来扩展切片语法。尽管如此，type 提示、存根文件或 function expressions 中还有一些其他约定。

.. code-block:: python

    >>> ...
    Ellipsis
    >>> ... == Ellipsis
    True
    >>> type(...)
    <class 'ellipsis'>

下面的代码片段显示我们可以使用省略号来表示尚未实现的 function 或 class。

.. code-block:: python

    >>> class Foo: ...
    ...
    >>> def foo(): ...
    ...

if ... elif ... else 条件语句（if ... elif ... else）
----------------------------------------------------------------------------------------------

**if 语句** 用于控制代码流。 Python 使用 ``if ... elif ... else`` 序列，而不是使用 ``switch`` 或 ``case`` statements 控制代码的逻辑。尽管有人建议我们可以使用 ``dict`` 来实现 ``switch`` statements，但这种解决方案可能会带来不必要的开销，例如创建一次性 dictionaries 并破坏可读代码。因此，不推荐该解决方案。

.. code-block:: python

    >>> import random
    >>> num = random.randint(0, 10)
    >>> if num < 3:
    ...     print("less than 3")
    ... elif num < 5:
    ...     print("less than 5")
    ... else:
    ...     print(num)
    ...
    less than 3

for 循环（for Loop）
--------------------------------

在Python中，我们可以直接通过 **for语句** 来访问iterable object的items。如果我们需要同时获取iterable object（例如list或tuple）的indexes和items，则使用 ``enumerate`` 比 ``range(len(iterable))`` 更好。更多信息请参见 `Looping Techniques <https://docs.python.org/3/tutorial/datastructures.html#looping-techniques>`_ 。

.. code-block:: python

    >>> for val in ["foo", "bar"]:
    ...     print(val)
    ...
    foo
    bar
    >>> for idx, val in enumerate(["foo", "bar", "baz"]):
    ...     print(idx, val)
    ...
    (0, 'foo')
    (1, 'bar')
    (2, 'baz')

for ... else ... 语句（for ... else ...）
--------------------------------------------------------------------------

当我们第一次看到 ``else`` 属于 ``for`` loop时，可能会有点奇怪。 ``else`` 子句可以帮助我们避免在loops中使用标志variables。 loop 的 ``else`` 子句在未发生中断时运行。

.. code-block:: python

    >>> for _ in range(5):
    ...     pass
    ... else:
    ...     print("no break")
    ...
    no break

以下代码片段显示了使用标志 variable 和 ``else`` 子句来控制 loop 之间的区别。我们可以看到，当 ``break`` 出现在loop中时， ``else`` 并没有运行。

.. code-block:: python

    >>> is_break = False
    >>> for x in range(5):
    ...     if x % 2 == 0:
    ...         is_break = True
    ...         break
    ...
    >>> if is_break:
    ...     print("break")
    ...
    break

    >>> for x in range(5):
    ...     if x % 2 == 0:
    ...         print("break")
    ...         break
    ... else:
    ...     print("no break")
    ...
    break

使用 ``range`` （Using ``range`` ）
--------------------------------------------------------------

Python 2中 ``range`` 的问题是，如果我们需要多次迭代loop， ``range`` 可能会占用大量内存。因此，建议在 Python 2 中使用 ``xrange`` 。

.. code-block:: python

    >>> import platform
    >>> import sys
    >>> platform.python_version()
    '2.7.15'
    >>> sys.getsizeof(range(100000000))
    800000072
    >>> sys.getsizeof(xrange(100000000))
    40

在Python 3中，内置function ``range`` 返回iterable **range对象** 而不是list。 ``range`` 的行为与 Python 2 中的 ``xrange`` 相同。因此，如果我们想在 loop 中多次运行代码块，则使用 ``range`` 不再占用大量内存。更多信息请参见 PEP `3100 <https://www.python.org/dev/peps/pep-3100>`_ 。

.. code-block:: python

    >>> import platform
    >>> import sys
    >>> platform.python_version()
    '3.7.1'
    >>> sys.getsizeof(range(100000000))
    48

while ... else ... 语句（while ... else ...）
----------------------------------------------------------------------------------

``else`` 子句属于 while loop，与 for loop 中的 ``else`` 子句具有相同的用途。我们可以观察到，当 ``break`` 出现在 loop 中时， ``else`` 不会运行。

.. code-block:: python

    >>> n = 0
    >>> while n < 5:
    ...     if n == 3:
    ...         break
    ...     n += 1
    ... else:
    ...     print("no break")
    ...

do while 语句（The ``do while`` Statement）
------------------------------------------------------------------------------

有许多编程语言，例如C/C++、Ruby或Javascript，提供了 ``do while`` statement。在Python中，没有 ``do while`` statement。但是，我们可以将条件和 ``break`` 放在 ``while`` loop 的末尾来实现相同的效果。

.. code-block:: python

    >>> n = 0
    >>> while True:
    ...     n += 1
    ...     if n == 5:
    ...         break
    ...
    >>> n
    5

try ... except ... else ... 语句（try ... except ... else ...）
----------------------------------------------------------------------------------------------------------------------

大多数时候，我们在 ``except`` 子句中处理错误并在 ``finally`` 子句中清理资源。有趣的是， ``try`` statement 还为我们提供了一个 ``else`` 子句，以避免捕获由不应受 ``try ... except`` 保护的代码引发的 exception。当 ``try`` 和 ``except`` 之间没有出现 exception 时， ``else`` 子句运行。

.. code-block:: python

    >>> try:
    ...     print("No exception")
    ... except:
    ...     pass
    ... else:
    ...     print("Success")
    ...
    No exception
    Success

字符串（String）
----------------------

与其他编程语言不同，Python 不直接支持 string 的 item 赋值。因此，如果需要操作string的items、e.g、交换items，我们必须将string转换为list，并在series item赋值完成后进行连接操作。

.. code-block:: python

    >>> a = "Hello Python"
    >>> l = list(a)
    >>> l[0], l[6] = 'h', 'p'
    >>> ''.join(l)
    'hello python'

列表（List）
----------------

Lists 是多功能容器。 Python提供了 **负索引**、**切片语句**或**list comprehension** 等多种方式来操作lists。以下代码片段显示了 lists 的一些常见操作。

.. code-block:: python

    >>> a = [1, 2, 3, 4, 5]
    >>> a[-1]                     # 负向 index
    5
    >>> a[1:]                     # 切片
    [2, 3, 4, 5]
    >>> a[1:-1]
    [2, 3, 4]
    >>> a[1:-1:2]
    [2, 4]
    >>> a[::-1]                   # 反转
    [5, 4, 3, 2, 1]
    >>> a[0] = 0                  # 设置 item
    >>> a
    [0, 2, 3, 4, 5]
    >>> a.append(6)               # 附加 item
    >>> a
    [0, 2, 3, 4, 5, 6]
    >>> del a[-1]                 # 删除 item
    >>> a
    [0, 2, 3, 4, 5]
    >>> b = [x for x in range(3)] # list comprehension
    >>> b
    [0, 1, 2]
    >>> a + b                     # 添加两个lists
    [0, 2, 3, 4, 5, 0, 1, 2]

字典（Dict）
----------------

Dictionaries是key-value成对容器。与 lists 一样，Python 支持多种方式（例如 **字典推导式** ）来操作 dictionaries。在Python 3.6之后，dictionaries保留keys的插入顺序。以下代码片段显示了 dictionaries 的一些常见操作。

.. code-block:: python

    >>> d = {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}
    >>> d
    {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}
    >>> d['timmy'] = "yellow"        # set数据
    >>> d
    {'timmy': 'yellow', 'barry': 'green', 'guido': 'blue'}
    >>> del d['guido']               # 删除数据
    >>> d
    >>> 'guido' in d                 # 包含数据
    False
    {'timmy': 'yellow', 'barry': 'green'}
    >>> {k: v for k ,v in d.items()} # dict comprehension
    {'timmy': 'yellow', 'barry': 'green'}
    >>> d.keys()                     # list 全部 keys
    dict_keys(['timmy', 'barry'])
    >>> d.values()                   # list 全部 values
    dict_values(['yellow', 'green'])

函数（Function）
------------------------

在Python中定义function是灵活的。我们可以用 **定义一个function，函数文档**，**默认值**，**任意参数**，**关键字参数**，** 仅关键字参数** ，依此类推。以下代码片段显示了一些常见的 expressions 来定义 functions。

.. code-block:: python

    def foo_with_doc():
        """Documentation String."""

    def foo_with_arg(arg): ...
    def foo_with_args(*arg): ...
    def foo_with_kwarg(a, b="foo"): ...
    def foo_with_args_kwargs(*args, **kwargs): ...
    def foo_with_kwonly(a, b, *, k): ...           # 蟒蛇3
    def foo_with_annotations(a: int) -> int: ...   # 蟒蛇3

函数标注（Function Annotations）
----------------------------------------------------

我们可以通过 **函数注释** 来表示 types，而不是在 functions 中编写 string 文档来暗示 parameters 和 return values 的 type。 Function注释，详细信息可以在PEP、 `3017 <https://www.python.org/dev/peps/pep-3107>`_ 和PEP、 `484 <https://www.python.org/dev/peps/pep-0484/>`_ 上找到，在Python 3.0中进行了介绍。它们是 **Python 3**中的** 可选 **功能。使用 function 注释将失去**Python 2** 中的兼容性。我们可以通过存根文件来解决这个问题。另外，我们还可以通过 `mypy <http://mypy-lang.org/>`_ 进行静态type检查。

.. code-block:: python

    >>> def fib(n: int) -> int:
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         b, a = a + b, b
    ...     return a
    ...
    >>> fib(10)
    55

生成器（Generators）
------------------------------

Python 使用 ``yield`` statement 定义 **生成器函数** 。换句话说，当我们调用generator function时，generator function将返回 **generator**而不是return values来创建**iterator** 。

.. code-block:: python

    >>> def fib(n):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         yield a
    ...         b, a = a + b, b
    ...
    >>> g = fib(10)
    >>> g
    <generator object fib at 0x10b240c78>
    >>> for f in fib(5):
    ...     print(f)
    ...
    0
    1
    1
    2
    3

生成器委托（Generator Delegation）
------------------------------------------------------

Python 3.3介绍了 ``yield from`` expression。它允许 generator 将部分操作委托给另一个 generator。换句话说，我们可以在当前 **生成器函数**中从**yield**一个序列**from**其他**生成器** 。更多信息请参见 PEP `380 <https://www.python.org/dev/peps/pep-0380>`_ 。

.. code-block:: python

    >>> def fib(n):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         yield a
    ...         b, a = a + b, b
    ...
    >>> def fibonacci(n):
    ...     yield from fib(n)
    ...
    >>> [f for f in fibonacci(5)]
    [0, 1, 1, 2, 3]

类（Class）
----------------

Python支持很多常用功能如 **类文件**、**多重继承**、**类变量**、**实例变量**、**静态方法**、**类方法**等。此外，Python还提供了一些special methods供程序员实现**迭代器**、**上下文管理器** 等。以下代码片段显示了class的常见定义。

.. code-block:: python

    class A: ...
    class B: ...
    class Foo(A, B):
        """A class document."""

        foo = "class variable"

        def __init__(self, v):
            self.attr = v
            self.__private = "private var"

        @staticmethod
        def bar_static_method(): ...

        @classmethod
        def bar_class_method(cls): ...

        def bar(self):
            """A method document."""

        def bar_with_arg(self, arg): ...
        def bar_with_args(self, *args): ...
        def bar_with_kwarg(self, kwarg="bar"): ...
        def bar_with_args_kwargs(self, *args, **kwargs): ...
        def bar_with_kwonly(self, *, k): ...
        def bar_with_annotations(self, a: int): ...

``async`` / ``await`` 用法（ ``async`` / ``await`` ）
--------------------------------------------------------------------------------------------------

``async`` 和 ``await`` 语法是从 Python 3.5 引入的。它们设计用于与 event loop 一起使用。其他一些功能，例如 **异步发电机** 在后续版本中实现。

**协程函数**（ ``async def`` ）用于为event loop创建**协程**。 Python 提供内置的 module、**asyncio**，通过 ``async`` / ``await`` 语法编写并发代码。以下代码片段显示了使用**asyncio** 的简单示例。该代码必须在 Python 3.7 或更高版本上运行。

.. code-block:: python

    import asyncio

    async def http_ok(r, w):
        head = b"HTTP/1.1 200 OK\r\n"
        head += b"Content-Type: text/html\r\n"
        head += b"\r\n"

        body = b"<html>"
        body += b"<body><h1>Hello world!</h1></body>"
        body += b"</html>"

        _ = await r.read(1024)
        w.write(head + body)
        await w.drain()
        w.close()

    async def main():
        server = await asyncio.start_server(
            http_ok, "127.0.0.1", 8888
        )

        async with server:
            await server.serve_forever()

    asyncio.run(main())

避免 ``exec`` 和 ``eval`` （Avoid ``exec`` and ``eval`` ）
----------------------------------------------------------------------------------------------------------

以下代码片段展示了如何使用内置 function ``exec`` 。然而，由于一些安全问题和人类不可读的代码，不建议使用 ``exec`` 和 ``eval`` 。进一步阅读可在 `Be careful with exec and eval in Python <http://lucumr.pocoo.org/2011/2/1/exec-in-python/>`_ 和 `Eval really is dangerous <https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html>`_ 上找到


.. code-block:: python

    >>> py = '''
    ... def fib(n):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         b, a = b + a, b
    ...     return a
    ... print(fib(10))
    ... '''
    >>> exec(py, globals(), locals())
    55
