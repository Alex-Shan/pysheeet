.. meta::
    :description lang=zh_CN: Python 线程教程，涵盖 thread 创建、同步原语、locks、semaphores、事件、条件和 thread-safe 数据结构
    :keywords: Python, Python3, threading, Thread, Lock, RLock, Semaphore, Event, Condition, synchronization, GIL, concurrent, parallel

==========================
线程（Threading）
==========================

:Source: `src/basic/concurrency_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/concurrency_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

``threading`` module 提供了用于在 Python 中创建和管理 threads 的高级接口。 Threads 是轻量级执行单元，它们在 process 内共享相同的内存空间，这使得它们能够高效地执行 I/O 绑定的任务，在这些任务中程序需要花时间等待外部资源。然而，由于 Python 的 Global Interpreter Lock (GIL)，threads 对于 CPU 绑定任务无法实现 true 并行性——只有一个 thread 可以在同一时间执行 Python 字节码。时间。对于 CPU 密集型工作，请考虑使用 ``multiprocessing`` 代替。

创建线程（Creating Threads）
--------------------------------------------

创建 threads 有两种主要方法：子类化 ``Thread`` 或传递目标 function。基于 function 的方法更加灵活且常用，而当您需要将 thread 状态和行为封装在 class 中时，子类化非常有用。

.. code-block:: python

    from threading import Thread

    # Method 1：Subclass Thread
    class Worker(Thread):
        def __init__(self, worker_id):
            super().__init__()
            self.worker_id = worker_id

        def run(self):
            print(f"Worker {self.worker_id} running")

    # Method 2：通过目标 function（首选）
    def task(worker_id):
        print(f"Task {worker_id} running")

    # 使用subclass
    t1 = Worker(1)
    t1.start()
    t1.join()

    # 使用目标 function
    t2 = Thread(target=task, args=(2,))
    t2.start()
    t2.join()

有返回值的线程（Thread with Return Value）
------------------------------------------------------------------

Threads 不会直接从目标 functions 获取 return values。要取回结果，您可以使用共享的 mutable objects、queues，或者在子类化 Thread 时将结果存储为 instance attributes。

.. code-block:: python

    from threading import Thread
    from queue import Queue

    def compute(n, results):
        """Store result in shared dict."""
        results[n] = n * n

    # 使用共享dictionary
    results = {}
    threads = []
    for i in range(5):
        t = Thread(target=compute, args=(i, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(results)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

    # 使用 Queue (thread-safe)
    def compute_queue(n, q):
        q.put((n, n * n))

    q = Queue()
    threads = []
    for i in range(5):
        t = Thread(target=compute_queue, args=(i, q))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    while not q.empty():
        n, result = q.get()
        print(f"{n}: {result}")

守护线程（Daemon Threads）
----------------------------------------

守护进程 threads 在后台运行，并在所有非守护进程 threads 完成后自动终止。它们对于不应阻止程序退出的后台任务非常有用，例如监视或清理任务。

.. code-block:: python

    from threading import Thread
    import time

    def background_task():
        while True:
            print("Background task running...")
            time.sleep(1)

    # 守护进程 thread - 不会阻止程序退出
    t = Thread(target=background_task, daemon=True)
    t.start()

    # thread主要工作
    time.sleep(3)
    print("Main thread done, daemon will be killed")

锁定 - 互斥（Lock - Mutual Exclusion）
----------------------------------------------------------------

``Lock`` 是最简单的同步原语，可防止多个 threads 同时访问共享资源。修改共享状态时始终使用 locks 以防止 race conditions。 context manager 语法 ( ``with lock:`` ) 是首选，因为它保证即使出现 exception 也能释放 lock。

.. code-block:: python

    from threading import Thread, Lock

    counter = 0
    lock = Lock()

    def increment(n):
        global counter
        for _ in range(n):
            with lock:  # 自动获取和释放
                counter += 1

    threads = [Thread(target=increment, args=(100000,)) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Counter: {counter}")  # lock 始终为 500000

RLock - 可重入锁（RLock - Reentrant Lock）
------------------------------------------------------------------------

同一个 thread 可以多次获取 ``RLock`` (reentrant lock)，而不会导致 deadlock。当 thread 需要调用也获取相同 lock 的 methods 时，例如在 recursive functions 中或当 methods 在同一 object 上调用其他 methods 时，这一点至关重要。

.. code-block:: python

    from threading import Thread, RLock

    class Counter:
        def __init__(self):
            self.value = 0
            self.lock = RLock()

        def increment(self):
            with self.lock:
                self.value += 1

        def increment_twice(self):
            with self.lock:  # 首次收购
                self.increment()  # 第二次收购 - 带 RLock 的 OK
                self.increment()

    counter = Counter()
    threads = [Thread(target=counter.increment_twice) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Value: {counter.value}")  # 200

信号量 - 资源限制（Semaphore - Resource Limiting）
----------------------------------------------------------------------------------

``Semaphore`` 限制可以同时访问资源的 threads 的数量。与仅允许一个 thread 的 lock 不同，计数为 N 的 semaphore 允许最多 N 个 threads 继续进行。这对于连接池、速率限制或控制对有限资源的访问很有用。

.. code-block:: python

    from threading import Thread, Semaphore
    import time

    # 最多允许 3 个并发连接
    connection_pool = Semaphore(3)

    def access_database(thread_id):
        print(f"Thread {thread_id} waiting for connection...")
        with connection_pool:
            print(f"Thread {thread_id} connected")
            time.sleep(1)  # 模拟数据库工作
            print(f"Thread {thread_id} disconnected")

    threads = [Thread(target=access_database, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

事件 - 线程信号（Event - Thread Signaling）
----------------------------------------------------------------------

``Event`` 是一种简单的信号发送机制，允许一个 thread 向其他 threads 发送发生了某事的信号。 Threads可以等待事件set，thread可以set或者清除事件。这对于协调 threads 之间的启动、关闭或状态更改非常有用。

.. code-block:: python

    from threading import Thread, Event
    import time

    ready = Event()

    def worker(worker_id):
        print(f"Worker {worker_id} waiting for signal...")
        ready.wait()  # 阻塞直到事件为 set
        print(f"Worker {worker_id} starting work")

    def coordinator():
        print("Coordinator preparing...")
        time.sleep(2)
        print("Coordinator: All systems go!")
        ready.set()  # 信号全部等待 threads

    threads = [Thread(target=worker, args=(i,)) for i in range(3)]
    threads.append(Thread(target=coordinator))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

条件 - 复杂同步（Condition - Complex Synchronization）
--------------------------------------------------------------------------------------------

``Condition`` 将 lock 与等待和通知状态更改的功能相结合。这对于生产者-消费者模式至关重要，在这种模式中，threads 需要等待特定条件（如 "buffer not empty" 或 "buffer not full"）才能继续。

.. code-block:: python

    from threading import Thread, Condition
    import time

    items = []
    condition = Condition()

    def producer():
        for i in range(5):
            time.sleep(0.5)
            with condition:
                items.append(i)
                print(f"Produced: {i}")
                condition.notify()  # 唤醒一位等待的消费者

    def consumer():
        while True:
            with condition:
                while not items:  # 等待 items 可用
                    condition.wait()
                item = items.pop(0)
                print(f"Consumed: {item}")
                if item == 4:
                    break

    t1 = Thread(target=producer)
    t2 = Thread(target=consumer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

屏障 - 同步点（Barrier - Synchronization Point）
----------------------------------------------------------------------------------

``Barrier`` 会阻塞指定数量的 threads，直到所有 threads 都到达 barrier point，再同时释放它们。如果需要多个 threads 全部完成某一阶段后才能开始下一阶段，可以使用它。

.. code-block:: python

    from threading import Thread, Barrier
    import time
    import random

    barrier = Barrier(3)

    def worker(worker_id):
        # 第一阶段：初始化
        print(f"Worker {worker_id} initializing...")
        time.sleep(random.uniform(0.5, 2))
        print(f"Worker {worker_id} waiting at barrier")

        barrier.wait()  # 等待所有threads

        # 第2阶段：所有threads一起进行
        print(f"Worker {worker_id} proceeding")

    threads = [Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

定时器 - 延迟执行（Timer - Delayed Execution）
--------------------------------------------------------------------------

``Timer`` 是在指定延迟后执行 function 的 thread。它可以在触发之前取消。这对于超时、延迟清理或调度一次性任务很有用。

.. code-block:: python

    from threading import Timer

    def delayed_task():
        print("Task executed after delay")

    # 2秒后执行
    timer = Timer(2.0, delayed_task)
    timer.start()

    # 可以在触发前取消
    # timer.cancel()

线程本地数据（Thread-Local Data）
--------------------------------------------------

``threading.local()`` 提供 thread 本地存储，其中每个 thread 都有自己独立的数据副本。这对于存储每个 thread 状态而不通过 function arguments 传递它非常有用，例如 Web 应用程序中的数据库连接或请求上下文。

.. code-block:: python

    from threading import Thread, local

    # 每个 thread 都有自己的 'data' attribute
    thread_data = local()

    def worker(worker_id):
        thread_data.value = worker_id
        process()

    def process():
        # 访问 thread-本地数据，无需传递为 argument
        print(f"Processing with value: {thread_data.value}")

    threads = [Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

带队列的生产者-消费者（Producer-Consumer with Queue）
----------------------------------------------------------------------------------

``queue.Queue`` class 提供了 thread-safe FIFO queue 来处理内部所有锁定。这是 threads 之间以生产者-消费者模式进行通信的推荐方式，因为它消除了手动同步的需要。

.. code-block:: python

    from threading import Thread
    from queue import Queue
    import time

    def producer(q, items):
        for item in items:
            time.sleep(0.1)
            q.put(item)
            print(f"Produced: {item}")
        q.put(None)  # 发出完成信号的哨兵

    def consumer(q):
        while True:
            item = q.get()
            if item is None:
                break
            print(f"Consumed: {item}")
            q.task_done()

    q = Queue(maxsize=5)  # 有界 queue
    items = list(range(10))

    t1 = Thread(target=producer, args=(q, items))
    t2 = Thread(target=consumer, args=(q,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

死锁示例及预防（Deadlock Example and Prevention）
--------------------------------------------------------------------------------

当两个或多个 threads 相互等待释放 locks 时，会发生 Deadlock，从而创建循环依赖关系。典型的例子是当thread A持有lock 1并等待lock 2，而thread B持有lock 2并等待lock 1时。通过始终以一致的顺序获取locks来防止deadlocks。

.. code-block:: python

    from threading import Thread, Lock
    import time

    lock1 = Lock()
    lock2 = Lock()

    # DEADLOCK EXAMPLE - DON'T DO THIS
    def task_a_bad():
        with lock1:
            print("Task A acquired lock1")
            time.sleep(0.1)
            with lock2:  # 等待锁2
                print("Task A acquired lock2")

    def task_b_bad():
        with lock2:
            print("Task B acquired lock2")
            time.sleep(0.1)
            with lock1:  # 等待锁1 - DEADLOCK！
                print("Task B acquired lock1")

    # CORRECT - 始终以相同的顺序获取 locks
    def task_a_good():
        with lock1:
            with lock2:
                print("Task A acquired both locks")

    def task_b_good():
        with lock1:  # 与 task_a 相同的订单
            with lock2:
                print("Task B acquired both locks")

了解 GIL（Understanding the GIL）
----------------------------------------------------------

全局 Interpreter Lock (GIL) 是一个 mutex，它保护对 Python objects 的访问，防止多个 threads 同时执行 Python 字节码。这意味着 threads 不会为 CPU 绑定任务提供加速。但是，GIL 在 I/O 操作期间释放，使得 threads 对于 I/O 绑定任务有效。

.. code-block:: python

    from threading import Thread
    import time

    def cpu_bound(n):
        """CPU-bound task - GIL limits parallelism."""
        count = 0
        for i in range(n):
            count += i
        return count

    def io_bound(seconds):
        """I/O-bound task - GIL released during sleep."""
        time.sleep(seconds)

    # CPU 绑定：threads 不会有帮助（可能由于 GIL 争用而变慢）
    start = time.time()
    threads = [Thread(target=cpu_bound, args=(10**7,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"CPU-bound threaded: {time.time() - start:.2f}s")

    # I/O 绑定：threads 有显着帮助
    start = time.time()
    threads = [Thread(target=io_bound, args=(1,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"I/O-bound threaded: {time.time() - start:.2f}s")  # ~1 秒，而不是 4 秒
