.. meta::
    :description lang=zh_CN: Python generator 速查表涵盖 generator functions、generator expressions、yield、yield from、send、async generators 和 coroutines 以及代码示例
    :keywords: Python, Python3, Python generator, Python generator cheat sheet, yield, yield from, generator expression, async generator, iterator, coroutine, contextmanager

============================
生成器（Generator）
============================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Generators 是 Python 中用于创建 iterators 的强大功能。它们允许您迭代数据，而无需将整个序列存储在内存中，这使得它们非常适合处理大型数据集或无限序列。本速查表涵盖了 generator、functions、generator expressions、 ``yield`` 、 ``yield from`` 、发送 values 到 generators 以及异步 generators。

生成器函数与生成器表达式（Generator Function vs Generator Expression）
----------------------------------------------------------------------------------------------------------------

generator function 的定义与普通 function 类似，但使用 ``yield`` 生成 values 序列。调用时，它返回可迭代的 generator object。 generator expression 是类似于 list comprehensions 的紧凑语法，但根据需要延迟生成 values。

.. code-block:: python

    # generator function
    >>> def gen_func():
    ...     yield 5566
    ...
    >>> g = gen_func()
    >>> g
    <generator object gen_func at 0x...>
    >>> next(g)
    5566

    # generator expression
    >>> g = (x for x in range(3))
    >>> next(g)
    0
    >>> next(g)
    1

从生成器产出值（Yield Values from Generator）
------------------------------------------------------------------------

``yield`` statement 生成 value 并暂停 generator 的执行。当再次调用 ``next()`` 时，将从中断处恢复执行。此示例通过检查每个候选数的整除性来生成素数。

.. code-block:: python

    >>> def prime(n):
    ...     p = 2
    ...     while n > 0:
    ...         for x in range(2, p):
    ...             if p % x == 0:
    ...                 break
    ...         else:
    ...             yield p
    ...             n -= 1
    ...         p += 1
    ...
    >>> list(prime(5))
    [2, 3, 5, 7, 11]

解包生成器（Unpack Generators）
------------------------------------------------

Python 3.5+ (PEP 448) 允许使用以下命令将 generators 直接解包为 lists、sets、function、arguments 和 variables ``*`` operator。这提供了一种方便的方式来使用 generator values，而无需显式 iteration。

.. code-block:: python

    # PEP 448 - 在 list 内拆包
    >>> g1 = (x for x in range(3))
    >>> g2 = (x**2 for x in range(2))
    >>> [1, *g1, 2, *g2]
    [1, 0, 1, 2, 2, 0, 1]

    # 在 set 内拆箱
    >>> g = (x for x in [5, 5, 6, 6])
    >>> {*g}
    {5, 6}

    # 拆包至 variables
    >>> g = (x for x in range(3))
    >>> a, b, c = g
    >>> a, b, c
    (0, 1, 2)

    # 扩展拆包
    >>> g = (x for x in range(6))
    >>> a, b, *c, d = g
    >>> a, b, d
    (0, 1, 5)
    >>> c
    [2, 3, 4]

    # 在 function 内拆箱
    >>> print(*(x for x in range(3)))
    0 1 2

通过生成器的可迭代类（Iterable Class via Generator）
--------------------------------------------------------------------------------

您可以通过将 ``__iter__`` 实现为 generator method 来制作 class iterable。这种方法比实现单独的 iterator class 更干净。 ``__reversed__`` method 也可以实现为 generator，以支持内置 ``reversed()`` function。

.. code-block:: python

    >>> class Count:
    ...     def __init__(self, n):
    ...         self._n = n
    ...     def __iter__(self):
    ...         n = self._n
    ...         while n > 0:
    ...             yield n
    ...             n -= 1
    ...     def __reversed__(self):
    ...         n = 1
    ...         while n <= self._n:
    ...             yield n
    ...             n += 1
    ...
    >>> list(Count(5))
    [5, 4, 3, 2, 1]
    >>> list(reversed(Count(5)))
    [1, 2, 3, 4, 5]

将值发送到生成器（Send Values to Generator）
--------------------------------------------------------------------

Generators 可以通过 ``send()`` method 接收 values。传入的 value 会成为 generator 内部 ``yield`` expression 的结果。在发送 values 之前，必须先调用 ``next()`` 或 ``send(None)`` ，将 generator 推进到第一个 ``yield`` 。

