.. meta::
    :description lang=zh_CN: Python TLS/SSL socket 编程教程，涵盖安全服务器、证书处理、密码配置、双向 TLS (mTLS) 以及用于 HTTPS 和加密通信的非阻塞 SSL
    :keywords: Python, socket, SSL, TLS, secure socket, certificate, cipher, HTTPS, encryption, network security, mTLS, mutual TLS, X.509, OpenSSL, cryptography

========================================================
SSL/TLS 套接字（SSL/TLS Sockets）
========================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

传输层安全 (TLS)，以前称为安全 Sockets 层 (SSL)，是加密网络通信的标准协议。 TLS为properties提供了三个基本安全性：机密性（数据经过加密，窃听者无法读取）、完整性（数据在传输过程中不能被修改而不被检测到）和身份验证（各方可以使用证书验证彼此的身份）。每个 HTTPS 连接、安全电子邮件和 VPN 在底层都使用 TLS。

Python的 ``ssl`` module为TLS提供了全面的接口，允许您对常规sockets进行加密包装。本节介绍创建支持 TLS 的服务器和客户端、配置密码套件以实现安全合规性、处理 X.509 证书、实现用于客户端身份验证的相互 TLS (mTLS) 以及为高性能应用程序构建非阻塞 TLS 服务器。无论您是构建安全的 API 服务器、实施证书固定，还是 debugging TLS 握手问题，这些示例都可以为您提供所需的基础。

简单 TLS Echo 服务器（Simple TLS Echo Server）
------------------------------------------------------------------------------

基本的 TLS 服务器将接受的 TCP 连接与 SSL 上下文包装起来以提供加密。服务器需要证书（公共key）和私有key，可以自签名用于测试或从证书颁发机构（CA）获取用于生产使用。 ``SSLContext`` object 管理所有 TLS 设置，包括协议版本、密码套件和证书验证选项。

.. code-block:: python

    import socket
    import ssl

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 5566))
    sock.listen(10)

    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslctx.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    try:
        while True:
            conn, addr = sock.accept()
            sslconn = sslctx.wrap_socket(conn, server_side=True)
            msg = sslconn.recv(1024)
            if msg:
                sslconn.send(msg)
            sslconn.close()
    finally:
        sock.close()

生成自签名证书并测试：

.. code-block:: bash

    # 生成私有key和自签名证书
    $ openssl genrsa -out key.pem 2048
    $ openssl req -x509 -new -nodes -key key.pem -days 365 -out cert.pem

    # 运行服务器
    $ python3 ssl_server.py &

    # 使用openssl客户端进行测试
    $ openssl s_client -connect localhost:5566
    Hello SSL
    Hello SSL

带密码配置的 TLS 服务器（TLS Server with Cipher Configuration）
--------------------------------------------------------------------------------------------------------

配置特定的密码套件以实现安全合规性或兼容性。

.. code-block:: python

    import socket
    import ssl
    import json

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 5566))
    sock.listen(10)

    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslctx.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    # Set 特定密码 (TLS 1.2)
    sslctx.set_ciphers('ECDHE+AESGCM:DHE+AESGCM')

    # 打印配置的密码
    print(json.dumps(sslctx.get_ciphers(), indent=2))

    try:
        while True:
            conn, addr = sock.accept()
            sslconn = sslctx.wrap_socket(conn, server_side=True)
            print(f"Cipher: {sslconn.cipher()}")
            msg = sslconn.recv(1024)
            if msg:
                sslconn.send(msg)
            sslconn.close()
    finally:
        sock.close()

TLS 客户端（TLS Client）
--------------------------------------

连接到带有证书验证的 TLS 服务器。

.. code-block:: python

    import socket
    import ssl

    hostname = 'www.google.com'
    port = 443

    # 创建默认 SSL 上下文（验证证书）
    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"TLS version: {ssock.version()}")
            print(f"Cipher: {ssock.cipher()}")

            # 发送 HTTP 请求
            ssock.send(b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")
            response = ssock.recv(4096)
            print(response[:200])

TLS 自定义 CA 客户端（TLS Client with Custom CA）
----------------------------------------------------------------------------------

根据自定义证书颁发机构验证服务器证书。

.. code-block:: python

    import socket
    import ssl

    hostname = 'localhost'
    port = 5566

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations('ca-cert.pem')  # CA 证书
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.send(b"Hello")
            print(ssock.recv(1024))

双向 TLS（mTLS）（Mutual TLS (mTLS)）
--------------------------------------------------------------

客户端和服务器都提供证书以进行相互身份验证。

服务器：

.. code-block:: python

    import socket
    import ssl

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 5566))
    sock.listen(10)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server-cert.pem', 'server-key.pem')
    context.load_verify_locations('ca-cert.pem')
    context.verify_mode = ssl.CERT_REQUIRED  # 需要客户证书

    try:
        while True:
            conn, addr = sock.accept()
            sslconn = context.wrap_socket(conn, server_side=True)
            # 获取客户端证书信息
            cert = sslconn.getpeercert()
            print(f"Client: {cert.get('subject')}")
            msg = sslconn.recv(1024)
            if msg:
                sslconn.send(msg)
            sslconn.close()
    finally:
        sock.close()

