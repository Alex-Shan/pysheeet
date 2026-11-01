.. meta::
    :description lang=zh_CN: Python asyncio 基础知识 - coroutines、任务、event loop、异步/等待语法
    :keywords: Python, Python3, Asyncio, Coroutines, Event Loop, async await, Asynchronous Programming

============================================
异步基础知识（Asyncio Basics）
============================================

:Source: `src/basic/asyncio_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/asyncio_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

``asyncio`` module 在 Python 3.4 中引入，并在 Python 3.5+ 中使用 ``async/await`` 语法进行了显着改进，为编写 asynchronous 代码提供了基础。与使用抢占式多任务处理（OS 决定何时切换）的 threads 不同，asyncio 使用协作式多任务处理，其中 coroutines 使用 ``await`` 显式让出控制权。这消除了线程代码中常见的 race conditions，并使程序流的推理变得更加容易。

Key概念：

- **Coroutine** ：用​​ ``async def`` 定义的function，可以暂停和恢复
- **Event Loop** ：运行coroutines并处理I/O事件的中央调度程序
- **Task** ：coroutine 的包装器，安排其执行
- **Future** ：稍后可用的结果的占位符

使用 asyncio.run 运行协程（Running Coroutines with asyncio.run）
----------------------------------------------------------------------------------------------------------------

运行异步代码的最简单方法是 ``asyncio.run()`` ，在 Python 3.7 中介绍。它创建一个 event loop，运行 coroutine 直到完成，然后自动清理。这是 asyncio 程序的推荐入口点。

.. code-block:: python

    import asyncio

    async def hello():
        print("Hello")
        await asyncio.sleep(1)
        print("World")

    # Python 3.7+
    asyncio.run(hello())

对于文件 I/O 或其他阻塞操作，请使用 ``run_in_executor`` 以避免阻塞 event loop：

.. code-block:: python

    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    async def read_file(path):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            with open(path) as f:
                return await loop.run_in_executor(pool, f.read)

    content = asyncio.run(read_file('/etc/hosts'))

创建和管理任务（Creating and Managing Tasks）
------------------------------------------------------------------------

任务允许多个coroutines同时运行。当您创建任务时，它会立即在 event loop 上运行。使用 ``asyncio.create_task()`` （Python 3.7+）或 ``loop.create_task()`` 创建任务。

.. code-block:: python

    import asyncio

    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name} done"

    async def main():
        # 创建任务 - 它们立即开始运行
        task1 = asyncio.create_task(fetch("A", 2))
        task2 = asyncio.create_task(fetch("B", 1))

        # 等待两者都完成
        result1 = await task1
        result2 = await task2
        print(result1, result2)

    asyncio.run(main())

收集多个协程（Gathering Multiple Coroutines）
--------------------------------------------------------------------------

``asyncio.gather()`` 同时运行多个 coroutines 并按顺序收集它们的结果。这是并行运行多个异步操作并等待所有异步操作完成的最常见方法。

.. code-block:: python

    import asyncio

    async def fetch(url, delay):
        await asyncio.sleep(delay)
        return f"Response from {url}"

    async def main():
        urls = ["site1.com", "site2.com", "site3.com"]
        coros = [fetch(url, i * 0.5) for i, url in enumerate(urls)]

        # 同时运行所有内容，结果与输入的顺序相同
        results = await asyncio.gather(*coros)
        for r in results:
            print(r)

    asyncio.run(main())

带超时限制的等待（Waiting with Timeout）
------------------------------------------------------------

使用 ``asyncio.wait_for()`` 到 set 异步操作超时。这对于网络操作来说至关重要，因为您不想无限期地等待可能永远不会到来的响应。

.. code-block:: python

    import asyncio

    async def slow_operation():
        await asyncio.sleep(10)
        return "done"

    async def main():
        try:
            result = await asyncio.wait_for(slow_operation(), timeout=2.0)
        except asyncio.TimeoutError:
            print("Operation timed out!")

    asyncio.run(main())

等待首个任务完成（Waiting for First Completed）
--------------------------------------------------------------------------

``asyncio.wait()`` 比 ``gather()`` 提供更多控制。您可以等待第一个任务（第一个 exception）或所有任务完成。当您想要 process 结果可用时，这非常有用。

.. code-block:: python

    import asyncio

    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name}: {delay}s"

    async def main():
        tasks = [
            asyncio.create_task(fetch("fast", 1)),
            asyncio.create_task(fetch("slow", 3)),
        ]

        # 等待第一个完成
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )

        for task in done:
            print(f"Completed: {task.result()}")
        print(f"Still pending: {len(pending)}")

        # 取消待处理的任务
        for task in pending:
            task.cancel()

    asyncio.run(main())

异步迭代（Asynchronous Iteration）
--------------------------------------------------------

异步 iterators 允许您迭代异步到达的数据，例如流响应或数据库游标。实现 ``__aiter__`` 和 ``__anext__`` methods 以创建自定义异步 iterators。

.. code-block:: python

    import asyncio

    class AsyncRange:
        """Async iterator that yields numbers with delays."""

        def __init__(self, start, stop):
            self.current = start
            self.stop = stop

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.current >= self.stop:
                raise StopAsyncIteration
            await asyncio.sleep(0.5)
            value = self.current
            self.current += 1
            return value

    async def main():
        async for num in AsyncRange(0, 5):
            print(num)

    asyncio.run(main())

异步上下文管理器（Asynchronous Context Managers）
------------------------------------------------------------------------------

异步 context managers 对于管理需要异步设置或清理的资源（例如数据库连接、文件句柄或网络会话）至关重要。使用 ``async with`` 确保正确的资源管理。

.. code-block:: python

    import asyncio

    class AsyncConnection:
        """Simulated async database connection."""

        async def __aenter__(self):
            print("Connecting...")
            await asyncio.sleep(1)
            print("Connected")
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("Disconnecting...")
            await asyncio.sleep(0.5)
            print("Disconnected")

        async def query(self, sql):
            await asyncio.sleep(0.1)
            return f"Result of: {sql}"

    async def main():
        async with AsyncConnection() as conn:
            result = await conn.query("SELECT * FROM users")
            print(result)

    asyncio.run(main())

使用 @asynccontextmanager（Using @asynccontextmanager）
------------------------------------------------------------------------------------------------------

``@asynccontextmanager`` decorator (Python 3.7+) 提供了一种使用 generator 语法创建异步 context managers 的更简单方法，类似于 synchronous ``@contextmanager`` decorator。

.. code-block:: python

    import asyncio
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def managed_resource(name):
        print(f"Acquiring {name}")
        await asyncio.sleep(0.5)
        try:
            yield name
        finally:
            print(f"Releasing {name}")
            await asyncio.sleep(0.2)

    async def main():
        async with managed_resource("database") as resource:
            print(f"Using {resource}")

    asyncio.run(main())

在执行器中运行阻塞代码（Running Blocking Code in Executor）
--------------------------------------------------------------------------------------------

当您需要调用阻塞代码（文件I/O、CPU密集型操作或不支持异步的libraries）时，使用 ``run_in_executor()`` 在thread pool中运行它，而不阻塞event loop。

.. code-block:: python

    import asyncio
    import time
    from concurrent.futures import ThreadPoolExecutor

    def blocking_io():
        """Simulates blocking I/O operation."""
        time.sleep(2)
        return "IO complete"

    def cpu_bound():
        """Simulates CPU-intensive operation."""
        return sum(i * i for i in range(10**6))

    async def main():
        loop = asyncio.get_event_loop()

        # 在默认执行器（ThreadPoolExecutor）中运行
        result1 = await loop.run_in_executor(None, blocking_io)
        print(result1)

        # 在自定义执行器中运行
        with ThreadPoolExecutor(max_workers=4) as pool:
            result2 = await loop.run_in_executor(pool, cpu_bound)
            print(result2)

    asyncio.run(main())

异步生成器（Async Generators）
----------------------------------------------

Async generators (Python 3.6+) 将 generators 与 async/await 结合起来，允许您异步生成 values。它们对于流数据或更简洁地实现异步 iterators 非常有用。

.. code-block:: python

    import asyncio

    async def async_range(start, stop):
        """Async generator that yields numbers with delays."""
        for i in range(start, stop):
            await asyncio.sleep(0.5)
            yield i

    async def main():
        async for num in async_range(0, 5):
            print(num)

        # 异步 comprehension
        results = [x async for x in async_range(0, 3)]
        print(results)

    asyncio.run(main())

任务中的异常处理（Exception Handling in Tasks）
--------------------------------------------------------------------------

当您等待任务或调用 ``result()`` 时，任务中的 Exceptions 会被存储并重新引发。从未等待的任务中未处理的 exceptions 将被记录，但可能会被默默忽略，因此请始终等待您的任务。

.. code-block:: python

    import asyncio

    async def failing_task():
        await asyncio.sleep(1)
        raise ValueError("Something went wrong")

    async def main():
        task = asyncio.create_task(failing_task())

        try:
            await task
        except ValueError as e:
            print(f"Caught exception: {e}")

        # 将聚集与 return_exceptions 一起使用
        tasks = [
            asyncio.create_task(asyncio.sleep(1)),
            asyncio.create_task(failing_task()),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"Task failed: {r}")
            else:
                print(f"Task succeeded: {r}")

    asyncio.run(main())

取消任务（Cancelling Tasks）
--------------------------------------------

可以使用 ``task.cancel()`` 取消任务。取消的任务将在下一个等待点引发 ``asyncio.CancelledError`` 。处理此 exception 以在任务取消时执行清理。

.. code-block:: python

    import asyncio

    async def long_running():
        try:
            while True:
                print("Working...")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Task was cancelled, cleaning up...")
            raise  # 重新加注以将任务标记为已取消

    async def main():
        task = asyncio.create_task(long_running())

        await asyncio.sleep(3)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            print("Task cancellation confirmed")

    asyncio.run(main())