.. code-block:: python

    >>> def spam():
    ...     msg = yield
    ...     print("Message:", msg)
    ...
    >>> g = spam()
    >>> next(g)  # 启动 generator
    >>> try:
    ...     g.send("Hello World!")
    ... except StopIteration:
    ...     pass
    Message: Hello World!

yield from 表达式（yield from Expression）
--------------------------------------------------------------------------

``yield from`` expression 将 iteration 委托给另一个 generator 或 iterable。它自动处理将 ``send()`` 、 ``throw()`` 和 ``close()`` 调用转发到子生成器，使其成为创建 generator 管道和 recursive generators 的理想选择。

.. code-block:: python

    >>> def subgen():
    ...     try:
    ...         yield 9527
    ...     except ValueError:
    ...         print("got ValueError")
    ...
    >>> def delegating_gen():
    ...     yield from subgen()
    ...
    >>> g = delegating_gen()
    >>> next(g)
    9527
    >>> try:
    ...     g.throw(ValueError)
    ... except StopIteration:
    ...     pass
    got ValueError

您可以将多个 ``yield from`` expressions 链接在一起。 ``inspect.getgeneratorstate()`` function 通过以下状态帮助跟踪 generator 的生命周期：GEN_CREATED、GEN_RUNNING、GEN_SUSPENDED 和 GEN_CLOSED。

.. code-block:: python

    # 产量 + 产量
    >>> import inspect
    >>> def subgen():
    ...     yield from range(3)
    ...
    >>> def delegating_gen():
    ...     yield from subgen()
    ...
    >>> g = delegating_gen()
    >>> inspect.getgeneratorstate(g)
    'GEN_CREATED'
    >>> next(g)
    0
    >>> inspect.getgeneratorstate(g)
    'GEN_SUSPENDED'
    >>> g.close()
    >>> inspect.getgeneratorstate(g)
    'GEN_CLOSED'

带返回值的 yield from（yield from with Return）
--------------------------------------------------------------------------------

Generators 可以使用 ``return`` statement 返回 value。返回的 value 可通过 ``StopIteration`` exception 的 ``value`` attribute 访问。当使用 ``yield from`` 时，副发电机的return value变为 ``yield from`` expression的value。

.. code-block:: python

    >>> def average():
    ...     total = .0
    ...     count = 0
    ...     while True:
    ...         val = yield
    ...         if not val:
    ...             break
    ...         total += val
    ...         count += 1
    ...     return total / count
    ...
    >>> g = average()
    >>> next(g)
    >>> g.send(3)
    >>> g.send(5)
    >>> try:
    ...     g.send(None)
    ... except StopIteration as e:
    ...     print(e.value)
    4.0

.. code-block:: python

    >>> def subgen():
    ...     yield 9527
    ...
    >>> def delegating_gen():
    ...     yield from subgen()
    ...     return 5566
    ...
    >>> g = delegating_gen()
    >>> next(g)
    9527
    >>> try:
    ...     next(g)
    ... except StopIteration as e:
    ...     print(e.value)
    5566

生成序列（Generate Sequences）
------------------------------------------------

``yield from`` expression 提供了一种从 iterable 生成所有 values 的简洁方法。这对于将多个序列链接在一​​起或展平嵌套结构特别有用。

.. code-block:: python

    >>> def chain():
    ...     yield from 'ab'
    ...     yield from range(3)
    ...
    >>> list(chain())
    ['a', 'b', 0, 1, 2]

``RES = yield from EXP`` 的作用（What ``RES = yield from EXP`` Does）
--------------------------------------------------------------------------------------------------------------------------------

此代码片段显示了 ``yield from`` 内部执行的简化等效项，如 PEP 380 中所述。它处理通过 ``send()`` 传递的 iteration、value，并从子生成器捕获 return value。

.. code-block:: python

    # 简化版（参考：PEP 380）
    >>> def subgen():
    ...     for x in range(3):
    ...         yield x
    ...
    >>> def delegating_gen():
    ...     _i = iter(subgen())
    ...     try:
    ...         _y = next(_i)
    ...     except StopIteration as _e:
    ...         RES = _e.value
    ...     else:
    ...         while True:
    ...             _s = yield _y
    ...             try:
    ...                 _y = _i.send(_s)
    ...             except StopIteration as _e:
    ...                 RES = _e.value
    ...                 break
    ...
    >>> list(delegating_gen())
    [0, 1, 2]

检查生成器类型（Check Generator Type）
----------------------------------------------------------

使用 ``types.GeneratorType`` 检查 object 是否为 generator。这对于编写需要以不同于其他 iterables 的方式处理 generators 的 functions 非常有用。

