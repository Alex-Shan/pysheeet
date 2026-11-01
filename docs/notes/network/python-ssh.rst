.. meta::
    :description lang=zh_CN: 面向 Python 开发人员的全面 SSH 速查表，涵盖 Paramiko library、SSH 隧道（本地、反向、动态）、端口转发、SFTP 文件传输、跳转主机和 key 管理以及实际示例
    :keywords: Python, Python3, SSH, Paramiko, SFTP, SSH Tunnel, Port Forwarding, Reverse Tunnel, Jump Host, ProxyJump, Bastion Host, SOCKS Proxy, SSH Agent, Key Authentication, Remote Execution

==================================================================
SSH 和安全隧道（SSH and Secure Tunnels）
==================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

SSH（安全Shell）是安全远程访问的标准协议，为机器之间的命令执行、文件传输和网络隧道提供加密通信。 SSH 最初是作为 telnet 和 rsh 的安全替代品而开发的，现已成为系统管理、部署自动化和安全网络访问的重要基础设施。 Python 的 ``paramiko`` library 提供了 SSHv2 协议的完整实现，支持编程 SSH 连接、SFTP 文件传输和复杂的端口转发场景。本速查表涵盖了 SSH 操作的全部范围，从基本密码和 key 身份验证到高级隧道技术，例如用于 NAT 遍历的反向隧道、用于访问隔离网络的跳转主机以及用于通过安全通道路由任意流量的动态 SOCKS 代理。

SSH 基本连接（Basic SSH Connection）
------------------------------------------------------------

SSH 的基础是与远程主机建立安全、经过身份验证的连接。 Paramiko 中的 ``SSHClient`` class 管理整个连接生命周期，包括 TCP 连接、加密握手、主机 key 验证、用户身份验证和通道复用。连接后，您可以执行命令、打开交互式 shell 或建立 SFTP 会话。 context manager 模式 ( ``with`` statement) 确保即使出现 exceptions 也能正确关闭连接，从而防止长时间运行的应用程序中的资源泄漏。

.. code-block:: python

    from paramiko.client import SSHClient

    # 基本密码验证
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("example.com", username="user", password="secret")
        stdin, stdout, stderr = ssh.exec_command("uname -a")
        print(stdout.read().decode())

.. code-block:: python

    # 连接到非标准端口
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("example.com", port=2222, username="user", password="secret")
        stdin, stdout, stderr = ssh.exec_command("hostname")
        print(stdout.read().decode())

主机密钥验证（Host Key Verification）
----------------------------------------------------------

SSH 的安全模型依赖于在发送凭据之前验证服务器的身份。每个SSH服务器都有一个唯一的主机key对，客户端将已知主机公共keys存储在 ``~/.ssh/known_hosts`` 中。首次连接时，SSH 会警告未知主机 - 这是您看到的 "fingerprint" 提示。盲目接受未知的 keys 会破坏这种保护，并导致攻击者拦截您的连接，从而引发中间人攻击。对于自动化来说， ``AutoAddPolicy`` 很方便，但只能在可信网络中或需要额外验证的情况下使用。在生产中，预填充 known_hosts 或使用基于证书的主机身份验证。

.. code-block:: python

    import paramiko
    from paramiko.client import SSHClient

    # 自动添加未知主机keys（谨慎使用）
    # Equivalent to: ssh -o StrictHostKeyChecking=no
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("example.com", username="user", password="secret")
        stdin, stdout, stderr = ssh.exec_command("whoami")
        print(stdout.read().decode())

    # 拒绝未知主机（默认，最安全）
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.load_system_host_keys()  # 加载~/.ssh/known_hosts
        ssh.connect("example.com", username="user", password="secret")

基于密钥的身份验证（Key-Based Authentication）
----------------------------------------------------------------------

