"""Network/socket examples and tests for pysheeet documentation."""

import socket
import threading
import time
import pytest


class TestHostname:
    """Test hostname and DNS resolution."""

    def test_gethostname(self):
        hostname = socket.gethostname()
        assert isinstance(hostname, str)
        assert len(hostname) > 0

    def test_gethostbyname_localhost(self):
        ip = socket.gethostbyname("localhost")
        assert ip == "127.0.0.1"

    def test_getaddrinfo(self):
        results = socket.getaddrinfo(
            "localhost", None, proto=socket.IPPROTO_TCP
        )
        assert len(results) > 0
        family, socktype, proto, canonname, sockaddr = results[0]
        assert family in (socket.AF_INET, socket.AF_INET6)


class TestByteOrder:
    """Test network byte order conversion."""

    def test_htons(self):
        # 主机到网络短路
        result = socket.htons(1)
        # 在 little-endian 上，1 变为 256
        assert result in (1, 256)

    def test_htonl(self):
        # 主机到网络长
        result = socket.htonl(1)
        assert result in (1, 16777216)

    def test_ntohs(self):
        # 网络到主机短
        val = socket.htons(1234)
        assert socket.ntohs(val) == 1234

    def test_ntohl(self):
        # 网络托管长
        val = socket.htonl(12345678)
        assert socket.ntohl(val) == 12345678


class TestIPConversion:
    """Test IP address string/binary conversion."""

    def test_inet_aton(self):
        addr = socket.inet_aton("127.0.0.1")
        assert addr == b"\x7f\x00\x00\x01"

    def test_inet_ntoa(self):
        ip = socket.inet_ntoa(b"\x7f\x00\x00\x01")
        assert ip == "127.0.0.1"

    def test_inet_pton_ipv4(self):
        addr = socket.inet_pton(socket.AF_INET, "192.168.1.1")
        assert addr == b"\xc0\xa8\x01\x01"

    def test_inet_ntop_ipv4(self):
        ip = socket.inet_ntop(socket.AF_INET, b"\xc0\xa8\x01\x01")
        assert ip == "192.168.1.1"

    def test_inet_pton_ipv6(self):
        addr = socket.inet_pton(socket.AF_INET6, "::1")
        assert addr == b"\x00" * 15 + b"\x01"

    def test_inet_ntop_ipv6(self):
        ip = socket.inet_ntop(socket.AF_INET6, b"\x00" * 15 + b"\x01")
        assert ip == "::1"


class TestSocketOptions:
    """Test socket options."""

    def test_reuseaddr(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        val = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        assert val != 0  # 非零表示启用
        sock.close()

    def test_timeout(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        assert sock.gettimeout() == 5.0
        sock.close()

    def test_blocking(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        assert sock.getblocking() is False
        sock.setblocking(True)
        assert sock.getblocking() is True
        sock.close()


class TestTCPEchoServer:
    """Test TCP echo server functionality."""

    def test_echo(self):
        host, port = "localhost", 15566

        # 在thread中启动服务器
        server_ready = threading.Event()

        def server():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(1)
            server_ready.set()
            conn, addr = sock.accept()
            data = conn.recv(1024)
            conn.send(data)
            conn.close()
            sock.close()

        t = threading.Thread(target=server)
        t.daemon = True
        t.start()
        server_ready.wait()

        # 客户
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(b"Hello")
        response = client.recv(1024)
        client.close()

        assert response == b"Hello"
        t.join(timeout=1)


class TestUDPEchoServer:
    """Test UDP echo server functionality."""

    def test_echo(self):
        host, port = "localhost", 15567

        server_ready = threading.Event()

        def server():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((host, port))
            server_ready.set()
            data, addr = sock.recvfrom(1024)
            sock.sendto(data, addr)
            sock.close()

        t = threading.Thread(target=server)
        t.daemon = True
        t.start()
        server_ready.wait()

        # 客户
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(b"Hello UDP", (host, port))
        response, _ = client.recvfrom(1024)
        client.close()

        assert response == b"Hello UDP"
        t.join(timeout=1)


class TestSocketPair:
    """Test socketpair for IPC."""

    def test_socketpair(self):
        parent, child = socket.socketpair()

        # 从父母发送给孩子
        parent.send(b"Hello")
        assert child.recv(1024) == b"Hello"

        # 从孩子发送给父母
        child.send(b"World")
        assert parent.recv(1024) == b"World"

        parent.close()
        child.close()


class TestPortCheck:
    """Test port availability checking."""

    def test_port_available(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("", 0))  # 绑定到任何可用端口
            port = sock.getsockname()[1]
            assert port > 0
        finally:
            sock.close()

    def test_port_in_use(self):
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock1.bind(("", 15568))
        sock1.listen(1)

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock2.bind(("", 15568))
            assert False, "Should have raised OSError"
        except OSError:
            pass
        finally:
            sock1.close()
            sock2.close()


class TestMACConversion:
    """Test MAC address conversion."""

    def test_mac_to_bytes(self):
        import binascii

        mac = "00:11:22:33:44:55"
        byte = binascii.unhexlify(mac.replace(":", ""))
        assert byte == b'\x00\x11"3DU'

    def test_bytes_to_mac(self):
        import binascii

        byte = b'\x00\x11"3DU'
        mac = ":".join(f"{b:02x}" for b in byte)
        assert mac == "00:11:22:33:44:55"


class TestSelectorsEcho:
    """Test selectors-based async server."""

    def test_selectors_echo(self):
        import selectors

        host, port = "localhost", 15569
        server_ready = threading.Event()
        stop_server = threading.Event()

        def server():
            sel = selectors.DefaultSelector()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(False)
            sock.bind((host, port))
            sock.listen(1)

            def accept(sock):
                conn, addr = sock.accept()
                conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ, read)

            def read(conn):
                data = conn.recv(1024)
                if data:
                    conn.send(data)
                sel.unregister(conn)
                conn.close()
                stop_server.set()

            sel.register(sock, selectors.EVENT_READ, accept)
            server_ready.set()

            while not stop_server.is_set():
                events = sel.select(timeout=0.1)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)

            sel.unregister(sock)
            sock.close()
            sel.close()

        t = threading.Thread(target=server)
        t.daemon = True
        t.start()
        server_ready.wait()

        # 客户
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(b"Async Hello")
        response = client.recv(1024)
        client.close()

        assert response == b"Async Hello"
        t.join(timeout=2)
