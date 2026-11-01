.. meta::
    :description lang=zh_CN: 现代 Python C/C++ 扩展的综合指南，涵盖 pybind11、ctypes、cffi 和 Cython，以及构建高性能 Python、modules、NumPy 集成、GIL 管理、和 class 绑定
    :keywords: Python, Python3, pybind11, C Extension, C++, ctypes, cffi, Cython, NumPy, Performance, GIL, Native Code, PyTorch, TensorFlow, SciPy, shared library

========================================================================
现代 C/C++ 扩展（Modern C/C++ Extensions）
========================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

与编译语言相比，Python 的灵活性和易用性是以性能为代价的。当您需要最大速度进行数值计算、实时处理、系统接口或包装现有的 C/C++ libraries 时，本机扩展可以弥补 Python 的生产力和 C/C++ 的性能之间的差距。本指南涵盖了构建 Python 扩展的现代方法： **pybind11**（C++ 项目的推荐选择）、**ctypes/cffi**（用于在不编译的情况下调用 C libraries）以及**Cython** （用于编译为 C 的类似 Python 的语法）。我们使用相同的斐波那契 benchmark 来比较每种方法，以帮助您为您的特定用例选择正确的工具。

.. note::

    对于大多数 C++ 项目，建议选择 **pybind11** 。它被 PyTorch、TensorFlow 等主要机器学习框架和 SciPy 等科学计算 libraries 使用。 pybind11 提供干净的 C++11 语法、Python 和 C++ types 之间的自动 type 转换、出色的 NumPy 数值计算集成以及跨语言边界的无缝 exception 处理。

方法比较（Comparison of Approaches）
------------------------------------------------------------

::

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    C/C++ EXTENSION APPROACHES                           │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  APPROACH      │ PROS                      │ CONS                       │
    ├────────────────┼───────────────────────────┼────────────────────────────┤
    │  pybind11      │ Clean C++11 syntax        │ Requires C++ compiler      │
    │  (recommended) │ Automatic type conversion │ Compile step needed        │
    │                │ NumPy support built-in    │ C++ only (not C)           │
    │                │ Used by PyTorch, SciPy    │                            │
    ├────────────────┼───────────────────────────┼────────────────────────────┤
    │  ctypes        │ No compilation needed     │ Manual type declarations   │
    │                │ Standard library          │ Error-prone                │
    │                │ Works with any C library  │ No C++ support             │
    ├────────────────┼───────────────────────────┼────────────────────────────┤
    │  cffi          │ No compilation needed     │ Extra dependency           │
    │                │ Cleaner than ctypes       │ No C++ support             │
    │                │ PyPy compatible           │                            │
    ├────────────────┼───────────────────────────┼────────────────────────────┤
    │  Cython        │ Python-like syntax        │ New language to learn      │
    │                │ Gradual optimization      │ Build complexity           │
    │                │ Good NumPy integration    │ Debugging harder           │
    ├────────────────┼───────────────────────────┼────────────────────────────┤
    │  Python C API  │ Maximum control           │ Very verbose               │
    │  (legacy)      │ No dependencies           │ Manual refcounting         │
    │                │                           │ Error-prone                │
    └────────────────┴───────────────────────────┴────────────────────────────┘

    When to use what:
    - Wrapping existing C++ library → pybind11
    - Wrapping existing C library  → ctypes or cffi
    - Writing new high-perf code   → pybind11 or Cython
    - Need PyPy compatibility      → cffi or Cython
    - Quick prototype              → ctypes

pybind11：入门（pybind11: Getting Started）
----------------------------------------------------------------------------

:Source: `src/cext/example.cpp <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/example.cpp>`_

pybind11 是一个轻量级的仅标头 C++ library，它为现有 C++ 代码创建 Python 绑定。与传统的 Python C API 不同，pybind11 使用现代 C++11 功能（例如可变参数模板和 lambda expressions）来提供干净、直观的语法。 ``pip install pybind11`` 的安装非常简单，只需要兼容 C++11 的 compiler（GCC 4.8+、Clang 3.3+、MSVC 2015+）。 ``PYBIND11_MODULE`` 宏定义了module入口点， ``m.def()`` 将C++ functions绑定到Python，并自动将type转换为常见的types，如int， float、string 和 STL 容器。

**简单function绑定：**

