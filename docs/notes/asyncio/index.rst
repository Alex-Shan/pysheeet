.. meta::
    :description lang=zh_CN: Python asyncio 教程涵盖 coroutines、event loops、任务、异步/等待语法、网络和 asynchronous 编程模式
    :keywords: Python, Python3, asyncio, async, await, coroutine, event loop, asynchronous, concurrent, networking, TCP, UDP

异步编程（Asyncio）
==========================

Python 的 ``asyncio`` module 提供了使用 coroutines 编写单线程并发代码、通过 sockets 和其他资源复用 I/O 访问、运行网络客户端和服务器以及其他相关原语的基础设施。与线程不同，asyncio 使用协作式多任务处理，其中任务自愿让出控制权以允许其他任务运行。这使得它非常适合 I/O 绑定的应用程序，例如 Web 服务器、数据库客户端和网络服务，其中等待外部资源是主要瓶颈。

本节涵盖 asyncio 从基本概念到高级模式，包括 event loop、coroutines、任务、同步原语以及 TCP/UDP 服务器、HTTP 客户端和连接池等实际示例。

.. toctree::
   :maxdepth: 1

   python-asyncio-guide
   python-asyncio-basic
   python-asyncio-server
   python-asyncio-advanced
