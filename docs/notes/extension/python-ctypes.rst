.. meta::
    :description lang=zh_CN: Python ctypes 教程，用于加载共享 libraries、调用 C functions、处理指针、结构和错误处理
    :keywords: Python, ctypes, shared library, .so, .dylib, .dll, C library, FFI, foreign function interface, pointers, structures

==================================
ctypes 接口（ctypes）
==================================

:Source: `src/basic/cext_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/cext_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

ctypes是Python的内置外部function接口（FFI）library，允许在共享libraries上调用functions（.so在Linux上，.dylib在macOS上，.dll在Windows）无需编写任何C代码或编译扩展。它非常适合快速原型设计、访问系统 libraries 或在您不需要编译步骤时包装现有的 C libraries。但是，ctypes 需要手动 type 声明和仔细的内存管理，这使得它比 cffi 或 pybind11 等 complex 用例的替代方案更容易出错。

加载共享库（Loading Shared Libraries）
--------------------------------------------------------------

ctypes 为共享 libraries 提供特定于平台的加载器。使用 ``CDLL`` 进行标准 C 调用约定，或在 Windows 上使用 ``WinDLL`` 进行 stdcall 约定。 library 搜索遵循系统约定： ``LD_LIBRARY_PATH`` 位于 Linux、 ``DYLD_LIBRARY_PATH`` 位于 macOS 以及 ``PATH`` 位于 Windows。

.. code-block:: python

    import platform
    from ctypes import CDLL

    # 加载平台特定的C library
    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib")
    elif platform.system() == "Linux":
        libc = CDLL("libc.so.6")
    else:
        from ctypes import windll
        libc = windll.msvcrt

    # 调用 printf
    libc.printf(b"Hello from C: %d\n", 42)

加载自定义库（Loading Custom Libraries）
----------------------------------------------------------------

对于您自己编译的 C libraries，请提供完整路径或确保 library 位于系统的 library 搜索路径中。 ``use_errno=True`` parameter 支持正确的 errno 处理以进行错误检测。

.. code-block:: python

    from ctypes import CDLL
    from ctypes.util import find_library
    import os

    # 从当前目录加载
    lib_path = os.path.join(os.path.dirname(__file__), "libfoo.so")
    lib = CDLL(lib_path, use_errno=True)

    # 或对系统 libraries 使用 find_library
    libm_path = find_library("m")  # 查找 libm.so 或 libm.dylib
    if libm_path:
        libm = CDLL(libm_path)

基本类型映射（Basic Type Mapping）
----------------------------------------------------

ctypes 为 C types 提供 Python 等效项。始终显式声明 argument types ( ``argtypes`` ) 并返回 types ( ``restype`` ) 以避免崩溃并确保正确的数据转换。如果没有这些声明，ctypes 假定所有 arguments 和 return values 都是 C ``int`` 。

.. code-block:: python

    import platform
    from ctypes import CDLL, c_double, c_char_p

    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib")
    else:
        libc = CDLL("libc.so.6")

    # Declare function signature: double atof(const char *)
    libc.atof.argtypes = [c_char_p]
    libc.atof.restype = c_double

    result = libc.atof(b"3.14159")
    print(result)  # 3.14159

    # 常见的type映射：
    # c_int -> int
    # c_long -> 长
    # c_double -> 双
    # c_char_p -> char*（Python 中的 bytes）
    # c_void_p -> 无效*
    # c_bool -> _Bool

调用strlen和abs（Calling strlen and abs）
------------------------------------------------------------------------

使用正确的 type 声明调用标准 C library functions 的简单示例。

.. code-block:: python

    import platform
    from ctypes import CDLL, c_char_p, c_size_t

    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib")
    else:
        libc = CDLL("libc.so.6")

    # 斯特伦
    libc.strlen.argtypes = [c_char_p]
    libc.strlen.restype = c_size_t
    assert libc.strlen(b"hello") == 5

    # abs（默认int types工作）
    assert libc.abs(-42) == 42

从 libm 调用 sqrt（Calling sqrt from libm）
----------------------------------------------------------------------------

.. code-block:: python

    import platform
    from ctypes import CDLL, c_double

    if platform.system() == "Darwin":
        libm = CDLL("libm.dylib")
    else:
        libm = CDLL("libm.so.6")

    libm.sqrt.argtypes = [c_double]
    libm.sqrt.restype = c_double

    result = libm.sqrt(16.0)
    assert abs(result - 4.0) < 1e-10

调用 C 函数（Calling C Functions）
--------------------------------------------------------

此示例显示了完整的工作流程：编译 C library，使用 ctypes 加载它，并使用正确的 type 声明调用 functions。斐波那契 function 演示了从 Python 调用的 C 代码的性能优势。

**C源（fib.c）：**

.. code-block:: c

    // 编译：
    //   Linux：gcc -共享-fPIC -o libfib.so fib.c
    //   macOS：clang -共享-fPIC -o libfib.dylib fib.c

    unsigned long fib(unsigned long n) {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }

**Python用法：**

.. code-block:: python

    import platform
    from ctypes import CDLL, c_ulong

    # 加载library
    if platform.system() == "Darwin":
        lib = CDLL("./libfib.dylib")
    else:
        lib = CDLL("./libfib.so")

    # 声明types
    lib.fib.argtypes = [c_ulong]
    lib.fib.restype = c_ulong

    # 拨打function
    print(lib.fib(35))  # 9227465

**性能对比：**

.. code-block:: python

    >>> from time import time
    >>> def py_fib(n):
    ...     if n < 2: return n
    ...     return py_fib(n - 1) + py_fib(n - 2)
    ...
    >>> s = time(); _ = py_fib(35); e = time(); e - s
    4.918856859207153
    >>> s = time(); _ = lib.fib(35); e = time(); e - s
    0.07283687591552734

指针与 byref（Pointers and byref）
----------------------------------------------------------

使用 ``byref()`` 通过引用传递 arguments（如 C 中的 ``&var`` ）和 ``POINTER()`` 创建指针 types。当您只需要传递对 function 的引用时， ``byref()`` 比 ``pointer()`` 更高效。

.. code-block:: python

    from ctypes import c_int, byref, pointer, POINTER

    # 指向 integer 的指针
    value = c_int(42)
    ptr = pointer(value)
    assert ptr.contents.value == 42

    # 通过指针修改
    ptr.contents.value = 100
    assert value.value == 100

    # byref 创建一个轻量级指针用于传递给 C functions
    ref = byref(value)

    # 创建指针type和array
    IntPtr = POINTER(c_int)
    arr = (c_int * 3)(1, 2, 3)

结构（Structures）
----------------------------

通过子类化 ``Structure`` 并指定 ``_fields_`` 来定义 C 结构。字段顺序必须与 C 结构体完全匹配。如果需要，使用 ``_pack_`` 来控制 alignment（e.g.、 ``_pack_ = 1`` 用于打包结构）。

.. code-block:: python

    import ctypes
    import math

    class Point(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_double),
            ("y", ctypes.c_double),
        ]

    # 创建和使用
    p = Point(3.0, 4.0)
    assert p.x == 3.0
    assert p.y == 4.0

    # 计算距离
    distance = math.sqrt(p.x ** 2 + p.y ** 2)
    assert abs(distance - 5.0) < 1e-10

嵌套结构（Nested Structures）
----------------------------------------------

.. code-block:: python

    import ctypes

    class Point(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_double),
            ("y", ctypes.c_double),
        ]

    class Rectangle(ctypes.Structure):
        _fields_ = [
            ("top_left", Point),
            ("bottom_right", Point),
        ]

    rect = Rectangle(Point(0, 10), Point(10, 0))
    assert rect.top_left.x == 0
    assert rect.top_left.y == 10
    assert rect.bottom_right.x == 10

数组（Arrays）
--------------------

使用乘法语法 ``type * size`` 创建 C arrays。 Arrays 可以使用 values 进行初始化，并像 Python lists 一样进行访问。当传递给 C functions 时，它们会自动转换为指针。

.. code-block:: python

    from ctypes import c_int, c_double, c_char

    # Integer array
    IntArray5 = c_int * 5
    arr = IntArray5(1, 2, 3, 4, 5)
    assert arr[0] == 1
    assert arr[4] == 5

    # 修改elements
    arr[0] = 100
    assert list(arr) == [100, 2, 3, 4, 5]

    # 字符 array (C string buffer)
    buf = (c_char * 256)()
    buf.value = b"Hello"
    assert buf.value == b"Hello"

    # 双 array 用于数值工作
    data = (c_double * 3)(1.1, 2.2, 3.3)
    assert abs(sum(data) - 6.6) < 1e-10

结构体中的数组（Array in Structure）
------------------------------------------------------

结构可以包含固定大小的 arrays 作为成员。

.. code-block:: python

    import ctypes

    class Data(ctypes.Structure):
        _fields_ = [
            ("values", ctypes.c_int * 5),
            ("count", ctypes.c_int)
        ]

    d = Data()
    d.count = 5
    for i in range(5):
        d.values[i] = i * 10

    assert list(d.values) == [0, 10, 20, 30, 40]
    assert d.count == 5

使用 cffi（Using cffi）
--------------------------------------

cffi 是 ctypes 的更干净的替代品，具有更好的 PyPy 兼容性。它使用类似 C 的声明而不是 Python type objects。

.. code-block:: python

    import platform
    from cffi import FFI

    ffi = FFI()
    ffi.cdef("""
        int abs(int x);
        size_t strlen(const char *s);
        double sqrt(double x);
    """)

    if platform.system() == "Darwin":
        libc = ffi.dlopen("libc.dylib")
        libm = ffi.dlopen("libm.dylib")
    else:
        libc = ffi.dlopen("libc.so.6")
        libm = ffi.dlopen("libm.so.6")

    assert libc.abs(-42) == 42
    assert libc.strlen(b"hello") == 5
    assert abs(libm.sqrt(16.0) - 4.0) < 1e-10

错误处理（Error Handling）
----------------------------------------

当调用 C functions 失败时出现 set errno 时，在加载 library 和 ``get_errno()`` 时使用 ``use_errno=True`` 检索错误代码。这对于系统调用的正确错误处理至关重要。

.. code-block:: python

    import os
    import platform
    from ctypes import CDLL, get_errno

    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib", use_errno=True)
    else:
        libc = CDLL("libc.so.6", use_errno=True)

    # 尝试打开一个不存在的文件
    fd = libc.open(b"/nonexistent/path", 0)
    if fd == -1:
        errno = get_errno()
        errmsg = f"open failed: {os.strerror(errno)}"
        print(errmsg)  # 打开失败：没有这样的文件或目录

回调（Callbacks）
--------------------------

ctypes 可以使用 ``CFUNCTYPE`` 从 Python functions 创建 C 可调用的 function 指针。这对于接受 callback functions 的 C libraries 很有用，例如 ``qsort()`` 或事件处理程序。

.. code-block:: python

    import platform
    from ctypes import CDLL, CFUNCTYPE, POINTER, c_int, c_void_p, cast, sizeof

    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib")
    else:
        libc = CDLL("libc.so.6")

    # Define callback type: int (*compare)(const void*, const void*)
    CMPFUNC = CFUNCTYPE(c_int, c_void_p, c_void_p)

    def py_compare(a, b):
        """Compare function for qsort"""
        a_val = cast(a, POINTER(c_int)).contents.value
        b_val = cast(b, POINTER(c_int)).contents.value
        return a_val - b_val

    # 从 Python function 创建 C callback
    c_compare = CMPFUNC(py_compare)

    # 与 qsort 一起使用
    arr = (c_int * 5)(5, 2, 8, 1, 9)
    libc.qsort(arr, len(arr), sizeof(c_int), c_compare)
    print(list(arr))  # [1, 2, 5, 8, 9]

字符串处理（String Handling）
--------------------------------------------

C strings 需要在 ctypes 中小心处理。使用 ``c_char_p`` 表示 immutable strings，使用 ``create_string_buffer()`` 表示 mutable buffers。当传递到 C functions 时，始终使用 bytes ( ``b"string"`` ) 而不是 str。

.. code-block:: python

    import platform
    from ctypes import CDLL, c_char_p, c_int, create_string_buffer

    if platform.system() == "Darwin":
        libc = CDLL("libc.dylib")
    else:
        libc = CDLL("libc.so.6")

    # Immutable string (c_char_p)
    libc.puts.argtypes = [c_char_p]
    libc.puts(b"Hello, World!")

    # Mutable buffer 为修改 strings 的 functions
    buf = create_string_buffer(100)
    libc.strcpy(buf, b"Hello")
    libc.strcat(buf, b", World!")
    print(buf.value)  # b“你好，世界！”

    # 获取string长度
    libc.strlen.argtypes = [c_char_p]
    libc.strlen.restype = c_int
    print(libc.strlen(b"Hello"))  # 5
