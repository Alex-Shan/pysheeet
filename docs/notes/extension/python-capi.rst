.. meta::
    :description lang=zh_CN: 全面的 Python C API 教程，涵盖本机 C 扩展开发、module 创建、argument 解析、reference counting、GIL 管理、exception 处理和 Python type 操作，包括lists、dictionaries、tuples、sets 和 strings
    :keywords: Python, C API, C Extension, PyObject, reference counting, GIL, module, CPython, native extension, PyList, PyDict, PyTuple, PySet, PyUnicode, memory management

==========================================================
Python C API 用法（Python C API）
==========================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Python C API 是为 CPython 编写本机扩展的传统且最强大的方法。它提供对 Python 内部结构的直接访问，使开发人员能够完全控制内存管理、object 创建和 interpreter 交互。虽然比 pybind11 或 cffi 等现代替代方案更冗长，但 C API 对于维护遗留扩展、了解 Python 内部工作原理、实现性能关键代码路径或访问高级工具未公开的低级功能仍然至关重要。 C API 也是构建 Cython 和 pybind11 等工具的基础。

.. warning::

    C 扩展接口特定于 CPython，可能不适用于 PyPy、Jython 或 GraalPython 等替代 Python 实现。此外，API 可以在 Python 版本之间（特别是在 Python 2 和 Python 3 之间）进行更改，需要仔细的版本处理和条件编译以实现兼容性。

简单setup.py（Simple setup.py）
------------------------------------------------------

构建 C 扩展需要一个 ``setup.py`` 文件，该文件告诉 Python 如何编译 C 代码。 ``distutils`` module（或其现代替代品 ``setuptools`` ）处理跨平台编译，链接到 Python library，并生成正确的共享 library 格式（Linux 上的 .so、macOS 上的 .dylib、 Windows 上的 .pyd）。这个最小的示例将单个 C 文件编译为 Python 可导入的 module。

.. code-block:: python

    from distutils.core import setup, Extension

    ext = Extension('foo', sources=['foo.c'])
    setup(name="Foo", version="1.0", ext_modules=[ext])

构建并安装：

.. code-block:: bash

    $ python setup.py build
    $ python setup.py install

定制CFLAGS（Customize CFLAGS）
----------------------------------------------------

对于生产质量的扩展，您需要自定义 compiler 标志以启用警告、优化或 debugging 符号。 ``extra_compile_args`` parameter 将标志直接传递给 C compiler（gcc、clang 或 MSVC）。常见标志包括用于全面警告的 ``-Wall`` 和 ``-Wextra`` 、用于将警告视为错误的 ``-Werror`` 、用于积极优化的 ``-O3`` 以及用于调试符号的 ``-g`` 。

.. code-block:: python

    import sysconfig
    from distutils.core import setup, Extension

    cflags = sysconfig.get_config_var("CFLAGS")
    extra_compile_args = cflags.split()
    extra_compile_args += ["-Wextra", "-Wall", "-Werror"]

    ext = Extension(
        "foo", ["foo.c"],
        extra_compile_args=extra_compile_args
    )

    setup(name="foo", version="1.0", ext_modules=[ext])

简单的 C 扩展（Simple C Extension）
--------------------------------------------------------

:Source: `src/cext/capi/simple.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/simple.c>`_

每个 Python C 扩展都遵循包含三个基本组件的标准结构：描述 module 名称的 module 定义 ( ``PyModuleDef`` ) 和 methods、映射 Python 的 method 表 ( ``PyMethodDef`` ) function 命名为 C functions，以及 Python 在导入 module 时调用的初始化 function ( ``PyInit_<modulename>`` )。 ``PyDoc_STRVAR`` 宏创建出现在 Python 的 ``help()`` 系统中的文档字符串。此示例演示了最小的工作扩展。

**foo.c:**

