.. meta::
    :description lang=zh_CN: Python asyncio 高级 - 同步、queues、子流程、debugging、模式
    :keywords: Python, Python3, Asyncio, Synchronization, Queue, Semaphore, Lock, Subprocess, Debugging

========================================================
Asyncio 进阶（Asyncio Advanced）
========================================================

:Source: `src/basic/asyncio_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/asyncio_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

除了基本的 coroutines 和网络之外，asyncio 还提供同步原语、queues、子进程管理和 debugging 工具。本节介绍用于构建强大的异步应用程序的高级模式，包括生产者-消费者模式、速率限制、正常关闭以及与 synchronous 代码的集成。

锁（Locks）
----------------

``asyncio.Lock`` 防止多个 coroutines 同时访问共享资源。与线程 locks 不同，异步 locks 必须与 ``await`` 一起使用，并且只能在同一个 event loop 中工作。

.. code-block:: python

    import asyncio

    class SharedCounter:
        def __init__(self):
            self.value = 0
            self._lock = asyncio.Lock()

        async def increment(self):
            async with self._lock:
                current = self.value
                await asyncio.sleep(0.01)  # 模拟工作
                self.value = current + 1

    async def worker(counter, name, count):
        for _ in range(count):
            await counter.increment()
        print(f"{name} done")

    async def main():
        counter = SharedCounter()
        await asyncio.gather(
            worker(counter, "A", 100),
            worker(counter, "B", 100),
            worker(counter, "C", 100),
        )
        print(f"Final value: {counter.value}")  # 应该是300

    asyncio.run(main())

用于速率限制的信号量（Semaphores for Rate Limiting）
--------------------------------------------------------------------------------

``asyncio.Semaphore`` 限制并发操作数。这对于限制 API 调用速率、限制数据库连接或控制资源使用至关重要。

.. code-block:: python

    import asyncio

    async def fetch(url, semaphore):
        async with semaphore:
            print(f"Fetching {url}")
            await asyncio.sleep(1)  # 模拟网络请求
            return f"Response from {url}"

    async def main():
        # 限制为 3 个并发请求
        semaphore = asyncio.Semaphore(3)

        urls = [f"https://api.example.com/{i}" for i in range(10)]
        tasks = [fetch(url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

        for r in results:
            print(r)

    asyncio.run(main())

信令事件（Events for Signaling）
----------------------------------------------------

``asyncio.Event`` 允许 coroutines 等待来自另一个 coroutine 的信号。这对于协调多个任务之间的启动、关闭或状态更改非常有用。

.. code-block:: python

    import asyncio

    async def waiter(event, name):
        print(f"{name} waiting for event")
        await event.wait()
        print(f"{name} got the event!")

    async def setter(event):
        print("Setting event in 2 seconds...")
        await asyncio.sleep(2)
        event.set()
        print("Event set!")

    async def main():
        event = asyncio.Event()

        await asyncio.gather(
            waiter(event, "Task 1"),
            waiter(event, "Task 2"),
            waiter(event, "Task 3"),
            setter(event),
        )

    asyncio.run(main())

复杂同步的条件（Conditions for Complex Synchronization）
----------------------------------------------------------------------------------------------

``asyncio.Condition`` 将 lock 与等待条件的功能结合起来。这对于消费者需要等待特定条件的生产者-消费者模式非常有用。

.. code-block:: python

    import asyncio

    class Buffer:
        def __init__(self, size):
            self.buffer = []
            self.size = size
            self.condition = asyncio.Condition()

        async def put(self, item):
            async with self.condition:
                while len(self.buffer) >= self.size:
                    await self.condition.wait()
                self.buffer.append(item)
                self.condition.notify()

        async def get(self):
            async with self.condition:
                while not self.buffer:
                    await self.condition.wait()
                item = self.buffer.pop(0)
                self.condition.notify()
                return item

    async def producer(buffer, name):
        for i in range(5):
            await buffer.put(f"{name}-{i}")
            print(f"Produced: {name}-{i}")
            await asyncio.sleep(0.1)

    async def consumer(buffer, name):
        for _ in range(5):
            item = await buffer.get()
            print(f"{name} consumed: {item}")
            await asyncio.sleep(0.2)

    async def main():
        buffer = Buffer(size=2)
        await asyncio.gather(
            producer(buffer, "P1"),
            consumer(buffer, "C1"),
            consumer(buffer, "C2"),
        )

    asyncio.run(main())

生产者-消费者队列（Queues for Producer-Consumer）
------------------------------------------------------------------------------

``asyncio.Queue`` 是实现生产者-消费者模式的首选方式。它在内部处理同步，并提供具有可选超时的阻塞 get/put 操作。

.. code-block:: python

    import asyncio

    async def producer(queue, name):
        for i in range(5):
            item = f"{name}-item-{i}"
            await queue.put(item)
            print(f"Produced: {item}")
            await asyncio.sleep(0.5)

    async def consumer(queue, name):
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=2.0)
                print(f"{name} consumed: {item}")
                queue.task_done()
                await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                print(f"{name} timed out, exiting")
                break

    async def main():
        queue = asyncio.Queue(maxsize=3)

        producers = [
            asyncio.create_task(producer(queue, "P1")),
            asyncio.create_task(producer(queue, "P2")),
        ]
        consumers = [
            asyncio.create_task(consumer(queue, "C1")),
            asyncio.create_task(consumer(queue, "C2")),
        ]

        await asyncio.gather(*producers)
        await queue.join()  # 等待所有items处理完毕

        for c in consumers:
            c.cancel()

    asyncio.run(main())

优先队列（Priority Queue）
----------------------------------------

``asyncio.PriorityQueue`` processes items 按优先级。首先处理优先级较低的 values。 Items 必须可比较或包装在 tuples 中，优先级与第一个 element 相同。

.. code-block:: python

    import asyncio

    async def producer(queue):
        items = [
            (3, "low priority"),
            (1, "high priority"),
            (2, "medium priority"),
        ]
        for priority, item in items:
            await queue.put((priority, item))
            print(f"Added: {item} (priority {priority})")

    async def consumer(queue):
        while not queue.empty():
            priority, item = await queue.get()
            print(f"Processing: {item} (priority {priority})")
            await asyncio.sleep(0.5)
            queue.task_done()

    async def main():
        queue = asyncio.PriorityQueue()
        await producer(queue)
        await consumer(queue)

    asyncio.run(main())

运行子进程（Running Subprocesses）
------------------------------------------------------

Asyncio可以异步运行并与子进程通信。这对于运行 shell 命令、外部工具或并行 processes 且不阻塞 event loop 非常有用。

.. code-block:: python

    import asyncio

    async def run_command(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        return {
            'cmd': cmd,
            'returncode': proc.returncode,
            'stdout': stdout.decode().strip(),
            'stderr': stderr.decode().strip()
        }

    async def main():
        commands = [
            "echo 'Hello World'",
            "python --version",
            "date",
        ]

        results = await asyncio.gather(*[run_command(c) for c in commands])

        for r in results:
            print(f"Command: {r['cmd']}")
            print(f"Output: {r['stdout']}")
            print()

    asyncio.run(main())

具有流输出的子进程（Subprocess with Streaming Output）
--------------------------------------------------------------------------------------

对于长时间运行的processes，可以逐行输出stream，而不用等待process完成。这对于监视日志或进度很有用。

.. code-block:: python

    import asyncio

    async def stream_subprocess(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            print(f"[{cmd[:20]}] {line.decode().strip()}")

        await proc.wait()
        return proc.returncode

    async def main():
        # 运行多个命令及其输出 stream
        await asyncio.gather(
            stream_subprocess("for i in 1 2 3; do echo $i; sleep 1; done"),
            stream_subprocess("for i in a b c; do echo $i; sleep 0.5; done"),
        )

    asyncio.run(main())

平稳关闭（Graceful Shutdown）
----------------------------------------------

正确的关闭处理可确保所有任务顺利完成并释放资源。使用信号处理程序捕获 SIGINT/SIGTERM 并优雅地取消任务。

.. code-block:: python

    import asyncio
    import signal

    async def worker(name):
        try:
            while True:
                print(f"{name} working...")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print(f"{name} cancelled, cleaning up...")
            await asyncio.sleep(0.5)  # 清理时间
            print(f"{name} cleanup done")
            raise

    async def main():
        loop = asyncio.get_event_loop()
        tasks = [
            asyncio.create_task(worker("Worker-1")),
            asyncio.create_task(worker("Worker-2")),
        ]

        def shutdown():
            print("\nShutdown requested...")
            for task in tasks:
                task.cancel()

        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("All tasks cancelled")

    asyncio.run(main())

在线程中运行异步代码（Running Async Code in Threads）
----------------------------------------------------------------------------------

当您需要从 synchronous 代码（e.g.，在 callback 或另一个 thread 中）运行异步代码时，请使用 ``asyncio.run_coroutine_threadsafe()`` 。

.. code-block:: python

    import asyncio
    import threading
    import time

    async def async_task(value):
        await asyncio.sleep(1)
        return value * 2

    def thread_function(loop):
        # 从不同的 thread 运行异步代码
        future = asyncio.run_coroutine_threadsafe(
            async_task(21), loop
        )
        result = future.result(timeout=5)
        print(f"Thread got result: {result}")

    async def main():
        loop = asyncio.get_event_loop()

        # 启动将调用异步代码的 thread
        thread = threading.Thread(target=thread_function, args=(loop,))
        thread.start()

        # 保持 event loop 运行
        await asyncio.sleep(2)
        thread.join()

    asyncio.run(main())

调试异步（Debugging Asyncio）
----------------------------------------------

启用调试模式以捕获常见错误，例如阻塞调用、未等待的 coroutines 和缓慢的 callbacks。调试模式会增加开销，因此仅在开发期间使用它。

.. code-block:: python

    import asyncio
    import logging

    # 启用调试日志记录
    logging.basicConfig(level=logging.DEBUG)

    async def slow_callback():
        import time
        time.sleep(0.2)  # 这将在调试模式下触发警告

    async def main():
        await slow_callback()

    # Method 1：环境 variable
    # PYTHONASYNCIODEBUG=1 python script.py

    # Method 2: asyncio.run with debug=True
    asyncio.run(main(), debug=True)

自定义事件循环（Custom Event Loop）
----------------------------------------------------

您可以通过子类化或修补来自定义 event loop 行为。这对于 debugging、profiling 或添加自定义功能非常有用。

.. code-block:: python

    import asyncio

    class DebugEventLoop(asyncio.SelectorEventLoop):
        def _run_once(self):
            # 预定的曲目号 callbacks
            num_ready = len(self._ready)
            num_scheduled = len(self._scheduled)
            if num_ready or num_scheduled:
                print(f"Ready: {num_ready}, Scheduled: {num_scheduled}")
            super()._run_once()

    async def task(n):
        await asyncio.sleep(n)
        print(f"Task {n} done")

    # 使用定制event loop
    loop = DebugEventLoop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(asyncio.gather(
            task(0.1),
            task(0.2),
            task(0.3),
        ))
    finally:
        loop.close()

超时模式（Timeout Patterns）
--------------------------------------------

针对不同用例的不同超时模式：每个操作超时、整体超时和回退超时。

.. code-block:: python

    import asyncio

    async def fetch(url, delay):
        await asyncio.sleep(delay)
        return f"Response from {url}"

    async def fetch_with_timeout(url, delay, timeout):
        """Per-operation timeout."""
        try:
            return await asyncio.wait_for(fetch(url, delay), timeout)
        except asyncio.TimeoutError:
            return f"Timeout for {url}"

    async def fetch_all_with_timeout(urls, timeout):
        """Overall timeout for all operations."""
        async def fetch_all():
            return await asyncio.gather(*[fetch(u, i) for i, u in enumerate(urls)])

        try:
            return await asyncio.wait_for(fetch_all(), timeout)
        except asyncio.TimeoutError:
            return ["Overall timeout"]

    async def fetch_with_fallback(url, delay, timeout, fallback):
        """Timeout with fallback value."""
        try:
            return await asyncio.wait_for(fetch(url, delay), timeout)
        except asyncio.TimeoutError:
            return fallback

    async def main():
        # 每次操作超时
        result = await fetch_with_timeout("slow.com", 5, 1)
        print(result)

        # 带有后备的超时
        result = await fetch_with_fallback("slow.com", 5, 1, "cached response")
        print(result)

    asyncio.run(main())

重试模式（Retry Pattern）
--------------------------------------

通过指数退避实现瞬态故障的重试逻辑。这对于强大的网络客户端至关重要。

.. code-block:: python

    import asyncio
    import random

    class RetryError(Exception):
        pass

    async def unreliable_operation():
        """Simulates an operation that fails randomly."""
        if random.random() < 0.7:
            raise ConnectionError("Network error")
        return "Success!"

    async def retry(coro_func, max_retries=3, base_delay=1.0):
        """Retry with exponential backoff."""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await coro_func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, 0.1 * delay)
                    print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay + jitter)

        raise RetryError(f"Failed after {max_retries} attempts") from last_exception

    async def main():
        try:
            result = await retry(unreliable_operation, max_retries=5)
            print(f"Result: {result}")
        except RetryError as e:
            print(f"All retries failed: {e}")

    asyncio.run(main())

异步上下文变量（Async Context Variable）
--------------------------------------------------------------

上下文 variables (Python 3.7+) 提供任务本地存储，类似于 thread 本地存储，但用于异步任务。对于请求 ID、用户上下文或数据库连接很有用。

.. code-block:: python

    import asyncio
    import contextvars

    # 创建上下文 variable
    request_id = contextvars.ContextVar('request_id', default=None)

    async def process_request(rid):
        request_id.set(rid)
        await step1()
        await step2()

    async def step1():
        rid = request_id.get()
        print(f"[{rid}] Step 1")
        await asyncio.sleep(0.1)

    async def step2():
        rid = request_id.get()
        print(f"[{rid}] Step 2")
        await asyncio.sleep(0.1)

    async def main():
        await asyncio.gather(
            process_request("req-001"),
            process_request("req-002"),
            process_request("req-003"),
        )

    asyncio.run(main())

TaskGroup 任务组（Python 3.11+）（TaskGroup (Python 3.11+)）
----------------------------------------------------------------------------------------------------------

``TaskGroup`` 提供结构化并发，确保所有任务一起完成或取消。 Exceptions 任何任务中取消组中的所有其他任务。

.. code-block:: python

    import asyncio

    async def task(name, delay, should_fail=False):
        await asyncio.sleep(delay)
        if should_fail:
            raise ValueError(f"{name} failed!")
        return f"{name} done"

    async def main():
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(task("A", 1))
                tg.create_task(task("B", 2))
                tg.create_task(task("C", 0.5, should_fail=True))
        except* ValueError as eg:
            for exc in eg.exceptions:
                print(f"Caught: {exc}")

    # Python 3.11+
    asyncio.run(main())