SSH key 对提供比密码更强的安全性，同时实现无密码自动化。 key 对由私有 key（在您的计算机上保密）和公共 key（复制到您要访问的服务器）组成。身份验证通过证明您拥有私有 key 而不传输它来进行。尽管 RSA (4096-bit) 仍然广泛兼容，但现代最佳实践建议使用 Ed25519 keys 的安全性和性能。使用密码短语保护私人 keys 进行深度防御 - 如果 key 文件被盗，密码短语将提供额外的屏障。使用 ``ssh-agent`` 到cache解密内存中的keys，避免重复输入密码。

.. code-block:: python

    from paramiko.client import SSHClient

    # 使用私有 key 文件
    # ssh-keygen -t ed25519 -f mykey
    # ssh-copy-id -i mykey.pub 用户@example.com
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("example.com", username="user", key_filename="mykey")
        stdin, stdout, stderr = ssh.exec_command("id")
        print(stdout.read().decode())

.. code-block:: python

    # Key 带密码
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect(
            "example.com",
            username="user",
            key_filename="mykey",
            passphrase="my-key-passphrase"
        )

.. code-block:: python

    # 直接使用RSAKey object
    from paramiko import RSAKey

    pkey = RSAKey.from_private_key_file("mykey", password="passphrase")
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("example.com", username="user", pkey=pkey)

SFTP 文件传输（SFTP File Transfer）
----------------------------------------------------------

SFTP（SSH 文件传输协议）通过 SSH 连接运行，提供安全、加密的文件操作，无需单独的服务或端口。与 FTP 以明文发送凭证并需要 complex 被动模式防火墙规则不同，SFTP 通过端口 22 上的现有 SSH 连接来隧道传输所有内容。Paramiko 的 SFTP 客户端支持完整的 range 文件操作：上传、下载、目录列表、文件元数据、权限和远程文件操纵。对于大额传输，SFTP 处理恢复并提供进度 callbacks。它是需要安全性的部署脚本、备份系统和数据管道中自动文件传输的标准选择。

.. code-block:: python

    from paramiko.client import SSHClient

    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("example.com", username="user", key_filename="mykey")
        sftp = ssh.open_sftp()

        # 上传文件
        sftp.put("local_file.txt", "/remote/path/file.txt")

        # 下载文件
        sftp.get("/remote/path/file.txt", "downloaded.txt")

        # List目录
        for entry in sftp.listdir("/remote/path"):
            print(entry)

        # 文件操作
        sftp.mkdir("/remote/newdir")
        sftp.rename("/remote/old.txt", "/remote/new.txt")
        sftp.remove("/remote/unwanted.txt")

        # 获取文件统计信息
        stat = sftp.stat("/remote/file.txt")
        print(f"Size: {stat.st_size}, Modified: {stat.st_mtime}")

        sftp.close()

SSH 隧道概述（SSH Tunneling Overview）
----------------------------------------------------------------

SSH 隧道（端口转发）是 SSH 最强大的功能之一，允许您通过加密的 SSH 连接安全地路由网络流量。这使得能够访问防火墙后面的服务、加密其他不安全的协议以及绕过网络限制。 types 共有三种：本地转发为您的计算机带来远程服务，远程（反向）转发将您的本地服务暴露给远程网络，动态转发创建用于路由任意流量的 SOCKS 代理。了解这些模式对于安全访问专用网络中的数据库、内部 Web 应用程序和服务至关重要。下图说明了每个 type 的流量。

::

    ┌─────────────────────────────────────────────────────────────────┐
    │                    SSH TUNNEL TYPES                             │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │  LOCAL FORWARDING (-L)                                          │
    │  Access remote service through local port                       │
    │                                                                 │
    │    [You] ──► localhost:8080 ══SSH══► [Server] ──► db:5432       │
    │                                                                 │
    │    ssh -L 8080:database.internal:5432 user@server               │
    │    Then connect to localhost:8080 to reach database             │
    │                                                                 │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │  REMOTE/REVERSE FORWARDING (-R)                                 │
    │  Expose local service to remote server                          │
    │                                                                 │
    │    [You:3000] ◄── [Server]:9000 ◄══SSH══◄ [You initiate]        │
    │                                                                 │
    │    ssh -R 9000:localhost:3000 user@server                       │
    │    Server's port 9000 forwards to your localhost:3000           │
    │                                                                 │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │  DYNAMIC FORWARDING (-D) - SOCKS Proxy                          │
    │  Route any traffic through SSH server                           │
    │                                                                 │
    │    [You] ──► localhost:1080 ══SSH══► [Server] ──► anywhere      │
    │                                                                 │
    │    ssh -D 1080 user@server                                      │
    │    Configure browser/app to use SOCKS5 proxy localhost:1080     │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