客户：

.. code-block:: python

    import socket
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_cert_chain('client-cert.pem', 'client-key.pem')
    context.load_verify_locations('ca-cert.pem')

    with socket.create_connection(('localhost', 5566)) as sock:
        with context.wrap_socket(sock, server_hostname='localhost') as ssock:
            ssock.send(b"Hello mTLS")
            print(ssock.recv(1024))

使用 selectors 的非阻塞 TLS（Non-blocking TLS with selectors）
------------------------------------------------------------------------------------------------------------

使用选择器 module 异步处理 TLS 握手和 I/O。

.. code-block:: python

    import socket
    import selectors
    import ssl
    from functools import partial

    sslctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslctx.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    def accept(sock, sel):
        conn, addr = sock.accept()
        sslconn = sslctx.wrap_socket(conn,
                                     server_side=True,
                                     do_handshake_on_connect=False)
        sel.register(sslconn, selectors.EVENT_READ, do_handshake)

    def do_handshake(sslconn, sel):
        try:
            sslconn.do_handshake()
            sel.modify(sslconn, selectors.EVENT_READ, read)
        except ssl.SSLWantReadError:
            pass  # 需要更多数据，等待下一个事件
        except ssl.SSLWantWriteError:
            sel.modify(sslconn, selectors.EVENT_WRITE, do_handshake)

    def read(sslconn, sel):
        try:
            msg = sslconn.recv(1024)
            if msg:
                sel.modify(sslconn, selectors.EVENT_WRITE,
                          partial(write, msg=msg))
            else:
                sel.unregister(sslconn)
                sslconn.close()
        except ssl.SSLWantReadError:
            pass

    def write(sslconn, sel, msg=None):
        try:
            if msg:
                sslconn.send(msg)
            sel.modify(sslconn, selectors.EVENT_READ, read)
        except ssl.SSLWantWriteError:
            pass

    # 主服务器 loop
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 5566))
    sock.listen(10)

    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, accept)

    try:
        while True:
            events = sel.select()
            for key, mask in events:
                handler = key.data
                handler(key.fileobj, sel)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        sel.close()

获取证书信息（Get Certificate Information）
----------------------------------------------------------------------

检索并检查服务器证书详细信息。

.. code-block:: python

    import socket
    import ssl
    import pprint

    hostname = 'www.google.com'
    port = 443

    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            pprint.pprint(cert)

            # 获取特定字段
            print(f"Subject: {dict(x[0] for x in cert['subject'])}")
            print(f"Issuer: {dict(x[0] for x in cert['issuer'])}")
            print(f"Not Before: {cert['notBefore']}")
            print(f"Not After: {cert['notAfter']}")

            # 获取DER格式的证书
            der_cert = ssock.getpeercert(binary_form=True)
            print(f"Certificate size: {len(der_cert)} bytes")

TLS 版本和安全设置（TLS Version and Security Settings）
--------------------------------------------------------------------------------------------

配置最低 TLS 版本和安全选项。

.. code-block:: python

    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Set 最低 TLS 版本（TLS 1.2+）
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # 显式禁用旧协议
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1

    # 禁用压缩（CRIME 攻击缓解）
    context.options |= ssl.OP_NO_COMPRESSION

    # 使用服务器的密码首选项
    context.options |= ssl.OP_CIPHER_SERVER_PREFERENCE

    # 加载证书
    context.load_cert_chain('cert.pem', 'key.pem')

    # Set 仅强密码
    context.set_ciphers('ECDHE+AESGCM:DHE+AESGCM:!aNULL:!MD5:!DSS')

    print(f"Min version: {context.minimum_version}")
    print(f"Ciphers: {len(context.get_ciphers())}")
