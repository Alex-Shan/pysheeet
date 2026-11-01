.. meta::
    :description lang=zh_CN: Python 并发教程，涵盖线程、multiprocessing、locks、semaphores、queues、process 池和 concurrent.futures
    :keywords: Python, Python3, threading, multiprocessing, concurrency, parallel, lock, semaphore, queue, ThreadPoolExecutor, ProcessPoolExecutor, GIL

并发（Concurrency）
==============================

Python 提供多种并发执行方法，以高效处理 CPU 绑定和 I/O 绑定任务。 ``threading`` module 可在单个 process 内实现轻量级并发执行，而 ``multiprocessing`` 通过使用单独的 processes 实现 true 并行性来绕过全局 Interpreter Lock (GIL)。 ``concurrent.futures`` module 提供了一个高级接口，将 threads 和 processes 之间的差异抽象为统一的 API。

了解何时使用每种方法至关重要：threads 擅长于 I/O 绑定任务（网络请求、文件操作），其中 GIL 在等待期间被释放，而 processes 更适合 CPU 绑定任务（计算、数据处理），其中 true 需要并行执行。

.. toctree::
   :maxdepth: 1

   python-threading
   python-multiprocessing
   python-futures
