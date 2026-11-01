.. meta::
    :description lang=zh_CN: Python操作系统界面教程，涵盖文件操作、process管理、环境variables、路径操作、系统信息和跨平台OS交互
    :keywords: Python, os module, operating system, file system, process, environment variables, path, directory, subprocess, platform, system info, CPU, memory

============================================
操作系统（Operating System）
============================================

:Source: `src/basic/os_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/os_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

Python 的 ``os`` module 提供了一种与操作系统交互的便携式方式，在一致的 API 后面抽象出平台特定的细节。无论您是管理文件和目录、生成 processes、读取环境 variables 还是查询系统信息， ``os`` module 都能处理 Windows、Linux 和 macOS 之间的差异。对于路径操作， ``os.path`` 子模块（或现代 ``pathlib`` ）提供跨平台路径处理。本速查表涵盖了常见的 OS 操作和实际示例。

获取系统信息（Get System Information）
------------------------------------------------------------

检索有关操作系统、平台和当前 process 的基本信息。这些 functions 对于编写适应运行时环境的跨平台代码很有用。

.. code-block:: python

    import os
    import platform

    # 操作系统名称
    os.name                    # 'posix' (Linux/macOS) 或 'nt' (Windows)

    # 平台详情
    platform.system()          # 'Linux'、'Darwin'、'Windows'
    platform.release()         # '5.15.0-generic'、'22.1.0'、'10'
    platform.machine()         # 'x86_64'、'arm64'、'AMD64'
    platform.processor()       # 'x86_64'，'arm'，''
    platform.python_version()  # '3.12.0'

    # 当前process
    os.getpid()               # Process ID
    os.getppid()              # 母体 process ID
    os.getcwd()               # 当前工作目录
    os.getlogin()             # 当前用户名

获取CPU数量（Get Number of CPUs）
------------------------------------------------------

确定可用于并行处理的 CPU 内核的数量。这对于配置 thread pools、multiprocessing 工作线程或了解系统容量至关重要。请注意， ``cpu_count()`` 返回逻辑核心（包括超线程），而不是物理核心。

.. code-block:: python

    import os

    # 逻辑CPU数量
    cpu_count = os.cpu_count()
    print(f"CPUs: {cpu_count}")  # CPU：8

    # 对于物理内核（仅限 Linux）
    # cat /proc/cpuinfo | grep "cpu cores" | uniq

设置 CPU 亲和力（Set CPU Affinity）
--------------------------------------------------------

CPU 亲和力将 process 绑定到特定的 CPU 内核，可用于性能优化、减少 cache 缺失或隔离工作负载。此功能是 Linux 特定的，在 macOS 或 Windows 上通过 ``os`` module 不可用。

.. code-block:: python

    import os

    # 仅 Linux - set process 在特定 CPU 上运行
    pid = os.getpid()
    affinity = {0, 1}  # 仅在 CPU 0 和 1 上运行
    os.sched_setaffinity(pid, affinity)

    # 获取当前亲和力
    current = os.sched_getaffinity(pid)
    print(f"Running on CPUs: {current}")  # 在 CPU 上运行：{0, 1}

环境变量（Environment Variables）
------------------------------------------------------

环境 variables 存储在 process 调用期间持续存在的配置。使用 ``os.environ`` 作为dictionary来读取set或删除variables。更改仅影响当前 process 及其子项，而不影响父项 shell。

.. code-block:: python

    import os

    # 读取环境 variable
    home = os.environ.get('HOME')           # 如果不是 set，则返回 None
    path = os.environ['PATH']               # 如果不是 set，则引发 KeyError
    debug = os.getenv('DEBUG', 'false')     # 默认为value

    # Set 环境 variable
    os.environ['MY_VAR'] = 'my_value'

    # 删除环境variable
    del os.environ['MY_VAR']
    os.unsetenv('MY_VAR')  # 选择

    # List 全环境 variables
    for key, value in os.environ.items():
        print(f"{key}={value}")

路径操作（Path Operations）
------------------------------------------

路径操作是最常见的 OS 任务之一。 ``os.path`` module 提供跨平台 functions，可自动处理路径分隔符（ ``/`` 与 ``\`` ）。对于现代 Python (3.4+)，请考虑使用 ``pathlib`` 进行面向 object 的方法。

