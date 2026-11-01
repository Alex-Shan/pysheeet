"""Tests for concurrency examples."""

import pytest
import time
from threading import Thread, Lock, RLock, Semaphore, Event, Condition, Barrier
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed


# Module 级 functions 用于 multiprocessing（必须可酸洗）
def _mp_square(x):
    return x * x


def _mp_add(a, b):
    return a + b


def _mp_worker(q, n):
    q.put(n * n)


def _mp_increment(counter):
    for _ in range(100):
        with counter.get_lock():
            counter.value += 1


def _mp_double(arr):
    for i in range(len(arr)):
        arr[i] *= 2


class TestThreading:
    """Test threading operations."""

    def test_thread_creation(self):
        """Test basic thread creation."""
        results = []

        def task(n):
            results.append(n)

        threads = [Thread(target=task, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert sorted(results) == [0, 1, 2, 3, 4]

    def test_thread_with_return_value(self):
        """Test getting return values from threads."""
        results = {}

        def compute(n, res):
            res[n] = n * n

        threads = [Thread(target=compute, args=(i, results)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results == {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

    def test_lock(self):
        """Test Lock for mutual exclusion."""
        counter = [0]
        lock = Lock()

        def increment():
            for _ in range(1000):
                with lock:
                    counter[0] += 1

        threads = [Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert counter[0] == 10000

    def test_rlock(self):
        """Test RLock for reentrant locking."""
        lock = RLock()
        results = []

        def outer():
            with lock:
                results.append("outer")
                inner()

        def inner():
            with lock:  # 相同的thread可以再次获取
                results.append("inner")

        t = Thread(target=outer)
        t.start()
        t.join()

        assert results == ["outer", "inner"]

    def test_semaphore(self):
        """Test Semaphore for resource limiting."""
        max_concurrent = [0]
        current = [0]
        sem = Semaphore(3)

        def task():
            with sem:
                current[0] += 1
                max_concurrent[0] = max(max_concurrent[0], current[0])
                time.sleep(0.01)
                current[0] -= 1

        threads = [Thread(target=task) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert max_concurrent[0] <= 3

    def test_event(self):
        """Test Event for thread signaling."""
        event = Event()
        results = []

        def waiter(n):
            event.wait()
            results.append(n)

        threads = [Thread(target=waiter, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()

        time.sleep(0.1)
        assert len(results) == 0  # 一切等待

        event.set()
        for t in threads:
            t.join()

        assert sorted(results) == [0, 1, 2]

    def test_condition(self):
        """Test Condition for complex synchronization."""
        items = []
        condition = Condition()
        consumed = []

        def producer():
            for i in range(3):
                with condition:
                    items.append(i)
                    condition.notify()

        def consumer():
            for _ in range(3):
                with condition:
                    while not items:
                        condition.wait()
                    consumed.append(items.pop(0))

        t1 = Thread(target=producer)
        t2 = Thread(target=consumer)
        t2.start()
        time.sleep(0.01)
        t1.start()
        t1.join()
        t2.join()

        assert consumed == [0, 1, 2]

    def test_barrier(self):
        """Test Barrier for synchronization point."""
        barrier = Barrier(3)
        order = []

        def worker(n):
            order.append(f"before_{n}")
            barrier.wait()
            order.append(f"after_{n}")

        threads = [Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 所有 "before" 应出现在所有 "after" 之前
        before_count = sum(1 for x in order[:3] if x.startswith("before"))
        assert before_count == 3

    def test_queue(self):
        """Test thread-safe Queue."""
        q = Queue()
        results = []

        def producer():
            for i in range(5):
                q.put(i)

        def consumer():
            for _ in range(5):
                results.append(q.get())
                q.task_done()

        t1 = Thread(target=producer)
        t2 = Thread(target=consumer)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert sorted(results) == [0, 1, 2, 3, 4]


class TestMultiprocessing:
    """Test multiprocessing operations."""

    def test_process_creation(self):
        """Test basic process creation."""
        from multiprocessing import Process, Queue as MPQueue

        q = MPQueue()
        processes = [Process(target=_mp_worker, args=(q, i)) for i in range(4)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        results = [q.get() for _ in range(4)]
        assert sorted(results) == [0, 1, 4, 9]

    def test_pool_map(self):
        """Test Pool.map for parallel execution."""
        from multiprocessing import Pool

        with Pool(2) as pool:
            results = pool.map(_mp_square, range(5))

        assert results == [0, 1, 4, 9, 16]

    def test_pool_starmap(self):
        """Test Pool.starmap for multiple arguments."""
        from multiprocessing import Pool

        with Pool(2) as pool:
            results = pool.starmap(_mp_add, [(1, 2), (3, 4), (5, 6)])

        assert results == [3, 7, 11]

    def test_shared_value(self):
        """Test shared Value between processes."""
        from multiprocessing import Process, Value

        counter = Value("i", 0)
        processes = [
            Process(target=_mp_increment, args=(counter,)) for _ in range(4)
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        assert counter.value == 400

    def test_shared_array(self):
        """Test shared Array between processes."""
        from multiprocessing import Process, Array

        arr = Array("i", [1, 2, 3, 4])
        p = Process(target=_mp_double, args=(arr,))
        p.start()
        p.join()

        assert list(arr) == [2, 4, 6, 8]


class TestConcurrentFutures:
    """Test concurrent.futures operations."""

    def test_thread_pool_map(self):
        """Test ThreadPoolExecutor.map."""

        def square(x):
            return x * x

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(square, range(5)))

        assert results == [0, 1, 4, 9, 16]

    def test_thread_pool_submit(self):
        """Test ThreadPoolExecutor.submit."""

        def compute(x):
            return x * 2

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(compute, i) for i in range(5)]
            results = [f.result() for f in futures]

        assert results == [0, 2, 4, 6, 8]

    def test_as_completed(self):
        """Test as_completed for processing results."""

        def task(n):
            time.sleep(0.1 - n * 0.02)  # 不同的延误
            return n

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(task, i) for i in range(3)]
            results = [f.result() for f in as_completed(futures)]

        # 结果可以按任意顺序排列
        assert sorted(results) == [0, 1, 2]

    def test_future_callback(self):
        """Test Future.add_done_callback."""
        results = []

        def on_complete(future):
            results.append(future.result())

        def compute(x):
            return x * x

        with ThreadPoolExecutor(max_workers=2) as executor:
            for i in range(3):
                future = executor.submit(compute, i)
                future.add_done_callback(on_complete)

        time.sleep(0.1)  # 等待callbacks
        assert sorted(results) == [0, 1, 4]

    def test_future_exception(self):
        """Test exception handling in futures."""

        def failing_task():
            raise ValueError("test error")

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(failing_task)

            with pytest.raises(ValueError, match="test error"):
                future.result()

    def test_future_timeout(self):
        """Test timeout on future.result()."""

        def slow_task():
            time.sleep(10)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(slow_task)

            from concurrent.futures import TimeoutError

            with pytest.raises(TimeoutError):
                future.result(timeout=0.1)

    def test_future_cancel(self):
        """Test cancelling a future."""

        def slow_task():
            time.sleep(10)

        with ThreadPoolExecutor(max_workers=1) as executor:
            # 第一个任务阻塞了worker
            future1 = executor.submit(slow_task)
            # 第二个任务已排队
            future2 = executor.submit(slow_task)

            time.sleep(0.01)  # 让第一个任务开始

            # 可以取消排队任务
            assert future2.cancel() == True
            assert future2.cancelled() == True

    def test_process_pool_map(self):
        """Test ProcessPoolExecutor.map."""
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(_mp_square, range(5)))

        assert results == [0, 1, 4, 9, 16]


class TestProducerConsumer:
    """Test producer-consumer patterns."""

    def test_basic_producer_consumer(self):
        """Test basic producer-consumer with Queue."""
        q = Queue()
        produced = []
        consumed = []

        def producer():
            for i in range(5):
                produced.append(i)
                q.put(i)
            q.put(None)  # 哨兵

        def consumer():
            while True:
                item = q.get()
                if item is None:
                    break
                consumed.append(item)

        t1 = Thread(target=producer)
        t2 = Thread(target=consumer)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert produced == consumed

    def test_multiple_consumers(self):
        """Test multiple consumers."""
        q = Queue()
        consumed = []
        lock = Lock()

        def producer():
            for i in range(10):
                q.put(i)
            for _ in range(3):  # 每个消费者的哨兵
                q.put(None)

        def consumer():
            while True:
                item = q.get()
                if item is None:
                    break
                with lock:
                    consumed.append(item)

        producer_thread = Thread(target=producer)
        consumer_threads = [Thread(target=consumer) for _ in range(3)]

        producer_thread.start()
        for t in consumer_threads:
            t.start()

        producer_thread.join()
        for t in consumer_threads:
            t.join()

        assert sorted(consumed) == list(range(10))
