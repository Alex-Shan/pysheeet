.. meta::
    :description lang=zh_CN: Python function 速查表涵盖 function 定义、arguments、decorators、lambda、closures 和带有代码示例的 functools
    :keywords: Python, Python3, Python function, Python function cheat sheet, decorator, lambda, closure, *args, **kwargs, functools, lru_cache, partial

========================
函数（Function）
========================

.. contents:: 目录（Table of Contents）
    :backlinks: none

function 可以帮助程序员将逻辑包装到任务中，以避免重复代码。在Python中，function的定义非常通用，我们可以使用decorator、注释、文档字符串、default arguments等许多特性来定义function。在此速查表中，它收集了定义 function 的多种方法，并揭开了 functions 中一些神秘语法的神秘面纱。

为函数编写文档（Document Functions）
------------------------------------------------------

文档为程序员提供了有关如何使用 function 的提示。文档字符串提供了一种编写 functions 可读文档的便捷方法。文档字符串应作为 function 正文中的第一个 statement 放置，并用三引号括起来。可通过 ``__doc__`` attribute 或内置 ``help()`` function 进行访问。 PEP `257 <https://www.python.org/dev/peps/pep-0257>`_ 定义文档字符串的约定， ``pydocstyle`` 等工具可以帮助在代码库中强制执行这些约定。

.. code-block:: python

    >>> def example():
    ...     """This is an example function."""
    ...     print("Example function")
    ...
    >>> example.__doc__
    'This is an example function.'
    >>> help(example)

默认参数（Default Arguments）
----------------------------------------------

在 Python 中定义 function（其中 arguments 是可选的并且具有默认值 value）非常简单。我们可以在定义中分配 values 并确保 default arguments 出现在最后。调用 function 时，您可以省略具有默认值的 arguments，按位置传递它们，或使用关键字语法显式指定它们。这种灵活性使 functions 更加通用，更易于在不同环境中使用。

.. code-block:: python

    >>> def add(a, b=0):
    ...     return a + b
    ...
    >>> add(1)
    1
    >>> add(1, 2)
    3
    >>> add(1, b=2)
    3

.. warning::

    避免将 mutable objects（如 lists 或 dictionaries）用作 default arguments。 Default argument values 仅在定义 function 时评估一次，而不是每次调用 function 时评估。这意味着 mutable 默认值在所有调用之间共享，这可能会导致意外行为，即 function 调用之间的修改仍然存在。

    .. code-block:: python

        >>> def bad(items=[]):  # DON'不这样做
        ...     items.append(1)
        ...     return items
        ...
        >>> bad()
        [1]
        >>> bad()  # 意外！
        [1, 1]

        >>> def good(items=None):  # DO 这个改为
        ...     if items is None:
        ...         items = []
        ...     items.append(1)
        ...     return items

可变参数 ``*args`` 与 ``**kwargs`` （Variable Arguments ``*args`` and ``**kwargs`` ）
------------------------------------------------------------------------------------------------------------------------------------------------------------

Python 可以灵活处理需要接收可变数量 arguments 的 functions。使用 ``*args`` 将任意数量的 positional arguments 收集到 tuple，使用 ``**kwargs`` 将任意数量的 keyword arguments 收集到 dictionary。编写 wrapper functions、decorators，或需要向其他 functions 转发 arguments 的 functions 时，经常使用这两种方式。 ``args`` 和 ``kwargs`` 是惯用名称；在 ``*`` 或 ``**`` 后可以使用任何有效标识符。

.. code-block:: python

    >>> def example(a, b=None, *args, **kwargs):
    ...     print(a, b)
    ...     print(args)
    ...     print(kwargs)
    ...
    >>> example(1, "var", 2, 3, word="hello")
    1 var
    (2, 3)
    {'word': 'hello'}

解包参数（Unpack Arguments）
--------------------------------------------

调用 function 时，您可以使用 ``*`` 将序列（如 list 或 tuple）解包到单独的 positional arguments 中，并使用 ``**`` 将 dictionary 解包到 keyword arguments 中。这是 function 定义中的 ``*args`` 和 ``**kwargs`` 的逆。当您希望将 collection 中的数据传递给需要单独 arguments 的 function 时，解包特别有用。