.. code-block:: python

    >>> from types import GeneratorType
    >>> def gen_func():
    ...     yield 5566
    ...
    >>> isinstance(gen_func(), GeneratorType)
    True

检查生成器状态（Check Generator State）
------------------------------------------------------------

``inspect.getgeneratorstate()`` function 返回 generator 的当前状态。这对于 debugging 和理解 generator 生命周期很有帮助。四种可能的状态是：GEN_CREATED（未开始）、GEN_RUNNING（当前正在执行）、GEN_SUSPENDED（在屈服时暂停）和GEN_CLOSED（已完成或关闭）。

.. code-block:: python

    >>> import inspect
    >>> def gen_func():
    ...     yield 9527
    ...
    >>> g = gen_func()
    >>> inspect.getgeneratorstate(g)
    'GEN_CREATED'
    >>> next(g)
    9527
    >>> inspect.getgeneratorstate(g)
    'GEN_SUSPENDED'
    >>> g.close()
    >>> inspect.getgeneratorstate(g)
    'GEN_CLOSED'

通过生成器进行上下文管理（Context Manager via Generator）
--------------------------------------------------------------------------------------

``@contextlib.contextmanager`` decorator 将 generator function 转换为 context manager。 ``yield`` 之前的代码在进入 ``with`` 块时运行， ``yield`` 之后的代码（通常在 ``finally`` 中）在退出时运行。生成的value在 ``as`` 之后绑定到variable。

.. code-block:: python

    >>> import contextlib
    >>> @contextlib.contextmanager
    ... def mylist():
    ...     try:
    ...         l = [1, 2, 3, 4, 5]
    ...         yield l
    ...     finally:
    ...         print("exit scope")
    ...
    >>> with mylist() as l:
    ...     print(l)
    [1, 2, 3, 4, 5]
    exit scope

``@contextmanager`` 的作用（What ``@contextmanager`` Does）
------------------------------------------------------------------------------------------------------------

此代码片段显示了 ``@contextmanager`` 内部工作原理的简化实现。它将 generator 包装在实现 context manager 协议（ ``__enter__`` 和 ``__exit__`` ）的 class 中，处理正常退出和 exception 传播。

.. code-block:: python

    class GeneratorCM:
        def __init__(self, gen):
            self._gen = gen

        def __enter__(self):
            return next(self._gen)

        def __exit__(self, *exc_info):
            try:
                if exc_info[0] is None:
                    next(self._gen)
                else:
                    self._gen.throw(*exc_info)
            except StopIteration:
                return True
            raise

    def contextmanager(func):
        def run(*a, **k):
            return GeneratorCM(func(*a, **k))
        return run

分析代码块性能（Profile Code Block）
------------------------------------------------------

使用基于generator的context managers测量代码块执行时间的实际示例。 ``yield`` statement 标记了设置（记录开始时间）和拆卸（计算经过时间）之间的边界。

.. code-block:: python

    >>> import time
    >>> from contextlib import contextmanager
    >>> @contextmanager
    ... def profile(msg):
    ...     try:
    ...         s = time.time()
    ...         yield
    ...     finally:
    ...         print(f'{msg} cost: {time.time() - s:.2f}s')
    ...
    >>> with profile('block'):
    ...     time.sleep(0.1)
    block cost: 0.10s

``yield from`` 和 ``__iter__`` （ ``yield from`` and ``__iter__`` ）
----------------------------------------------------------------------------------------------------------------------------------

当 ``yield from`` 与 class instance 一起使用时，Python 调用 object 的 ``__iter__`` method 来获取 iterator。这使得定制的 classes 能够与 ``yield from`` 委派无缝协作，从而实现 iterables 的优雅组合。

.. code-block:: python

    >>> class FakeGen:
    ...     def __iter__(self):
    ...         n = 0
    ...         while n < 3:
    ...             yield n
    ...             n += 1
    ...     def __reversed__(self):
    ...         n = 2
    ...         while n >= 0:
    ...             yield n
    ...             n -= 1
    ...
    >>> def spam():
    ...     yield from FakeGen()
    ...
    >>> list(spam())
    [0, 1, 2]
    >>> list(reversed(FakeGen()))
    [2, 1, 0]

使用生成器实现闭包（Closure Using Generator）
--------------------------------------------------------------------