本地端口转发（Local Port Forwarding）
----------------------------------------------------------

本地转发 ( ``-L`` ) 是最常见的隧道 type，绑定本地计算机上的端口，通过 SSH 服务器将流量转发到目标主机。这对于访问未暴露在互联网上的专用网络（数据库、内部 Web 应用程序、管理界面）中的服务非常宝贵。 SSH 服务器充当中继：您的本地应用程序连接到 ``localhost:port`` ，SSH 加密并将流量转发到服务器，然后服务器连接到最终目的地。目的地不必是 SSH 服务器本身；它可以是从服务器可访问的任何主机，这非常适合您通过 SSH 到网关计算机来访问内部资源的堡垒/跳转主机场景。

::

    Scenario: Access internal database through bastion host

    ┌──────────┐      ┌──────────────┐      ┌────────────────┐
    │  Your    │ SSH  │   Bastion    │      │   Database     │
    │  Machine │─────►│   Server     │─────►│   (internal)   │
    │          │      │              │      │   db:5432      │
    └──────────┘      └──────────────┘      └────────────────┘
         │
         │ Connect to localhost:5432
         │ Traffic tunneled to db:5432
         ▼

    Command: ssh -L 5432:db.internal:5432 user@bastion
    Then:    psql -h localhost -p 5432 mydb

.. code-block:: python

    # 使用 Paramiko 进行本地端口转发
    import paramiko
    from paramiko.client import SSHClient
    import socket
    import select
    import threading

    def forward_tunnel(local_port, remote_host, remote_port, ssh_client):
        """Forward local_port to remote_host:remote_port via SSH."""
        transport = ssh_client.get_transport()

        # 创建本地监听 socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', local_port))
        server.listen(5)
        print(f"Forwarding localhost:{local_port} -> {remote_host}:{remote_port}")

        while True:
            client, addr = server.accept()
            # 打开通往远程目的地的通道
            channel = transport.open_channel(
                'direct-tcpip',
                (remote_host, remote_port),
                client.getpeername()
            )
            if channel is None:
                client.close()
                continue

            # thread 中的双向转发
            threading.Thread(
                target=_forward_data, args=(client, channel), daemon=True
            ).start()

    def _forward_data(sock, channel):
        """Forward data between socket and SSH channel."""
        while True:
            r, w, x = select.select([sock, channel], [], [])
            if sock in r:
                data = sock.recv(4096)
                if not data:
                    break
                channel.send(data)
            if channel in r:
                data = channel.recv(4096)
                if not data:
                    break
                sock.send(data)
        sock.close()
        channel.close()

    # 用法
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("bastion.example.com", username="user", key_filename="mykey")
        # 将 localhost:5432 转发到internal-db:5432
        forward_tunnel(5432, "internal-db.local", 5432, ssh)

反向端口转发（Reverse Port Forwarding）
--------------------------------------------------------------

反向转发 ( ``-R`` ) 解决相反的问题：将本地计算机上的服务公开到远程服务器的网络。当您位于 NAT、公司防火墙或任何阻止传入连接的网络后面时，这一点至关重要。您启动出站 SSH 连接（防火墙通常允许），SSH 服务器打开一个侦听端口，通过隧道返回到您的计算机。常见用例包括与远程同事共享本地开发服务器、为 debugging 提供对本地服务的临时访问，或者在无法直接入站连接时创建 "callback" 通道。注意，默认情况下，服务器只绑定 ``127.0.0.1`` ；为了允许外部访问，服务器的 ``sshd_config`` 需要 ``GatewayPorts yes`` 。

