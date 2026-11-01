.. meta::
    :description lang=zh_CN: 了解 Python 中的 asynchronous 编程的综合指南，从阻塞 I/O 到 event loops、callbacks、generators 和 async/await 语法
    :keywords: Python, Python3, asyncio, coroutine, event loop, async await, asynchronous programming, C10k problem, non-blocking I/O, selectors, generators, callback

====================================================================================================================
异步编程漫游指南（A Hitchhiker's Guide to Asynchronous Programming）
====================================================================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

摘要（Abstract）
------------------------

对于寻求高效处理大量并发连接的程序员来说， `C10k problem`_ 仍然是一个基本挑战。传统上，开发人员使用 **threads**、**epoll**或**kqueue** 来处理大量的 I/O 操作，以防止软件阻塞昂贵的操作。然而，由于数据共享和任务依赖性的复杂性，开发可读且无错误的并发代码具有挑战性。即使像 `Valgrind`_ 这样帮助检测 deadlocks 和 race conditions 的强大工具也无法消除耗时的 debugging process 随着软件的扩展。

为了应对这些挑战，许多编程语言（包括 Python、JavaScript 和 C++）开发了更好的 libraries、框架和语法，以帮助程序员正确管理并发任务。本文不关注如何使用现代并行 APIs，而是关注 asynchronous 编程模式背后的 **设计理念** ，追踪从阻塞 I/O 到优雅的 ``async/await`` 语法的演变。

使用 threads 是在不阻塞主 thread 的情况下调度任务的最自然方法。然而，threads 引入了上下文切换的性能开销，并且需要仔细锁定原子操作的关键部分。虽然 event loops 可以增强 I/O 绑定场景中的性能，但由于 callback 的复杂性（通常称为 "callback hell"），编写可读的事件驱动代码具有挑战性。幸运的是，Python 引入了 ``async/await`` 语法来帮助开发人员编写易于理解的高性能代码。下图说明了 ``async/await`` 如何以 threads 的简单性和 event loops 的效率来处理 socket 连接。

.. image:: /_static/appendix/event-loop-vs-thread.png
   :alt: 左侧 Event Loop 表示事件循环，右侧 Thread 表示线程；图中的 Python 代码保持原样。

.. admonition:: 图例

   左侧 Event Loop 表示事件循环，右侧 Thread 表示线程；图中的 Python 代码保持原样。

介绍（Introduction）
--------------------------------

处理 I/O 操作（例如网络连接）是任何程序中最昂贵的任务之一。考虑一个简单的 TCP 阻塞回显服务器（如下所示）。如果客户端连接时未发送任何数据，它将阻止所有其他连接。即使客户端及时发送数据，服务器也无法处理并发请求，因为它浪费大量时间等待网络接口等硬件的 I/O 响应。因此，socket 并发编程对于管理高请求量至关重要。

.. code-block:: python

    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5566))
    s.listen(10)

    while True:
        conn, addr = s.accept()
        msg = conn.recv(1024)
        conn.send(msg)

防止阻塞的一种解决方案是将任务分派到单独的 threads。以下示例演示使用 threads 同时处理连接。然而，创建大量的threads会消耗计算资源，而不会成比例地获得throughput。更糟糕的是，应用程序在处理关键部分的任务时可能会浪费时间等待 locks。虽然 threads 解决了阻塞问题，但 CPU 利用率和内存开销等因素对于解决 C10k 问题仍然至关重要。在不创建无限的 threads 的情况下， **事件循环** 提供了一种有效管理连接的替代解决方案。

.. code-block:: python

    import threading
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5566))
    s.listen(10240)

    def handler(conn):
        while True:
            msg = conn.recv(65535)
            conn.send(msg)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handler, args=(conn,))
        t.start()

简单的事件驱动socket服务器包括三个主要组件： **I/O复用模块**（e.g.、 `select`_ ）、**调度器**（loop）和**回调函数** （事件处理程序）。以下服务器在 loop 内使用 Python 的高级 I/O 复用 module、 `selectors`_ 来检查 I/O 操作是否准备就绪。当数据可供读取或写入时，loop 检索 I/O 事件并执行相应的 callback functions（ ``accept`` 、 ``read`` 或 ``write`` ）以完成任务。

.. code-block:: python

    import socket
    from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
    from functools import partial

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5566))
    s.listen(10240)
    s.setblocking(False)

    sel = DefaultSelector()

    def accept(s, mask):
        conn, addr = s.accept()
        conn.setblocking(False)
        sel.register(conn, EVENT_READ, read)

    def read(conn, mask):
        msg = conn.recv(65535)
        if not msg:
            sel.unregister(conn)
            return conn.close()
        sel.modify(conn, EVENT_WRITE, partial(write, msg=msg))

    def write(conn, mask, msg=None):
        if msg:
            conn.send(msg)
        sel.modify(conn, EVENT_READ, read)

    sel.register(s, EVENT_READ, accept)
    while True:
        events = sel.select()
        for e, m in events:
            cb = e.data
            cb(e.fileobj, m)