.. code-block:: c

    #include <Python.h>

    PyDoc_STRVAR(doc_mod, "Module document\n");
    PyDoc_STRVAR(doc_foo, "foo() -> None\n\nPrint 'foo' to stdout.");

    static PyObject* foo(PyObject* self)
    {
        PyObject* s = PyUnicode_FromString("foo");
        PyObject_Print(s, stdout, 0);
        Py_DECREF(s);
        Py_RETURN_NONE;
    }

    static PyMethodDef methods[] = {
        {"foo", (PyCFunction)foo, METH_NOARGS, doc_foo},
        {NULL, NULL, 0, NULL}
    };

    static struct PyModuleDef module = {
        PyModuleDef_HEAD_INIT,
        "foo",      /* module 名称 */
        doc_mod,    /* 文档字符串 */
        -1,         /* size of per-interpreter state (-1 = global) */
        methods
    };

    PyMODINIT_FUNC PyInit_foo(void)
    {
        return PyModule_Create(&module);
    }

输出：

.. code-block:: bash

    $ python setup.py -q build && python setup.py -q install
    $ python -c "import foo; foo.foo()"
    'foo'

解析参数（Parse Arguments）
------------------------------------------

:Source: `src/cext/capi/args.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/args.c>`_

C 扩展 functions 将 arguments 作为 ``PyObject*`` 指针接收，并且必须将它们解析为 C types。 ``PyArg_ParseTuple()`` function 使用格式代码处理 positional arguments： ``i`` 表示 int、 ``l`` 表示长、 ``d`` 表示双、 ``s`` 表示 string、 ``O`` 对于任何 Python object。对于 keyword arguments，请使用 ``PyArg_ParseTupleAndKeywords()`` 。 method 标志（ ``METH_NOARGS`` 、 ``METH_O`` 、 ``METH_VARARGS`` 、 ``METH_KEYWORDS`` ）告诉 Python 如何调用您的 function 并且必须与您的实现相匹配。

.. code-block:: c

    #include <Python.h>

    // 否 arguments：METH_NOARGS
    static PyObject *
    foo(PyObject *self)
    {
        Py_RETURN_NONE;
    }

    // 单object argument：METH_O
    static PyObject *
    bar(PyObject *self, PyObject *arg)
    {
        return Py_BuildValue("O", arg);
    }

    // 多个 positional arguments：METH_VARARGS
    static PyObject *
    baz(PyObject *self, PyObject *args)
    {
        PyObject *x = NULL, *y = NULL;
        if (!PyArg_ParseTuple(args, "OO", &x, &y)) {
            return NULL;
        }
        return Py_BuildValue("OO", x, y);
    }

    // Keyword arguments: METH_VARARGS | METH_KEYWORDS
    static PyObject *
    qux(PyObject *self, PyObject *args, PyObject *kwargs)
    {
        static char *keywords[] = {"x", "y", NULL};
        PyObject *x = NULL, *y = NULL;
        if (!PyArg_ParseTupleAndKeywords(args, kwargs,
                                         "O|O", keywords,
                                         &x, &y))
        {
            return NULL;
        }
        if (!y) {
            y = Py_None;
        }
        return Py_BuildValue("OO", x, y);
    }

    static PyMethodDef methods[] = {
        {"foo", (PyCFunction)foo, METH_NOARGS, NULL},
        {"bar", (PyCFunction)bar, METH_O, NULL},
        {"baz", (PyCFunction)baz, METH_VARARGS, NULL},
        {"qux", (PyCFunction)qux, METH_VARARGS | METH_KEYWORDS, NULL},
        {NULL, NULL, 0, NULL}
    };

输出：

.. code-block:: bash

    >>> import foo
    >>> foo.foo()
    >>> foo.bar(3.7)
    3.7
    >>> foo.baz(3, 7)
    (3, 7)
    >>> foo.qux(x=3, y=7)
    (3, 7)

释放 GIL（Release the GIL）
----------------------------------------------

:Source: `src/cext/capi/gil.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/gil.c>`_