.. code-block:: cpp

    // example.cpp
    #include <pybind11/pybind11.h>

    int add(int a, int b) {
        return a + b;
    }

    // 斐波那契性能比较
    unsigned long fib(unsigned long n) {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }

    PYBIND11_MODULE(example, m) {
        m.doc() = "Example pybind11 module";
        m.def("add", &add, "Add two integers",
              pybind11::arg("a"), pybind11::arg("b"));
        m.def("fib", &fib, "Compute Fibonacci number");
    }

**使用setup.py构建：**

.. code-block:: python

    # setup.py
    from pybind11.setup_helpers import Pybind11Extension, build_ext
    from setuptools import setup

    ext_modules = [
        Pybind11Extension(
            "example",
            ["example.cpp"],
        ),
    ]

    setup(
        name="example",
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
    )

.. code-block:: bash

    $ pip install pybind11
    $ python setup.py build_ext --inplace
    $ python -c "import example; print(example.add(1, 2))"
    3
    $ python -c "import example; print(example.fib(35))"
    9227465

pybind11：类（pybind11: Classes）
----------------------------------------------------------

:Source: `src/cext/vector.cpp <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/vector.cpp>`_

pybind11 使用 ``py::class_`` 模板将 C++ classes 直接绑定到 Python。您可以使用 ``def(py::init<...>())`` 公开构造函数，使用 ``def_readwrite()`` 或 ``def_readonly()`` 公开成员 variables，以及使用 ``def()`` 公开 methods。 Python special methods 与 ``__repr__`` 、 ``__add__`` 、 ``__eq__`` 一样按名称绑定，为 C++ objects 启用自然的 Python 语法。 Default argument values 通过 ``py::arg()`` 支持，您可以添加文档字符串来改善 Python help() 体验。

.. code-block:: cpp

    // vector.cpp
    #include <pybind11/pybind11.h>
    #include <cmath>

    namespace py = pybind11;

    class Vector2D {
    public:
        double x, y;

        Vector2D(double x = 0, double y = 0) : x(x), y(y) {}

        double length() const {
            return std::sqrt(x * x + y * y);
        }

        Vector2D operator+(const Vector2D& other) const {
            return Vector2D(x + other.x, y + other.y);
        }

        std::string repr() const {
            return "Vector2D(" + std::to_string(x) + ", " + std::to_string(y) + ")";
        }
    };

    PYBIND11_MODULE(vector, m) {
        py::class_<Vector2D>(m, "Vector2D")
            .def(py::init<double, double>(),
                 py::arg("x") = 0, py::arg("y") = 0)
            .def_readwrite("x", &Vector2D::x)
            .def_readwrite("y", &Vector2D::y)
            .def("length", &Vector2D::length)
            .def("__add__", &Vector2D::operator+)
            .def("__repr__", &Vector2D::repr);
    }

.. code-block:: python

    >>> from vector import Vector2D
    >>> v1 = Vector2D(3, 4)
    >>> v1.length()
    5.0
    >>> v2 = Vector2D(1, 2)
    >>> v3 = v1 + v2
    >>> v3
    Vector2D(4.0, 6.0)

pybind11：NumPy 集成（pybind11: NumPy Integration）
--------------------------------------------------------------------------------------------

:Source: `src/cext/numpy_example.cpp <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/numpy_example.cpp>`_

pybind11通过 ``pybind11/numpy.h`` 头提供第一个class NumPy支持，无需数据复制即可实现高性能数值计算。 ``py::array_t<T>`` 模板将 NumPy arrays 与 type 安全性封装在一起， ``unchecked<N>()`` 为性能关键的内部 loops 提供快速、无边界检查的访问。可以使用 ``mutable_unchecked<N>()`` 就地修改 Arrays，或者可以创建并返回新的 arrays。这种零复制方法对于科学计算至关重要，因为复制大型数据集的成本很高。

