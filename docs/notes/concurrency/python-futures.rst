.. meta::
    :description lang=zh_CN: Python concurrent.futures 教程，涵盖 ThreadPoolExecutor、ProcessPoolExecutor、Future objects、callbacks 和高级并行执行模式
    :keywords: Python, Python3, concurrent.futures, ThreadPoolExecutor, ProcessPoolExecutor, Future, executor, submit, map, as_completed, parallel

==================================================================================
concurrent.futures 用法（concurrent.futures）
==================================================================================

:Source: `src/basic/concurrency_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/concurrency_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

``concurrent.futures`` module 提供了一个高级接口，用于使用 threads 或 processes 异步执行可调用程序。它将线程和multiprocessing之间的差异抽象到统一的API背后，使得它们之间的切换变得很容易。 module 引入了两个 key 概念：管理工作池的 **Executors**和表示 asynchronous 操作的最终结果的**Futures** 。

ThreadPoolExecutor 基础知识（ThreadPoolExecutor Basics）
----------------------------------------------------------------------------------------------------

``ThreadPoolExecutor`` 管理并发执行任务的 threads 池。将其用于 I/O 绑定的任务，例如网络请求、文件操作或数据库查询，其中 threads 花费时间等待外部资源。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    import time

    def fetch_url(url):
        """Simulate fetching a URL."""
        time.sleep(1)  # 模拟网络延迟
        return f"Content from {url}"

    urls = ["http://site1.com", "http://site2.com", "http://site3.com"]

    # 顺序 - 需要约 3 秒
    start = time.time()
    results = [fetch_url(url) for url in urls]
    print(f"Sequential: {time.time() - start:.2f}s")

    # 并发 - 大约需要 1 秒
    start = time.time()
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_url, urls))
    print(f"Concurrent: {time.time() - start:.2f}s")

ProcessPoolExecutor 基础知识（ProcessPoolExecutor Basics）
--------------------------------------------------------------------------------------------------------

``ProcessPoolExecutor`` 管理用于 true 并行执行的 processes 池。将其用于 CPU 绑定任务，例如需要利用多个 CPU 内核的数据处理、计算或图像处理。

.. code-block:: python

    from concurrent.futures import ProcessPoolExecutor
    import time

    def cpu_intensive(n):
        """CPU-bound computation."""
        return sum(i * i for i in range(n))

    if __name__ == "__main__":
        numbers = [10**7] * 4

        # 顺序
        start = time.time()
        results = [cpu_intensive(n) for n in numbers]
        print(f"Sequential: {time.time() - start:.2f}s")

        # 与processes并联
        start = time.time()
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(cpu_intensive, numbers))
        print(f"Parallel: {time.time() - start:.2f}s")

使用 submit() 和 Future 对象（Using submit() and Future Objects）
--------------------------------------------------------------------------------------------------------------------

``submit()`` method 调度可调用并立即返回 ``Future`` object。 Future代表待处理的结果，并提供methods来检查状态、获取结果或取消任务。这比 ``map()`` 提供了更多的控制来处理单个任务。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    import time

    def task(name, duration):
        time.sleep(duration)
        return f"{name} completed in {duration}s"

    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务-立即返回Future
        future1 = executor.submit(task, "Task A", 2)
        future2 = executor.submit(task, "Task B", 1)
        future3 = executor.submit(task, "Task C", 3)

        # 检查是否完成（非阻塞）
        print(f"Task A done: {future1.done()}")

        # 获取结果（阻塞）
        print(future2.result())  # 等待完成
        print(future1.result())
        print(future3.result())

按完成顺序处理结果（Processing Results as They Complete）
--------------------------------------------------------------------------------------------

无论提交顺序如何， ``as_completed()`` 都会在完成后产生期货。当您希望在 process 结果可用时立即获取结果而不是等待所有任务完成时，这非常有用。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    import random

    def fetch_data(source_id):
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
        return f"Data from source {source_id} (took {delay:.2f}s)"

    sources = range(5)

    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_source = {
            executor.submit(fetch_data, src): src
            for src in sources
        }

        # Process 完成后的结果
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                result = future.result()
                print(f"Source {source}: {result}")
            except Exception as e:
                print(f"Source {source} failed: {e}")

使用 wait() 控制完成条件（Using wait() for Completion Control）
----------------------------------------------------------------------------------------------------------

``wait()`` 会阻塞，直到指定的期货完成。您可以等待所有任务、第一个任务或第一个 exception。这提供了对何时继续进行的细粒度控制。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
    import time

    def task(task_id, duration):
        time.sleep(duration)
        return f"Task {task_id} done"

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(task, 1, 3),
            executor.submit(task, 2, 1),
            executor.submit(task, 3, 2),
        ]

        # 等待第一个完成
        done, not_done = wait(futures, return_when=FIRST_COMPLETED)
        print(f"First completed: {done.pop().result()}")
        print(f"Still running: {len(not_done)}")

        # 等待所有剩余的
        done, not_done = wait(not_done, return_when=ALL_COMPLETED)
        for f in done:
            print(f"Completed: {f.result()}")

向 Future 添加回调（Adding Callbacks to Futures）
------------------------------------------------------------------------------------

Callbacks 是在 future 完成时自动执行的 functions。它们对于处理结果而不阻塞主 thread 或链接操作非常有用。 callback 接收未来作为其 argument。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    import time

    def compute(n):
        time.sleep(1)
        return n * n

    def on_complete(future):
        """Callback executed when future completes."""
        try:
            result = future.result()
            print(f"Callback: result is {result}")
        except Exception as e:
            print(f"Callback: task failed with {e}")

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(5):
            future = executor.submit(compute, i)
            future.add_done_callback(on_complete)

        # 主 thread 继续，而 callbacks 开火
        print("Main thread: tasks submitted")
        time.sleep(2)
        print("Main thread: done waiting")

异常处理（Exception Handling）
------------------------------------------------

当您调用 ``result()`` 时，任务中引发的 Exceptions 将被捕获并重新引发。您还可以使用 ``exception()`` 检查 exceptions。始终处理 exceptions 以防止无提示故障。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def risky_task(n):
        if n == 3:
            raise ValueError(f"Bad value: {n}")
        return n * 2

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(risky_task, i): i for i in range(5)}

        for future in as_completed(futures):
            n = futures[future]
            try:
                result = future.result()
                print(f"Task {n}: {result}")
            except ValueError as e:
                print(f"Task {n} failed: {e}")

        # 替代方案：检查 exception 而不加注
        future = executor.submit(risky_task, 3)
        future.result()  # 等待完成
        if future.exception() is not None:
            print(f"Exception occurred: {future.exception()}")

超时处理（Timeout Handling）
--------------------------------------------

``result()`` 和 ``as_completed()`` 都接受超时 parameters。如果任务未在超时内完成，则会引发 ``TimeoutError`` 。这可以防止无限期地阻塞缓慢或卡住的任务。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
    import time

    def slow_task(duration):
        time.sleep(duration)
        return f"Completed after {duration}s"

    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(slow_task, 5)

        try:
            # 最多等待 2 秒即可得到结果
            result = future.result(timeout=2)
            print(result)
        except TimeoutError:
            print("Task timed out!")
            # 注意：任务继续在后台运行

        # as_completed 超时
        futures = [executor.submit(slow_task, i) for i in [1, 3, 5]]
        try:
            for future in as_completed(futures, timeout=2):
                print(future.result())
        except TimeoutError:
            print("Some tasks didn't complete in time")

取消任务（Cancelling Tasks）
--------------------------------------------

使用 ``cancel()`` 可以在任务开始执行之前取消任务。任务一旦开始就无法取消。检查 ``cancelled()`` 是否取消成功。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    import time

    def long_task(n):
        time.sleep(2)
        return n

    with ThreadPoolExecutor(max_workers=1) as executor:
        # 将多个任务提交给单个工人
        future1 = executor.submit(long_task, 1)
        future2 = executor.submit(long_task, 2)  # 已排队，未开始
        future3 = executor.submit(long_task, 3)  # 已排队，未开始

        time.sleep(0.1)  # 让第一个任务开始

        # 尝试取消排队任务
        cancelled2 = future2.cancel()
        cancelled3 = future3.cancel()

        print(f"Future 2 cancelled: {cancelled2}")  # True
        print(f"Future 3 cancelled: {cancelled3}")  # True
        print(f"Future 1 cancelled: {future1.cancel()}")  # False（已运行）

Executor 上下文管理器（Executor Context Manager）
----------------------------------------------------------------------------------

使用执行器作为 context managers ( ``with`` statement) 可确保正确的清理。退出上下文时，会自动调用 ``shutdown(wait=True)`` ，等待所有待处理任务完成后再返回。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    import time

    def task(n):
        time.sleep(1)
        return n * 2

    # Context manager - 自动清理
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(task, i) for i in range(5)]
        # 执行器在退出'with'块时等待所有任务

    print("All tasks completed")

    # 手动管理（不推荐）
    executor = ThreadPoolExecutor(max_workers=3)
    try:
        futures = [executor.submit(task, i) for i in range(5)]
    finally:
        executor.shutdown(wait=True)  # 必须显式调用

分块映射（Map with Chunking）
----------------------------------------------

对于大型 iterables， ``map()`` 通过分块可以更加高效。 ``chunksize`` parameter 将 items 组合在一起，从而减少使用 ``ProcessPoolExecutor`` 时 process 间通信的开销。

.. code-block:: python

    from concurrent.futures import ProcessPoolExecutor
    import time

    def process_item(x):
        return x * x

    if __name__ == "__main__":
        items = range(100000)

        # 没有分块 - 更多 IPC 开销
        start = time.time()
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_item, items))
        print(f"No chunking: {time.time() - start:.2f}s")

        # 通过分块 - 减少 IPC 开销
        start = time.time()
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_item, items, chunksize=1000))
        print(f"With chunking: {time.time() - start:.2f}s")

实际示例：并行下载（Real-World Example: Parallel Downloads）
--------------------------------------------------------------------------------------------------

此示例演示了一个实际用例：同时下载多个文件以及进度跟踪、错误处理和超时管理。

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import urllib.request
    import time

    def download(url, timeout=10):
        """Download URL content with timeout."""
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                content = response.read()
                return url, len(content), None
        except Exception as e:
            return url, 0, str(e)

    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.google.com",
        "https://httpbin.org/delay/5",  # 慢端点
    ]

    print("Starting downloads...")
    start = time.time()

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(download, url): url for url in urls}

        for future in as_completed(future_to_url, timeout=15):
            url, size, error = future.result()
            if error:
                print(f"FAILED: {url} - {error}")
            else:
                print(f"OK: {url} - {size} bytes")

    print(f"Total time: {time.time() - start:.2f}s")