全局 Interpreter Lock (GIL) 是一个 mutex，可保护对 Python objects 的访问，防止多个本机 threads 同时执行 Python 字节码。虽然 GIL 简化了 CPython 的实现，但它可能成为 CPU 绑定的多线程代码的瓶颈。对于不访问 Python objects 的长时间运行的 C 操作（文件 I/O、网络调用、繁重计算），请使用 ``Py_BEGIN_ALLOW_THREADS`` 和 ``Py_END_ALLOW_THREADS`` 宏释放 GIL。这允许其他 Python threads 并发运行，从而显着提高多线程性能。

.. code-block:: c

    #include <Python.h>

    static PyObject* foo(PyObject* self)
    {
        Py_BEGIN_ALLOW_THREADS
        sleep(3);  // 阻塞操作-其他threads可以运行
        Py_END_ALLOW_THREADS
        Py_RETURN_NONE;
    }

**与GIL发布** （threads并发运行）：

.. code-block:: bash

    >>> import threading, foo
    >>> from datetime import datetime
    >>> def f(n):
    ...     print(f'{datetime.now()}: thread {n}')
    ...     foo.foo()
    >>> ts = [threading.Thread(target=f, args=(n,)) for n in range(3)]
    >>> [t.start() for t in ts]; [t.join() for t in ts]
    2018-11-04 20:15:34.860454: thread 0
    2018-11-04 20:15:34.860592: thread 1  # 同一时间！
    2018-11-04 20:15:34.860705: thread 2

**没有GIL释放** （threads顺序运行）：

.. code-block:: bash

    2018-11-04 20:16:44.055932: thread 0
    2018-11-04 20:16:47.059718: thread 1  # 3秒后
    2018-11-04 20:16:50.063579: thread 2  # 3 seconds later

.. warning::

    切勿在 ``Py_BEGIN_ALLOW_THREADS`` 和 ``Py_END_ALLOW_THREADS`` 之间调用 Python C API functions。必须握住 GIL 才能安全访问 Python objects。

获取 GIL（Acquire the GIL）
----------------------------------------------

:Source: `src/cext/capi/gil.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/gil.c>`_

当从 C 代码（使用 pthread 或平台线程 APIs）创建 threads 时，它们不会自动保存 GIL。在这些 threads 可以安全地调用任何 Python C API function 或访问 Python objects 之前，它们必须使用 ``PyGILState_Ensure()`` 获取 GIL。完成Python操作后，将GIL与 ``PyGILState_Release()`` 一起释放，以允许其他threads运行。在访问 Python objects 之前未能获取 GIL 会导致崩溃、数据损坏或未定义的行为。

.. code-block:: c

    void *worker_thread(void *arg)
    {
        PyObject *result = NULL;
        PyObject *callback = (PyObject *)arg;

        // C 在这里工作吗（不需要 GIL）
        do_heavy_computation();

        // 调用 Python 之前获取 GIL
        PyGILState_STATE state = PyGILState_Ensure();

        result = PyObject_CallFunction(callback, "s", "Done!");
        Py_XDECREF(result);

        // 发布GIL
        PyGILState_Release(state);
        return NULL;
    }

引发异常（Raise Exception）
------------------------------------------

:Source: `src/cext/capi/errors.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/errors.c>`_

C 扩展中的错误处理遵循一个简单的模式：使用 ``PyErr_SetString()`` 或 ``PyErr_Format()`` 的 set 和 exception，然后返回 ``NULL`` 以表示失败。 Python 提供内置 exception types 作为全局 variables： ``PyExc_ValueError`` 、 ``PyExc_TypeError`` 、 ``PyExc_RuntimeError`` 、 ``PyExc_KeyError`` 、 ``PyExc_IndexError`` 等。始终从 C API functions 检查 return values，并在 exception 已经是 set 时通过返回 ``NULL`` 来传播错误。

.. code-block:: c

    static PyObject*
    foo(PyObject* self)
    {
        PyErr_SetString(PyExc_NotImplementedError, "Not implemented");
        return NULL;
    }

输出：

