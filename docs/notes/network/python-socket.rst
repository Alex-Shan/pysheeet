.. meta::
    :description lang=zh_CN: Python socket 编程教程，包含 DNS 分辨率、TCP/UDP 客户端、IP 地址转换、网络 byte 顺序、超时、多播和 SOCKS 代理的示例
    :keywords: Python, socket, networking, TCP, UDP, DNS, IP address, hostname, getaddrinfo, inet_aton, inet_ntoa, network programming, timeout, multicast, SOCKS proxy, HTTP client

============================================
套接字基础知识（Socket Basics）
============================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Socket 编程是 Python 和几乎所有网络应用程序中网络通信的基础。 socket 是用于通过网络发送和接收数据的端点，通过 Internet 在同一台机器上或不同机器上的 processes 之间提供双向通信通道。虽然 Python 提供 ``urllib`` 、 ``requests`` 和 ``asyncio`` 等高级网络接口，但了解低级 socket 操作对于构建自定义协议、debugging 网络问题、实施网络工具以及与系统级网络 APIs 进行交互至关重要。

本速查表涵盖了 Python 中 socket 编程的基础知识，包括主机名和 DNS 解析、IP 地址操作、网络 byte 顺序转换、超时处理、多播通信和代理支持。无论您是构建简单的客户端-服务器应用程序、实施自定义协议，还是解决网络连接问题，这些示例都提供了您所需的构建块。

获取主机名（Get Hostname）
--------------------------------------

``socket.gethostname()`` function 返回操作系统中配置的当前计算机的主机名，而 ``socket.gethostbyname()`` 执行 DNS 查找以将主机名解析为其 IPv4 地址。这些 functions 是网络编程最基本的构建块，允许您的应用程序识别自身并解析网络上的其他主机。请注意， ``gethostbyname()`` 仅返回 IPv4 地址；使用 ``getaddrinfo()`` 来支持 IPv6。

.. code-block:: python

    >>> import socket
    >>> socket.gethostname()
    'MacBookPro-4380.local'
    >>> hostname = socket.gethostname()
    >>> socket.gethostbyname(hostname)
    '172.20.10.4'
    >>> socket.gethostbyname('localhost')
    '127.0.0.1'

获取地址信息（DNS 解析）（Get Address Info (DNS Resolution)）
--------------------------------------------------------------------------------------------------

``socket.getaddrinfo()`` 是现代 Python 代码中 DNS 分辨率的最通用且推荐的 function。与 ``gethostbyname()`` 不同，它支持 IPv4 和 IPv6 地址，在可用时返回多个结果，并提供完整的信息，包括地址族、socket type、协议、规范名称和 socket 地址。 function 对于编写与 IPv4 和 IPv6 网络无缝协作的协议无关代码至关重要。

.. code-block:: python

    import socket
    import sys

    try:
        for res in socket.getaddrinfo(sys.argv[1], None,
                                      proto=socket.IPPROTO_TCP):
            family = res[0]
            sockaddr = res[4]
            print(family, sockaddr)
    except socket.gaierror:
        print("Invalid")

输出：

.. code-block:: console

    $ python gai.py 192.0.2.244
    AddressFamily.AF_INET ('192.0.2.244', 0)
    $ python gai.py 2001:db8:f00d::1:d
    AddressFamily.AF_INET6 ('2001:db8:f00d::1:d', 0, 0, 0)
    $ python gai.py www.google.com
    AddressFamily.AF_INET6 ('2607:f8b0:4006:818::2004', 0, 0, 0)
    AddressFamily.AF_INET ('172.217.10.132', 0)

它处理异常情况，有效和无效：

.. code-block:: console

    $ python gai.py 10.0.0.256  # 八位位组溢出
    Invalid
    $ python gai.py not-exist.example.com  # 无法解决的
    Invalid
    $ python gai.py fe80::1%eth0  # 范围内的
    AddressFamily.AF_INET6 ('fe80::1%eth0', 0, 0, 2)
    $ python gai.py ::ffff:192.0.2.128  # IPv4 映射
    AddressFamily.AF_INET6 ('::ffff:192.0.2.128', 0, 0, 0)
    $ python gai.py 0xc000027b  # IPv4（十六进制）
    AddressFamily.AF_INET ('192.0.2.123', 0)

高级 DNS 查询（Advanced DNS Queries）
--------------------------------------------------------------