.. code-block:: python

    >>> def foo(a, b, c='BAZ'):
    ...     print(a, b, c)
    ...
    >>> foo(*("FOO", "BAR"), **{"c": "baz"})
    FOO BAR baz

    >>> args = [1, 2, 3]
    >>> print(*args)
    1 2 3

仅关键字参数（Keyword-Only Arguments）
------------------------------------------------------------

在 function 定义中出现在 ``*`` 或 ``*args`` 之后的 Arguments 仅是关键字，这意味着它们必须按名称传递，不能按位置传递。 Python 3.0 中引入的此功能有助于防止当 functions 有多个 parameters 时出现错误，因为它强制调用者明确他们正在提供哪个 argument。仅关键字 arguments 可以有默认值 values，使它们成为可选的。

**Python新品 3.0**

.. code-block:: python

    >>> def f(a, b, *, kw):
    ...     print(a, b, kw)
    ...
    >>> f(1, 2, kw=3)
    1 2 3
    >>> f(1, 2, 3)
    Traceback (most recent call last):
    TypeError: f() takes 2 positional arguments but 3 were given

    >>> # 仅关键字，默认
    >>> def g(a, *, kw=10):
    ...     return a + kw
    ...
    >>> g(5)
    15

仅位置参数（Positional-Only Arguments）
----------------------------------------------------------------

在 function 定义中出现在 ``/`` 之前的 Arguments 是仅位置的， 这意味着它们不能通过关键字名称传递。 这个功能， 在Python 3.8中引入， 当 parameter 名称对调用者没有意义或当您想要保留更改 parameter 名称而不破坏现有代码的灵活性时，此选项非常有用。 许多内置 functions（如 ``len()`` 和 ``pow()`` ）使用仅位置 parameters。 您可以在同一个 function 中组合仅位置 ( ``/`` ) 和仅关键字 ( ``*`` )。

**Python新品 3.8**

.. code-block:: python

    >>> def f(a, b, /, c):
    ...     print(a, b, c)
    ...
    >>> f(1, 2, 3)
    1 2 3
    >>> f(1, 2, c=3)
    1 2 3
    >>> f(a=1, b=2, c=3)
    Traceback (most recent call last):
    TypeError: f() got some positional-only arguments passed as keyword arguments

    >>> # 结合仅位置和仅关键字
    >>> def g(a, /, b, *, c):
    ...     return a + b + c
    ...
    >>> g(1, 2, c=3)
    6

标注（Annotations）
------------------------------

Function 注释提供了一种将元数据附加到 function、parameters 和 return values 的方法。虽然 Python 不在运行时强制执行这些注释，但它们充当文档，并由 ``mypy`` 等静态 type 检查器使用，以在代码运行之前捕获 type 错误。注释作为 dictionary 存储在 function 的 ``__annotations__`` attribute 中。 ``typing`` module (Python 3.5+) 提供额外的 types，如 ``List`` 、 ``Dict`` 、 ``Optional`` 和 ``Union`` ，以获得更具表现力的 type hints。

**Python新品 3.0**

.. code-block:: python

    >>> def fib(n: int) -> int:
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         b, a = a + b, b
    ...     return a
    ...
    >>> fib(10)
    55
    >>> fib.__annotations__
    {'n': <class 'int'>, 'return': <class 'int'>}

Lambda 表达式（Lambda）
------------------------------------

Lambda expressions 创建小型匿名 functions 内联。它们在语法上仅限于隐式返回的单个 expression。 Lambdas 对于短的、一次性的 functions 非常有用，尤其是 arguments 到高阶 functions，如 ``sorted()`` 、 ``map()`` 、 ``filter()`` 和 ``reduce()`` 。虽然 lambdas 可以使代码更加简洁，但 complex 逻辑应该编写为常规名称 functions 以获得更好的可读性和 debugging。

.. code-block:: python

    >>> square = lambda x: x ** 2
    >>> square(5)
    25

    >>> # lambda 与多个 arguments
    >>> add = lambda a, b: a + b
    >>> add(2, 3)
    5

    >>> # lambda 有条件
    >>> max_val = lambda a, b: a if a > b else b
    >>> max_val(3, 5)
    5

    >>> # 常用：排序key
    >>> pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
    >>> sorted(pairs, key=lambda x: x[1])
    [(2, 'a'), (1, 'b'), (3, 'c')]