.. code-block:: bash

    >>> import foo; foo.foo()
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    NotImplementedError: Not implemented

自定义异常（Custom Exception）
----------------------------------------------

:Source: `src/cext/capi/errors.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/errors.c>`_

对于特定于域的错误，请使用 ``PyErr_NewException()`` 创建自定义 exception classes。第一个 argument 是完全限定名称 ( ``"module.ExceptionName"`` )，第二个是 base class（ ``NULL`` 默认为 ``Exception`` ），第三个是 class attributes 的可选 dictionary。将 exception 注册为 module attribute，以便 Python 代码可以使用 ``except module.ExceptionName`` 捕获它。请记住在将 ``Py_INCREF()`` exception object 添加到 module 之前，以防止过早 garbage collection。

.. code-block:: c

    static PyObject *FooError;

    static PyObject *
    foo(PyObject *self)
    {
        PyErr_SetString(FooError, "Something went wrong");
        return NULL;
    }

    PyMODINIT_FUNC PyInit_foo(void)
    {
        PyObject *m = PyModule_Create(&module);
        if (!m) return NULL;

        FooError = PyErr_NewException("foo.FooError", NULL, NULL);
        Py_INCREF(FooError);
        PyModule_AddObject(m, "FooError", FooError);
        return m;
    }

输出：

.. code-block:: bash

    >>> import foo; foo.foo()
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    foo.FooError: Something went wrong

引用计数（Reference Counting）
------------------------------------------------

Python 使用 reference counting 作为其主要内存管理策略。每个 ``PyObject*`` 都会维护指向它的引用数量的计数。当计数达到零时，object 被释放。存储对 object 的新引用时使用 ``Py_INCREF()`` ，完成后使用 ``Py_DECREF()`` 。变体 ``Py_XDECREF()`` 可以安全地处理 ``NULL`` 指针。了解 reference counting 对于避免内存泄漏（忘记 decref）和释放后使用错误（过早 decref）至关重要。返回 "new references" 的 Functions 将所有权转移给调用者，而 "borrowed references" 不应被取消。

.. code-block:: c

    static PyObject *
    getrefcount(PyObject *self, PyObject *a)
    {
        return PyLong_FromSsize_t(Py_REFCNT(a));
    }

输出：

.. code-block:: bash

    >>> import sys, foo
    >>> l = [1, 2, 3]
    >>> sys.getrefcount(l[0])
    104
    >>> foo.getrefcount(l[0])
    104
    >>> i = l[0]  # 新参考
    >>> foo.getrefcount(l[0])
    105

迭代列表（Iterate a List）
----------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Python C API 提供了两种迭代序列的方法。使用 ``PyObject_GetIter()`` 和 ``PyIter_Next()`` 的通用 iterator 协议可与任何 iterable object（lists、tuples、generators、自定义 iterables）配合使用。具体对于lists，可以使用 ``PyList_Size()`` 和 ``PyList_GetItem()`` 进行直接索引访问，速度稍快但灵活性较差。请注意， ``PyList_GetItem()`` 返回借用的引用，而 ``PyIter_Next()`` 返回新的引用，在使用后必须将其取消引用。