虽然 ``socket.getaddrinfo()`` 处理基本的主机名解析，但许多应用程序需要更高级的 DNS 操作，例如查询特定记录 types。 MX 记录标识域的邮件服务器，TXT 记录存储用于电子邮件身份验证的 SPF 和 DKIM 数据，NS 记录 list 权威名称服务器，SRV 记录启用服务发现。 ``dnspython`` library 提供了全面的 DNS 工具包，支持所有记录 types、自定义名称服务器、DNSSEC 验证和区域传输。这对于构建电子邮件验证系统、服务发现机制和 DNS 监控工具至关重要。

.. code-block:: python

    # pip install dnspython
    import dns.resolver

    # 查询MX记录（邮件服务器）
    answers = dns.resolver.resolve('google.com', 'MX')
    for rdata in answers:
        print(f"MX: {rdata.exchange} (priority: {rdata.preference})")

    # 查询TXT记录（SPF、DKIM等）
    answers = dns.resolver.resolve('google.com', 'TXT')
    for rdata in answers:
        print(f"TXT: {rdata}")

    # 查询NS记录（名称服务器）
    answers = dns.resolver.resolve('google.com', 'NS')
    for rdata in answers:
        print(f"NS: {rdata}")

    # 使用自定义名称服务器查询 A 记录
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']  # 使用谷歌DNS
    answers = resolver.resolve('example.com', 'A')
    for rdata in answers:
        print(f"A: {rdata}")

反向 DNS 查找（Reverse DNS Lookup）
----------------------------------------------------------

反向 DNS (rDNS) 查找通过查询 in-addr.arpa (IPv4) 或 ip6.arpa (IPv6) 域中的 PTR 记录，将 IP 地址转换回其关联的主机名。这通常用于日志记录以使 IP 地址可读、安全分析以验证连接客户端的 IP 是否与其声明的主机名匹配、垃圾邮件过滤以检查邮件服务器是否具有有效的反向 DNS 以及网络故障排除以识别网络上的设备。

.. code-block:: python

    >>> import socket
    >>> # 反向查找返回（主机名、别名、地址）
    >>> socket.gethostbyaddr('8.8.8.8')
    ('dns.google', [], ['8.8.8.8'])
    >>> socket.gethostbyaddr('140.82.112.4')
    ('github.com', [], ['140.82.112.4'])

    >>> # 使用 getfqdn 获取完全限定域名
    >>> socket.getfqdn('8.8.8.8')
    'dns.google'

网络字节顺序转换（Network Byte Order Conversion）
------------------------------------------------------------------------------

网络协议普遍采用big-endian byte顺序（最高位byte在前）， 也称为 "network byte order,"，而大多数现代 CPU（x86、 little-endian 模式下的 ARM）使用 little-endian（最低有效位 byte 在前）。 通过网络发送多个byte integers时， 您必须从主机 byte 订单转换为网络 byte 订单， 接收时反之亦然。 ``htons`` / ``htonl`` functions 将主机转换为短 (16-bit) 和长 (32-bit) integers 的网络顺序， 而 ``ntohs`` / ``ntohl`` 则将网络顺序转换为主机顺序。 未能执行这些转换会导致细微的错误，其中 values 在具有不同 endianness 的计算机上出现损坏。

.. code-block:: python

    # little-endian机
    >>> import socket
    >>> a = 1  # 主机字节序
    >>> socket.htons(a)  # 主机到网络短路 (16-bit)
    256
    >>> socket.htonl(a)  # 主机到网络长 (32-bit)
    16777216
    >>> socket.ntohs(256)  # 网络到主机短
    1
    >>> socket.ntohl(16777216)  # 网络到主机长
    1

IP 地址字符串/二进制转换（IP Address String/Binary Conversion）
------------------------------------------------------------------------------------------------------

IP 地址通常显示为人类可读的 strings（IPv4 的点分四组，如 "192.168.1.1"，或 IPv6 的冒号十六进制，如 "2001:db8::1"），但网络协议将它们作为二进制数据传输（4 bytes 表示 IPv4，16 bytes 表示 IPv6）。 ``inet_aton`` 和 ``inet_ntoa`` functions 在 string 和二进制格式之间进行转换（仅适用于 IPv4）。对于需要同时支持 IPv4 和 IPv6 的代码，请使用 ``inet_pton`` （表示到网络）和 ``inet_ntop`` （网络到表示），它们采用地址族 parameter 来指定 IP 版本。