Generators 提供了一种优雅的方式来实现 closures 来维护调用之间的状态。每次调用 ``next()`` 都会恢复执行，并且可以访问和修改随附的 variables。这通常比使用基于 ``nonlocal`` 或 class 的方法更干净。

.. code-block:: python

    # generator版本
    >>> def closure_gen():
    ...     x = 5566
    ...     while True:
    ...         x += 1
    ...         yield x
    ...
    >>> g = closure_gen()
    >>> next(g)
    5567
    >>> next(g)
    5568

简单的调度程序（Simple Scheduler）
--------------------------------------------------

此示例演示了如何使用 generators 来实现协作多任务处理。每个 generator 代表一个将控制权交还给调度程序的任务。调度程序使用 deque 在任务之间进行循环，一次推进每一步。

.. code-block:: python

    >>> from collections import deque
    >>> def fib(n):
    ...     if n <= 2: return 1
    ...     return fib(n-1) + fib(n-2)
    ...
    >>> def g_fib(n):
    ...     for x in range(1, n + 1):
    ...         yield fib(x)
    ...
    >>> q = deque([g_fib(3), g_fib(5)])
    >>> def run():
    ...     while q:
    ...         try:
    ...             t = q.popleft()
    ...             print(next(t))
    ...             q.append(t)
    ...         except StopIteration:
    ...             print("Task done")
    ...
    >>> run()
    1
    1
    1
    1
    2
    2
    Task done
    3
    5
    Task done

带阻塞操作的简单 Round-Robin 调度（Simple Round-Robin with Blocking）
------------------------------------------------------------------------------------------------------------------

更高级的调度程序，使用 ``select()`` 处理 I/O 阻塞。任务产生 tuples，指示它们正在等待什么操作（'recv' 或 'send'）以及哪个 socket。调度程序将阻塞的任务移至等待 queues，并且仅在 I/O 准备就绪时才运行它们。这是异步 I/O 框架的基础。

.. code-block:: python

    from collections import deque
    from select import select
    import socket

    tasks = deque()
    w_read = {}
    w_send = {}

    def run():
        while any([tasks, w_read, w_send]):
            while not tasks:
                can_r, can_s, _ = select(w_read, w_send, [])
                for _r in can_r:
                    tasks.append(w_read.pop(_r))
                for _w in can_s:
                    tasks.append(w_send.pop(_w))
            try:
                task = tasks.popleft()
                why, what = next(task)
                if why == 'recv':
                    w_read[what] = task
                elif why == 'send':
                    w_send[what] = task
            except StopIteration:
                pass

    def server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', 5566))
        sock.listen(5)
        while True:
            yield 'recv', sock
            conn, addr = sock.accept()
            tasks.append(client_handler(conn))

    def client_handler(conn):
        while True:
            yield 'recv', conn
            msg = conn.recv(1024)
            if not msg: break
            yield 'send', conn
            conn.send(msg)
        conn.close()

    tasks.append(server())
    run()

异步生成器 (Python 3.6+)（Async Generator (Python 3.6+)）
----------------------------------------------------------------------------------------------------

异步 generators 将 ``async def`` 与 ``yield`` 组合起来创建 asynchronous iterators。他们可以使用 ``await`` 在收益率之间暂停异步操作。使用 ``async for`` 迭代异步 generators。这对于来自网络连接或数据库等异步源的流数据至关重要。

.. code-block:: python

    >>> import asyncio
    >>> async def slow_gen(n, t):
    ...     for x in range(n):
    ...         await asyncio.sleep(t)
    ...         yield x
    ...
    >>> async def task(n):
    ...     async for x in slow_gen(n, 0.1):
    ...         print(x)
    ...
    >>> asyncio.run(task(3))
    0
    1
    2

带有 try..finally 的异步生成器（Async Generator with try..finally）
------------------------------------------------------------------------------------------------------------------

异步 generators 支持 ``try..finally`` 块进行清理，就像常规 generators 一样。 ``finally`` 块在 generator 关闭或垃圾收集时执行，确保即使在 iteration 期间发生 exception 时也能正确释放资源。

.. code-block:: python

    >>> import asyncio
    >>> async def agen(t):
    ...     try:
    ...         await asyncio.sleep(t)
    ...         yield 1 / 0
    ...     finally:
    ...         print("finally")
    ...
    >>> async def main():
    ...     try:
    ...         g = agen(0.1)
    ...         await g.__anext__()
    ...     except Exception as e:
    ...         print(repr(e))
    ...
    >>> asyncio.run(main())
    finally
    ZeroDivisionError('division by zero')

