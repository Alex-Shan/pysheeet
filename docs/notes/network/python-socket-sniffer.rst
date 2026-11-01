.. meta::
    :description lang=zh_CN: Python 数据包嗅探和原始 socket 编程教程，用于捕获和解析 IP、TCP、UDP、ARP 数据包、网络分析和 Linux 内核加密 API
    :keywords: Python, socket, raw socket, packet sniffer, IP header, TCP header, ARP, network analysis, ctypes, struct, Wireshark, tcpdump, AF_ALG, kernel crypto, scapy

============================================
数据包嗅探（Packet Sniffing）
============================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Raw sockets 提供对 IP 层及以下层网络数据包的直接访问，绕过正常的 TCP/UDP 协议 stack。这种低级访问对于构建网络分析工具、入侵检测系统、自定义协议实现和安全研究工具至关重要。虽然像 Wireshark 和 tcpdump 这样的 libraries 通常用于数据包捕获，但了解如何解析 Python 中的数据包可以让您灵活地构建适合您特定需求的自定义分析工具。

本节介绍使用 Python 的原始 socket 接口、用于定义 C 兼容数据结构的 ``ctypes`` module 以及用于二进制数据解析的 ``struct`` module 来捕获和解析网络数据包。您将学习使用 decode IP 标头提取源地址和目标地址，解析 TCP 标头以分析连接状态和标志，捕获 ARP 数据包以监控地址解析，以及使用 Linux 内核的 AF_ALG 接口进行硬件加速加密。这些技术构成了构建网络监视器、协议分析器和安全扫描器等工具的基础。

.. warning::

    在大多数操作系统上，原始 socket 操作通常需要 root/管理员权限。负责任地使用这些技术，并且仅在您拥有或具有明确分析权限的网络上使用。未经授权的数据包嗅探可能违反您所在司法管辖区的法律和法规。

嗅探器 IP 数据包（Sniffer IP Packets）
------------------------------------------------------------

捕获 IP 数据包需要使用 ``SOCK_RAW`` 创建原始 socket 并指定要捕获的协议（e.g.、ICMP 数据包为 ``IPPROTO_ICMP`` ）。 IP 标头是一个 20-byte 结构（无选项），包含版本、标头长度、服务 type、总长度、标识、标志、片段偏移、TTL、协议、校验和以及源/目标地址。使用 ``ctypes.Structure`` ，我们可以定义一个 Python class 直接映射到此二进制布局，以便于现场访问。

.. code-block:: python

    from ctypes import Structure, c_ubyte, c_uint8, c_uint16, c_uint32
    import socket
    import struct

    # IP 协议号
    PROTO_MAP = {
        1: "ICMP",
        2: "IGMP",
        6: "TCP",
        17: "UDP",
        27: "RDP"
    }

    class IP(Structure):
        """IP header structure (20 bytes)."""
        _fields_ = [
            ("ip_hl", c_ubyte, 4),   # 标头长度
            ("ip_v", c_ubyte, 4),    # 版本
            ("ip_tos", c_uint8),     # 服务Type
            ("ip_len", c_uint16),    # 总长度
            ("ip_id", c_uint16),     # 鉴别
            ("ip_off", c_uint16),    # 片段偏移
            ("ip_ttl", c_uint8),     # 生存时间
            ("ip_p", c_uint8),       # 协议
            ("ip_sum", c_uint16),    # 校验和
            ("ip_src", c_uint32),    # 源地址
            ("ip_dst", c_uint32),    # 目的地地址
        ]

        def __new__(cls, buf=None):
            return cls.from_buffer_copy(buf)

        def __init__(self, buf=None):
            src = struct.pack("<L", self.ip_src)
            self.src = socket.inet_ntoa(src)
            dst = struct.pack("<L", self.ip_dst)
            self.dst = socket.inet_ntoa(dst)
            self.proto = PROTO_MAP.get(self.ip_p, f"Unknown({self.ip_p})")

    # 为 ICMP 创建原始 socket
    host = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.bind((host, 0))

    print("Sniffer start... (Ctrl+C to stop)")
    try:
        while True:
            buf = s.recvfrom(65535)[0]
            ip_header = IP(buf[:20])
            print(f'{ip_header.proto}: {ip_header.src} -> {ip_header.dst}')
    except KeyboardInterrupt:
        s.close()

输出：

.. code-block:: console

    $ sudo python sniffer.py
    Sniffer start...
    ICMP: 127.0.0.1 -> 127.0.0.1
    ICMP: 127.0.0.1 -> 127.0.0.1

