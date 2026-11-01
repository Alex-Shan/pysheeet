.. meta::
    :description lang=zh_CN: Python TCP 和 UDP 服务器教程，包含 echo 服务器、IPv6 双 stack、Unix 域 sockets、SocketServer module、线程服务器和零拷贝发送文件的示例
    :keywords: Python, socket, TCP server, UDP server, echo server, IPv6, dual-stack, Unix domain socket, SocketServer, network programming, threaded server, sendfile, IPC

============================================
套接字服务器（Socket Servers）
============================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

构建网络服务器是socket编程最常见的应用之一。服务器侦听特定端口上的传入连接，接受客户端连接和 processes 请求。 Python 的 socket module 提供了构建强大的 TCP 和 UDP 服务器所需的所有原语，从简单的单线程回显服务器到 complex 多客户端应用程序。

本节介绍使用 socket module 在 Python 中构建 TCP 和 UDP 服务器，包括用于学习基础知识的简单回显服务器、用于现代网络兼容性的 IPv6 和双 stack 服务器、用于高性能本地的 Unix 域 sockets IPC、用于快速开发的 SocketServer module、用于处理多个客户端的线程服务器以及使用 sendfile 进行零复制文件传输。这些模式构成了构建生产就绪的网络服务的基础。

简单 TCP Echo 服务器（Simple TCP Echo Server）
------------------------------------------------------------------------------

基本的 TCP 回显服务器演示了基本服务器模式：创建 socket、绑定到地址、侦听连接、接受客户端和 process 数据。此示例使用 Python 的 context manager 协议进行正确的资源清理，确保即使发生 exception 也关闭 socket。 ``SO_REUSEADDR`` 选项允许服务器立即重新启动，而无需等待 TIME_WAIT 状态过期。

.. code-block:: python

    import socket

    class Server:
        def __init__(self, host, port):
            self._host = host
            self._port = port

        def __enter__(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self._host, self._port))
            sock.listen(10)
            self._sock = sock
            return self._sock

        def __exit__(self, *exc_info):
            if exc_info[0]:
                import traceback
                traceback.print_exception(*exc_info)
            self._sock.close()

    if __name__ == '__main__':
        with Server('localhost', 5566) as s:
            while True:
                conn, addr = s.accept()
                msg = conn.recv(1024)
                conn.send(msg)
                conn.close()

输出：

.. code-block:: console

    $ nc localhost 5566
    Hello World
    Hello World

TCP 通过 IPv6 的 Echo 服务器（TCP Echo Server via IPv6）
------------------------------------------------------------------------------------------------

使用 ``AF_INET6`` 地址族的 IPv6 服务器。请注意不同的地址 tuple 格式，其中包括流信息和 scope ID。

.. code-block:: python

    import contextlib
    import socket

    host = "::1"
    port = 5566

    @contextlib.contextmanager
    def server(host, port):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(10)
            yield s
        finally:
            s.close()

    with server(host, port) as s:
        try:
            while True:
                conn, addr = s.accept()
                msg = conn.recv(1024)
                if msg:
                    conn.send(msg)
                conn.close()
        except KeyboardInterrupt:
            pass

输出：

.. code-block:: bash

    $ python3 ipv6.py &
    $ nc -6 ::1 5566
    Hello IPv6
    Hello IPv6

双栈服务器（IPv4 和 IPv6）（Dual-Stack Server (IPv4 and IPv6)）
----------------------------------------------------------------------------------------------------------

通过绑定到 ``::`` 并禁用 ``IPV6_V6ONLY`` 来接受 IPv4 和 IPv6 连接的服务器。 IPv4 客户端显示为 IPv4 映射的 IPv6 地址。

.. code-block:: python

    import contextlib
    import socket

    host = "::"
    port = 5566

    @contextlib.contextmanager
    def server(host, port):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            s.bind((host, port))
            s.listen(10)
            yield s
        finally:
            s.close()

    with server(host, port) as s:
        try:
            while True:
                conn, addr = s.accept()
                print(f"Connection from: {conn.getpeername()}")
                msg = conn.recv(1024)
                if msg:
                    conn.send(msg)
                conn.close()
        except KeyboardInterrupt:
            pass

输出：

.. code-block:: bash

    $ python3 dual_stack.py &
    $ nc -4 127.0.0.1 5566
    Connection from: ('::ffff:127.0.0.1', 42604, 0, 0)
    Hello IPv4
    Hello IPv4
    $ nc -6 ::1 5566
    Connection from: ('::1', 50882, 0, 0)
    Hello IPv6
    Hello IPv6

TCP 通过 SocketServer 的服务器（TCP Server via SocketServer）
----------------------------------------------------------------------------------------------------------

``socketserver`` module 为构建服务器提供了更高级别的接口。它自动处理 socket 设置和连接管理。

.. code-block:: python

    import socketserver

    class EchoHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = self.request.recv(1024)
            print(f"Client: {self.client_address}")
            self.request.sendall(data)

    if __name__ == '__main__':
        with socketserver.TCPServer(('localhost', 5566), EchoHandler) as server:
            server.serve_forever()

