.. meta::
    :description lang=zh_CN: Python asynchronous socket 编程教程，包含 select、poll、epoll、kqueue 和选择器 module，用于构建高性能非阻塞服务器
    :keywords: Python, socket, async, select, poll, epoll, kqueue, selectors, non-blocking, event-driven, I/O multiplexing, concurrent connections, high-performance server

======================================================
异步套接字 I/O（Async Socket I/O）
======================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Asynchronous I/O 是构建高性能网络服务器的关键，使其能够高效处理数千个并发连接。传统 blocking I/O 为每个连接使用一个 thread，受内存开销和 context switching 成本限制，难以扩展。Asynchronous I/O 通过 I/O multiplexing，让单个 thread 处理多个连接：程序同时监视多个 sockets，并处理其中已准备好读取或写入的 sockets。

本节介绍 Python 中 I/O 复用的演变，从经典的 ``select()`` 系统调用（可移植但有限）到现代高性能机制，如 ``epoll`` (Linux) 和 ``kqueue`` (BSD/macOS)处理数万个连接。我们还介绍了 ``selectors`` module，它提供了一个高级、独立于平台的接口，可自动使用最佳的可用机制。即使您使用 ``asyncio`` 等更高级别的框架，理解这些原语也很有价值，因为它们构建在这些相同的概念之上。

异步 TCP 服务器：select（Async TCP Server - select）
----------------------------------------------------------------------------------------

``select()`` 是最古老、最便携的 I/O 复用机制，几乎可用于所有平台，包括 Windows、Linux 和 macOS。它监视 file descriptors 的三个条件：可读性（可供读取的数据）、可写性（buffer 的空间可供写入）和异常条件（错误）。虽然可移植，但 ``select()`` 也有局限性：它通常仅支持最多 1024 个 file descriptors，并且具有 O(n) 性能，因为它必须在每次调用时扫描所有受监控的描述符。

.. code-block:: python

    from select import select
    import socket

    host = ('localhost', 5566)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(host)
    sock.listen(5)

    read_list = [sock]
    write_list = []
    messages = {}

    try:
        while True:
            readable, writable, _ = select(read_list, write_list, [])

            for s in readable:
                if s == sock:
                    conn, addr = sock.accept()
                    read_list.append(conn)
                else:
                    msg = s.recv(1024)
                    if msg:
                        messages[s.fileno()] = msg
                        write_list.append(s)
                    else:
                        read_list.remove(s)
                        s.close()

            for s in writable:
                msg = messages.pop(s.fileno(), None)
                if msg:
                    s.send(msg)
                write_list.remove(s)
    except KeyboardInterrupt:
        sock.close()

异步 TCP 服务器：poll（Async TCP Server - poll）
--------------------------------------------------------------------------------

``poll()`` 与 ``select()`` 类似，但对于大量 file descriptors 效率更高。在 Unix 系统上可用。