尽管通过 threads 管理连接可能效率低下，但基于事件 loop 的程序更难以读取和维护。为了增强代码可读性，许多编程语言（包括 Python）引入了 **coroutines**、**futures**和**async/await** 等抽象概念来处理 I/O优雅地复用。以下各节探讨这些概念及其解决的问题。

回调函数（Callback Functions）
------------------------------------------------

Callback functions 在事件发生时控制运行时的数据流。然而，在 callbacks 中保存状态具有挑战性。例如，通过 TCP 实现握手协议需要将先前的状态存储在后续 callbacks 可访问的地方。

.. code-block:: python

    import socket
    from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
    from functools import partial

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5566))
    s.listen(10240)
    s.setblocking(False)

    sel = DefaultSelector()
    is_hello = {}

    def accept(s, mask):
        conn, addr = s.accept()
        conn.setblocking(False)
        is_hello[conn] = False
        sel.register(conn, EVENT_READ, read)

    def read(conn, mask):
        msg = conn.recv(65535)
        if not msg:
            sel.unregister(conn)
            return conn.close()

        # 检查握手是否成功
        if is_hello[conn]:
            sel.modify(conn, EVENT_WRITE, partial(write, msg=msg))
            return

        # 进行握手
        if msg.decode("utf-8").strip() != "hello":
            sel.unregister(conn)
            return conn.close()

        is_hello[conn] = True

    def write(conn, mask, msg=None):
        if msg:
            conn.send(msg)
        sel.modify(conn, EVENT_READ, read)

    sel.register(s, EVENT_READ, accept)
    while True:
        events = sel.select()
        for e, m in events:
            cb = e.data
            cb(e.fileobj, m)

尽管 ``is_hello`` dictionary 存储状态来跟踪握手状态，但代码变得难以理解。底层逻辑实际上很简单——相当于这个阻塞版本：

.. code-block:: python

    def accept(s):
        conn, addr = s.accept()
        success = handshake(conn)
        if not success:
            conn.close()

    def handshake(conn):
        data = conn.recv(65535)
        if not data:
            return False
        if data.decode('utf-8').strip() != "hello":
            return False
        conn.send(b"hello")
        return True

为了在非阻塞代码中实现类似的结构，function（或任务）在等待 I/O 操作时必须对其当前状态进行快照，包括 arguments、本地 variables 和执行位置。然后，调度程序必须能够将 **重新输入** 和 function，并在 I/O 完成后执行剩余的代码。与 C++ 等语言不同，Python 自然地实现了这一点，因为 **generators** 保留所有状态，并且可以通过调用 ``next()`` 重新输入。通过利用 generators，可以在 event loop 内使用可读的线性代码（称为*内联 callbacks*）以非阻塞方式处理 I/O 操作。

事件循环（Event Loop）
--------------------------------

event loop 是一个用户空间调度程序，它管理程序内的任务，而不是依赖操作系统 thread 调度。以下代码片段演示了一个简单的 event loop 异步处理 socket 连接。当 I/O 操作未准备好时，该实现将任务附加到 FIFO 作业 queue 并使用*选择器*进行注册。 *generator* 保留任务状态，允许在 I/O 结果可用时在没有 callback functions 的情况下恢复执行。了解 event loop 的工作原理表明，Python generator 确实是 **coroutine** 的一种形式。

.. code-block:: python

    # loop.py

    from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

    class Loop:
        def __init__(self):
            self.sel = DefaultSelector()
            self.queue = []

        def create_task(self, task):
            self.queue.append(task)

        def polling(self):
            for e, m in self.sel.select(0):
                self.queue.append((e.data, None))
                self.sel.unregister(e.fileobj)

        def is_registered(self, fileobj):
            try:
                self.sel.get_key(fileobj)
            except KeyError:
                return False
            return True

        def register(self, t, data):
            if not data:
                return False

            event_type, fileobj = data
            if event_type in (EVENT_READ, EVENT_WRITE):
                if self.is_registered(fileobj):
                    self.sel.modify(fileobj, event_type, t)
                else:
                    self.sel.register(fileobj, event_type, t)
                return True
            return False

        def accept(self, s):
            while True:
                try:
                    conn, addr = s.accept()
                except BlockingIOError:
                    yield (EVENT_READ, s)
                else:
                    break
            return conn, addr

        def recv(self, conn, size):
            while True:
                try:
                    msg = conn.recv(size)
                except BlockingIOError:
                    yield (EVENT_READ, conn)
                else:
                    break
            return msg

        def send(self, conn, msg):
            while True:
                try:
                    size = conn.send(msg)
                except BlockingIOError:
                    yield (EVENT_WRITE, conn)
                else:
                    break
            return size

        def once(self):
            self.polling()
            unfinished = []
            for t, data in self.queue:
                try:
                    data = t.send(data)
                except StopIteration:
                    continue

                if self.register(t, data):
                    unfinished.append((t, None))

            self.queue = unfinished

        def run(self):
            while self.queue or self.sel.get_map():
                self.once()