可调用（Callable）
--------------------------

在Python中，任何实现 ``__call__`` method的object都是可调用的，这意味着它可以像function一样使用括号来调用。这包括 functions、methods、lambdas、classes（调用 class 创建 instance）以及定义 ``__call__`` 的 classes 的 instances。如果 object 显示为可调用，内置 ``callable()`` function 返回 ``True`` ，这对于在尝试调用 object 之前进行检查以避免 ``TypeError`` exceptions 很有用。

.. code-block:: python

    >>> callable(print)
    True
    >>> callable(42)
    False

    >>> class Adder:
    ...     def __init__(self, n):
    ...         self.n = n
    ...     def __call__(self, x):
    ...         return self.n + x
    ...
    >>> add_five = Adder(5)
    >>> callable(add_five)
    True
    >>> add_five(10)
    15

获取函数名称（Get Function Name）
--------------------------------------------------

Python 中的 Functions 首先是 class objects 以及提供有关它们的元数据的各种 attributes。 ``__name__`` attribute 包含所定义的 function 的名称， ``__doc__`` 包含文档字符串， ``__module__`` 指示 function 是在哪个 module 中定义的， ``__annotations__`` 包含 type hints。这些 attributes 对于 debugging、日志记录和内省很有用。

.. code-block:: python

    >>> def example_function():
    ...     """Example docstring."""
    ...     pass
    ...
    >>> example_function.__name__
    'example_function'
    >>> example_function.__doc__
    'Example docstring.'
    >>> example_function.__module__
    '__main__'

闭包（Closure）
----------------------

closure 是一个 function，它从其封闭的词法 scope 中捕获并记住 values，即使在 scope 完成执行之后也是如此。当嵌套 function 从其外部 function 引用 variables 时，会发生这种情况。 Closures 功能强大，可用于创建 function 工厂（返回自定义 functions 的 functions）、实现 decorators 以及在不使用全局 variables 或 classes 的情况下维护状态。使用 ``nonlocal`` 关键字修改从封闭的 scope 捕获的 variables。

.. code-block:: python

    >>> def make_multiplier(n):
    ...     def multiplier(x):
    ...         return x * n
    ...     return multiplier
    ...
    >>> double = make_multiplier(2)
    >>> triple = make_multiplier(3)
    >>> double(5)
    10
    >>> triple(5)
    15

    >>> # closure 与 mutable 状态
    >>> def make_counter():
    ...     count = 0
    ...     def counter():
    ...         nonlocal count
    ...         count += 1
    ...         return count
    ...     return counter
    ...
    >>> counter = make_counter()
    >>> counter()
    1
    >>> counter()
    2

生成器（Generator）
----------------------------

Generator functions 使用 ``yield`` statement 一次一个地延迟生成一系列 values，而不是预先计算所有 values 并将它们存储在内存中。调用时，generator function 返回 generator iterator，可以使用 ``for`` loops 或 ``next()`` 进行迭代。 Generators 对于大型序列来说具有内存效率，并且可以表示无限序列。 Generator expressions 提供类似于 list comprehensions 的简洁语法，但具有惰性求值。

.. code-block:: python

    >>> def fib(n):
    ...     a, b = 0, 1
    ...     for _ in range(n):
    ...         yield a
    ...         b, a = a + b, b
    ...
    >>> list(fib(10))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    >>> # generator expression
    >>> squares = (x**2 for x in range(5))
    >>> list(squares)
    [0, 1, 4, 9, 16]

装饰器（Decorator）
----------------------------

Decorators 是一种强大的模式，可以在不修改 functions 源码的情况下修改或扩展其行为。Decorator 是一个接收 function 并返回新 function 的 function；返回值通常是 wrapper，在调用原 function 前后增加功能。 ``@decorator`` 语法是 ``func = decorator(func)`` 的 syntactic sugar。应在 wrapper function 中使用 ``functools`` 提供的 ``@wraps`` ，保留原 function 的 ``__name__`` 、 ``__doc__`` 和 ``__annotations__`` 等 metadata。