::

    Scenario: Expose local dev server to public server

    ┌──────────────┐                    ┌──────────────┐
    │  Your Machine│   SSH Connection   │ Public Server│
    │  (behind NAT)│═══════════════════►│              │
    │              │   You initiate     │              │
    │  localhost   │                    │  0.0.0.0     │
    │    :3000     │◄───────────────────│    :9000     │
    │  (your app)  │   Tunnel back      │  (exposed)   │
    └──────────────┘                    └──────────────┘

    Command: ssh -R 9000:localhost:3000 user@public-server
    Result:  Anyone connecting to public-server:9000
             reaches your localhost:3000

    Note: Server needs "GatewayPorts yes" in sshd_config
          to allow binding to 0.0.0.0 (not just 127.0.0.1)

.. code-block:: python

    # 与 Paramiko 反向隧道
    import paramiko
    from paramiko.client import SSHClient
    import socket
    import select
    import threading

    def reverse_tunnel(server_port, local_host, local_port, ssh_client):
        """Expose local_host:local_port on SSH server's server_port."""
        transport = ssh_client.get_transport()

        # 请求远程端口转发
        transport.request_port_forward('', server_port)
        print(f"Reverse tunnel: server:{server_port} -> {local_host}:{local_port}")

        while True:
            # 接受来自服务器的转发连接
            channel = transport.accept(1000)
            if channel is None:
                continue

            # 连接到本地服务
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((local_host, local_port))
            except Exception as e:
                print(f"Local connection failed: {e}")
                channel.close()
                continue

            # 双向转发
            threading.Thread(
                target=_forward_data, args=(sock, channel), daemon=True
            ).start()

    # 用法：在远程端口 9000 上公开本地 Web 服务器
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("public-server.com", username="user", key_filename="mykey")
        reverse_tunnel(9000, "localhost", 3000, ssh)

动态端口转发（SOCKS 代理）（Dynamic Port Forwarding (SOCKS Proxy)）
--------------------------------------------------------------------------------------------------------------

动态转发 ( ``-D`` ) 创建一个本地 SOCKS 代理服务器，该服务器通过 SSH 连接路由流量。与指定固定目标的本地转发不同，动态转发允许应用程序连接到可从 SSH 服务器访问的任何主机 - 目标由 SOCKS 协议根据每个连接确定。这是非常通用的：将您的浏览器配置为使用 SOCKS 代理，所有网络流量都流经 SSH 服务器，从而有效地从该服务器的网络位置进行浏览。使用案例包括访问地理限制内容、从办公室外部浏览内部网站或加密不受信任网络（咖啡店 WiFi）上的流量。 SOCKS5 支持 TCP 和 UDP 以及身份验证，使其比 HTTP 代理更强大。

::

    ┌──────────┐      ┌──────────────┐      ┌─────────────┐
    │  Your    │ SSH  │   SSH        │      │  Any        │
    │  Machine │═════►│   Server     │─────►│  Destination│
    │          │      │              │      │             │
    └──────────┘      └──────────────┘      └─────────────┘
         │
         │ SOCKS5 proxy on localhost:1080
         │ Browser/apps route traffic through it
         ▼

    Command: ssh -D 1080 user@server
    Config:  Set browser proxy to SOCKS5 localhost:1080
             All browsing now goes through SSH server

.. code-block:: bash

    # Command line用途
    ssh -D 1080 -N -f user@server

    # -D 1080：1080端口动态转发
    # -N：无远程命令（仅转发）
    # -f：认证后后台

    # 与卷曲一起使用
    curl --socks5 localhost:1080 http://internal-site.local

跳板主机（ProxyJump）（Jump Hosts (ProxyJump)）
------------------------------------------------------------------------------

跳转主机（也称为堡垒主机或网关服务器）是强化机器，提供进入专用网络的唯一入口点。组织不是将内部服务器直接暴露到互联网，而是通过可受到严格监控和保护的跳转主机路由所有 SSH 访问。 SSH 的 ``ProxyJump`` ( ``-J`` ) 选项使这一过程变得无缝 — 您指定跳转主机，SSH 会自动链接连接，对每个跃点进行身份验证。与最终目的地的连接是端到端加密的；跳转主机只能看到经过的加密流量。您可以为深度分段的网络链接多个跳转主机。此模式对于云环境中的基础设施访问安全至关重要，在云环境中，生产服务器不应具有公共 IP 地址。