.. code-block:: python

    >>> import socket
    >>> # IPv4：string 转为二进制
    >>> addr = socket.inet_aton('127.0.0.1')
    >>> addr
    b'\x7f\x00\x00\x01'
    >>> # IPv4：二进制为 string
    >>> socket.inet_ntoa(addr)
    '127.0.0.1'

    >>> # IPv4/IPv6：使用inet_pton/inet_ntop
    >>> socket.inet_pton(socket.AF_INET, '192.168.1.1')
    b'\xc0\xa8\x01\x01'
    >>> socket.inet_pton(socket.AF_INET6, '::1')
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
    >>> socket.inet_ntop(socket.AF_INET6, b'\x00' * 15 + b'\x01')
    '::1'

MAC 地址转换（MAC Address Conversion）
----------------------------------------------------------------

MAC（媒体访问控制）地址是分配给网络接口卡的 48-bit 硬件标识符，通常显示为六个以冒号分隔的十六进制对，如 "00:11:22:33:44:55"。在处理原始以太网帧或 ARP 数据包时，您需要在这种人类可读的格式与网络协议中使用的 6-byte 二进制格式之间进行转换。 ``binascii`` module 为该转换提供了 ``hexlify`` 和 ``unhexlify`` functions。

.. code-block:: python

    >>> import binascii
    >>> mac = '00:11:32:3c:c3:0b'
    >>> byte = binascii.unhexlify(mac.replace(':', ''))
    >>> byte
    b'\x00\x112<\xc3\x0b'
    >>> binascii.hexlify(byte)
    b'0011323cc30b'
    >>> # 格式恢复为冒号分隔
    >>> ':'.join(f'{b:02x}' for b in byte)
    '00:11:32:3c:c3:0b'

检查端口可用性（Check Port Availability）
----------------------------------------------------------------

在启动服务器之前，您通常需要验证所需的端口是否可用于绑定。同样，网络监控工具需要检查远程服务是否可达。 ``is_port_open`` function 尝试 TCP 连接来测试远程服务可用性，而 ``is_port_available`` 尝试本地绑定以检查端口是否空闲。这些检查对于服务运行状况监控、端口扫描以及避免启动服务器时出现 "Address already in use" 错误至关重要。

.. code-block:: python

    import socket

    def is_port_open(host, port, timeout=3):
        """Check if a port is open on a remote host."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
        finally:
            sock.close()

    def is_port_available(port):
        """Check if a local port is available for binding."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            return True
        except OSError:
            return False
        finally:
            sock.close()

    # 用法
    print(is_port_open('google.com', 443))  # True
    print(is_port_available(8080))  # True 如果不使用

获取网络接口（Get Network Interfaces）
------------------------------------------------------------

多宿主服务器（具有多个网络接口的计算机）需要发现其可用的 IP 地址以绑定到特定接口或将其地址通告给客户端。基本方法在主机名上使用 ``getaddrinfo`` ，但对于包括接口名称、网络掩码和 broadcast 地址在内的详细接口信息， ``netifaces`` library 提供了跨平台解决方案。这对于网络配置工具、服务发现以及构建需要选择特定网络接口的应用程序非常有用。

.. code-block:: python

    import socket

    def get_local_ips():
        """Get all local IP addresses."""
        ips = []
        hostname = socket.gethostname()
        try:
            # 获取主机名的所有地址
            for info in socket.getaddrinfo(hostname, None):
                ip = info[4][0]
                if ip not in ips:
                    ips.append(ip)
        except socket.gaierror:
            pass
        return ips

    # 有关更详细的接口信息，请使用 netifaces
    # pip install netifaces
    import netifaces

    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                print(f"{iface}: {addr['addr']}")

套接字选项（Socket Options）
------------------------------------------

Socket 选项控制低级 socket 行为，对于构建强大的网络应用程序至关重要。 ``SO_REUSEADDR`` 允许立即重新启动服务器，而无需等待 TIME_WAIT 过期。 ``SO_REUSEPORT`` 可以将多个 processes 绑定到同一端口以实现负载均衡。 Buffer 尺寸选项（ ``SO_SNDBUF`` 、 ``SO_RCVBUF`` ）可针对高 bandwidth 应用调整 throughput。 ``SO_KEEPALIVE`` 通过发送周期性探测来检测死连接。了解这些选项有助于您优化性能并处理生产系统中的边缘情况。