发送并抛出到异步生成器（Send and Throw to Async Generator）
--------------------------------------------------------------------------------------------

异步generators支持 ``asend()`` 发送values和 ``athrow()`` 抛出exceptions，与常规generators类似。这些methods是必须等待的coroutines。这可以实现与异步 generators 的双向通信，以构建 complex 异步数据管道。

.. code-block:: python

    >>> import asyncio
    >>> async def agen(n):
    ...     try:
    ...         for x in range(n):
    ...             await asyncio.sleep(0.1)
    ...             val = yield x
    ...             print(f'got: {val}')
    ...     except RuntimeError as e:
    ...         yield repr(e)
    ...
    >>> async def main():
    ...     g = agen(5)
    ...     ret = await g.asend(None) + await g.asend('foo')
    ...     print(ret)
    ...     ret = await g.athrow(RuntimeError('error'))
    ...     print(ret)
    ...
    >>> asyncio.run(main())
    got: foo
    1
    RuntimeError('error')

异步推导式（Python 3.6+）（Async Comprehension (Python 3.6+)）
----------------------------------------------------------------------------------------------------------

PEP 530引入了异步comprehensions，允许list、set和dict comprehensions中的 ``async for`` 。这提供了一种从异步 generators 收集 values 的简洁方法。您还可以使用 ``if`` 子句来过滤 values 和条件 expressions 进行转换。

.. code-block:: python

    >>> import asyncio
    >>> async def agen(n):
    ...     for x in range(n):
    ...         await asyncio.sleep(0.01)
    ...         yield x
    ...
    >>> async def main():
    ...     ret = [x async for x in agen(5)]
    ...     print(ret)
    ...     ret = [x async for x in agen(5) if x < 3]
    ...     print(ret)
    ...     ret = {f'{x}': x async for x in agen(3)}
    ...     print(ret)
    ...
    >>> asyncio.run(main())
    [0, 1, 2, 3, 4]
    [0, 1, 2]
    {'0': 0, '1': 1, '2': 2}

简单异步循环（Simple Async Round-Robin）
----------------------------------------------------------------

此示例展示了异步 generators 的协作多任务处理。 多个异步generators被调度在一个deque中， 调度程序使用 ``__anext__()`` 依次等待每一个。 此模式对于公平地交错多个异步数据 streams 很有用。

.. code-block:: python

    >>> import asyncio
    >>> from collections import deque
    >>> async def agen(n):
    ...     for x in range(n):
    ...         await asyncio.sleep(0.1)
    ...         yield x
    ...
    >>> async def main():
    ...     q = deque([agen(3), agen(5)])
    ...     while q:
    ...         try:
    ...             g = q.popleft()
    ...             print(await g.__anext__())
    ...             q.append(g)
    ...         except StopAsyncIteration:
    ...             pass
    ...
    >>> asyncio.run(main())
    0
    0
    1
    1
    2
    2
    3
    4

异步生成器与异步迭代器性能（Async Generator vs Async Iterator Performance）
------------------------------------------------------------------------------------------------------------------------

Async generators 比手动实现的 async iterators 具有更好的性能，因为它们在 CPython 中在 C 级别进行了优化。此 benchmark 表明，对于 iteration 繁重的工作负载，异步 generators 的速度可以显着加快。

.. code-block:: python

    >>> import time
    >>> import asyncio
    >>> class AsyncIter:
    ...     def __init__(self, n):
    ...         self._n = n
    ...     def __aiter__(self):
    ...         return self
    ...     async def __anext__(self):
    ...         ret = self._n
    ...         if self._n == 0:
    ...             raise StopAsyncIteration
    ...         self._n -= 1
    ...         return ret
    ...
    >>> async def agen(n):
    ...     for i in range(n):
    ...         yield i
    ...
    >>> async def task_agen(n):
    ...     s = time.time()
    ...     async for _ in agen(n): pass
    ...     cost = time.time() - s
    ...     print(f"agen cost time: {cost}")
    ...
    >>> async def task_aiter(n):
    ...     s = time.time()
    ...     async for _ in AsyncIter(n): pass
    ...     cost = time.time() - s
    ...     print(f"aiter cost time: {cost}")
    ...
    >>> n = 10 ** 7
    >>> asyncio.run(task_agen(n))
    agen cost time: 1.2698817253112793
    >>> asyncio.run(task_aiter(n))
    aiter cost time: 4.168368101119995

``yield from == await`` 表达式（ ``yield from == await`` Expression）
--------------------------------------------------------------------------------------------------------------------------------