**Python 中的新功能 2.4** - PEP `318 <https://www.python.org/dev/peps/pep-0318/>`_

.. code-block:: python

    >>> from functools import wraps
    >>> def log_calls(func):
    ...     @wraps(func)
    ...     def wrapper(*args, **kwargs):
    ...         print(f"Calling {func.__name__}")
    ...         return func(*args, **kwargs)
    ...     return wrapper
    ...
    >>> @log_calls
    ... def greet(name):
    ...     return f"Hello, {name}!"
    ...
    >>> greet("Alice")
    Calling greet
    'Hello, Alice!'

    >>> # 相当于：
    >>> # greet = log_calls(greet)

.. note::

    始终在decorators中使用 ``@wraps(func)`` ，以保留原始function的 ``__name__`` 、 ``__doc__`` 和其他attributes。如果没有它，装饰后的 function 将具有包装器的 attributes，这使得 debugging 更难。

带参数的装饰器（Decorator with Arguments）
------------------------------------------------------------------

要创建接受 arguments 的 decorator，您需要额外的嵌套层。最外面的function采用decorator的arguments并返回实际的decorator。中间的 function 接受被装饰的 function 并返回包装器。最里面的 function 是调用修饰后的 function 时执行的包装器。此模式通常用于 decorators，如 ``@repeat(3)`` 或 ``@route('/path')`` 。

.. code-block:: python

    >>> from functools import wraps
    >>> def repeat(times):
    ...     def decorator(func):
    ...         @wraps(func)
    ...         def wrapper(*args, **kwargs):
    ...             for _ in range(times):
    ...                 result = func(*args, **kwargs)
    ...             return result
    ...         return wrapper
    ...     return decorator
    ...
    >>> @repeat(3)
    ... def say_hello():
    ...     print("Hello!")
    ...
    >>> say_hello()
    Hello!
    Hello!
    Hello!

    >>> # 相当于：
    >>> # say_hello = repeat(3)(say_hello)

类装饰器（Class Decorator）
------------------------------------------

Decorators 也可以实现为 classes，而不是 functions。基于 class 的 decorator 实现 ``__init__`` 来接收修饰后的 function 和 ``__call__`` 来充当包装器。当 decorator 需要在对修饰的 function 的多个调用中维护状态（例如对调用进行计数、caching 结果或跟踪计时信息）时，此方法非常有用。

.. code-block:: python

    >>> class CountCalls:
    ...     def __init__(self, func):
    ...         self.func = func
    ...         self.count = 0
    ...     def __call__(self, *args, **kwargs):
    ...         self.count += 1
    ...         return self.func(*args, **kwargs)
    ...
    >>> @CountCalls
    ... def example():
    ...     return "result"
    ...
    >>> example()
    'result'
    >>> example()
    'result'
    >>> example.count
    2

使用 ``lru_cache`` 缓存（Cache with ``lru_cache`` ）
--------------------------------------------------------------------------------------------

``functools`` 中的 ``lru_cache`` decorator 根据传递的 arguments 自动缓存 function 结果。当再次用相同的arguments调用function时，返回cached结果而不是重新计算它。这对于昂贵的计算或像斐波那契这样的 recursive functions 特别有用。 ``maxsize`` parameter 限制了 cache 的大小（使用 ``None`` 则无限制）。使用 ``cache_info()`` 查看命中/未命中统计数据，使用 ``cache_clear()`` 重置 cache。

**Python新品 3.2**

.. code-block:: python

    >>> from functools import lru_cache
    >>> @lru_cache(maxsize=None)
    ... def fib(n):
    ...     if n < 2:
    ...         return n
    ...     return fib(n - 1) + fib(n - 2)
    ...
    >>> fib(100)
    354224848179261915075
    >>> fib.cache_info()
    CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
    >>> fib.cache_clear()  # 清除cache

**Python 中的新功能 3.9** - ``@cache`` 是 ``@lru_cache(maxsize=None)`` 的更简单别名

.. code-block:: python

    >>> from functools import cache
    >>> @cache
    ... def factorial(n):
    ...     return n * factorial(n-1) if n else 1