.. code-block:: python

    import socket
    import select
    import contextlib

    host = 'localhost'
    port = 5566

    connections = {}
    requests = {}
    responses = {}

    @contextlib.contextmanager
    def create_server(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind((host, port))
        s.listen(10)
        try:
            yield s
        finally:
            s.close()

    def accept(server, poll):
        conn, addr = server.accept()
        conn.setblocking(False)
        fd = conn.fileno()
        poll.register(fd, select.POLLIN)
        requests[fd] = conn
        connections[fd] = conn

    def recv(fd, poll):
        conn = requests.pop(fd, None)
        if not conn:
            return
        msg = conn.recv(1024)
        if msg:
            responses[fd] = msg
            poll.modify(fd, select.POLLOUT)
        else:
            poll.unregister(fd)
            conn.close()
            connections.pop(fd, None)

    def send(fd, poll):
        conn = connections.get(fd)
        msg = responses.pop(fd, None)
        if conn and msg:
            conn.send(msg)
            requests[fd] = conn
            poll.modify(fd, select.POLLIN)

    with create_server(host, port) as server:
        poll = select.poll()
        poll.register(server.fileno(), select.POLLIN)

        try:
            while True:
                events = poll.poll(1000)
                for fd, event in events:
                    if fd == server.fileno():
                        accept(server, poll)
                    elif event & (select.POLLIN | select.POLLPRI):
                        recv(fd, poll)
                    elif event & select.POLLOUT:
                        send(fd, poll)
        except KeyboardInterrupt:
            pass

异步 TCP 服务器 - epoll（Async TCP Server - epoll）
----------------------------------------------------------------------------------------

``epoll`` 是 Linux 专用的，对于处理数千个连接最有效。它使用边缘触发或电平触发的通知。

.. code-block:: python

    import socket
    import select
    import contextlib

    host = 'localhost'
    port = 5566

    connections = {}
    requests = {}
    responses = {}

    @contextlib.contextmanager
    def create_server(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind((host, port))
        s.listen(10)
        try:
            yield s
        finally:
            s.close()

    def accept(server, epoll):
        conn, addr = server.accept()
        conn.setblocking(False)
        fd = conn.fileno()
        epoll.register(fd, select.EPOLLIN)
        requests[fd] = conn
        connections[fd] = conn

    def recv(fd, epoll):
        conn = requests.pop(fd, None)
        if not conn:
            return
        msg = conn.recv(1024)
        if msg:
            responses[fd] = msg
            epoll.modify(fd, select.EPOLLOUT)
        else:
            epoll.unregister(fd)
            conn.close()
            connections.pop(fd, None)

    def send(fd, epoll):
        conn = connections.get(fd)
        msg = responses.pop(fd, None)
        if conn and msg:
            conn.send(msg)
            requests[fd] = conn
            epoll.modify(fd, select.EPOLLIN)

    with create_server(host, port) as server:
        epoll = select.epoll()
        epoll.register(server.fileno(), select.EPOLLIN)

        try:
            while True:
                events = epoll.poll(1)
                for fd, event in events:
                    if fd == server.fileno():
                        accept(server, epoll)
                    elif event & select.EPOLLIN:
                        recv(fd, epoll)
                    elif event & select.EPOLLOUT:
                        send(fd, epoll)
        except KeyboardInterrupt:
            pass
        finally:
            epoll.close()

异步 TCP 服务器 - kqueue（Async TCP Server - kqueue）
--------------------------------------------------------------------------------------------

``kqueue`` 相当于 epoll 的 BSD/macOS，为大量 file descriptors 提供高效的事件通知。

.. code-block:: python

    import socket
    import select
    import contextlib

    if not hasattr(select, 'kqueue'):
        print("kqueue not supported on this platform")
        exit(1)

    host = 'localhost'
    port = 5566

    connections = {}
    requests = {}
    responses = {}

    @contextlib.contextmanager
    def create_server(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind((host, port))
        s.listen(10)
        try:
            yield s
        finally:
            s.close()

    def accept(server, kq):
        conn, addr = server.accept()
        conn.setblocking(False)
        fd = conn.fileno()
        ke = select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_ADD)
        kq.control([ke], 0)
        requests[fd] = conn
        connections[fd] = conn

    def recv(fd, kq):
        conn = requests.pop(fd, None)
        if not conn:
            return
        msg = conn.recv(1024)
        if msg:
            responses[fd] = msg
            # 从读切换到写
            ke_del = select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_DELETE)
            ke_add = select.kevent(fd, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)
            kq.control([ke_del, ke_add], 0)
            requests[fd] = conn
        else:
            ke = select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_DELETE)
            kq.control([ke], 0)
            conn.close()
            connections.pop(fd, None)

    def send(fd, kq):
        conn = connections.get(fd)
        msg = responses.pop(fd, None)
        if conn and msg:
            conn.send(msg)
            # 从写入切换到读取
            ke_del = select.kevent(fd, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)
            ke_add = select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_ADD)
            kq.control([ke_del, ke_add], 0)
            requests[fd] = conn

    with create_server(host, port) as server:
        kq = select.kqueue()
        ke = select.kevent(server.fileno(), select.KQ_FILTER_READ, select.KQ_EV_ADD)
        kq.control([ke], 0)

        try:
            while True:
                events = kq.control(None, 1024, 1)
                for e in events:
                    fd = e.ident
                    if fd == server.fileno():
                        accept(server, kq)
                    elif e.filter == select.KQ_FILTER_READ:
                        recv(fd, kq)
                    elif e.filter == select.KQ_FILTER_WRITE:
                        send(fd, kq)
        except KeyboardInterrupt:
            pass
        finally:
            kq.close()

高层 API：selectors（High-Level API - selectors）
----------------------------------------------------------------------------------------

``selectors`` module (Python 3.4+) 提供了一个高级的、独立于平台的接口，它自动使用最佳的可用机制（epoll、kqueue 等）。

.. code-block:: python

    import selectors
    import socket
    import contextlib

    @contextlib.contextmanager
    def create_server(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(10)
        sel = selectors.DefaultSelector()
        try:
            yield s, sel
        finally:
            s.close()
            sel.close()

    def accept_handler(sock, sel):
        conn, addr = sock.accept()
        sel.register(conn, selectors.EVENT_READ, read_handler)

    def read_handler(conn, sel):
        msg = conn.recv(1024)
        if msg:
            conn.send(msg)
        else:
            sel.unregister(conn)
            conn.close()

    host = 'localhost'
    port = 5566

    with create_server(host, port) as (sock, sel):
        sel.register(sock, selectors.EVENT_READ, accept_handler)
        try:
            while True:
                events = sel.select()
                for key, mask in events:
                    handler = key.data
                    handler(key.fileobj, sel)
        except KeyboardInterrupt:
            pass

I/O 复用方法比较（Comparison of I/O Multiplexing Methods）
----------------------------------------------------------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Method
     - 平台
     - 可扩展性
     - 笔记
   * - 选择
     - 全部
     - O(n) - 有限公司
     - 最多 ~1024 个 FD
   * - 轮询
     - Unix
     - O(n) - 更好
     - 无 FD 限制
   * - epoll
     - Linux
     - O(1) - 优秀
     - 边沿/电平触发
   * - 队列
     - BSD/macOS
     - O(1) - 优秀
     - 类似于 epoll
   * - 选择器
     - 全部
     - 最好的可用
     - 推荐用于新代码


.. note::

    对于新代码，请使用 ``selectors`` module 或 ``asyncio`` 进行异步 I/O。低级 APIs（select、poll、epoll、kqueue）主要用于了解异步 I/O 的工作原理或何时需要细粒度控制。
