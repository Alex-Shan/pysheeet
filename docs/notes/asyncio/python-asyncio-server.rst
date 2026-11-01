.. meta::
    :description lang=zh_CN: Python asyncio 网络 - TCP/UDP 服务器、HTTP 客户端、SSL/TLS、协议
    :keywords: Python, Python3, Asyncio, TCP Server, UDP Server, HTTP Client, SSL TLS, Network Programming

================================================
异步网络（Asyncio Networking）
================================================

:Source: `src/basic/asyncio_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/asyncio_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

Asyncio 擅长网络编程，因为网络 I/O 本质上就是 asynchronous - 您发送请求并等待响应。 asyncio 允许其他任务运行，而不是在等待时阻塞 thread。本节介绍构建 TCP/UDP 服务器和客户端、HTTP 请求、SSL/TLS 加密以及用于低级控制的传输/协议 API。

TCP 带流的 Echo 服务器（TCP Echo Server with Streams）
--------------------------------------------------------------------------------------------

streams API（ ``asyncio.start_server`` 、 ``open_connection`` ）为 TCP 网络提供高级接口。它自动处理缓冲、encoding 和连接管理，使其成为大多数应用程序的推荐方法。

.. code-block:: python

    import asyncio

    async def handle_client(reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected: {addr}")

        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received: {message!r} from {addr}")
            writer.write(data)
            await writer.drain()

        print(f"Disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

    async def main():
        server = await asyncio.start_server(
            handle_client, 'localhost', 8888
        )
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    asyncio.run(main())

TCP 带流的客户端（TCP Client with Streams）
----------------------------------------------------------------------

客户端使用 ``asyncio.open_connection()`` 建立连接。返回的读写器objects提供异步methods用于发送和接收数据。

.. code-block:: python

    import asyncio

    async def tcp_client(message):
        reader, writer = await asyncio.open_connection(
            'localhost', 8888
        )

        print(f"Sending: {message!r}")
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(1024)
        print(f"Received: {data.decode()!r}")

        writer.close()
        await writer.wait_closed()

    asyncio.run(tcp_client("Hello, Server!"))

使用 Sockets 的底层 TCP（Low-Level TCP with Sockets）
--------------------------------------------------------------------------------------------

为了获得更多控制，您可以将原始 sockets 与 event loop 的 socket methods 一起使用。当您需要对 socket 选项进行细粒度控制或与现有的基于 socket 的代码集成时，此方法非常有用。

.. code-block:: python

    import asyncio
    import socket

    async def handle_client(loop, conn):
        while True:
            data = await loop.sock_recv(conn, 1024)
            if not data:
                break
            await loop.sock_sendall(conn, data)
        conn.close()

    async def server():
        loop = asyncio.get_event_loop()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind(('localhost', 8888))
        sock.listen(100)

        print("Server listening on localhost:8888")
        while True:
            conn, addr = await loop.sock_accept(sock)
            print(f"Connected: {addr}")
            asyncio.create_task(handle_client(loop, conn))

    asyncio.run(server())

UDP 回显服务器（UDP Echo Server）
----------------------------------------------------

UDP 是无连接的，因此 API 与 TCP 不同。使用 ``create_datagram_endpoint()`` 和协议 class 来处理 UDP 数据包。每个数据包都是独立的，并且可能不按顺序到达或根本不到达。

.. code-block:: python

    import asyncio

    class EchoUDPProtocol(asyncio.DatagramProtocol):
        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            message = data.decode()
            print(f"Received {message!r} from {addr}")
            self.transport.sendto(data, addr)

    async def main():
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            EchoUDPProtocol,
            local_addr=('localhost', 9999)
        )
        print("UDP server listening on localhost:9999")

        try:
            await asyncio.sleep(3600)  # 跑1小时
        finally:
            transport.close()

    asyncio.run(main())

HTTP 客户端与 SSL（HTTP Client with SSL）
----------------------------------------------------------------------

发出 HTTPS 请求需要 SSL 上下文配置。此示例演示如何使用低级 streams 和适当的 SSL 验证来获取网页。

.. code-block:: python

    import asyncio
    import ssl

    async def fetch_https(host, path="/"):
        # 创建带有证书验证的 SSL 上下文
        ctx = ssl.create_default_context()

        reader, writer = await asyncio.open_connection(
            host, 443, ssl=ctx
        )

        # 发送 HTTP 请求
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        writer.write(request.encode())
        await writer.drain()

        # 阅读回复
        response = await reader.read()
        writer.close()
        await writer.wait_closed()

        return response.decode()

    async def main():
        urls = [
            ("www.python.org", "/"),
            ("github.com", "/"),
        ]
        tasks = [fetch_https(host, path) for host, path in urls]
        responses = await asyncio.gather(*tasks)

        for (host, _), resp in zip(urls, responses):
            status = resp.split('\r\n')[0]
            print(f"{host}: {status}")

    asyncio.run(main())

HTTPS 服务器与 SSL（HTTPS Server with SSL）
--------------------------------------------------------------------------

创建 HTTPS 服务器需要 SSL 证书。此示例显示了一个简单的 HTTPS 服务器，该服务器通过 TLS 加密提供静态内容。

.. code-block:: python

    import asyncio
    import ssl

    async def handle_request(reader, writer):
        request = await reader.read(1024)

        response = b"HTTP/1.1 200 OK\r\n"
        response += b"Content-Type: text/html\r\n\r\n"
        response += b"<html><body><h1>Hello HTTPS!</h1></body></html>"

        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def main():
        # 创建 SSL 上下文
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain('cert.pem', 'key.pem')

        server = await asyncio.start_server(
            handle_request, 'localhost', 8443, ssl=ctx
        )
        print("HTTPS server on https://localhost:8443")

        async with server:
            await server.serve_forever()

    # 生成自签名证书：
    # openssl 请求 -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -天 365 -节点
    asyncio.run(main())

传输和协议 API（Transport and Protocol API）
--------------------------------------------------------------------------

传输/协议 API 提供对网络连接的低级控制。传输处理实际的 I/O，而协议处理数据处理。这种分离允许灵活且可重用的网络代码。

.. code-block:: python

    import asyncio

    class EchoProtocol(asyncio.Protocol):
        def connection_made(self, transport):
            self.transport = transport
            peername = transport.get_extra_info('peername')
            print(f"Connection from {peername}")

        def data_received(self, data):
            print(f"Received: {data.decode()!r}")
            self.transport.write(data)

        def connection_lost(self, exc):
            print("Connection closed")

    async def main():
        loop = asyncio.get_event_loop()
        server = await loop.create_server(
            EchoProtocol, 'localhost', 8888
        )

        async with server:
            await server.serve_forever()

    asyncio.run(main())

DNS 解析（DNS Resolution）
--------------------------------------------

Asyncio 通过 ``getaddrinfo()`` 提供异步 DNS 分辨率。当您需要解析主机名而不阻止 event loop 时，这非常有用。

.. code-block:: python

    import asyncio
    import socket

    async def resolve_host(host, port=80):
        loop = asyncio.get_event_loop()
        infos = await loop.getaddrinfo(
            host, port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM
        )

        for family, type_, proto, canonname, sockaddr in infos:
            ip, port = sockaddr[:2]
            family_name = "IPv4" if family == socket.AF_INET else "IPv6"
            print(f"{host} -> {ip} ({family_name})")

    async def main():
        hosts = ["python.org", "github.com", "google.com"]
        await asyncio.gather(*[resolve_host(h) for h in hosts])

    asyncio.run(main())

简单 HTTP 服务器（Simple HTTP Server）
--------------------------------------------------------------

最小的 HTTP 服务器实现，展示如何解析请求和发送响应。对于生产使用，请考虑 aiohttp 或 FastAPI 等框架。

.. code-block:: python

    import asyncio

    async def handle_http(reader, writer):
        request = await reader.read(1024)
        request_line = request.decode().split('\r\n')[0]
        method, path, _ = request_line.split(' ')

        print(f"{method} {path}")

        # 简单的路由
        if path == '/':
            body = b"<h1>Home</h1>"
            status = "200 OK"
        elif path == '/about':
            body = b"<h1>About</h1>"
            status = "200 OK"
        else:
            body = b"<h1>404 Not Found</h1>"
            status = "404 Not Found"

        response = f"HTTP/1.1 {status}\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Content-Type: text/html\r\n\r\n"

        writer.write(response.encode() + body)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def main():
        server = await asyncio.start_server(
            handle_http, 'localhost', 8080
        )
        print("HTTP server on http://localhost:8080")

        async with server:
            await server.serve_forever()

    asyncio.run(main())

使用 sendfile 进行高效文件传输（Using sendfile for Efficient File Transfer）
--------------------------------------------------------------------------------------------------------------------------------

``sendfile()`` method (Python 3.7+) 使用 OS 的 sendfile 系统调用有效地将文件内容传输到传输，避免通过 Python 复制数据。

.. code-block:: python

    import asyncio

    async def handle_request(reader, writer):
        await reader.read(1024)  # 读取请求

        with open('index.html', 'rb') as f:
            # 获取文件大小
            f.seek(0, 2)
            size = f.tell()
            f.seek(0)

            # 发送标头
            headers = f"HTTP/1.1 200 OK\r\n"
            headers += f"Content-Length: {size}\r\n"
            headers += "Content-Type: text/html\r\n\r\n"
            writer.write(headers.encode())

            # 高效发送文件
            loop = asyncio.get_event_loop()
            await loop.sendfile(writer.transport, f)

        writer.close()
        await writer.wait_closed()

    async def main():
        server = await asyncio.start_server(
            handle_request, 'localhost', 8080
        )
        async with server:
            await server.serve_forever()

    asyncio.run(main())

连接池（Connection Pool）
----------------------------------------

连接池重用连接以避免为每个请求建立新连接的开销。这对于向同一服务器发出许多请求的高性能客户端至关重要。

.. code-block:: python

    import asyncio
    from collections import deque

    class ConnectionPool:
        def __init__(self, host, port, size=5):
            self.host = host
            self.port = port
            self.size = size
            self._pool = deque()
            self._lock = asyncio.Lock()

        async def get(self):
            async with self._lock:
                if self._pool:
                    return self._pool.popleft()

            # 创建新连接
            reader, writer = await asyncio.open_connection(
                self.host, self.port
            )
            return reader, writer

        async def put(self, reader, writer):
            async with self._lock:
                if len(self._pool) < self.size:
                    self._pool.append((reader, writer))
                else:
                    writer.close()
                    await writer.wait_closed()

        async def close(self):
            async with self._lock:
                while self._pool:
                    reader, writer = self._pool.popleft()
                    writer.close()
                    await writer.wait_closed()

    async def fetch(pool, message):
        reader, writer = await pool.get()
        try:
            writer.write(message.encode())
            await writer.drain()
            data = await reader.read(1024)
            return data.decode()
        finally:
            await pool.put(reader, writer)

    async def main():
        pool = ConnectionPool('localhost', 8888, size=3)
        try:
            tasks = [fetch(pool, f"msg{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)
            for r in results:
                print(r)
        finally:
            await pool.close()

    asyncio.run(main())
