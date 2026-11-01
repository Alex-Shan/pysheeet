.. meta::
    :description lang=zh_CN: Python interpreter 中 GNU Debugger (GDB)
    :keywords: Python, Python3, GDB

================================================================================================================
GNU 调试器中的 Python 解释器（Python Interpreter in GNU Debugger）
================================================================================================================

:Date: 2025-08-30

摘要（Abstract）
------------------------

GNU Debugger (GDB) 是最强大的 debugging 工具，可供开发人员排除代​​码中的错误。然而，对于初学者来说很难学习，这就是为什么许多程序员更喜欢插入 ``print`` 来检查运行时状态。幸运的是， `GDB Text User Interface (TUI)`_ 为开发人员提供了一种同时查看源代码和调试的方法。更令人兴奋的是，在GDB 7中， **Python Interpreter** 被内置到GDB中。此功能提供了更直接的方法来通过 Python library 定制 GDB 打印机和命令。通过讨论示例，本文尝试通过 Python 探索先进的 debugging 技术，为 GDB 开发工具包。

介绍（Introduction）
--------------------------------

解决软件错误对开发人员来说是一个巨大的挑战。虽然GDB提供了许多“调试命令”来检查程序的运行状态，但其不直观的用法阻碍了程序员使用它来解决问题。确实，掌握GDB是一个长期的process。然而，快速启动并不复杂；你必须像尤达那样忘记你所学到的东西。为了更好地理解如何在GDB中使用Python，本文将重点讨论GDB中的Python interpreter。

定义命令（Define Commands）
------------------------------------------

GDB支持使用 ``define`` 自定义命令。同时运行一批命令来排除故障非常有用。例如，开发者可以通过定义 ``sf`` 命令来显示当前帧信息。

.. code-block:: bash

    # define in .gdbinit
    define sf
      where        # 找出程序在哪里
      info args    # 显示 arguments
      info locals  # 显示本地 variables
    end

然而，由于APIs的限制，编写用户自定义命令可能会很不方便。幸运的是，通过与GDB中的Python interpreter交互，开发人员可以利用Python libraries轻松建立他们的debugging工具包。以下部分介绍如何使用 Python 来简化 debugging processes。

转储内存（Dump Memory）
----------------------------------

检查process的内存信息是解决内存问题的有效方法。开发者可以通过 ``info proc mappings`` 和 ``dump memory`` 获取内存内容。为了简化这些步骤，定义自定义命令很有用。然而，使用纯 GDB 语法的实现并不简单。尽管GDB支持条件，但处理输出并不直观。为了解决这个问题，在 GDB 中使用 Python API 会很有帮助，因为 Python 包含许多处理 strings 的有用操作。

.. code-block:: python

    # mem.py
    import gdb
    import time
    import re

    class DumpMemory(gdb.Command):
        """Dump memory info into a file."""

        def __init__(self):
            super().__init__("dm", gdb.COMMAND_USER)

        def get_addr(self, p, tty):
            """Get memory addresses."""
            cmd = "info proc mappings"
            out = gdb.execute(cmd, tty, True)
            addrs = []
            for l in out.split("\n"):
                if re.match(f".*{p}*", l):
                    s, e, *_ = l.split()
                    addrs.append((s, e))
            return addrs

        def dump(self, addrs):
            """Dump memory result."""
            if not addrs:
                return

            for s, e in addrs:
                f = int(time.time() * 1000)
                gdb.execute(f"dump memory {f}.bin {s} {e}")

        def invoke(self, args, tty):
            try:
                # cat /proc/self/maps
                addrs = self.get_addr(args, tty)
                # 转储内存
                self.dump(addrs)
            except Exception as e:
                print("Usage: dm [pattern]")

    DumpMemory()


运行 ``dm`` 命令将调用 ``DumpMemory.invoke`` 。通过在 *.gdbinit* 中获取或实现 Python 脚本，开发人员可以利用用户定义的命令来跟踪程序运行时的错误。例如，以下步骤显示如何在 GDB 中调用 ``DumpMemory`` 。

.. code-block:: bash

    (gdb) start
    ...
    (gdb) source mem.py  # source commands
    (gdb) dm stack       # 将 stack 转储到 ${timestamp}.bin
    (gdb) shell ls       # ls current dir
    1577283091687.bin  a.cpp  a.out  mem.py

