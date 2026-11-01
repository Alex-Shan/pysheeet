.. meta::
    :description lang=zh_CN: Python multiprocessing 教程涵盖 process 创建、池、共享内存、process 间通信以及并行 CPU 绑定任务执行
    :keywords: Python, Python3, multiprocessing, Process, Pool, Queue, Pipe, shared memory, parallel, CPU-bound, GIL bypass

========================================
多进程（Multiprocessing）
========================================

:Source: `src/basic/concurrency_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/concurrency_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

``multiprocessing`` module 通过生成单独的 Python processes 来实现 true 并行执行， 每个都有自己的 Python interpreter 和内存空间。 与threads不同， processes 绕过全局 Interpreter Lock (GIL)， 使 multiprocessing 成为需要利用多个 CPU 内核的 CPU 绑定任务的理想选择。 与 threads 相比，代价是 process 创建和 process 间通信的开销更高。

创建进程（Creating Processes）
------------------------------------------------

创建 processes 与创建 threads 类似。每个 process 在独立的 memory space 中运行，因此一个 process 对 variables 的修改不会影响其他 processes。使用 ``start()`` 开始执行，使用 ``join()`` 等待执行完成。

.. code-block:: python

    from multiprocessing import Process
    import os

    def worker(name):
        print(f"Worker {name}, PID: {os.getpid()}")

    if __name__ == "__main__":
        processes = []
        for i in range(4):
            p = Process(target=worker, args=(i,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        print(f"Main process PID: {os.getpid()}")

进程池（Process Pool）
----------------------------------

一个 ``Pool`` 管理一个collection的worker processes，并在它们之间分配任务。这比为每个任务创建新的 process 更有效，因为 processes 被重复使用。该池提供 methods（如 ``map()`` 、 ``apply()`` ）及其针对不同用例的异步变体。

.. code-block:: python

    from multiprocessing import Pool
    import time

    def cpu_intensive(n):
        """Simulate CPU-bound work."""
        total = 0
        for i in range(n):
            total += i * i
        return total

    if __name__ == "__main__":
        numbers = [10**6, 10**6, 10**6, 10**6]

        # 顺序执行
        start = time.time()
        results = [cpu_intensive(n) for n in numbers]
        print(f"Sequential: {time.time() - start:.2f}s")

        # 与 Pool 并行执行
        start = time.time()
        with Pool(4) as pool:
            results = pool.map(cpu_intensive, numbers)
        print(f"Parallel: {time.time() - start:.2f}s")

池方法（Pool Methods）
----------------------------------

池class提供了多个methods用于分配工作。 ``map()`` 将 function 应用于 iterable 中的每个 item，并按顺序返回结果。 ``apply()`` 使用 arguments 调用 function 并阻塞直至完成。 ``_async`` 变体立即返回，并带有 ``AsyncResult`` object。

.. code-block:: python

    from multiprocessing import Pool

    def square(x):
        return x * x

    def add(a, b):
        return a + b

    if __name__ == "__main__":
        with Pool(4) as pool:
            # 地图 - 将 function 应用于 iterable
            results = pool.map(square, range(10))
            print(f"map: {results}")

            # starmap - 从 iterable 中解压 arguments
            pairs = [(1, 2), (3, 4), (5, 6)]
            results = pool.starmap(add, pairs)
            print(f"starmap: {results}")

            # apply_async - 非阻塞单次调用
            result = pool.apply_async(square, (10,))
            print(f"apply_async: {result.get()}")

            # map_async - 非阻塞地图
            result = pool.map_async(square, range(5))
            print(f"map_async: {result.get()}")

使用 Queue 共享数据（Sharing Data with Queue）
----------------------------------------------------------------------------

Processes 默认不共享内存。 ``multiprocessing.Queue`` 提供 thread-safe 和 process-safe 的方式，在 processes 之间交换数据。对于大多数 inter-process communication 场景，推荐使用这种方式。

.. code-block:: python

    from multiprocessing import Process, Queue

    def producer(q, items):
        for item in items:
            q.put(item)
            print(f"Produced: {item}")
        q.put(None)  # 哨兵

    def consumer(q):
        while True:
            item = q.get()
            if item is None:
                break
            print(f"Consumed: {item}")

    if __name__ == "__main__":
        q = Queue()
        items = list(range(5))

        p1 = Process(target=producer, args=(q, items))
        p2 = Process(target=consumer, args=(q,))

        p1.start()
        p2.start()
        p1.join()
        p2.join()

使用 Pipe 共享数据（Sharing Data with Pipe）
------------------------------------------------------------------------

``Pipe`` 在两个 processes 之间创建双向通信通道。它比 Queue 的点对点通信更简单、更快，但仅支持两个端点。每端都可以发送和接收数据。

.. code-block:: python

    from multiprocessing import Process, Pipe

    def sender(conn):
        conn.send("Hello from sender")
        conn.send([1, 2, 3])
        response = conn.recv()
        print(f"Sender received: {response}")
        conn.close()

    def receiver(conn):
        msg = conn.recv()
        print(f"Receiver got: {msg}")
        data = conn.recv()
        print(f"Receiver got: {data}")
        conn.send("Thanks!")
        conn.close()

    if __name__ == "__main__":
        parent_conn, child_conn = Pipe()

        p1 = Process(target=sender, args=(parent_conn,))
        p2 = Process(target=receiver, args=(child_conn,))

        p1.start()
        p2.start()
        p1.join()
        p2.join()

使用 Value 与 Array 共享内存（Shared Memory with Value and Array）
------------------------------------------------------------------------------------------------------------------

对于简单共享状态， ``Value`` 和 ``Array`` 提供多个 processes 可以访问的共享内存。对于频繁访问的数据，它们比 Queue/Pipe 更快，但需要仔细同步以避免 race conditions。

.. code-block:: python

    from multiprocessing import Process, Value, Array

    def increment(counter, lock_needed=True):
        for _ in range(10000):
            with counter.get_lock():
                counter.value += 1

    def modify_array(arr):
        for i in range(len(arr)):
            arr[i] = arr[i] * 2

    if __name__ == "__main__":
        # 共享integer
        counter = Value('i', 0)  # 'i' = 签名 int
        processes = [Process(target=increment, args=(counter,)) for _ in range(4)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        print(f"Counter: {counter.value}")  # 40000

        # 共享array
        arr = Array('d', [1.0, 2.0, 3.0, 4.0])  # 'd' = 双
        p = Process(target=modify_array, args=(arr,))
        p.start()
        p.join()
        print(f"Array: {list(arr)}")  # [2.0, 4.0, 6.0, 8.0]

使用 Manager 共享复杂对象（Manager for Complex Shared Objects）
----------------------------------------------------------------------------------------------------------

``Manager`` 提供了一种在 processes 之间共享更多 complex Python objects（lists、dicts）的方法。管理器运行一个服务器 process，该服务器保存实际的 objects，其他 processes 通过代理访问它们。这比 Value/Array 慢，但支持任意 Python objects。

.. code-block:: python

    from multiprocessing import Process, Manager

    def worker(shared_dict, shared_list, worker_id):
        shared_dict[worker_id] = worker_id * 10
        shared_list.append(worker_id)

    if __name__ == "__main__":
        with Manager() as manager:
            shared_dict = manager.dict()
            shared_list = manager.list()

            processes = []
            for i in range(4):
                p = Process(target=worker, args=(shared_dict, shared_list, i))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            print(f"Dict: {dict(shared_dict)}")
            print(f"List: {list(shared_list)}")

进程同步（Process Synchronization）
----------------------------------------------------------

Multiprocessing 提供与线程相同的同步原语： ``Lock`` 、 ``RLock`` 、 ``Semaphore`` 、 ``Event`` 、 ``Condition`` 和 ``Barrier`` 。它们适用于 processes 而不是 threads。

.. code-block:: python

    from multiprocessing import Process, Lock, Value

    def safe_increment(counter, lock):
        for _ in range(10000):
            with lock:
                counter.value += 1

    if __name__ == "__main__":
        lock = Lock()
        counter = Value('i', 0)

        processes = [
            Process(target=safe_increment, args=(counter, lock))
            for _ in range(4)
        ]

        for p in processes:
            p.start()
        for p in processes:
            p.join()

        print(f"Counter: {counter.value}")  # 40000

守护进程（Daemon Processes）
--------------------------------------------

与守护进程 threads 一样，守护进程 processes 在主 process 退出时终止。它们对于不应该阻止程序终止的后台任务很有用。 Set ``daemon=True`` 在调用 ``start()`` 之前。

.. code-block:: python

    from multiprocessing import Process
    import time

    def background_task():
        while True:
            print("Background process running...")
            time.sleep(1)

    if __name__ == "__main__":
        p = Process(target=background_task, daemon=True)
        p.start()

        time.sleep(3)
        print("Main process exiting, daemon will be terminated")

处理进程终止（Handling Process Termination）
------------------------------------------------------------------------

Processes 可以使用 ``terminate()`` 正常终止，也可以使用 ``kill()`` 强制终止。始终正确清理资源，并考虑在生产代码中使用信号正常关闭。

.. code-block:: python

    from multiprocessing import Process
    import time
    import signal

    def long_running_task():
        try:
            while True:
                print("Working...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Graceful shutdown")

    if __name__ == "__main__":
        p = Process(target=long_running_task)
        p.start()

        time.sleep(3)

        # 优雅终止 (SIGTERM)
        p.terminate()
        p.join(timeout=2)

        # 如果还活着就强制杀死
        if p.is_alive():
            p.kill()
            p.join()

        print(f"Exit code: {p.exitcode}")

ProcessPoolExecutor 进程池（ProcessPoolExecutor）
----------------------------------------------------------------------------------------

``concurrent.futures.ProcessPoolExecutor`` 为 process 池提供与 ``ThreadPoolExecutor`` 一致的更高级别接口。它通常比 ``multiprocessing.Pool`` 更容易使用，并且与期货模式很好地集成。

.. code-block:: python

    from concurrent.futures import ProcessPoolExecutor, as_completed

    def compute(n):
        return sum(i * i for i in range(n))

    if __name__ == "__main__":
        numbers = [10**6, 10**6, 10**6, 10**6]

        with ProcessPoolExecutor(max_workers=4) as executor:
            # 提交个人任务
            futures = [executor.submit(compute, n) for n in numbers]

            # Process 完成后的结果
            for future in as_completed(futures):
                print(f"Result: {future.result()}")

            # 或者使用地图来获取有序结果
            results = list(executor.map(compute, numbers))
            print(f"All results: {results}")

比较线程与进程（Comparing Threads vs Processes）
------------------------------------------------------------------------------

对于 I/O 绑定任务（网络、文件 I/O）选择 threads，其中 GIL 在等待期间被释放。对于需要 true 并行性的 CPU 绑定任务，请选择 processes。此示例演示了性能差异。

.. code-block:: python

    from threading import Thread
    from multiprocessing import Process, Pool
    import time

    def cpu_bound(n):
        """CPU-intensive task."""
        return sum(i * i for i in range(n))

    if __name__ == "__main__":
        n = 10**7
        count = 4

        # 顺序
        start = time.time()
        for _ in range(count):
            cpu_bound(n)
        print(f"Sequential: {time.time() - start:.2f}s")

        # Threads（受GIL限制）
        start = time.time()
        threads = [Thread(target=cpu_bound, args=(n,)) for _ in range(count)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print(f"Threads: {time.time() - start:.2f}s")

        # Processes（true并行度）
        start = time.time()
        with Pool(count) as pool:
            pool.map(cpu_bound, [n] * count)
        print(f"Processes: {time.time() - start:.2f}s")