.. code-block:: c

    static PyObject *iter_list(PyObject *self, PyObject *args) {
        PyObject *list, *iter, *item;
        if (!PyArg_ParseTuple(args, "O", &list)) {
            return NULL;
        }
        iter = PyObject_GetIter(list);
        if (!iter) return NULL;

        PyObject *result = PyList_New(0);
        while ((item = PyIter_Next(iter)) != NULL) {
            PyObject *doubled = PyLong_FromLong(PyLong_AsLong(item) * 2);
            PyList_Append(result, doubled);
            Py_DECREF(doubled);
            Py_DECREF(item);
        }
        Py_DECREF(iter);
        return result;
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.iter_list([1, 2, 3])
    [2, 4, 6]

迭代字典（Iterate a Dictionary）
----------------------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

C 语言中的 Dictionary iteration 使用 ``PyDict_Next()`` 以及跟踪 iteration 状态的位置 variable。在loop之前将 ``pos`` 初始化为0，function会自动更新。 key 和 value 指针接收对每个 iteration 上当前 item 的借用引用，除非先递增，否则不要递减它们。即使在 iteration 期间修改了 dictionary（尽管修改可能会导致 items 被跳过或访问两次），此 function 也可以安全使用。对于只读 iteration，这是最有效的方法。

.. code-block:: c

    static PyObject *iter_dict(PyObject *self, PyObject *args) {
        PyObject *dict;
        if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict)) {
            return NULL;
        }
        PyObject *result = PyList_New(0);
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(dict, &pos, &key, &value)) {
            PyObject *pair = PyTuple_Pack(2, key, value);
            PyList_Append(result, pair);
            Py_DECREF(pair);
        }
        return result;
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.iter_dict({"a": 1, "b": 2})
    [('a', 1), ('b', 2)]

创建列表（Create a List）
--------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

从 C 创建 Python lists 涉及到 ``PyList_New()`` 来分配 list 和 ``PyList_Append()`` 或 ``PyList_SetItem()`` 来填充它。当使用非零大小的 ``PyList_New(n)`` 时，必须在使用 list 之前使用 ``PyList_SetItem()`` 初始化所有插槽。 ``PyList_SetItem()`` 窃取对 item 的引用，而 ``PyList_Append()`` 则递增 reference count。要动态构建 lists，请从 ``PyList_New(0)`` 开始并使用 ``PyList_Append()`` 。

