.. meta::
    :description lang=zh_CN: Python 网络编程教程，涵盖 sockets、TCP/UDP 服务器、异步 I/O、SSL/TLS、数据包嗅探和 SSH 隧道
    :keywords: Python, Python3, socket, networking, TCP, UDP, SSL, TLS, async, select, epoll, SSH, packet sniffing, server, client

======================
网络（Network）
======================

网络编程是现代软件开发的基础，支持 processes 之间跨机器、数据中心和互联网的通信。本节介绍 Python 的网络功能，从低级 socket 编程到安全通信。您将找到构建 TCP/UDP 服务器、使用异步 I/O（select、poll、epoll）处理多个连接、实现 TLS/SSL 加密、用于网络分析的数据包嗅探以及用于安全远程访问和隧道的 SSH 的实用示例。无论您是构建 Web 服务、物联网应用程序、网络工具还是自动化脚本，这些速查表都提供您所需的基本模式和代码片段。

.. toctree::
    :maxdepth: 1

    python-socket
    python-socket-server
    python-socket-async
    python-socket-ssl
    python-socket-sniffer
    python-ssh