转储 JSON（Dump JSON）
------------------------------------

当开发人员在正在运行的程序中检查 JSON string 时，解析 JSON 非常有用。 GDB 可以通过 ``gdb.parse_and_eval`` 解析 ``std::string`` 并将其作为 ``gdb.Value`` 返回。通过处理 ``gdb.Value`` ，开发人员可以将 JSON string 传递给 Python ``json`` API 并以漂亮的格式打印。

.. code-block:: python

    # dj.py
    import gdb
    import re
    import json

    class DumpJson(gdb.Command):
        """Dump std::string as a styled JSON."""

        def __init__(self):
            super().__init__("dj", gdb.COMMAND_USER)

        def get_json(self, args):
            """Parse std::string to JSON string."""
            ret = gdb.parse_and_eval(args)
            typ = str(ret.type)
            if re.match("^std::.*::string", typ):
                return json.loads(str(ret))
            return None

        def invoke(self, args, tty):
            try:
                # string 至 json string
                s = self.get_json(args)
                # json string 至 object
                o = json.loads(s)
                print(json.dumps(o, indent=2))
            except Exception as e:
                print(f"Parse json error! {args}")

    DumpJson()

命令 ``dj`` 以 GDB 形式显示更易读的 JSON 格式。当 JSON string 较大时，此命令有助于提高视觉识别率。另外，通过该命令还可以检测或监控 ``std::string`` 是否为JSON。

.. code-block:: bash

    (gdb) start
    (gdb) list
    1       #include <string>
    2
    3       int main(int argc, char *argv[])
    4       {
    5           std::string json = R"({"foo": "FOO","bar": "BAR"})";
    6           return 0;
    7       }
    ...
    (gdb) ptype json
    type = std::string
    (gdb) p json
    $1 = "{\"foo\": \"FOO\",\"bar\": \"BAR\"}"
    (gdb) source dj.py
    (gdb) dj json
    {
      "foo": "FOO",
      "bar": "BAR"
    }

突出显示语法（Highlight Syntax）
------------------------------------------------

Syntax highlighting 对于开发人员跟踪源代码或解决问题很有用。通过使用 `Pygments`_ ，可以轻松地将颜色应用于源，而无需手动定义 ANSI escape 代码。以下示例显示如何将颜色应用于 ``list`` 命令输出。

.. code-block:: python

    import gdb

    from pygments import highlight
    from pygments.lexers import CLexer
    from pygments.formatters import TerminalFormatter

    class PrettyList(gdb.Command):
        """Print source code with color."""

        def __init__(self):
            super().__init__("pl", gdb.COMMAND_USER)
            self.lex = CLexer()
            self.fmt = TerminalFormatter()

        def invoke(self, args, tty):
            try:
                out = gdb.execute(f"l {args}", tty, True)
                print(highlight(out, self.lex, self.fmt))
            except Exception as e:
                print(e)

    PrettyList()

跟踪点（Tracepoints）
--------------------------------

虽然开发人员可以插入 ``printf`` 、 ``std::cout`` 或 ``syslog`` 来检查 functions，但当项目很大时，打印消息并不是一种有效的调试方法。开发人员可能会浪费时间构建源代码，并且可能获得很少的信息。更糟糕的是，输出可能会变得太大而无法检测到问题。事实上，检查 functions 或 variables 不需要在代码中嵌入*print functions*。通过使用 GDB API 编写 Python 脚本，开发人员可以自定义观察点以在运行时动态跟踪问题。例如，通过实现 ``gdb.Breakpoint`` 和 ``gdb.Command`` ，开发人员可以获取必要的信息，例如parameters、调用stacks或内存使用情况。