在 Python 3.5 引入 ``async`` / ``await`` 语法之前，coroutines 是使用 generators 与 ``@asyncio.coroutine`` decorator 和 ``yield from`` 实现的。 ``await`` 关键字本质上等同于 coroutines 的 ``yield from`` 。此示例显示了 echo 服务器的旧语法和新语法。

.. code-block:: python

    import asyncio
    import socket

    loop = asyncio.get_event_loop()
    host = 'localhost'
    port = 5566
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind((host, port))
    sock.listen(10)

    # 旧语法（Python 3.4）
    @asyncio.coroutine
    def echo_server():
        while True:
            conn, addr = yield from loop.sock_accept(sock)
            loop.create_task(handler(conn))

    @asyncio.coroutine
    def handler(conn):
        while True:
            msg = yield from loop.sock_recv(conn, 1024)
            if not msg:
                break
            yield from loop.sock_sendall(conn, msg)
        conn.close()

    # 新语法（Python 3.5+）
    async def echo_server():
        while True:
            conn, addr = await loop.sock_accept(sock)
            loop.create_task(handler(conn))

    async def handler(conn):
        while True:
            msg = await loop.sock_recv(conn, 1024)
            if not msg:
                break
            await loop.sock_sendall(conn, msg)
        conn.close()

    loop.create_task(echo_server())
    loop.run_forever()

使用生成器的简单编译器（Simple Compiler Using Generators）
------------------------------------------------------------------------------------------

David Beazley 的这个高级示例演示了如何使用 generators 实现简单的 expression compiler。它包括一个分词器、解析器和评估器，使用 generators 的访问者模式进行基于 stack 的评估。

.. code-block:: python

    import re
    import types
    from collections import namedtuple

    tokens = [
        r'(?P<NUMBER>\d+)',
        r'(?P<PLUS>\+)',
        r'(?P<MINUS>-)',
        r'(?P<TIMES>\*)',
        r'(?P<DIVIDE>/)',
        r'(?P<WS>\s+)']

    Token = namedtuple('Token', ['type', 'value'])
    lex = re.compile('|'.join(tokens))

    def tokenize(text):
        scan = lex.scanner(text)
        gen = (Token(m.lastgroup, m.group())
                for m in iter(scan.match, None) if m.lastgroup != 'WS')
        return gen

    class Node:
        _fields = []
        def __init__(self, *args):
            for attr, value in zip(self._fields, args):
                setattr(self, attr, value)

    class Number(Node):
        _fields = ['value']

    class BinOp(Node):
        _fields = ['op', 'left', 'right']

    def parse(toks):
        lookahead, current = next(toks, None), None

        def accept(*toktypes):
            nonlocal lookahead, current
            if lookahead and lookahead.type in toktypes:
                current, lookahead = lookahead, next(toks, None)
                return True

        def expr():
            left = term()
            while accept('PLUS', 'MINUS'):
                left = BinOp(current.value, left)
                left.right = term()
            return left

        def term():
            left = factor()
            while accept('TIMES', 'DIVIDE'):
                left = BinOp(current.value, left)
                left.right = factor()
            return left

        def factor():
            if accept('NUMBER'):
                return Number(int(current.value))
            else:
                raise SyntaxError()
        return expr()

    class NodeVisitor:
        def visit(self, node):
            stack = [self.genvisit(node)]
            ret = None
            while stack:
                try:
                    node = stack[-1].send(ret)
                    stack.append(self.genvisit(node))
                    ret = None
                except StopIteration as e:
                    stack.pop()
                    ret = e.value
            return ret

        def genvisit(self, node):
            ret = getattr(self, 'visit_' + type(node).__name__)(node)
            if isinstance(ret, types.GeneratorType):
                ret = yield from ret
            return ret

    class Evaluator(NodeVisitor):
        def visit_Number(self, node):
            return node.value

        def visit_BinOp(self, node):
            leftval = yield node.left
            rightval = yield node.right
            if node.op == '+':
                return leftval + rightval
            elif node.op == '-':
                return leftval - rightval
            elif node.op == '*':
                return leftval * rightval
            elif node.op == '/':
                return leftval / rightval

    def evaluate(exp):
        toks = tokenize(exp)
        tree = parse(toks)
        return Evaluator().visit(tree)

    print(evaluate('2 * 3 + 5 / 2'))  # 8.5
    print(evaluate('+'.join([str(x) for x in range(10000)])))  # 49995000