嗅探器 TCP 数据包（Sniffer TCP Packets）
----------------------------------------------------------------

解析 TCP 标头以提取端口号、序列号和标志。

.. code-block:: python

    import socket
    import platform
    from struct import unpack
    from contextlib import contextmanager

    if platform.system() != "Linux":
        print("This example requires Linux")
        exit(1)

    @contextmanager
    def create_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        try:
            yield s
        finally:
            s.close()

    def parse_tcp_packet(pkt):
        # IP 标头（前 20 个 bytes、variable 长度）
        iphdr = unpack('!BBHHHBBH4s4s', pkt[0:20])
        iplen = (iphdr[0] & 0xf) * 4

        # TCP 标头（最少接下来 20 个 bytes）
        tcphdr = unpack('!HHLLBBHHH', pkt[iplen:iplen+20])

        return {
            'src_port': tcphdr[0],
            'dst_port': tcphdr[1],
            'seq': tcphdr[2],
            'ack': tcphdr[3],
            'data_offset': tcphdr[4] >> 4,
            'flags': {
                'FIN': tcphdr[5] & 0x01,
                'SYN': tcphdr[5] & 0x02,
                'RST': tcphdr[5] & 0x04,
                'PSH': tcphdr[5] & 0x08,
                'ACK': tcphdr[5] & 0x10,
                'URG': tcphdr[5] & 0x20,
            },
            'window': tcphdr[6],
            'checksum': tcphdr[7],
        }

    try:
        with create_socket() as s:
            print("TCP Sniffer started...")
            while True:
                pkt, addr = s.recvfrom(65535)
                tcp = parse_tcp_packet(pkt)

                # 跳过没有数据的数据包
                iplen = (pkt[0] & 0xf) * 4
                tcplen = tcp['data_offset'] * 4
                data = pkt[iplen + tcplen:]
                if not data:
                    continue

                flags = [k for k, v in tcp['flags'].items() if v]
                print(f"Port {tcp['src_port']} -> {tcp['dst_port']} "
                      f"[{','.join(flags)}] Seq={tcp['seq']}")
                print(f"Data: {data[:50]}...")
    except KeyboardInterrupt:
        pass

嗅探器 ARP 数据包（Sniffer ARP Packets）
----------------------------------------------------------------

捕获 ARP（地址解析协议）数据包以查看 MAC 到 IP 的映射。

.. code-block:: python

    import socket
    import struct
    import binascii

    # 为所有数据包创建原始 socket
    rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                              socket.htons(0x0003))

    print("ARP Sniffer started...")
    while True:
        packet = rawSocket.recvfrom(2048)

        # 以太网接头 (14 bytes)
        ethhdr = packet[0][0:14]
        eth = struct.unpack("!6s6s2s", ethhdr)

        # 检查是否为 ARP 数据包（0x0806）
        if eth[2] != b'\x08\x06':
            continue

        # ARP 接头 (28 bytes)
        arphdr = packet[0][14:42]
        arp = struct.unpack("2s2s1s1s2s6s4s6s4s", arphdr)

        print("=" * 50)
        print("ETHERNET FRAME")
        print(f"  Dest MAC:   {binascii.hexlify(eth[0]).decode()}")
        print(f"  Source MAC: {binascii.hexlify(eth[1]).decode()}")
        print("ARP HEADER")
        print(f"  Hardware:   {binascii.hexlify(arp[0]).decode()}")
        print(f"  Protocol:   {binascii.hexlify(arp[1]).decode()}")
        print(f"  Opcode:     {binascii.hexlify(arp[4]).decode()} "
              f"({'Request' if arp[4] == b'\\x00\\x01' else 'Reply'})")
        print(f"  Sender MAC: {binascii.hexlify(arp[5]).decode()}")
        print(f"  Sender IP:  {socket.inet_ntoa(arp[6])}")
        print(f"  Target MAC: {binascii.hexlify(arp[7]).decode()}")
        print(f"  Target IP:  {socket.inet_ntoa(arp[8])}")

使用 struct 解析数据包（Parse Packet with struct）
----------------------------------------------------------------------------------

使用 ``struct`` module进行灵活的数据包解析。