.. code-block:: cpp

    // numpy_example.cpp
    #include <pybind11/pybind11.h>
    #include <pybind11/numpy.h>

    namespace py = pybind11;

    // Element 方向乘法（就地修改）
    void multiply_inplace(py::array_t<double> arr, double factor) {
        auto buf = arr.mutable_unchecked<1>();
        for (py::ssize_t i = 0; i < buf.shape(0); i++) {
            buf(i) *= factor;
        }
    }

    // 返回新的 array
    py::array_t<double> add_arrays(py::array_t<double> a, py::array_t<double> b) {
        auto buf_a = a.unchecked<1>();
        auto buf_b = b.unchecked<1>();

        if (buf_a.shape(0) != buf_b.shape(0)) {
            throw std::runtime_error("Arrays must have same length");
        }

        auto result = py::array_t<double>(buf_a.shape(0));
        auto buf_r = result.mutable_unchecked<1>();

        for (py::ssize_t i = 0; i < buf_a.shape(0); i++) {
            buf_r(i) = buf_a(i) + buf_b(i);
        }
        return result;
    }

    PYBIND11_MODULE(numpy_example, m) {
        m.def("multiply_inplace", &multiply_inplace);
        m.def("add_arrays", &add_arrays);
    }

.. code-block:: python

    >>> import numpy as np
    >>> from numpy_example import multiply_inplace, add_arrays
    >>> arr = np.array([1.0, 2.0, 3.0])
    >>> multiply_inplace(arr, 2.0)
    >>> arr
    array([2., 4., 6.])
    >>> a = np.array([1.0, 2.0, 3.0])
    >>> b = np.array([4.0, 5.0, 6.0])
    >>> add_arrays(a, b)
    array([5., 7., 9.])

pybind11：释放 GIL（pybind11: Releasing the GIL）
----------------------------------------------------------------------------------------

:Source: `src/cext/gil_example.cpp <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/gil_example.cpp>`_

Python 的全局 Interpreter Lock (GIL) 阻止 true 在 threads 上并行执行 Python 代码。对于 CPU 密集型 C++ 操作或阻塞不需要 Python objects 的 I/O，释放 GIL 允许其他 Python threads 并发运行。 pybind11 为 RAII 式的 GIL 管理提供 ``py::gil_scoped_release`` ——GIL 在创建 object 时释放，在 scope 退出时自动重新获取。此模式对于多线程应用程序至关重要，其中 C++ 代码执行繁重的计算，而 Python threads 处理其他任务，例如 UI 更新或网络 I/O。

.. code-block:: cpp

    #include <pybind11/pybind11.h>
    #include <thread>
    #include <chrono>

    namespace py = pybind11;

    // 释放GIL的缓慢操作
    void slow_operation(int seconds) {
        // 在执行 CPU 工作时释放 GIL
        py::gil_scoped_release release;

        // 模拟慢速工作
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
    }

    // CPU 密集型工作
    unsigned long fib_nogil(unsigned long n) {
        py::gil_scoped_release release;

        std::function<unsigned long(unsigned long)> fib_impl;
        fib_impl = [&](unsigned long n) -> unsigned long {
            if (n < 2) return n;
            return fib_impl(n - 1) + fib_impl(n - 2);
        };
        return fib_impl(n);
    }

    PYBIND11_MODULE(gil_example, m) {
        m.def("slow_operation", &slow_operation);
        m.def("fib_nogil", &fib_nogil);
    }

.. code-block:: python

    import threading
    from datetime import datetime
    from gil_example import slow_operation

    def worker(n):
        print(f"{datetime.now()}: Thread {n} starting")
        slow_operation(1)
        print(f"{datetime.now()}: Thread {n} done")

    # Threads 并行运行，因为 GIL 已发布
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()

ctypes：快速 C 库访问（ctypes: Quick C Library Access）
----------------------------------------------------------------------------------------------

:Source: `src/cext/fib.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/fib.c>`_

ctypes 是 Python 的内置外部 function 接口 (FFI)，可让您从共享 libraries（.so、.dylib、.dll）调用 C functions，而无需编写任何 C 包装器代码或编译 Python 扩展。它非常适合快速原型设计、访问系统 libraries 或在不需要构建步骤时包装现有 C 代码。 key 要求使用 ``argtypes`` 和 ``restype`` 声明 function 签名 - 如果没有这些声明，ctypes 会假定所有 arguments 和 return values 都是 C ``int`` ，这会导致静默错误或与其他 types 发生崩溃，例如 ``double`` 或指针。

.. code-block:: c

    // fib.c - 编译：gcc -shared -fPIC -o libfib.so fib.c
    unsigned long fib(unsigned long n) {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }

    double add_doubles(double a, double b) {
        return a + b;
    }