.. code-block:: python

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 重用地址（避免"Address already in use"错误）
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 复用端口（多个processes可以绑定到同一个端口）
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Set 发送/接收 buffer 尺寸
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

    # 启用 TCP 保活
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    # Set 超时（秒）
    sock.settimeout(10.0)

    # 非阻塞模式
    sock.setblocking(False)

    # 获取当前选项 value
    print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))

故障排除：连接被拒绝（Troubleshooting: Connection Refused）
----------------------------------------------------------------------------------------------

"Connection refused" 是最常见的网络错误之一，但其原因并不总是显而易见。这可能意味着目标端口没有侦听服务、防火墙主动拒绝连接或服务崩溃。其他错误（例如 "Connection timed out"）表明主机无法访问或防火墙正在默默地丢弃数据包，而 "Network unreachable" 则表明存在路由问题。此诊断 function 对不同的错误 types 进行分类，以帮助识别根本原因，这对于开发和生产环境中的 debugging 网络连接问题至关重要。

.. code-block:: python

    import socket
    import errno

    def diagnose_connection(host, port):
        """Diagnose connection issues."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((host, port))
            print(f"✓ Connected to {host}:{port}")
        except socket.timeout:
            print(f"✗ Timeout - host may be unreachable or firewalled")
        except ConnectionRefusedError:
            print(f"✗ Connection refused - no service on {port}")
        except socket.gaierror as e:
            print(f"✗ DNS error - cannot resolve {host}: {e}")
        except OSError as e:
            if e.errno == errno.ENETUNREACH:
                print(f"✗ Network unreachable")
            elif e.errno == errno.EHOSTUNREACH:
                print(f"✗ Host unreachable")
            else:
                print(f"✗ OS error: {e}")
        finally:
            sock.close()

    diagnose_connection('localhost', 8080)


超时处理（Timeout Handling）
--------------------------------------------

如果远程主机没有响应，网络操作可能会无限期地阻塞， 网络路径失败， 或数据包丢失。 如果没有适当的超时处理， 您的应用程序可能会永远挂起，等待永远不会到达的数据。 Python sockets 支持多个级别的超时： 通过 ``settimeout()`` 的全局超时适用于所有操作， 或使用 ``select()`` 进行每个操作超时以实现更精确的控制。 始终根据应用程序的要求设置适当的超时 set — 太短会导致 false 失败， 太长会延迟错误检测。

.. code-block:: python

    import socket
    import errno

    def connect_with_timeout(host, port, timeout=5):
        """Connect with timeout and proper error handling."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return sock
        except socket.timeout:
            print(f"Connection to {host}:{port} timed out")
            sock.close()
            return None
        except OSError as e:
            print(f"Connection failed: {e}")
            sock.close()
            return None

    def recv_with_timeout(sock, bufsize=4096, timeout=10):
        """Receive data with timeout."""
        sock.settimeout(timeout)
        try:
            return sock.recv(bufsize)
        except socket.timeout:
            return None  # 超时，无数据

    # 使用 select 的每个操作超时
    import select

    def recv_timeout(sock, bufsize, timeout):
        """Receive with timeout using select (more precise)."""
        ready, _, _ = select.select([sock], [], [], timeout)
        if ready:
            return sock.recv(bufsize)
        raise socket.timeout("recv timed out")

平稳关闭（Graceful Shutdown）
----------------------------------------------

仅在 socket 上调用 ``close()`` 可能会丢失仍在传输中的数据。 TCP 协议需要正确的四次握手（FIN-ACK 序列）以确保双方都完成发送。 ``shutdown()`` method 提供细粒度控制： ``SHUT_WR`` 发送 FIN 数据包，发送 "I'm done sending" 信号，同时仍允许读取， ``SHUT_RD`` 停止接收， ``SHUT_RDWR`` 执行这两种操作。对于干净终止，首先调用 ``shutdown(SHUT_WR)`` ，耗尽所有剩余的传入数据，然后调用 ``close()`` 。此模式对于服务器在发送最终响应之前等待客户端 EOF 的协议尤其重要。

