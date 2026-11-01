.. meta::
    :description lang=zh_CN: Python 文件 I/O 教程涵盖读取、写入、二进制文件、pathlib、context managers、文件模式、临时文件和高效文件处理模式
    :keywords: Python, Python3, file, I/O, read, write, binary, text, pathlib, Path, context manager, open, with statement, encoding, shutil, tempfile, glob

============================================
文件和 I/O（Files and I/O）
============================================

:Source: `src/basic/fileio_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/fileio_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

Python通过几个内置的modules为文件操作和文件系统操作提供全面的支持。 ``open()`` function 是读写文件的基础，通过可配置的 encoding 支持文本和二进制模式。 ``pathlib`` module (Python 3.4+) 提供了一个现代化的、面向 object 的路径操作界面，可在不同操作系统中一致工作。对于复制目录树或跨文件系统移动文件等高级操作， ``shutil`` module 提供了方便的 functions。 ``tempfile`` module 通过自动清理来处理临时文件和目录的创建，这对于安全处理中间数据至关重要。这些 modules 几乎涵盖了从简单文本处理到 complex 文件系统操作的所有文件 I/O 需求。

读取文件（Reading Files）
--------------------------------------

``open()`` function 返回支持多次读取 methods 的文件 object。始终使用 ``with`` statement (context manager) 以确保即使发生 exception 也能正确关闭文件。 ``read()`` method 将整个文件加载到内存中，同时迭代文件 object processes 一次一行，这对于大文件来说更节省内存。始终显式指定 ``encoding="utf-8"`` 以避免平台相关行为。

.. code-block:: python

    # 将整个文件读取为 string
    with open("example.txt", encoding="utf-8") as f:
        content = f.read()

    # 将所有行读取为 list
    with open("example.txt", encoding="utf-8") as f:
        lines = f.readlines()

    # 逐行迭代（节省内存）
    with open("example.txt", encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())

    # 读取特定数量的字符
    with open("example.txt", encoding="utf-8") as f:
        first_100 = f.read(100)

    # 读取单行
    with open("example.txt", encoding="utf-8") as f:
        first_line = f.readline()

写入文件（Writing Files）
--------------------------------------

Python提供了多种写入文件的模式。模式 ``"w"`` 创建一个新文件或截断现有文件， ``"a"`` 追加到末尾而不截断， ``"x"`` 独占创建（如果文件已存在，则提高 ``FileExistsError`` ）。 ``write()`` method 写入单个 string，而 ``writelines()`` 写入 strings 的 iterable。请注意，method 都不会自动添加换行符 — 您必须在 strings 中包含 ``\n`` 。您还可以使用 ``file`` parameter 将 ``print()`` 输出重定向到文件。

.. code-block:: python

    # 将 string 写入文件（覆盖）
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write("Hello, World!\n")

    # 写入多行
    lines = ["line 1\n", "line 2\n", "line 3\n"]
    with open("output.txt", "w", encoding="utf-8") as f:
        f.writelines(lines)

    # 附加到文件
    with open("output.txt", "a", encoding="utf-8") as f:
        f.write("Appended line\n")

    # 创建新文件（如果存在则失败）
    with open("new_file.txt", "x", encoding="utf-8") as f:
        f.write("New content")

    # 打印到文件
    with open("output.txt", "w", encoding="utf-8") as f:
        print("Hello", "World", sep=", ", file=f)

二进制文件（Binary Files）
--------------------------------------

二进制模式（ ``"rb"`` 、 ``"wb"`` ）读取和写入原始 bytes，无需任何 encoding 或换行符转换。这对于图像、PDF、可执行文件等非文本文件或任何 byte 级精度很重要的文件至关重要。二进制数据在Python中表示为 ``bytes`` objects。处理大型二进制文件时，请分块读取，以避免一次将整个文件加载到内存中。

.. code-block:: python

    # 读取二进制文件
    with open("image.png", "rb") as f:
        data = f.read()
    print(type(data))  # <class 'bytes'>

    # 写入二进制文件
    with open("copy.png", "wb") as f:
        f.write(data)

    # 分块读取二进制文件
    chunk_size = 8192
    with open("large_file.bin", "rb") as f:
        while chunk := f.read(chunk_size):
            process(chunk)

文件模式（File Modes）
--------------------------------

``open()`` function 接受控制文件打开方式的模式 string。该模式将访问 type（读、写、追加）与内容 type（文本或二进制）相结合。文本模式执行 encoding/decoding 和换行符翻译，而二进制模式则使用原始 bytes。 ``+`` 修饰符允许在同一文件句柄上进行读取和写入。

常见的文件模式：

- ``"r"`` - 读取文本（默认）
- ``"w"`` - 写入文本（截断）
- ``"a"`` - 附加文本
- ``"x"`` - 独占创建（如果存在则失败）
- ``"rb"`` - 读取二进制
- ``"wb"`` - 写入二进制文件
- ``"r+"`` - 读写
- ``"w+"`` - 写入和读取（截断）

分块读取文件（Reading File in Chunks）
------------------------------------------------------------

当处理大于可用内存的文件时，分块读取可以防止内存耗尽。生成块的 generator function 内存效率高，并且适用于流处理。海象 operator ( ``:=`` ) 提供了一种干净的读取方式，直到文件耗尽。带有哨兵 value 的 ``iter()`` function 为基于块的读取提供了另一种模式。

.. code-block:: python

    def read_chunks(filepath, chunk_size=8192):
        """Read file in chunks."""
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    # Process 大文件
    for chunk in read_chunks("large_file.bin"):
        process(chunk)

    # 将 iter 与哨兵结合使用
    with open("file.txt", encoding="utf-8") as f:
        for chunk in iter(lambda: f.read(1024), ""):
            print(chunk, end="")

pathlib 基础（pathlib Basics）
----------------------------------------------------

``pathlib`` module（在 Python 3.4 中引入）提供了面向 object 的文件系统路径方法。与基于 string 的路径操作不同， ``Path`` objects 自动处理平台差异（Unix 上的正斜杠，Windows 上的反斜杠）。 ``/`` operator 直观地连接路径组件，而 methods 与 ``resolve()`` 一样将相对路径转换为绝对路径。 ``Path`` objects 是在现代 Python 中使用文件系统路径的推荐方法。

.. code-block:: python

    from pathlib import Path

    # 创建路径 objects
    p = Path("folder/file.txt")
    p = Path.home() / "Documents" / "file.txt"

    # 当前目录和主目录
    cwd = Path.cwd()
    home = Path.home()

    # 绝对路径
    abs_path = Path("file.txt").resolve()

路径属性（Path Properties）
------------------------------------------

``Path`` objects 公开各种 properties 以提取路径的组件。 ``name`` property 返回最终组件， ``stem`` 返回不带后缀的名称， ``suffix`` 返回包括点的文件扩展名。 ``parent`` property 返回包含路径的目录， ``parts`` 返回所有路径组件的 tuple。 Methods 与 ``with_suffix()`` 和 ``with_name()`` 一样，使用修改后的组件创建新路径，而不影响原始路径。

.. code-block:: python

    from pathlib import Path

    p = Path("/home/user/documents/report.pdf")

    print(p.name)      # report.pdf
    print(p.stem)      # 报告
    print(p.suffix)    # .pdf
    print(p.parent)    # /home/用户/文档
    print(p.parts)     # （'/'、'home'、'user'、'documents'、'report.pdf'）
    print(p.anchor)    # /

    # 多个后缀
    p2 = Path("archive.tar.gz")
    print(p2.suffixes)  # ['.tar'、'.gz']

    # 更改后缀
    p3 = p.with_suffix(".txt")
    print(p3)  # /home/用户/文档/report.txt

    # 更改姓名
    p4 = p.with_name("summary.pdf")
    print(p4)  # /home/用户/文档/summary.pdf

路径操作（Path Operations）
------------------------------------------

``Path`` objects 提供 methods 检查文件存在性和 type、检索文件元数据并执行读/写操作。 ``exists()`` 、 ``is_file()`` 和 ``is_dir()`` methods 测试路径状态，而不提高 exceptions。 ``stat()`` method 返回详细的文件信息，包括大小和修改时间。对于简单的文件操作， ``read_text()`` 、 ``write_text()`` 、 ``read_bytes()`` 和 ``write_bytes()`` 提供了 ``open()`` context manager 模式的便捷单行替代方案。

.. code-block:: python

    from pathlib import Path

    p = Path("example.txt")

    # 检查是否存在和 type
    p.exists()      # True/False
    p.is_file()     # True 如果是常规文件
    p.is_dir()      # True 如果目录
    p.is_symlink()  # True 如果是符号链接

    # 文件统计
    stat = p.stat()
    print(stat.st_size)   # 文件大小（bytes）
    print(stat.st_mtime)  # 修改时间

    # 使用pathlib读写
    content = p.read_text(encoding="utf-8")
    p.write_text("New content", encoding="utf-8")

    # 二进制读/写
    data = p.read_bytes()
    p.write_bytes(b"binary data")

列出目录（Listing Directories）
--------------------------------------------------

Python 提供了多种获取 list 目录内容的方法，每种方法都有不同的权衡。 ``pathlib`` method ``iterdir()`` 返回 ``Path`` objects 的 iterator，允许您检查文件 types 并直接访问 properties。 ``os.scandir()`` function 非常高效，因为它可以在目录 iteration 期间检索文件 type 信息，而无需额外的系统调用。更简单的 ``os.listdir()`` 仅返回文件名，如 strings，需要额外的调用来获取文件信息。

.. code-block:: python

    from pathlib import Path
    import os

    # pathlib - 迭代目录
    p = Path(".")
    for item in p.iterdir():
        print(item.name, "dir" if item.is_dir() else "file")

    # pathlib - 全局模式
    for py_file in Path(".").glob("*.py"):
        print(py_file)

    # Recursive 全局
    for py_file in Path(".").rglob("*.py"):
        print(py_file)

    # os.scandir（高效，返回DirEntry）
    with os.scandir(".") as entries:
        for entry in entries:
            print(entry.name, entry.is_file())

    # os.listdir（简单list）
    files = os.listdir(".")

Glob 匹配模式（Glob Patterns）
------------------------------------------------

Glob 模式提供了类似 shell 的语法来匹配多个文件。 ``*`` 通配符匹配除路径分隔符之外的任何字符， ``?`` 匹配单个字符， ``**`` 递归匹配任意数量的目录。 ``pathlib`` methods ``glob()`` 和 ``rglob()`` （recursive glob）返回匹配 ``Path`` objects 的 iterators。请注意， ``pathlib`` glob 不支持像 ``{py,txt}`` 那样的大括号扩展 — 使用多个 glob 调用或对 complex 模式使用 ``glob`` module。

.. code-block:: python

    from pathlib import Path

    # 当前目录中的所有 Python 文件
    list(Path(".").glob("*.py"))

    # 递归所有 Python 文件
    list(Path(".").rglob("*.py"))

    # 多种扩展
    list(Path(".").glob("*.{py,txt}"))  # 行不通
    # 改用：
    py_files = list(Path(".").glob("*.py"))
    txt_files = list(Path(".").glob("*.txt"))

    # 单字符通配符
    list(Path(".").glob("file?.txt"))  # file1.txt、file2.txt

    # 使用 glob module
    import glob
    glob.glob("**/*.py", recursive=True)

创建目录（Creating Directories）
----------------------------------------------------

使用 ``pathlib`` 和 ``os`` 创建目录都很简单。 ``mkdir()`` method 创建单个目录，如果 ``FileExistsError`` 已存在，则提升该目录。 ``parents=True`` parameter 创建所有中间目录（如 Unix 中的 ``mkdir -p`` ），如果该目录已存在， ``exist_ok=True`` 会抑制错误。这些选项一起使目录创建具有幂等性并且可以安全地并发执行。

.. code-block:: python

    from pathlib import Path
    import os

    # pathlib - 创建目录
    Path("new_dir").mkdir()

    # 与父母一起创建（如 mkdir -p）
    Path("path/to/nested/dir").mkdir(parents=True, exist_ok=True)

    # os.makedirs
    os.makedirs("path/to/dir", exist_ok=True)

shutil 高层文件操作（shutil - High-Level File Operations）
----------------------------------------------------------------------------------------------------

``shutil`` module 提供复制、移动和删除文件和目录树的高级操作。

**复制文件：**

.. code-block:: python

    import shutil

    # 复制文件（仅内容）
    shutil.copy("source.txt", "dest.txt")

    # 复制文件保留元数据（时间戳、权限）
    shutil.copy2("source.txt", "dest.txt")

    # 复制到目录（保留原始文件名）
    shutil.copy("file.txt", "backup/")  # -> 备份/file.txt

    # 将文件 object 复制到文件 object
    with open("src.txt", "rb") as src, open("dst.txt", "wb") as dst:
        shutil.copyfileobj(src, dst)

    # 仅复制文件内容（无元数据）
    shutil.copyfile("source.txt", "dest.txt")

**复制目录树：**

.. code-block:: python

    import shutil

    # 复制整个目录树
    shutil.copytree("source_dir", "dest_dir")

    # 使用忽略模式进行复制
    shutil.copytree(
        "source",
        "dest",
        ignore=shutil.ignore_patterns("*.pyc", "__pycache__", ".git")
    )

    # 复制到现有目录（Python 3.8+）
    shutil.copytree("source", "existing_dest", dirs_exist_ok=True)

    # 自定义忽略function
    def ignore_large_files(directory, files):
        """Ignore files larger than 1MB."""
        ignored = []
        for f in files:
            path = os.path.join(directory, f)
            if os.path.isfile(path) and os.path.getsize(path) > 1_000_000:
                ignored.append(f)
        return ignored

    shutil.copytree("source", "dest", ignore=ignore_large_files)

    # 复制并保留符号链接
    shutil.copytree("source", "dest", symlinks=True)

**移动文件和目录：**

.. code-block:: python

    import shutil
    from pathlib import Path

    # 移动文件（跨文件系统工作）
    shutil.move("old_name.txt", "new_name.txt")

    # 将文件移动到目录
    shutil.move("file.txt", "archive/")  # -> 存档/file.txt

    # 移动整个目录
    shutil.move("old_dir", "new_dir")

    # pathlib 重命名（仅限相同文件系统）
    Path("old.txt").rename("new.txt")

    # pathlib 替换（覆盖目标）
    Path("source.txt").replace("dest.txt")

**删除文件和目录：**

.. code-block:: python

    import shutil
    from pathlib import Path

    # 删除整个目录树
    shutil.rmtree("dir_with_contents")

    # 使用错误处理程序删除
    def on_error(func, path, exc_info):
        print(f"Error deleting {path}: {exc_info[1]}")

    shutil.rmtree("dir", onerror=on_error)

    # 删除忽略错误
    shutil.rmtree("dir", ignore_errors=True)

    # 删除文件
    Path("file.txt").unlink()
    Path("file.txt").unlink(missing_ok=True)  # 如果缺失也不会报错

    # 删除空目录
    Path("empty_dir").rmdir()

**磁盘用途：**

.. code-block:: python

    import shutil

    # 获取磁盘使用统计信息
    usage = shutil.disk_usage("/")
    print(f"Total: {usage.total // (1024**3)} GB")
    print(f"Used: {usage.used // (1024**3)} GB")
    print(f"Free: {usage.free // (1024**3)} GB")

**查找可执行文件：**

.. code-block:: python

    import shutil

    # 在 PATH 中查找可执行文件
    python_path = shutil.which("python")
    print(python_path)  # /usr/bin/python

    # 如果未找到则返回 None
    result = shutil.which("nonexistent")
    print(result)  # None

**归档：**

.. code-block:: python

    import shutil

    # 创建存档（zip、tar、gztar、bztar、xztar）
    shutil.make_archive("backup", "zip", "source_dir")  # -> backup.zip
    shutil.make_archive("backup", "gztar", "source_dir")  # -> backup.tar.gz

    # 提取存档
    shutil.unpack_archive("backup.zip", "extract_dir")
    shutil.unpack_archive("backup.tar.gz", "extract_dir")

    # List 支持的格式
    print(shutil.get_archive_formats())
    print(shutil.get_unpack_formats())

临时文件（Temporary Files）
------------------------------------------

``tempfile`` module 以安全的方式创建具有唯一名称的临时文件和目录。 ``NamedTemporaryFile`` 创建一个关闭时自动删除的文件（除非 ``delete=False`` ）。 ``suffix`` parameter 添加了文件扩展名，当其他程序需要识别文件 type 时很有用。 ``TemporaryDirectory`` 创建一个目录，当 context manager 退出时，该目录会递归删除，非常适合测试夹具或中间处理。这些functions默认使用系统的临时目录，您可以使用 ``gettempdir()`` 进行查询。

.. code-block:: python

    import tempfile
    from pathlib import Path

    # 临时文件（关闭时自动删除）
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True) as f:
        f.write("temporary content")
        print(f.name)  # /tmp/tmpXXXXXX.txt

    # 持续存在的临时文件
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        temp_path = f.name
        f.write("persistent temp")
    # 稍后手动清理
    Path(temp_path).unlink()

    # 临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / "file.txt"
        temp_file.write_text("content")
        # 退出上下文时删除目录

    # 获取临时目录路径
    print(tempfile.gettempdir())  # /tmp

符号链接（Symbolic Links）
----------------------------------------

符号链接（symlink）是指向另一个文件或目录的特殊文件。它们对于创建快捷方式、管理多个版本或组织文件而不重复非常有用。 ``symlink_to()`` method 创建指向指定目标的符号链接。 ``is_symlink()`` method 检查路径是否是符号链接， ``readlink()`` 返回目标路径。 ``resolve()`` method 遵循所有符号链接以返回规范的绝对路径。

.. code-block:: python

    from pathlib import Path
    import os

    # 使用pathlib创建符号链接
    Path("link_name").symlink_to("target_file")

    # 使用 os 创建符号链接
    os.symlink("target", "link")

    # 读取符号链接目标
    target = Path("link_name").readlink()
    target = os.readlink("link")

    # 检查是否有符号链接
    Path("link_name").is_symlink()

    # 将符号链接解析为真实路径
    real_path = Path("link_name").resolve()

文件权限（File Permissions）
--------------------------------------------

类Unix系统使用权限bits来控制文件访问。 ``stat()`` method 返回包括权限模式的文件元数据。 ``chmod()`` method 使用八进制表示法（e.g.、 ``0o644`` 所有者读/写、组/其他只读）或组合 ``stat`` module constants 来修改权限。 ``os.access()`` function 检查当前 process 是否对文件具有特定权限，这对于尝试操作之前的飞行前检查很有用。

.. code-block:: python

    from pathlib import Path
    import os
    import stat

    p = Path("script.sh")

    # 获取权限
    mode = p.stat().st_mode
    print(oct(mode))  # 0o100644

    # 使可执行
    p.chmod(p.stat().st_mode | stat.S_IXUSR)

    # Set 特定权限（所有者 rw、组 r、其他 r）
    p.chmod(0o644)

    # 检查是否可读/可写
    os.access("file.txt", os.R_OK)  # 可读
    os.access("file.txt", os.W_OK)  # 可写
    os.access("file.txt", os.X_OK)  # 可执行文件

使用 CSV 文件（Working with CSV Files）
------------------------------------------------------------------

CSV（逗号分隔的 Values）是表格数据交换的通用格式。 Python 的 ``csv`` module 处理 CSV 解析的复杂性，包括带引号的字段、不同的分隔符和适当的转义。 ``writer`` object 将行写入为 lists，而 ``DictWriter`` 使用列标题将 dictionaries 写入为 keys。同样， ``reader`` 生成的行为 lists， ``DictReader`` 生成的行为 dictionaries。始终使用 ``newline=""`` 打开 CSV 文件，以使 csv module 跨平台正确处理行结尾。

.. code-block:: python

    import csv

    # 写入CSV
    with open("data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age", "city"])
        writer.writerow(["Alice", 30, "NYC"])
        writer.writerows([["Bob", 25, "LA"], ["Carol", 35, "Chicago"]])

    # 读取 CSV
    with open("data.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            print(row)

    # 词典阅读器/词典编写器
    with open("data.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row["name"], row["age"])

使用 JSON 文件（Working with JSON Files）
----------------------------------------------------------------------

JSON（JavaScript Object 表示法）是 Web APIs 和配置文件中数据交换的标准格式。 Python 的 ``json`` module 将 Python objects（dicts、lists、strings、数字、booleans、None）序列化为JSON strings 并将 JSON 反序列化回 Python objects。 ``dump()`` 和 ``load()`` functions 直接使用文件 objects，而 ``dumps()`` 和 ``loads()`` 则使用 strings。 ``indent`` parameter 生成人类可读的格式化输出。

.. code-block:: python

    import json
    from pathlib import Path

    data = {"name": "Alice", "scores": [95, 87, 92]}

    # 写入JSON
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 读取 JSON
    with open("data.json", encoding="utf-8") as f:
        loaded = json.load(f)

    # 路径库简写
    Path("data.json").write_text(json.dumps(data, indent=2))
    loaded = json.loads(Path("data.json").read_text())

压缩文件（Compressed Files）
--------------------------------------------

Python通过专用modules支持多种压缩格式。 ``gzip`` module 处理 gzip 压缩，通常用于日志文件和 Web 内容。对于文本使用 ``"rt"`` 和 ``"wt"`` 模式，对于二进制使用 ``"rb"`` 和 ``"wb"`` 模式。 ``zipfile`` module 创建并提取 ZIP 存档，支持单个存档中的多个文件。 ``writestr()`` method 直接从 strings 添加内容，无需创建临时文件。两者 modules 都与 Python 的文件处理模式无缝集成。

.. code-block:: python

    import gzip
    import zipfile
    from pathlib import Path

    # 写入gzip文件
    with gzip.open("file.txt.gz", "wt", encoding="utf-8") as f:
        f.write("compressed content")

    # 读取gzip文件
    with gzip.open("file.txt.gz", "rt", encoding="utf-8") as f:
        content = f.read()

    # 创建 zip 存档
    with zipfile.ZipFile("archive.zip", "w") as zf:
        zf.write("file1.txt")
        zf.write("file2.txt")
        zf.writestr("new.txt", "content from string")

    # 提取 zip 存档
    with zipfile.ZipFile("archive.zip", "r") as zf:
        zf.extractall("output_dir")
        # 提取单个文件
        zf.extract("file1.txt", "output_dir")

    # List zip 内容
    with zipfile.ZipFile("archive.zip", "r") as zf:
        print(zf.namelist())

文件锁定（File Locking）
------------------------------------

文件锁定可防止多个 processes 访问同一文件时数据损坏。在 Unix 系统上， ``fcntl.flock()`` 提供咨询锁定 — processes 必须配合检查 locks。 ``LOCK_EX`` 请求独占 lock 进行写入，而 ``LOCK_SH`` 允许共享读取访问。 ``LOCK_NB`` 标志使调用非阻塞，如果 lock 不立即可用，则引发 ``BlockingIOError`` 。始终在 ``finally`` 块中释放 locks，以防止 deadlocks。请注意，Windows 使用不同的锁定机制 ( ``msvcrt`` )。

.. code-block:: python

    import fcntl
    import time

    # 独家 lock (Unix)
    with open("data.txt", "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write("exclusive write")
            time.sleep(1)  # 模拟工作
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # 非阻塞 lock 尝试
    with open("data.txt", "w") as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            f.write("got lock")
        except BlockingIOError:
            print("File is locked by another process")

观察文件变化（inotify）（Watching File Changes (inotify)）
------------------------------------------------------------------------------------------------

Linux inotify API 提供高效的文件系统事件监控，无需轮询。应用程序可以监视目录中的文件创建、删除、修改和其他事件。这对于自动重新加载配置文件、触发源更改构建或同步目录非常有用。下面的例子演示了通过 ``ctypes`` 直接进行inotify访问；对于生产用途，请考虑提供跨平台抽象的 ``watchdog`` library。

.. code-block:: python

    import ctypes
    import os
    import struct
    import selectors
    from ctypes.util import find_library
    from pathlib import Path

    # inotify constants
    IN_CREATE = 0x00000100
    IN_DELETE = 0x00000200
    IN_MODIFY = 0x00000002

    libc = ctypes.CDLL(find_library("c"))

    class Inotify:
        def __init__(self, path, mask=IN_CREATE | IN_DELETE | IN_MODIFY):
            self.path = path
            self.mask = mask
            self.fd = None
            self.wd = None

        def __enter__(self):
            self.fd = libc.inotify_init()
            path_bytes = str(self.path).encode("utf-8")
            self.wd = libc.inotify_add_watch(self.fd, path_bytes, self.mask)
            return self

        def __exit__(self, *args):
            libc.inotify_rm_watch(self.fd, self.wd)
            os.close(self.fd)

        def read_events(self):
            data = os.read(self.fd, 4096)
            offset = 0
            while offset < len(data):
                wd, mask, cookie, length = struct.unpack_from("iIII", data, offset)
                offset += 16
                name = data[offset:offset + length].rstrip(b"\0").decode("utf-8")
                offset += length
                yield mask, name

    # 用法
    with Inotify(Path("/tmp")) as inotify:
        for mask, filename in inotify.read_events():
            print(f"Event {mask}: {filename}")