.. code-block:: python

    # tp.py
    import gdb

    tp = {}

    class Tracepoint(gdb.Breakpoint):
        def __init__(self, *args):
            super().__init__(*args)
            self.silent = True
            self.count = 0

        def stop(self):
            self.count += 1
            frame = gdb.newest_frame()
            block = frame.block()
            sym_and_line = frame.find_sal()
            framename = frame.name()
            filename = sym_and_line.symtab.filename
            line = sym_and_line.line
            # 显示跟踪点信息
            print(f"{framename} @ {filename}:{line}")
            # 显示参数和变量
            for s in block:
                if not s.is_argument and not s.is_variable:
                    continue
                typ = s.type
                val = s.value(frame)
                size = typ.sizeof
                name = s.name
                print(f"\t{name}({typ}: {val}) [{size}]")
            # 不要在跟踪点停止
            return False

    class SetTracepoint(gdb.Command):
        def __init__(self):
            super().__init__("tp", gdb.COMMAND_USER)

        def invoke(self, args, tty):
            try:
                global tp
                tp[args] = Tracepoint(args)
            except Exception as e:
                print(e)

    def finish(event):
        for t, p in tp.items():
            c = p.count
            print(f"Tracepoint '{t}' Count: {c}")

    gdb.events.exited.connect(finish)
    SetTracepoint()

无需在 functions 的开头插入 ``std::cout`` ，而是在 function 的入口点使用跟踪点可提供有用的信息来检查 arguments、variables 和 stacks。对于instance，通过在 ``fib`` 处设置跟踪点，有助于检查内存使用情况、stack和调用次数。

.. code-block:: cpp

    int fib(int n)
    {
        if (n < 2) {
            return 1;
        }
        return fib(n-1) + fib(n-2);
    }

    int main(int argc, char *argv[])
    {
        fib(3);
        return 0;
    }

以下输出显示了 function ``fib`` 的检查结果。在这种情况下，跟踪点显示开发人员需要的所有信息，包括 arguments' value、recursive 流量和 variables' 大小。与 ``std::cout`` 相比，通过使用tracepoint，开发人员可以获得更多有用的信息。

.. code-block:: bash

    (gdb) source tp.py
    (gdb) tp main
    Breakpoint 1 at 0x647: file a.cpp, line 12.
    (gdb) tp fib
    Breakpoint 2 at 0x606: file a.cpp, line 3.
    (gdb) r
    Starting program: /root/a.out
    main @ a.cpp:12
            argc(int: 1) [4]
            argv(char **: 0x7fffffffe788) [8]
    fib @ a.cpp:3
            n(int: 3) [4]
    fib @ a.cpp:3
            n(int: 2) [4]
    fib @ a.cpp:3
            n(int: 1) [4]
    fib @ a.cpp:3
            n(int: 0) [4]
    fib @ a.cpp:3
            n(int: 1) [4]
    [Inferior 1 (process 5409) exited normally]
    Tracepoint 'main' Count: 1
    Tracepoint 'fib' Count: 5

分析（Profiling）
--------------------------

在不插入时间戳的情况下，profiling 通过跟踪点仍然可行。通过在 ``gdb.Breakpoint`` 、GDB、sets之后使用 ``gdb.FinishBreakpoint`` ，在帧的返回地址处使用临时breakpoint，以便开发人员获取当前时间戳并计算时间差。请注意，通过 GDB 的 profiling 并不精确。其他工具（例如 `Linux perf`_ 或 `Valgrind`_ ）提供更有用和更准确的信息来跟踪性能问题。

.. code-block:: python

    import gdb
    import time

    class EndPoint(gdb.FinishBreakpoint):
        def __init__(self, breakpoint, *a, **kw):
            super().__init__(*a, **kw)
            self.silent = True
            self.breakpoint = breakpoint

        def stop(self):
            # 正常完成
            end = time.time()
            start, out = self.breakpoint.stack.pop()
            diff = end - start
            print(out.strip())
            print(f"\tCost: {diff}")
            return False

    class StartPoint(gdb.Breakpoint):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.silent = True
            self.stack = []

        def stop(self):
            start = time.time()
            # 开始、结束、差异
            frame = gdb.newest_frame()
            sym_and_line = frame.find_sal()
            func = frame.function().name
            filename = sym_and_line.symtab.filename
            line = sym_and_line.line
            block = frame.block()

            args = []
            for s in block:
                if not s.is_argument:
                    continue
                name = s.name
                typ = s.type
                val = s.value(frame)
                args.append(f"{name}: {val} [{typ}]")

            # 格式
            out = ""
            out += f"{func} @ {filename}:{line}\n"
            for a in args:
                out += f"\t{a}\n"

            # 将当前状态附加到 breakpoint stack
            self.stack.append((start, out))
            EndPoint(self, internal=True)
            return False

    class Profile(gdb.Command):
        def __init__(self):
            super().__init__("prof", gdb.COMMAND_USER)

        def invoke(self, args, tty):
            try:
                StartPoint(args)
            except Exception as e:
                print(e)

    Profile()