::

    ┌──────────┐      ┌──────────────┐      ┌──────────────┐
    │  Your    │ SSH  │   Bastion    │ SSH  │   Internal   │
    │  Machine │═════►│   (jump)     │═════►│   Server     │
    │          │      │              │      │              │
    └──────────┘      └──────────────┘      └──────────────┘

    Command: ssh -J user@bastion user@internal-server

    Or in ~/.ssh/config:
    Host internal-server
        HostName 10.0.0.50
        User admin
        ProxyJump user@bastion.example.com

.. code-block:: python

    # 与 Paramiko 一起跳跃主持人
    from paramiko.client import SSHClient

    # 首先连接到堡垒
    bastion = SSHClient()
    bastion.load_system_host_keys()
    bastion.connect("bastion.example.com", username="user", key_filename="mykey")

    # 获取传输并打开到内部主机的通道
    bastion_transport = bastion.get_transport()
    dest_addr = ("internal-server.local", 22)
    local_addr = ("127.0.0.1", 0)
    channel = bastion_transport.open_channel("direct-tcpip", dest_addr, local_addr)

    # 通过通道连接内部服务器
    internal = SSHClient()
    internal.load_system_host_keys()
    internal.connect(
        "internal-server.local",
        username="admin",
        key_filename="mykey",
        sock=channel  # 使用堡垒通道为socket
    )

    # 在内部服务器上执行命令
    stdin, stdout, stderr = internal.exec_command("hostname")
    print(stdout.read().decode())

    internal.close()
    bastion.close()

SSH 配置文件（SSH Config File）
--------------------------------------------------

SSH 配置文件 ( ``~/.ssh/config`` ) 通过定义每个主机设置消除了重复的 command-line 选项。您无需键入 ``ssh -i ~/.ssh/mykey -p 2222 user@long.hostname.example.com`` ，而是定义一个主机别名并简单地定义 type ``ssh myserver`` 。配置文件支持通配符，允许您为主机组设置 set 默认值（所有 ``*.internal`` 主机都使用特定的跳转服务器）。您还可以定义自动端口转发，以便自动通过数据库隧道连接到主机 sets。对于团队来说，共享配置文件可确保每个人都使用一致、安全的设置。配置是从上到下处理的，第一场比赛获胜，因此将特定主机放在通配符之前。

.. code-block:: text

    # ~/.ssh/config

    # Default settings for all hosts
    Host *
        ServerAliveInterval 60
        ServerAliveCountMax 3
        AddKeysToAgent yes

    # Simple host alias
    Host myserver
        HostName server.example.com
        User admin
        Port 2222
        IdentityFile ~/.ssh/mykey

    # Jump host configuration
    Host bastion
        HostName bastion.example.com
        User jumpuser
        IdentityFile ~/.ssh/bastion_key

    Host internal-*
        ProxyJump bastion
        User admin
        IdentityFile ~/.ssh/internal_key

    Host internal-db
        HostName 10.0.0.50

    Host internal-web
        HostName 10.0.0.51

    # Local port forwarding on connect
    Host db-tunnel
        HostName bastion.example.com
        User admin
        LocalForward 5432 db.internal:5432
        LocalForward 6379 redis.internal:6379

SSH 代理转发（SSH Agent Forwarding）
------------------------------------------------------------

SSH 代理转发允许您在远程服务器上使用本地专用 keys，而无需在那里复制 keys。当您 SSH 到启用了代理转发的服务器 ( ``-A`` ) 时，远程服务器可以为后续的 SSH 连接请求本地 ssh 代理的签名。这对于从服务器克隆私有 git 存储库或在多台计算机之间跳转等工作流程至关重要。但是，代理转发具有安全隐患：在远程服务器上具有 root 访问权限的任何人都可以使用您转发的代理在您连接时向其他系统进行身份验证。对于敏感环境，请考虑使用 ``ProxyJump`` ，这会将 keys 保留在本地，或使用每主机部署 keys。