简单 UDP Echo 服务器（Simple UDP Echo Server）
------------------------------------------------------------------------------

UDP 服务器使用 ``SOCK_DGRAM`` 并且不需要连接处理。每个 ``recvfrom()`` 返回数据和发送者地址。

.. code-block:: python

    import socket

    class UDPServer:
        def __init__(self, host, port):
            self._host = host
            self._port = port

        def __enter__(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self._host, self._port))
            self._sock = sock
            return sock

        def __exit__(self, *exc_info):
            if exc_info[0]:
                import traceback
                traceback.print_exception(*exc_info)
            self._sock.close()

    if __name__ == '__main__':
        with UDPServer('localhost', 5566) as s:
            while True:
                msg, addr = s.recvfrom(1024)
                s.sendto(msg, addr)

输出：

.. code-block:: console

    $ nc -u localhost 5566
    Hello World
    Hello World

UDP 通过 SocketServer 的服务器（UDP Server via SocketServer）
----------------------------------------------------------------------------------------------------------

.. code-block:: python

    import socketserver

    class UDPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data, sock = self.request
            print(f"Client: {self.client_address}")
            sock.sendto(data, self.client_address)

    if __name__ == '__main__':
        with socketserver.UDPServer(('localhost', 5566), UDPHandler) as server:
            server.serve_forever()

UDP 客户端 - 发送者（UDP Client - Sender）
--------------------------------------------------------------------

发送周期性消息的简单 UDP 客户端。

.. code-block:: python

    import socket
    import time

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = ('localhost', 5566)

    while True:
        sock.sendto(b"Hello\n", host)
        time.sleep(5)

广播 UDP 数据包（Broadcast UDP Packets）
------------------------------------------------------------------

使用 broadcast 地址向本地网络上的所有主机发送 UDP 数据包。

.. code-block:: python

    import socket
    import time

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        msg = f'{time.time()}\n'.encode()
        sock.sendto(msg, ('<broadcast>', 5566))
        time.sleep(5)

输出：

.. code-block:: console

    $ nc -k -w 1 -ul 5566
    1431473025.72

Unix 域套接字（Unix Domain Socket）
----------------------------------------------------------

Unix 域 sockets 在同一台机器上提供 process 之间的通信，比 TCP/IP 环回更快，因为它们绕过网络 stack。

.. code-block:: python

    import socket
    import contextlib
    import os

    @contextlib.contextmanager
    def domain_server(addr):
        try:
            if os.path.exists(addr):
                os.unlink(addr)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(addr)
            sock.listen(10)
            yield sock
        finally:
            sock.close()
            if os.path.exists(addr):
                os.unlink(addr)

    addr = "./domain.sock"
    with domain_server(addr) as sock:
        while True:
            conn, _ = sock.accept()
            msg = conn.recv(1024)
            conn.send(msg)
            conn.close()

输出：

.. code-block:: console

    $ nc -U ./domain.sock
    Hello
    Hello

用于 IPC 的 Socket Pair（Socket Pair for IPC）
----------------------------------------------------------------------------------

``socketpair()`` 创建一对连接的 sockets，对于父 processes 之间的双向通信很有用。

.. code-block:: python

    import os
    import socket

    child_sock, parent_sock = socket.socketpair()
    pid = os.fork()

    try:
        if pid == 0:
            # 儿童 process
            parent_sock.close()
            child_sock.send(b'Hello Parent!')
            msg = child_sock.recv(1024)
            print(f'Parent says: {msg}')
        else:
            # 母体 process
            child_sock.close()
            msg = parent_sock.recv(1024)
            print(f'Child says: {msg}')
            parent_sock.send(b'Hello Child!')
            os.wait()
    finally:
        child_sock.close()
        parent_sock.close()

输出：

.. code-block:: bash

    $ python socketpair_demo.py
    Child says: b'Hello Parent!'
    Parent says: b'Hello Child!'

线程 TCP 服务器（Threaded TCP Server）
--------------------------------------------------------------

使用 threads 同时处理多个客户端。

.. code-block:: python

    from threading import Thread
    import socket

    def handle_client(conn):
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            conn.send(msg)
        conn.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 5566))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        t = Thread(target=handle_client, args=(conn,))
        t.daemon = True
        t.start()

使用 sendfile 进行零拷贝传输（Using sendfile for Zero-Copy Transfer）
--------------------------------------------------------------------------------------------------------------------

``os.sendfile()`` 高效地将文件数据传输到 socket，无需通过用户空间进行复制（零复制）。

.. code-block:: python

    import os
    import socket
    import contextlib

    @contextlib.contextmanager
    def server(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(10)
        try:
            yield s
        finally:
            s.close()

    def send_file(conn, filepath):
        with open(filepath, 'rb') as f:
            fd = f.fileno()
            size = os.fstat(fd).st_size
            offset = 0
            while size > 0:
                sent = os.sendfile(conn.fileno(), fd, offset, min(size, 65536))
                offset += sent
                size -= sent

    # 向每个客户端发送文件的服务器
    with server('localhost', 5566) as s:
        while True:
            conn, addr = s.accept()
            send_file(conn, 'large_file.bin')
            conn.close()