以下输出通过在 function ``fib`` 处设置跟踪点显示 profiling 结果。方便同时检查function和stack的性能。

.. code-block:: bash

    (gdb) source prof.py
    (gdb) prof fib
    Breakpoint 1 at 0x606: file a.cpp, line 3.
    (gdb) r
    Starting program: /root/a.out
    fib(int) @ a.cpp:3
            n: 1 [int]
            Cost: 0.0007786750793457031
    fib(int) @ a.cpp:3
            n: 0 [int]
            Cost: 0.002572298049926758
    fib(int) @ a.cpp:3
            n: 2 [int]
            Cost: 0.008517265319824219
    fib(int) @ a.cpp:3
            n: 1 [int]
            Cost: 0.0014069080352783203
    fib(int) @ a.cpp:3
            n: 3 [int]
            Cost: 0.01870584487915039

格式化输出（Pretty Print）
--------------------------------------

尽管 GDB 中的 ``set print pretty on`` 提供了更好的格式来检查 variables，但开发人员可能需要解析 variables' value 以提高可读性。以系统调用 ``stat`` 为例。虽然它提供了检查文件 attributes 的有用信息，但输出 values（例如权限）对于 debugging 可能无法读取。通过实现用户定义的漂亮打印，开发人员可以解析 ``struct stat`` 并以可读格式输出信息。

.. code-block:: python

    import gdb
    import pwd
    import grp
    import stat
    import time

    from datetime import datetime


    class StatPrint:
        def __init__(self, val):
            self.val = val

        def get_filetype(self, st_mode):
            if stat.S_ISDIR(st_mode):
                return "directory"
            if stat.S_ISCHR(st_mode):
                return "character device"
            if stat.S_ISBLK(st_mode):
                return "block device"
            if stat.S_ISREG:
                return "regular file"
            if stat.S_ISFIFO(st_mode):
                return "FIFO"
            if stat.S_ISLNK(st_mode):
                return "symbolic link"
            if stat.S_ISSOCK(st_mode):
                return "socket"
            return "unknown"

        def get_access(self, st_mode):
            out = "-"
            info = ("r", "w", "x")
            perm = [
                (stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR),
                (stat.S_IRGRP, stat.S_IRWXG, stat.S_IXGRP),
                (stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH),
            ]
            for pm in perm:
                for c, p in zip(pm, info):
                    out += p if st_mode & c else "-"
            return out

        def get_time(self, st_time):
            tv_sec = int(st_time["tv_sec"])
            return datetime.fromtimestamp(tv_sec).isoformat()

        def to_string(self):
            st = self.val
            st_ino = int(st["st_ino"])
            st_mode = int(st["st_mode"])
            st_uid = int(st["st_uid"])
            st_gid = int(st["st_gid"])
            st_size = int(st["st_size"])
            st_blksize = int(st["st_blksize"])
            st_blocks = int(st["st_blocks"])
            st_atim = st["st_atim"]
            st_mtim = st["st_mtim"]
            st_ctim = st["st_ctim"]

            out = "{\n"
            out += f"Size: {st_size}\n"
            out += f"Blocks: {st_blocks}\n"
            out += f"IO Block: {st_blksize}\n"
            out += f"Inode: {st_ino}\n"
            out += f"Access: {self.get_access(st_mode)}\n"
            out += f"File Type: {self.get_filetype(st_mode)}\n"
            out += f"Uid: ({st_uid}/{pwd.getpwuid(st_uid).pw_name})\n"
            out += f"Gid: ({st_gid}/{grp.getgrgid(st_gid).gr_name})\n"
            out += f"Access: {self.get_time(st_atim)}\n"
            out += f"Modify: {self.get_time(st_mtim)}\n"
            out += f"Change: {self.get_time(st_ctim)}\n"
            out += "}"
            return out

    p = gdb.printing.RegexpCollectionPrettyPrinter("sp")
    p.add_printer("stat", "^stat$", StatPrint)

    o = gdb.current_objfile()
    gdb.printing.register_pretty_printer(o, p)

通过获取之前的 Python 脚本， ``PrettyPrinter`` 可以识别 ``struct stat`` 并输出可读格式，供开发人员检查文件 attributes。无需插入functions来解析和打印 ``struct stat`` ，这是从Python API获得更好输出的更方便的方法。