.. code-block:: python

    import os

    # 连接路径（自动处理分隔符）
    path = os.path.join('/home', 'user', 'file.txt')
    # Linux: '/home/user/file.txt'
    # Windows: '\\home\\user\\file.txt'

    # 分割路径组件
    dirname = os.path.dirname('/home/user/file.txt')   # '/home/user'
    basename = os.path.basename('/home/user/file.txt') # 'file.txt'
    name, ext = os.path.splitext('file.txt')           # ('file'、'.txt')

    # 绝对路径和相对路径
    abs_path = os.path.abspath('.')           # 完整路径
    rel_path = os.path.relpath('/home/user')  # 相对于cwd
    real_path = os.path.realpath('link')      # 解析符号链接

    # 路径检查
    os.path.exists('/path/to/file')    # True 如果存在
    os.path.isfile('/path/to/file')    # True 如果是常规文件
    os.path.isdir('/path/to/dir')      # True 如果目录
    os.path.islink('/path/to/link')    # True 如果是符号链接

    # 路径信息
    os.path.getsize('/path/to/file')   # 尺寸为 bytes
    os.path.getmtime('/path/to/file')  # 修改时间（时间戳）

目录操作（Directory Operations）
----------------------------------------------------

创建、删除和导航目录。这些操作是文件管理、构建系统和数据处理管道的基础。

.. code-block:: python

    import os

    # 创建目录
    os.mkdir('new_dir')                    # 单一目录
    os.makedirs('path/to/new_dir')         # 也创建父目录
    os.makedirs('path/to/dir', exist_ok=True)  # 如果存在则不报错

    # 删除目录
    os.rmdir('empty_dir')                  # 必须为空
    # For non-empty: use shutil.rmtree()

    # 更改目录
    os.chdir('/path/to/dir')
    print(os.getcwd())                     # 打印当前目录

    # List 目录内容
    entries = os.listdir('.')              # 名称 List
    for entry in entries:
        print(entry)

    # 遍历目录树
    for root, dirs, files in os.walk('.'):
        for file in files:
            path = os.path.join(root, file)
            print(path)

文件操作（File Operations）
------------------------------------------

使用 file descriptors 进行低级文件操作。对于大多数用例，Python 的内置 ``open()`` function 是首选，但 ``os`` functions 对于非阻塞 I/O 等特殊情况或需要精确控制 file descriptors 时非常有用。

.. code-block:: python

    import os

    # 重命名/移动文件
    os.rename('old_name.txt', 'new_name.txt')
    os.replace('src.txt', 'dst.txt')  # 原子，覆盖 dst

    # 删除文件
    os.remove('file.txt')
    os.unlink('file.txt')  # 与删除相同

    # 文件权限（Unix）
    os.chmod('file.txt', 0o644)  # RW-R--R--
    os.chown('file.txt', uid, gid)  # 改变所有者

    # 创建符号链接
    os.symlink('target', 'link_name')

    # 低级文件操作
    fd = os.open('file.txt', os.O_RDONLY)
    data = os.read(fd, 1024)  # 最多读取 1024 bytes
    os.close(fd)

执行命令（Execute Commands）
--------------------------------------------

运行外部命令和程序。对于简单情况， ``os.system()`` 可以工作，但建议使用 ``subprocess`` module 来更好地控制输入/输出和错误处理。

.. code-block:: python

    import os
    import subprocess

    # 简单命令（返回exit code）
    exit_code = os.system('ls -la')

    # 更好：使用子流程
    result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
    print(result.stdout)
    print(result.returncode)

    # 运行并捕获输出
    output = subprocess.check_output(['date'], text=True)
    print(output.strip())

    # 带输入运行
    result = subprocess.run(
        ['grep', 'pattern'],
        input='line1\npattern here\nline3',
        capture_output=True,
        text=True
    )

进程管理（Process Management）
------------------------------------------------

创建并管理子 processes。 ``os.fork()`` function 是 Unix 特定的；对于跨平台 process 创建，请改用 ``multiprocessing`` module。