通过将作业分配给 event loop，编程模式类似于使用 threads，但具有用户级调度程序。 `PEP 380`_ 通过 ``yield from`` 引入了 generator 委派，允许 generator 等待其他 generators 完成。以下代码片段比基于 callback 的 I/O 处理更加直观和可读：

.. code-block:: python

    # server.py
    # $ python3 server.py &
    # $ nc localhost 5566

    import socket
    from loop import Loop

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5566))
    s.listen(10240)
    s.setblocking(False)

    loop = Loop()

    def handler(conn):
        while True:
            msg = yield from loop.recv(conn, 1024)
            if not msg:
                conn.close()
                break
            yield from loop.send(conn, msg)

    def main():
        while True:
            conn, addr = yield from loop.accept(s)
            conn.setblocking(False)
            loop.create_task((handler(conn), None))

    loop.create_task((main(), None))
    loop.run()

将 event loop 与 ``yield from`` 一起使用可以在不阻塞主 thread 的情况下管理连接 - 这就是 ``asyncio`` 在 Python 3.5 之前的工作方式。然而， ``yield from`` 是不明确的：为什么添加 ``@asyncio.coroutine`` 会将 generator 转换为 coroutine？ `PEP 492`_ 建议coroutines应该成为Python中的 **独立概念** ，而不是为asynchronous操作重载generator语法。这导致了 ``async/await`` 语法的引入，极大地提高了 asynchronous 编程的可读性。

什么是协程？（What is a Coroutine?）
--------------------------------------------------------

Python 文档将 coroutines 定义为 "a generalized form of subroutines." 该定义虽然在技术上是准确的，但可能会令人困惑。根据我们的讨论，event loop 调度 generators 执行特定任务，类似于 OS 将作业分派给 threads。在这种情况下，generators 充当 "routine workers."， **coroutine** 只是由程序内的 event loop 调度的任务，而不是由操作系统调度的任务。

以下代码片段说明了 ``@coroutine`` 的作用。此 decorator 将 function 转换为 generator function 并将其与 ``types.coroutine`` 包装以实现向后兼容性：

.. code-block:: python

    import asyncio
    import inspect
    import types
    from functools import wraps
    from asyncio.futures import Future

    def coroutine(func):
        """Simple prototype of coroutine decorator"""
        if inspect.isgeneratorfunction(func):
            return types.coroutine(func)

        @wraps(func)
        def coro(*a, **k):
            res = func(*a, **k)
            if isinstance(res, Future) or inspect.isgenerator(res):
                res = yield from res
            return res
        return types.coroutine(coro)

    @coroutine
    def foo():
        yield from asyncio.sleep(1)
        print("Hello Foo")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(loop.create_task(foo()))
    loop.close()

使用Python 3.5+， ``async def`` 语法直接创建原生coroutines，并用 ``await`` 替换 ``yield from`` 来暂停执行。这使得意图明确： ``async def`` 声明 coroutine，而 ``await`` 标记 event loop 可以切换到其他任务的挂起点。

结论（Conclusion）
----------------------------

由于现代语法和 library 支持，通过 event loops 的 Asynchronous 编程变得更加简单和可读。大多数编程语言（包括 Python）都实现了 libraries，通过与新语法集成来管理任务调度。虽然 ``async/await`` 最初可能看起来很神秘，但它为程序员提供了一种开发逻辑、线性代码结构的方法（类似于使用 threads），同时获得事件驱动的 I/O 的性能优势。

如果没有 callback functions 在处理程序之间传递状态，程序员不再需要担心跨 asynchronous 边界保留本地 variables 和 arguments 。这使得开发人员能够专注于应用程序逻辑，而不是花时间解决并发问题。从 callbacks 到 generators 再到 ``async/await`` 的演变代表了并发编程的可访问性和可维护性方面的重大进步。

参考资料（References）
--------------------------------

1. `asyncio — Asynchronous I/O`_
2. `PEP 342 - Coroutines via Enhanced Generators`_
3. `PEP 380 - Syntax for Delegating to a Subgenerator`_
4. `PEP 492 - Coroutines with async and await syntax`_

.. _C10k problem: https://en.wikipedia.org/wiki/C10k_problem
.. _Valgrind: https://valgrind.org/
.. _select: https://docs.python.org/3/library/select.html
.. _selectors: https://docs.python.org/3/library/selectors.html
.. _asyncio — Asynchronous I/O: https://docs.python.org/3/library/asyncio.html
.. _PEP 492: https://www.python.org/dev/peps/pep-0492/
.. _PEP 380: https://www.python.org/dev/peps/pep-0380/
.. _PEP 342 - Coroutines via Enhanced Generators: https://www.python.org/dev/peps/pep-0342/
.. _PEP 492 - Coroutines with async and await syntax: https://www.python.org/dev/peps/pep-0492/
.. _PEP 380 - Syntax for Delegating to a Subgenerator: https://www.python.org/dev/peps/pep-0380/