.. code-block:: bash

    (gdb) list 15
    10          struct stat st;
    11
    12          if ((rc = stat("./a.cpp", &st)) < 0) {
    13              perror("stat failed.");
    14              goto end;
    15          }
    16
    17          rc = 0;
    18       end:
    19          return rc;
    (gdb) source st.py
    (gdb) b 17
    Breakpoint 1 at 0x762: file a.cpp, line 17.
    (gdb) r
    Starting program: /root/a.out

    Breakpoint 1, main (argc=1, argv=0x7fffffffe788) at a.cpp:17
    17          rc = 0;
    (gdb) p st
    $1 = {
    Size: 298
    Blocks: 8
    IO Block: 4096
    Inode: 1322071
    Access: -rw-rw-r--
    File Type: regular file
    Uid: (0/root)
    Gid: (0/root)
    Access: 2019-12-28T15:53:17
    Modify: 2019-12-28T15:53:01
    Change: 2019-12-28T15:53:01
    }

请注意，开发人员可以通过命令 ``disable`` 禁用用户定义的漂亮打印。例如，前面的 Python 脚本在全局漂亮打印机下注册了一个漂亮打印机。通过调用 ``disable pretty-print`` ，打印机 ``sp`` 将被禁用。

.. code-block:: bash

    (gdb) disable pretty-print global sp
    1 printer disabled
    1 of 2 printers enabled
    (gdb) i pretty-print
    global pretty-printers:
      builtin
        mpx_bound128
      sp [disabled]
        stat

此外，如果不再需要打印机，开发人员可以将其排除在当前 GDB debugging 会话中。以下代码片段显示了如何通过 ``gdb.pretty_printers.remove`` 删除 ``sp`` 打印机。

.. code-block:: bash

    (gdb) python
    >import gdb
    >for p in gdb.pretty_printers:
    >    if p.name == "sp":
    >        gdb.pretty_printers.remove(p)
    >end
    (gdb) i pretty-print
    global pretty-printers:
      builtin
        mpx_bound128

结论（Conclusion）
----------------------------

将 Python interpreter 集成到 GDB 中提供了许多灵活的方法来解决问题。虽然许多集成开发环境 (IDE) 可能嵌入 GDB 进行可视化调试，但 GDB 允许开发人员在运行时实现其命令并解析 variables 的输出。通过使用debugging脚本，开发人员无需修改代码即可监控和记录必要的信息。老实说，插入或启用 debugging 代码块可能会改变程序的行为，开发人员应该改掉这个坏习惯。此外，当问题重现时，GDB 可以附加该 process 并检查其状态，而无需停止它。显然，如果出现具有挑战性的问题，debugging 经由 GDB 是不可避免的。由于将 Python 集成到 GDB 中，开发故障排除脚本变得更加容易，从而使开发人员能够以不同的方式建立他们的 debugging methods。


参考资料（Reference）
------------------------------

1. `Extending GDB using Python`_
2. `gcc/gcc/gdbhooks.py`_
3. `gdbinit/Gdbinit`_
4. `cyrus-and/gdb-dashboard`_
5. `hugsy/gef`_
6. `sharkdp/stack-inspector`_
7. `gdb Debugging Full Example (Tutorial)`_

.. _Pygments: https://pygments.org/
.. _Extending GDB using Python: https://sourceware.org/gdb/onlinedocs/gdb/Python.html
.. _gcc/gcc/gdbhooks.py: https://github.com/gcc-mirror/gcc/blob/master/gcc/gdbhooks.py
.. _hugsy/gef: https://github.com/hugsy/gef
.. _cyrus-and/gdb-dashboard: https://github.com/cyrus-and/gdb-dashboard
.. _gdbinit/Gdbinit: https://github.com/gdbinit/Gdbinit
.. _sharkdp/stack-inspector: https://github.com/sharkdp/stack-inspector
.. _GDB Text User Interface (TUI): https://sourceware.org/gdb/onlinedocs/gdb/TUI.html
.. _Linux perf: https://github.com/torvalds/linux/tree/master/tools/perf
.. _Valgrind: https://valgrind.org/
.. _gdb Debugging Full Example (Tutorial): http://www.brendangregg.com/blog/2016-08-09/gdb-example-ncurses.html