.. code-block:: python

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('example.com', 80))
    sock.send(b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n')

    # 关闭写入端 - 向服务器发出 EOF 信号
    sock.shutdown(socket.SHUT_WR)

    # 读取剩余数据
    response = b''
    while True:
        data = sock.recv(4096)
        if not data:
            break
        response += data

    # 现在关闭socket
    sock.close()

    # 关机选项：
    # SHUT_RD - 不再读取
    # SHUT_WR - 不再写入（发送 FIN）
    # SHUT_RDWR - 不再读取或写入

组播 UDP（Multicast UDP）
------------------------------------------

组播是一种一对多通信模型，其中单个数据包同时传送到多个接收者。与 broadcast（淹没整个网络）或单播（一个发送者，一个接收者）不同，多播使用特殊的 IP 地址（224.0.0.0 到 239.255.255.255）和 IGMP 协议来有效地将数据包仅路由到感兴趣的接收者。接收方必须显式加入多播组才能接收流量。 TTL（生存时间）控制数据包传输的距离 - TTL=1 保留在本地子网上，更高的 values 跨路由器。组播非常适合流媒体、实时数据源和服务发现，其中相同的数据会传送到许多客户端。

.. code-block:: python

    import socket
    import struct

    MCAST_GROUP = '224.1.1.1'
    MCAST_PORT = 5007

    # 发件人
    def multicast_sender():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(b'Hello Multicast!', (MCAST_GROUP, MCAST_PORT))
        sock.close()

    # 接收者
    def multicast_receiver():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', MCAST_PORT))

        # 加入多播组
        mreq = struct.pack('4sl', socket.inet_aton(MCAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        data, addr = sock.recvfrom(1024)
        print(f"Received: {data} from {addr}")
        sock.close()

带套接字的 HTTP 客户端（HTTP Client with Sockets）
--------------------------------------------------------------------------------

虽然像 ``urllib`` 和 ``requests`` 这样的高级 libraries 可以优雅地处理 HTTP，但了解原始 HTTP 而不是 sockets 对于 debugging、实现自定义协议或在受限环境中工作来说非常宝贵。 HTTP/1.1 是基于文本的协议：您发送请求行 ( ``GET /path HTTP/1.1`` )、标头（key-value 对）、空行以及可选的正文。服务器响应类似。 Key 标头包括 ``Host`` （HTTP/1.1 中需要）、 ``Connection: close`` （用于发出单个请求信号）和用于主体的 ``Content-Length`` 。这种低级方法准确地揭示了线路上发生的情况，从而更容易诊断格式错误的标头、encoding 问题或 TLS 握手失败等问题。

.. code-block:: python

    import socket
    import ssl

    def http_get(host, path='/', port=80, use_ssl=False):
        """Simple HTTP GET using raw sockets."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
            port = 443

        sock.connect((host, port))

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())

        response = b''
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data

        sock.close()

        # 拆分标题和正文
        header_end = response.find(b'\r\n\r\n')
        headers = response[:header_end].decode()
        body = response[header_end + 4:]

        return headers, body

    # 用法
    headers, body = http_get('example.com', '/', use_ssl=True)
    print(headers)

SOCKS 代理支持（SOCKS Proxy Support）
--------------------------------------------------------------

SOCKS (Socket Secure) 是一种通过代理服务器路由网络流量的协议，提供匿名性以及绕过防火墙或地理限制的能力。与仅处理 HTTP 流量的 HTTP 代理不同，SOCKS 在较低级别运行，可以代理任何 TCP（以及 SOCKS5、UDP）流量。 SOCKS5 添加了身份验证和 IPv6 支持。常见用例包括通过 Tor（在端口 9050 上使用 SOCKS5）路由流量、通过 SSH 隧道 ( ``ssh -D`` ) 访问内部网络或公司代理要求。 ``PySocks`` library 可以轻松地通过 SOCKS 代理路由 Python socket 连接，无论是全局（修补所有 sockets）还是每个连接。

.. code-block:: python

    # pip install PySocks
    import socks
    import socket

    # Method 1：全局修补所有 sockets
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
    socket.socket = socks.socksocket

    # 现在所有 socket 连接都通过代理
    s = socket.socket()
    s.connect(("example.com", 80))

    # Method 2：直接创建代理socket
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, "localhost", 9050)
    s.connect(("example.com", 80))

    # Method 3：带认证
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, "proxy.example.com", 1080,
                username="user", password="pass")