.. code-block:: python

    import ctypes
    from ctypes import c_ulong, c_double

    # 负载共享 library
    # Linux：libfib.so，macOS：libfib.dylib，Windows：fib.dll
    lib = ctypes.CDLL("./libfib.so")

    # 声明 function 签名（对于非 int types 很重要！）
    lib.fib.argtypes = [c_ulong]
    lib.fib.restype = c_ulong

    lib.add_doubles.argtypes = [c_double, c_double]
    lib.add_doubles.restype = c_double

    # 拨打 functions
    print(lib.fib(35))        # 9227465
    print(lib.add_doubles(1.5, 2.5))  # 4.0

ctypes：结构体和指针（ctypes: Structures and Pointers）
--------------------------------------------------------------------------------------------

在 ctype 中使用 C 结构和指针需要仔细的 type 声明，以准确反映 C 内存布局。通过子类化 ``Structure`` 并将 ``_fields_`` 指定为 (name, type) tuples 的 list 来定义结构，顺序与 C 结构体相同。使用 ``POINTER(Type)`` 创建指针types和 ``byref(obj)`` 通过引用传递objects（相当于C中的 ``&obj`` ）。这种方法比 pybind11 更容易出错，但无需任何编译步骤即可工作。

.. code-block:: c

    // point.c
    typedef struct {
        double x;
        double y;
    } Point;

    double distance(Point* p1, Point* p2) {
        double dx = p2->x - p1->x;
        double dy = p2->y - p1->y;
        return sqrt(dx*dx + dy*dy);
    }

    void scale_point(Point* p, double factor) {
        p->x *= factor;
        p->y *= factor;
    }

.. code-block:: python

    import ctypes
    from ctypes import Structure, c_double, POINTER, byref
    import math

    class Point(Structure):
        _fields_ = [("x", c_double), ("y", c_double)]

    lib = ctypes.CDLL("./libpoint.so")

    lib.distance.argtypes = [POINTER(Point), POINTER(Point)]
    lib.distance.restype = c_double

    lib.scale_point.argtypes = [POINTER(Point), c_double]
    lib.scale_point.restype = None

    # 创建点
    p1 = Point(0, 0)
    p2 = Point(3, 4)

    # 通过引用传递
    dist = lib.distance(byref(p1), byref(p2))
    print(f"Distance: {dist}")  # 5.0

    # 就地修改
    lib.scale_point(byref(p2), 2.0)
    print(f"Scaled: ({p2.x}, {p2.y})")  # (6.0, 8.0)

cffi：更干净的外部函数接口（cffi: Cleaner Foreign Function Interface）
------------------------------------------------------------------------------------------------------------------

cffi（C 外部 Function 接口）提供了比 ctypes 更干净、更 Pythonic API 的调用 C 代码。您可以使用 ``ffi.cdef()`` 中的实际 C 语法而不是 Python type objects 来声明 C function 签名，通常可以直接从头文件中复制。 cffi 自动处理 type 转换并提供更好的错误消息。它也是 PyPy 推荐的 FFI，它的运行速度明显快于 ctypes。使用 ``pip install cffi`` 安装。

.. code-block:: python

    from cffi import FFI

    ffi = FFI()

    # 声明 C functions（从头文件复制）
    ffi.cdef("""
        unsigned long fib(unsigned long n);
        double add_doubles(double a, double b);
    """)

    # 加载library
    lib = ffi.dlopen("./libfib.so")

    # 拨打 functions - types 是自动的！
    print(lib.fib(35))              # 9227465
    print(lib.add_doubles(1.5, 2.5))  # 4.0

**cffi 带有内联 C 代码（ABI 模式）：**

.. code-block:: python

    from cffi import FFI

    ffi = FFI()
    ffi.cdef("unsigned long fib(unsigned long n);")

    # 内联编译 C 代码
    ffi.set_source("_fib_cffi", """
        unsigned long fib(unsigned long n) {
            if (n < 2) return n;
            return fib(n - 1) + fib(n - 2);
        }
    """)

    ffi.compile()

    # 现在导入并使用
    from _fib_cffi import lib
    print(lib.fib(35))

Cython：类似 Python 的语法（Cython: Python-like Syntax）
------------------------------------------------------------------------------------------------