.. code-block:: python

    import os

    # Fork process（仅限 Unix）
    pid = os.fork()
    if pid == 0:
        # 儿童 process
        print(f"Child PID: {os.getpid()}")
        os._exit(0)
    else:
        # 母体 process
        print(f"Parent PID: {os.getpid()}, Child PID: {pid}")
        os.waitpid(pid, 0)  # 等孩子

    # 执行新程序（替换当前的process）
    # os.execv('/bin/ls', ['ls', '-la'])

    # 发送信号至process
    os.kill(pid, signal.SIGTERM)

临时文件（Temporary Files）
------------------------------------------

创建自动清理的临时文件和目录。 ``tempfile`` module 提供安全、跨平台的临时文件处理。

.. code-block:: python

    import tempfile
    import os

    # 临时文件（关闭时自动删除）
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('temporary data')
        temp_path = f.name
    print(f"Temp file: {temp_path}")
    os.unlink(temp_path)  # Manual cleanup if delete=False

    # 临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = os.path.join(tmpdir, 'file.txt')
        with open(temp_file, 'w') as f:
            f.write('data')
        # 使用块后删除的目录和内容

    # 获取临时目录路径
    print(tempfile.gettempdir())  # /tmp 或 C:\Users\...\Temp

使用pathlib（现代替代方案）（Using pathlib (Modern Alternative)）
----------------------------------------------------------------------------------------------------------

``pathlib`` module (Python 3.4+) 提供面向 object 的路径接口，使代码比基于 string 的 ``os.path`` 操作更具可读性且不易出错。

.. code-block:: python

    from pathlib import Path

    # 创建路径 objects
    p = Path('/home/user/file.txt')
    p = Path.home() / 'documents' / 'file.txt'  # 使用/operator

    # 路径组件
    p.name          # 'file.txt'
    p.stem          # 'file'
    p.suffix        # '.txt'
    p.parent        # Path('/home/user')
    p.parts         # （'/'、'home'、'user'、'file.txt'）

    # 路径检查
    p.exists()
    p.is_file()
    p.is_dir()

    # 读/写文件
    content = p.read_text()
    p.write_text('new content')
    data = p.read_bytes()

    # 目录操作
    Path('new_dir').mkdir(parents=True, exist_ok=True)
    for child in Path('.').iterdir():
        print(child)

    # 全局模式
    for py_file in Path('.').glob('**/*.py'):
        print(py_file)


使用 psutil 进行系统监控（System Monitoring with psutil）
----------------------------------------------------------------------------------------------

``psutil`` （process 和系统实用程序）library 提供对系统监控数据的跨平台访问，这是通过标准 ``os`` module 无法获得的。它涵盖了 CPU、内存、磁盘、网络和 process 信息。使用 ``pip install psutil`` 安装。

.. code-block:: python

    import psutil

    # CPU信息
    psutil.cpu_count()                    # 逻辑CPU
    psutil.cpu_count(logical=False)       # 物理核心
    psutil.cpu_percent(interval=1)        # CPU 使用率%
    psutil.cpu_percent(percpu=True)       # 每个 CPU 的使用情况
    psutil.cpu_freq()                     # CPU频率

    # 内存信息
    mem = psutil.virtual_memory()
    mem.total                             # bytes 中的总计 RAM
    mem.available                         # 可用 RAM
    mem.percent                           # 使用百分比
    mem.used                              # 二手 RAM

    # 交换内存
    swap = psutil.swap_memory()
    swap.total, swap.used, swap.percent

    # 磁盘信息
    psutil.disk_partitions()              # List 分区
    usage = psutil.disk_usage('/')
    usage.total, usage.used, usage.percent

    # 网络信息
    psutil.net_io_counters()              # Bytes 发送/接收
    psutil.net_connections()              # 活跃连接数
    psutil.net_if_addrs()                 # 接口地址

    # Process信息
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        print(proc.info)

    # 当前process
    p = psutil.Process()
    p.pid
    p.name()
    p.cpu_percent()
    p.memory_info()
    p.num_threads()

    # 系统启动时间
    import datetime
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