.. code-block:: bash

    # 启用代理转发
    ssh -A user@server

    # 在服务器上，您本地的 keys 可用
    git clone git@github.com:user/repo.git  # Uses forwarded key

.. code-block:: python

    # 使用 Paramiko 进行代理转发
    from paramiko.client import SSHClient
    from paramiko.agent import Agent

    # 从当地SSH代理处获取keys
    agent = Agent()
    agent_keys = agent.get_keys()

    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        # 使用代理 key 连接
        ssh.connect("server.example.com", username="user", pkey=agent_keys[0])

        # 启用此会话的代理转发
        transport = ssh.get_transport()
        paramiko.agent.AgentRequestHandler(transport.open_session())

Keepalive 和连接稳定性（Keepalive and Connection Stability）
--------------------------------------------------------------------------------------------------------

由于网络问题、NAT 网关超时或状态防火墙丢弃空闲连接，SSH 连接可能会悄然终止。如果没有保活，您将不会知道连接已断开，直到您尝试使用它，从而导致终端挂起或操作失败。 SSH提供了两种保活机制： ``TCPKeepAlive`` 使用TCP级别的保活数据包（可以被某些防火墙阻止），而 ``ServerAliveInterval`` 通过加密通道发送SSH协议消息（更可靠）。 ``ServerAliveCountMax`` 确定有多少错过的响应触发断开连接。为了获得可靠的长期运行连接（隧道、交互式会话或自动化），请配置客户端和服务器保持活动。 30-60 秒的间隔适用于大多数 NAT 环境。

.. code-block:: python

    from paramiko.client import SSHClient

    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect("server.example.com", username="user", key_filename="mykey")

        # 配置保活
        transport = ssh.get_transport()
        transport.set_keepalive(30)  # 每 30 秒发送一次 keepalive

        # 长时间运行的操作...

.. code-block:: text

    # In ~/.ssh/config
    Host *
        ServerAliveInterval 30
        ServerAliveCountMax 3
        TCPKeepAlive yes

SSH常用命令参考（Common SSH Commands Reference）
--------------------------------------------------------------------------------

基本 SSH 命令的快速参考，涵盖连接、隧道、key 管理和文件传输。这些命令构成了安全远程管理的基础，值得牢记。详细标志（ ``-v`` 到 ``-vvv`` ）对于 debugging 连接问题非常有用，可以显示 methods 尝试的身份验证、key 交换以及发生故障的位置。

.. code-block:: bash

    # 基本连接
    ssh user@host
    ssh -p 2222 user@host              # 自定义端口
    ssh -i ~/.ssh/mykey user@host      # 具体key

    # 隧道技术
    ssh -L 8080:localhost:80 user@host # 本地转发
    ssh -R 9000:localhost:3000 user@host # 远程转发
    ssh -D 1080 user@host              # SOCKS代理

    # 跳转主机
    ssh -J jump@bastion user@internal  # 代理跳转
    ssh -o ProxyCommand="ssh -W %h:%p jump@bastion" user@internal

    # 背景隧道
    ssh -N -f -L 5432:db:5432 user@host  # -N 无命令，-f 背景

    # Key 管理
    ssh-keygen -t ed25519 -C "comment"   # 生成key（推荐ed25519）
    ssh-keygen -t rsa -b 4096            # RSA 4096-bit
    ssh-copy-id -i ~/.ssh/mykey user@host # 将公共 key 复制到服务器
    ssh-add ~/.ssh/mykey                 # 将 key 添加到代理

    # Debugging
    ssh -v user@host                     # 冗长
    ssh -vvv user@host                   # 非常详细

    # 文件传输
    scp local.txt user@host:/path/       # 复制到远程
    scp user@host:/path/file.txt .       # 从远程复制
    scp -r dir/ user@host:/path/         # Recursive 副本
    rsync -avz -e ssh dir/ user@host:/path/  # Efficient sync