.. code-block:: c

    static PyObject *list_demo(PyObject *self) {
        PyObject *list = PyList_New(0);
        PyList_Append(list, PyLong_FromLong(1));
        PyList_Append(list, PyLong_FromLong(2));
        PyList_Append(list, PyLong_FromLong(3));
        return list;
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.list_demo()
    [1, 2, 3]

创建字典（Create a Dictionary）
--------------------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Python dictionaries 使用 ``PyDict_New()`` 创建，并使用 ``PyDict_SetItem()`` （对于 PyObject）keys 或 ``PyDict_SetItemString()`` （对于 C string keys）进行填充。两个 functions 都会递增 value 的 reference count，因此插入后您可能需要临时递减 objects。为了检索 values， ``PyDict_GetItem()`` 和 ``PyDict_GetItemString()`` 返回借用的引用（如果 key 不存在，则返回 NULL），而 ``PyDict_GetItemWithError()`` 区分丢失的 keys 和错误。

.. code-block:: c

    static PyObject *dict_demo(PyObject *self) {
        PyObject *dict = PyDict_New();
        PyDict_SetItemString(dict, "name", PyUnicode_FromString("Python"));
        PyDict_SetItemString(dict, "version", PyLong_FromLong(3));
        return dict;
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.dict_demo()
    {'name': 'Python', 'version': 3}

创建一个元组（Create a Tuple）
--------------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Tuples 是 immutable 序列，C API 反映了这一点：一旦创建并填充，tuple 内容就无法更改。使用 ``PyTuple_New(n)`` 创建大小为 n 的 tuple，然后使用 ``PyTuple_SetItem()`` 填充每个槽（这会窃取引用）。或者，带括号格式的 ``Py_BuildValue()`` 直接从 C values 创建 tuples： ``"(isd)"`` 创建 (int, string, double) 的 tuple。 ``PyTuple_Pack(n, ...)`` 是从现有 PyObject 指针创建 tuples 的另一种便捷方法。

.. code-block:: c

    static PyObject *tuple_demo(PyObject *self) {
        return Py_BuildValue("(isd)", 1, "hello", 3.14);
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.tuple_demo()
    (1, 'hello', 3.14)

创建一个集合（Create a Set）
----------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Sets 是唯一的 hashable objects 的无序 collections。使用 ``PySet_New(NULL)`` 创建空 set 或使用 ``PySet_New(iterable)`` 从 iterable 进行初始化。将 elements 与 ``PySet_Add()`` 添加，成功时返回 0，错误时返回 -1（e.g.，如果 object 是 unhashable）。使用 ``PySet_Contains()`` 检查成员资格，使用 ``PySet_Discard()`` 删除 elements（如果丢失则不会出错）或 ``PySet_Pop()`` 删除并返回任意 element。重复的添加将被默默地忽略。

.. code-block:: c

    static PyObject *set_demo(PyObject *self) {
        PyObject *set = PySet_New(NULL);
        PySet_Add(set, PyLong_FromLong(1));
        PySet_Add(set, PyLong_FromLong(2));
        PySet_Add(set, PyLong_FromLong(2));  /* 重复的被忽略 */
        PySet_Add(set, PyLong_FromLong(3));
        return set;
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.set_demo()
    {1, 2, 3}

字符串操作（String Operations）
------------------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Python 3 strings 是 Unicode objects，使用 ``PyUnicode_FromString()`` 创建，用于 UTF-8 编码的 C strings 或 ``PyUnicode_FromFormat()`` ，用于 printf 样式格式。将 strings 与 ``PyUnicode_Concat()`` 连接，返回新的 string object。要提取 C strings，请使用 ``PyUnicode_AsUTF8()`` （返回仅在 object 存在时有效的借用指针）或 ``PyUnicode_AsUTF8AndSize()`` 来获取长度。格式 function 支持 C strings 的 ``%s`` 、Python objects 的 ``%S`` （调用 str()）、repr() 的 ``%R`` 和 ``%d`` ， ``%u`` 、 ``%ld`` 为 integers。

.. code-block:: c

    static PyObject *str_demo(PyObject *self) {
        PyObject *s1 = PyUnicode_FromString("Hello");
        PyObject *s2 = PyUnicode_FromString(" World");
        PyObject *result = PyUnicode_Concat(s1, s2);
        Py_DECREF(s1);
        Py_DECREF(s2);
        return result;
    }

    static PyObject *str_format(PyObject *self, PyObject *args) {
        const char *name;
        int age;
        if (!PyArg_ParseTuple(args, "si", &name, &age)) {
            return NULL;
        }
        return PyUnicode_FromFormat("%s is %d years old", name, age);
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.str_demo()
    'Hello World'
    >>> types_demo.str_format("Alice", 30)
    'Alice is 30 years old'

字节操作（Bytes Operations）
--------------------------------------------

:Source: `src/cext/capi/types_demo.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/types_demo.c>`_

Bytes objects 表示 bytes 的 immutable 序列，对于二进制数据、文件 I/O 和网络协议至关重要。从 C strings 和 ``PyBytes_FromString()`` 创建 bytes（复制到空终止符）或 ``PyBytes_FromStringAndSize()`` （用于嵌入空值的二进制数据）。用 ``PyBytes_AsString()`` （借用指针）访问内部buffer，用 ``PyBytes_Size()`` 获取长度。对于 mutable byte 序列，请改用 ``PyByteArray_*`` functions。解析 arguments 时，使用格式代码 ``s#`` 表示 bytes 的长度或 ``S`` 仅接受 bytes objects。

.. code-block:: c

    static PyObject *bytes_demo(PyObject *self) {
        return PyBytes_FromString("hello bytes");
    }

    static PyObject *bytes_len(PyObject *self, PyObject *args) {
        PyObject *bytes;
        if (!PyArg_ParseTuple(args, "S", &bytes)) {
            return NULL;
        }
        return PyLong_FromSsize_t(PyBytes_Size(bytes));
    }

输出：

.. code-block:: bash

    >>> import types_demo
    >>> types_demo.bytes_demo()
    b'hello bytes'
    >>> types_demo.bytes_len(b"hello")
    5

简单类（Simple Class）
----------------------------------

用 C 语言定义自定义 Python types 需要创建一个 ``PyTypeObject`` 结构，用于描述 type 的行为、内存布局和 methods。最小的 type 需要 ``tp_name`` （完全限定名称，如 ``"module.ClassName"`` ）、 ``tp_basicsize`` （instance 结构的大小）和 ``tp_new`` （分配 function，通常为 ``PyType_GenericNew`` ）。使用前先调用 ``PyType_Ready()`` 来完成type，然后将其与 ``PyModule_AddObject()`` 一起添加到您的module中。 ``Py_TPFLAGS_DEFAULT`` 标志启用标准 type 功能。

.. code-block:: c

    typedef struct {
        PyObject_HEAD
    } FooObject;

    static PyTypeObject FooType = {
        PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "foo.Foo",
        .tp_doc = "Foo objects",
        .tp_basicsize = sizeof(FooObject),
        .tp_itemsize = 0,
        .tp_flags = Py_TPFLAGS_DEFAULT,
        .tp_new = PyType_GenericNew
    };

    PyMODINIT_FUNC PyInit_foo(void)
    {
        PyObject *m = NULL;
        if (PyType_Ready(&FooType) < 0)
            return NULL;
        if ((m = PyModule_Create(&module)) == NULL)
            return NULL;
        Py_INCREF(&FooType);
        PyModule_AddObject(m, "Foo", (PyObject *)&FooType);
        return m;
    }

具有成员和方法的类（Class with Members and Methods）
----------------------------------------------------------------------------------

C 语言中的全功能 Python classes 需要实现多个 type 插槽。使用 ``PyMemberDef`` 将 C 结构体字段公开为 Python attributes（具有自动 type 转换），并将 ``PyMethodDef`` 公开为 instance methods。实现 ``tp_new`` 进行内存分配（在 ``__init__`` 之前调用），实现 ``tp_init`` 进行初始化（ ``__init__`` method），实现 ``tp_dealloc`` 进行清理（必须 decref 所有拥有的 PyObject 成员并调用 ``tp_free`` ）。 ``Py_TPFLAGS_BASETYPE`` 标志允许在 Python 中对 type 进行子类化。

.. code-block:: c

    #include <Python.h>
    #include <structmember.h>

    typedef struct {
        PyObject_HEAD
        PyObject *foo;
        PyObject *bar;
    } FooObject;

    static void
    Foo_dealloc(FooObject *self)
    {
        Py_XDECREF(self->foo);
        Py_XDECREF(self->bar);
        Py_TYPE(self)->tp_free((PyObject *)self);
    }

    static PyObject *
    Foo_new(PyTypeObject *type, PyObject *args, PyObject *kw)
    {
        FooObject *self = (FooObject *)type->tp_alloc(type, 0);
        if (self) {
            self->foo = PyUnicode_FromString("");
            self->bar = PyUnicode_FromString("");
        }
        return (PyObject *)self;
    }

    static int
    Foo_init(FooObject *self, PyObject *args, PyObject *kw)
    {
        static char *keywords[] = {"foo", "bar", NULL};
        PyObject *foo = NULL, *bar = NULL;

        if (!PyArg_ParseTupleAndKeywords(args, kw, "|OO", keywords, &foo, &bar))
            return -1;

        if (foo) { Py_INCREF(foo); Py_XDECREF(self->foo); self->foo = foo; }
        if (bar) { Py_INCREF(bar); Py_XDECREF(self->bar); self->bar = bar; }
        return 0;
    }

    static PyMemberDef Foo_members[] = {
        {"foo", T_OBJECT_EX, offsetof(FooObject, foo), 0, "foo attribute"},
        {"bar", T_OBJECT_EX, offsetof(FooObject, bar), 0, "bar attribute"},
        {NULL}
    };

输出：

.. code-block:: bash

    >>> import foo
    >>> o = foo.Foo('hello', 'world')
    >>> o.foo
    'hello'
    >>> o.bar
    'world'

属性（Getter/Setter）（Properties (Getter/Setter)）
------------------------------------------------------------------------------------------

对于需要验证的计算 attributes 或 attributes，请使用 ``PyGetSetDef`` 来定义带有自定义 getter 和 setter functions 的 properties。 getter 接收 instance 和可选的 closure 指针，返回对 attribute value 的新引用。 setter 接收 instance、新的 value（或删除时的 NULL）和 closure，成功时返回 0，错误时返回 -1。这提供了与 Python 的 ``@property`` decorator 相同的功能，但具有对 attribute 访问的 C 级控制。

.. code-block:: c

    static PyObject *
    Foo_getfoo(FooObject *self, void *closure)
    {
        Py_INCREF(self->foo);
        return self->foo;
    }

    static int
    Foo_setfoo(FooObject *self, PyObject *value, void *closure)
    {
        if (!value || !PyUnicode_Check(value)) {
            PyErr_SetString(PyExc_TypeError, "value must be a string");
            return -1;
        }
        Py_INCREF(value);
        Py_XDECREF(self->foo);
        self->foo = value;
        return 0;
    }

    static PyGetSetDef Foo_getsetters[] = {
        {"foo", (getter)Foo_getfoo, (setter)Foo_setfoo, "foo property", NULL},
        {NULL}
    };

从 C 调用 Python（Calling Python from C）
------------------------------------------------------------------------

C 扩展通常需要回调 Python 代码 — 调用 callbacks、在 objects 上调用 methods 或使用 Python library functions。使用 ``PyObject_CallFunction()`` 以 C 风格格式 arguments、 ``PyObject_CallObject()`` 和 arguments 的 tuple 进行调用，或使用 ``PyObject_CallMethod()`` 按名称调用 method。在调用之前，请务必使用 ``PyCallable_Check()`` 检查可调用是否有效，并检查 NULL 的 return value（表示已引发 exception）。调用 Python functions 时必须持有 GIL。

.. code-block:: c

    static PyObject *
    call_callback(PyObject *self, PyObject *args)
    {
        PyObject *callback = NULL;
        PyObject *result = NULL;

        if (!PyArg_ParseTuple(args, "O:callback", &callback))
            return NULL;

        if (!PyCallable_Check(callback)) {
            PyErr_SetString(PyExc_TypeError, "argument must be callable");
            return NULL;
        }

        // Call: callback("Hello from C!")
        result = PyObject_CallFunction(callback, "s", "Hello from C!");
        return result;
    }

输出：

.. code-block:: bash

    >>> import foo
    >>> foo.call_callback(print)
    Hello from C!

性能比较（Performance Comparison）
--------------------------------------------------------

:Source: `src/cext/capi/simple.c <https://github.com/crazyguitar/pysheeet/blob/master/src/cext/capi/simple.c>`_

C 扩展通过消除 Python 的 interpreter 开销，为 CPU 绑定操作提供显着的加速。与纯 Python 相比，recursive 斐波那契 benchmark 的典型性能提升了 50-100 倍。加速来自于避免每个 function 调用上的 Python object 创建、method 调度和字节码解释。对于数字代码，与SIMD指令或多线程（已发布GIL）结合使用时，增益会更大。然而，跨越 Python/C 边界的开销意味着 C 扩展对于计算密集型内部 loops 最有利，而不是简单的操作。

.. code-block:: c

    static unsigned long fib(unsigned long n)
    {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }

    static PyObject *
    py_fib(PyObject *self, PyObject *args)
    {
        unsigned long n = 0;
        if (!PyArg_ParseTuple(args, "k", &n)) return NULL;
        return PyLong_FromUnsignedLong(fib(n));
    }

.. code-block:: python

    >>> from time import time
    >>> def py_fib(n):
    ...     if n < 2: return n
    ...     return py_fib(n-1) + py_fib(n-2)
    ...
    >>> s = time(); _ = py_fib(35); e = time(); e - s
    4.953313112258911
    >>> import foo
    >>> s = time(); _ = foo.fib(35); e = time(); e - s
    0.04628586769104004