Cython 是一种将 Python 语法与 C data types 相结合的编程语言，编译为高效的 C 代码。它非常适合逐步优化：从纯 Python 代码开始，然后将 type 声明添加到关键部分以实现显着的加速。 Cython 支持三个级别的优化：纯 Python ( ``def`` )、类型化 Python（ ``def`` 与 type hints）和纯 C functions ( ``cdef`` )。 ``cdef`` functions 以 C 速度运行，但只能从其他 Cython 代码调用，因此您通常用 ``def`` function 包装它们以进行 Python 访问。使用 ``pip install cython`` 安装。

.. code-block:: cython

    # fib.pyx
    def fib_py(n):
        """Pure Python - slow"""
        if n < 2:
            return n
        return fib_py(n - 1) + fib_py(n - 2)

    def fib_typed(long n):
        """With type hints - faster"""
        if n < 2:
            return n
        return fib_typed(n - 1) + fib_typed(n - 2)

    cdef unsigned long _fib_c(unsigned long n):
        """C function - fastest"""
        if n < 2:
            return n
        return _fib_c(n - 1) + _fib_c(n - 2)

    def fib_c(unsigned long n):
        """Python wrapper for C function"""
        return _fib_c(n)

.. code-block:: python

    # setup.py
    from setuptools import setup
    from Cython.Build import cythonize

    setup(
        ext_modules=cythonize("fib.pyx"),
    )

.. code-block:: bash

    $ python setup.py build_ext --inplace
    $ python -c "from fib import fib_c; print(fib_c(35))"
    9227465

性能比较（Performance Comparison）
--------------------------------------------------------

了解每种方法的性能特征有助于您选择正确的工具。此 benchmark 比较了使用 recursive 斐波那契 (n=35) 的所有方法，这是一个 CPU 绑定任务，突出显示了 Python 的 interpreter 的开销。通过消除 Python object 创建、method 调度和字节码解释，本机代码实现了 50-100 倍的加速。实际加速因工作负载而异，集成 NumPy 的数字代码可以获得更大的增益，而 I/O 绑定的代码受益较小。

.. code-block:: python

    from time import time

    def benchmark(func, n=35, runs=3):
        times = []
        for _ in range(runs):
            start = time()
            result = func(n)
            times.append(time() - start)
        return min(times), result

    # 纯正Python
    def fib_python(n):
        if n < 2: return n
        return fib_python(n - 1) + fib_python(n - 2)

    # 结果（近似值，因系统而异）：
    #
    # |方法|时间|加速|
    # |-------------------|----------|---------|
    # |纯Python | 2.50 | 1x |
    # | Cython（打字）| 0.08 | 31x |
    # | Cython (cdef) | 0.05 | 50 倍 |
    # | ctypes | 0.05 | 50 倍 |
    # | cffi | 0.05 | 50 倍 |
    # | pybind11 | 0.04 | 62x |
    # | pybind11（无 GIL）| 0.04 | 62x |

最佳实践（Best Practices）
----------------------------------------

遵循这些指南将帮助您编写高效、可维护且安全的本机扩展。最常见的错误是在长时间操作期间持有GIL（阻塞其他threads），不必要地复制大arrays（杀死性能），以及忽略错误处理（导致崩溃而不是Python exceptions）。

**Do：**

- 使用 pybind11 进行新的 C++ 绑定
- 发布GIL，用于CPU密集型操作
- 使用 NumPy arrays 作为数值数据（使用 pybind11 进行零复制）
- 在 ctypes/cffi 中声明 types（避免无声错误）
- 优化前的分析——找到真正的瓶颈

**不：**

- 为新项目编写Python C API代码（使用pybind11）
- 在阻塞 I/O 或长时间计算期间按住 GIL
- 在 Python 和 C 之间复制大 arrays（使用视图）
- 忽略 C 代码中的错误处理
- 过早优化 - Python 通常足够快

**错误处理：**

.. code-block:: cpp

    // pybind11 - exceptions 自动转换为 Python
    double divide(double a, double b) {
        if (b == 0) {
            throw std::runtime_error("Division by zero");
        }
        return a / b;
    }

    // In Python: raises RuntimeError

**内存管理：**

.. code-block:: cpp

    // pybind11 自动处理 Python object 重新计数
    // 对于原始指针，使用 return value 策略：

    py::class_<Parent>(m, "Parent")
        .def("get_child", &Parent::get_child,
             py::return_value_policy::reference_internal);  // Child tied to Parent lifetime