偏函数（Partial Functions）
--------------------------------------------

``functools.partial`` function 创建了一个新的可调用对象，其中预填充了原始 function 的一些 arguments。这对于使 functions 适应需要较少 arguments 的接口、创建通用 functions 的专用版本或准备 callback functions 非常有用。生成的部分 object 可以与剩余的 arguments 一起调用。您可以预填写位置和 keyword arguments。

.. code-block:: python

    >>> from functools import partial
    >>> def power(base, exponent):
    ...     return base ** exponent
    ...
    >>> square = partial(power, exponent=2)
    >>> cube = partial(power, exponent=3)
    >>> square(5)
    25
    >>> cube(5)
    125

    >>> # 适用于 callbacks
    >>> from functools import partial
    >>> def greet(greeting, name):
    ...     return f"{greeting}, {name}!"
    ...
    >>> say_hello = partial(greet, "Hello")
    >>> say_hello("Alice")
    'Hello, Alice!'

``singledispatch`` - 函数重载（ ``singledispatch`` - Function Overloading）
------------------------------------------------------------------------------------------------------------------------------------------

``functools`` 中的 ``singledispatch`` decorator 在第一个 argument 的 type 的基础上启用 function 重载。您定义一个基础 function，然后使用 ``@func.register`` decorator 注册不同 types 的专用实现。当调用function时，Python会根据argument的type自动调度到适当的实现。这对于编写对于不同的 types 具有不同行为的通用 functions 非常有用。

**Python新品 3.4**

.. code-block:: python

    >>> from functools import singledispatch
    >>> @singledispatch
    ... def process(arg):
    ...     return f"Default: {arg}"
    ...
    >>> @process.register(int)
    ... def _(arg):
    ...     return f"Integer: {arg * 2}"
    ...
    >>> @process.register(list)
    ... def _(arg):
    ...     return f"List with {len(arg)} items"
    ...
    >>> process("hello")
    'Default: hello'
    >>> process(5)
    'Integer: 10'
    >>> process([1, 2, 3])
    'List with 3 items'

``reduce`` - 累积运算（ ``reduce`` - Cumulative Operations）
------------------------------------------------------------------------------------------------------------

``functools`` 中的 ``reduce`` function 将两个 argument function 从左到右累加到序列的 items，从而将序列减少为单个 value。例如， ``reduce(f, [a, b, c, d])`` 计算 ``f(f(f(a, b), c), d)`` 。可选的第三个 argument 提供初始 value。虽然 ``reduce`` 功能强大，但对于简单情况，list comprehensions 或显式 loops 通常更具可读性。

.. code-block:: python

    >>> from functools import reduce
    >>> # list 之和
    >>> reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])
    15

    >>> # list的产品
    >>> reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])
    120

    >>> # 开头为 value
    >>> reduce(lambda x, y: x + y, [1, 2, 3], 10)
    16

高阶函数（Higher-Order Functions）
--------------------------------------------------------

高阶functions是将其他functions作为arguments或返回functions作为结果的functions。 Python 提供了几个常用于函数式编程模式的内置高阶 functions。 ``map()`` 将 function 应用于 iterable 中的每个 item， ``filter()`` 保留 items，其中 function 返回 ``True`` ，并且 ``sorted()`` / ``min()`` / ``max()`` 接受 ``key`` function 进行自定义比较。这些 functions 返回 iterators（ ``sorted`` 除外），因此如果您需要 list，请将它们包装在 ``list()`` 中。

.. code-block:: python

    >>> # 映射 - 将 function 应用于每个 item
    >>> list(map(lambda x: x**2, [1, 2, 3, 4]))
    [1, 4, 9, 16]

    >>> # 过滤器 - 保留 items，其中 function 返回 True
    >>> list(filter(lambda x: x > 2, [1, 2, 3, 4]))
    [3, 4]

    >>> # 按 key function 排序
    >>> sorted(['banana', 'apple', 'cherry'], key=len)
    ['apple', 'banana', 'cherry']

    >>> # 最小/最大 key function
    >>> max(['apple', 'banana', 'cherry'], key=len)
    'banana'
