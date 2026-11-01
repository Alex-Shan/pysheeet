.. meta::
    :description lang=zh_CN: Python __future__ module 指南涵盖未来的 statements、向后兼容性以及从较新的 Python 版本向后移植的功能
    :keywords: Python, __future__, future statements, backward compatibility, print_function, annotations, division

========================
未来特性（Future）
========================

.. contents:: 目录（Table of Contents）
    :backlinks: none


`Future statements <https://docs.python.org/3/reference/simple_stmts.html#future>`_ 告诉interpreter编译一些语义作为未来Python版本中可用的语义。换句话说，Python 使用 ``from __future__ import feature`` 将其他更高 Python 版本的功能向后移植到当前的 interpreter。在Python 3中，许多功能（例如 ``print_function`` ）已经启用，但我们仍然保留这些未来的statements以向后兼容。

未来statements是 **NOT**导入statements。未来的 statements 会改变 Python 解释代码的方式。它们**MUST** 位于文件顶部。否则，Python interpreter 将加注 ``SyntaxError`` 。

如果您对未来的statements感兴趣并希望获得更多解释，可以在 `PEP 236 - Back to the __future__ <https://www.python.org/dev/peps/pep-0236>`_ 上找到更多信息

列出所有新功能（List All New Features）
------------------------------------------------------------

`__future__ <https://docs.python.org/3/library/__future__.html>`_ 是 Python module。我们可以用它来检查未来什么样的功能可以导入到当前的 Python interpreter 中。有趣的是 ``import __future__`` 是 **NOT** 未来的statement，它是进口的statement。

.. code-block:: python

    >>> from pprint import pprint
    >>> import __future__
    >>> pprint(__future__.all_feature_names)
    ['nested_scopes',
     'generators',
     'division',
     'absolute_import',
     'with_statement',
     'print_function',
     'unicode_literals',
     'barry_as_FLUFL',
     'generator_stop',
     'annotations']

未来的 statements 不仅会更改 Python interpreter 的行为，还会将 ``__future__._Feature`` 导入到当前程序中。

.. code-block:: python

    >>> from __future__ import print_function
    >>> print_function
    _Feature((2, 6, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0), 65536)

print 函数（Print Function）
------------------------------------------------

将 **打印语句** 替换为 **打印函数** 是 Python 历史上最臭名昭著的决定之一。然而，这一变化带来了一些灵活性来扩展 ``print`` 的能力。更多信息请参见 PEP `3105 <https://www.python.org/dev/peps/pep-3105>`_ 。

.. code-block:: python

    >>> print "Hello World"  # 打印是 statement
    Hello World
    >>> from __future__ import print_function
    >>> print "Hello World"
      File "<stdin>", line 1
        print "Hello World"
                          ^
    SyntaxError: invalid syntax
    >>> print("Hello World") # 打印成function
    Hello World

Unicode 字符（Unicode）
--------------------------------------

正如 **打印功能** 一样，将文本变成Unicode是另一个臭名昭著的决定。然而，许多现代编程语言的文本是 Unicode。这一变化迫使我们尽早使用 decode 文本，以防止我们运行程序一段时间后出现运行时错误。更多信息请参见 PEP `3112 <https://www.python.org/dev/peps/pep-3112>`_ 。

.. code-block:: python

    >>> type("Guido") # string type在python2中是str
    <type 'str'>
    >>> from __future__ import unicode_literals
    >>> type("Guido") # string type 变为 unicode
    <type 'unicode'>

除法（Division）
------------------------

有时，当除法结果为 int 或 long 时，这是违反直觉的。在这种情况下，Python 3默认启用 **真除法** 。但是，在 Python 2 中，我们必须将 ``division`` 向后移植到当前的 interpreter。更多信息请参见 PEP `238 <https://www.python.org/dev/peps/pep-0238>`_ 。

.. code-block:: python

    >>> 1 / 2
    0
    >>> from __future__ import division
    >>> 1 / 2   # 返回 float（经典除法）
    0.5
    >>> 1 // 2  # 返回int（楼层划分）
    0

标注（Annotations）
------------------------------

在Python 3.7之前，如果当前scope中没有可用的注释，我们无法在class或function中分配注释。常见的情况是定义一个容器class。

.. code-block:: python

    class Tree(object):

        def insert(self, tree: Tree): ...

例子

.. code-block:: bash

    $ python3 foo.py
    Traceback (most recent call last):
      File "foo.py", line 1, in <module>
        class Tree(object):
      File "foo.py", line 3, in Tree
        def insert(self, tree: Tree): ...
    NameError: name 'Tree' is not defined

在这种情况下，class 的定义尚不可用。 Python interpreter 无法在定义时间内解析注释。为了解决这个问题，Python使用string literals来替代class。

.. code-block:: python

    class Tree(object):

        def insert(self, tree: 'Tree'): ...

在3.7版本之后，Python推出了未来的statement、 ``annotations`` ，进行推迟评估。它将成为Python 4中的默认功能。更多信息请参阅PEP `563 <https://www.python.org/dev/peps/pep-0563>`_ 。


.. code-block:: python

    from __future__ import annotations

    class Tree(object):

        def insert(self, tree: Tree): ...

BDFL 退休（BDFL Retirement）
------------------------------------------------

**Python新品 3.1**

PEP `401 <https://www.python.org/dev/peps/pep-0401/>`_ 只是一个复活节彩蛋。这一功能让现在的interpreter回到了过去。它使Python 3中的钻石operator ``<>`` 成为可能。

.. code-block:: python

    >>> 1 != 2
    True
    >>> from __future__ import barry_as_FLUFL
    >>> 1 != 2
      File "<stdin>", line 1
        1 != 2
           ^
    SyntaxError: with Barry as BDFL, use '<>' instead of '!='
    >>> 1 <> 2
    True

花括号（Braces）
----------------------

``braces`` 是一个复活节彩蛋。源代码可以在 `future.c <https://github.com/python/cpython/blob/master/Python/future.c>`_ 上找到。

.. code-block:: python

    >>> from __future__ import braces
      File "<stdin>", line 1
    SyntaxError: not a chance