.. code-block:: python

    import struct
    import socket

    def parse_ip_header(data):
        """Parse IP header from raw bytes."""
        # ! = network byte order (big-endian)
        # B = unsigned char, H = unsigned short, 4s = 4-byte string
        fields = struct.unpack('!BBHHHBBH4s4s', data[:20])

        return {
            'version': fields[0] >> 4,
            'ihl': fields[0] & 0x0F,
            'tos': fields[1],
            'total_length': fields[2],
            'identification': fields[3],
            'flags': fields[4] >> 13,
            'fragment_offset': fields[4] & 0x1FFF,
            'ttl': fields[5],
            'protocol': fields[6],
            'checksum': fields[7],
            'src_ip': socket.inet_ntoa(fields[8]),
            'dst_ip': socket.inet_ntoa(fields[9]),
        }

    def parse_udp_header(data):
        """Parse UDP header from raw bytes."""
        fields = struct.unpack('!HHHH', data[:8])
        return {
            'src_port': fields[0],
            'dst_port': fields[1],
            'length': fields[2],
            'checksum': fields[3],
        }

    # 捕获数据包的用法示例
    # ip_data = ... (raw IP packet bytes)
    # ip = parse_ip_header(ip_data)
    # if ip['protocol'] == 17:  # UDP
    #     udp = parse_udp_header(ip_data[ip['ihl']*4:])

Linux 内核加密 API (AF_ALG)（Linux Kernel Crypto API (AF_ALG)）
------------------------------------------------------------------------------------------------------------------

使用Linux内核的加密API到sockets进行硬件加速加密。需要 Linux 2.6.38+ 和 Python 3.6+。

.. code-block:: python

    import socket
    import hashlib
    import contextlib

    @contextlib.contextmanager
    def create_alg(typ, name):
        s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
        try:
            s.bind((typ, name))
            yield s
        finally:
            s.close()

    # SHA-256 hash 使用内核加密
    msg = b'Python is awesome!'

    with create_alg('hash', 'sha256') as algo:
        op, _ = algo.accept()
        with op:
            op.sendall(msg)
            digest = op.recv(512)
            print(f"AF_ALG SHA256: {digest.hex()}")

            # 对照 hashlib 进行验证
            expected = hashlib.sha256(msg).digest()
            assert digest == expected

AES-CBC 通过 AF_ALG 加密（AES-CBC Encryption via AF_ALG）
------------------------------------------------------------------------------------------------------

.. code-block:: python

    import socket
    import os

    BS = 16  # 块大小
    pad = lambda s: s + (BS - len(s) % BS) * bytes([BS - len(s) % BS])
    unpad = lambda s: s[:-s[-1]]

    def aes_cbc_encrypt(plaintext, key, iv):
        with socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0) as algo:
            algo.bind(('skcipher', 'cbc(aes)'))
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
            op, _ = algo.accept()
            with op:
                plaintext = pad(plaintext)
                op.sendmsg_afalg([plaintext],
                                op=socket.ALG_OP_ENCRYPT,
                                iv=iv)
                return op.recv(len(plaintext))

    def aes_cbc_decrypt(ciphertext, key, iv):
        with socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0) as algo:
            algo.bind(('skcipher', 'cbc(aes)'))
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
            op, _ = algo.accept()
            with op:
                op.sendmsg_afalg([ciphertext],
                                op=socket.ALG_OP_DECRYPT,
                                iv=iv)
                return unpad(op.recv(len(ciphertext)))

    # 例子
    key = os.urandom(32)  # AES-256
    iv = os.urandom(16)
    plaintext = b"Secret message!"

    ciphertext = aes_cbc_encrypt(plaintext, key, iv)
    decrypted = aes_cbc_decrypt(ciphertext, key, iv)

    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Decrypted: {decrypted}")

数据包分析的有用工具（Useful Tools for Packet Analysis）
----------------------------------------------------------------------------------------

虽然原始 sockets 具有教育意义，但请考虑将这些工具用于生产用途：

.. code-block:: python

    # Scapy - 强大的数据包操作 library
    # pip install scapy
    from scapy.all import sniff, IP, TCP

    def packet_callback(pkt):
        if IP in pkt and TCP in pkt:
            print(f"{pkt[IP].src}:{pkt[TCP].sport} -> "
                  f"{pkt[IP].dst}:{pkt[TCP].dport}")

    # 嗅探 10 个 TCP 数据包
    sniff(filter="tcp", prn=packet_callback, count=10)

    # dpkt - 快速数据包解析
    # pip install dpkt
    import dpkt

    with open('capture.pcap', 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                print(f"{dpkt.utils.inet_to_str(ip.src)} -> "
                      f"{dpkt.utils.inet_to_str(ip.dst)}")
