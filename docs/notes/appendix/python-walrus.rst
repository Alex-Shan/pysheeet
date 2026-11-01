.. meta::
    :description lang=zh_CN: pep 572海象operator的设计理念
    :keywords: Python3, PEP 572, walrus operator


PEP 572 与海象运算符（PEP 572 and The Walrus Operator）
==============================================================================================

:Date: 2025-08-30

摘要（Abstract）
------------------------

`PEP 572`_ 是 Python3 历史上最具争议的提案之一，因为在 expression 中分配 value 似乎没有必要。此外，开发人员很难区分海象运算符 ** ** ( ``:=`` ) 和同等的 operator ( ``=`` ) 之间的区别。尽管经验丰富的开发人员可以顺利使用 " ``:=`` "，但他们可能会担心代码的可读性。为了更好地理解 " ``:=`` ," 的用法，本文讨论了它的设计理念以及它试图解决什么样的问题。


介绍（Introduction）
--------------------------------

对于 C/C++ 开发人员来说，由于错误代码样式处理，将 function 返回分配给 variable 是很常见的。管理 function 错误包括两个步骤；一是检查return value；另一个是检查 ``errno`` 。例如，

.. code-block:: cpp

    #include <stdio.h>
    #include <unistd.h>
    #include <string.h>
    #include <errno.h>

    int main(int argc, char *argv[]) {
        int rc = -1;

        // 将访问权限返回给rc并检查其value
        if ((rc = access("hello_walrus", R_OK)) == -1) {
            fprintf(stderr, "%s", strerror(errno));
            goto end;
        }
        rc = 0;
    end:
        return rc;
    }

在这种情况下， ``access`` 将首先将其return value分配给variable ``rc`` 。然后，程序会比较 ``rc`` 、value和 ``-1`` ，检查 ``access`` 是否执行成功。但是，Python 不允许将 values 分配给 3.8 之前的 expression 内的 variables。因此，为了解决这个问题，PEP 572为开发者推出了海象operator。以下 Python 代码段与前面的 C 示例相同。

.. code-block:: python

    >>> import os
    >>> from ctypes import *
    >>> libc = CDLL("libc.dylib", use_errno=True)
    >>> access = libc.access
    >>> path = create_string_buffer(b"hello_walrus")
    >>> if (rc := access(path, os.R_OK)) == -1:
    ...     errno = get_errno()
    ...     print(os.strerror(errno), file=sys.stderr)
    ...
    No such file or directory


为什么是 ``:=`` ？（Why ``:=`` ?）
------------------------------------------------------

开发者可能会混淆" ``:=`` "和" ``=`` ."之间的区别，其实它们的目的是一样的，都是给variables分配一些东西。为什么Python引入" ``:=`` "而不是使用" ``=`` "？使用" ``:=`` "有什么好处？原因之一是为了加强视觉识别，这是 C/C++ 开发人员常犯的错误。对于instance，

.. code-block:: cpp

    int rc = access("hello_walrus", R_OK);

    // rc 无意中被赋值为 -1
    if (rc = -1) {
        fprintf(stderr, "%s", strerror(errno));
        goto end;
    }

variable、 ``rc`` 被错误地分配为 -1，而不是进行比较。为了防止出现此错误，有些人主张在 expression 中使用 `Yoda conditions`_ 。

.. code-block:: cpp

    int rc = access("hello_walrus", R_OK);

    // -1 = rc will raise a compile error
    if (-1 == rc) {
        fprintf(stderr, "%s", strerror(errno));
        goto end;
    }

然而，尤达风格的可读性不够，就像尤达说着不标准化的英语一样。此外，与 C/C++ 可以通过 compiler 选项（e.g., -W括号）在编译时检测分配错误不同，Python interpreter 很难在整个运行时区分此类错误。因此，PEP 572的最终结果是使用新的语法作为解决方案来实现*赋值expressions*。

海象operator并不是PEP 572的第一个解决方案。最初的提案使用 ``EXPR as NAME`` 将values分配给variables。不幸的是，这个解决方案和其他解决方案也存在一些被拒绝的原因。经过激烈辩论，最终判决为 ``:=`` 。

作用域（Scopes）
----------------------

与其他expressions不同，variable绑定到scope，分配expression属于当前scope。这种设计的目的是允许以紧凑的方式编写代码。

.. code-block:: python3

    >>> if not (env := os.environ.get("HOME")):
    ...     raise KeyError("env HOME does not find!")
    ...
    >>> print(env)
    /root

在 PEP 572 中，另一个好处是可以方便地捕获 ``any()`` 或 ``all()`` expression 的 "witness"。虽然捕获 function 输入可以辅助交互式 debugger，但优势并不那么明显，并且示例缺乏可读性。因此，这个好处这里不讨论。请注意，其他语言（e.g.、C/C++ 或 Go）可能会将赋值绑定到 scope。以Golang为例。

.. code-block:: go

    package main

    import (
        "fmt"
        "os"
    )

    func main() {
        if env := os.Getenv("HOME"); env == "" {
            panic(fmt.Sprintf("Home does not find"))
        }
        fmt.Print(env) // <--- 编译错误：未定义：env
    }

陷阱（Pitfalls）
------------------------

虽然分配 expression 允许编写紧凑的代码，但当开发人员在 list comprehension 中使用它时，存在许多陷阱。常见的 ``SyntaxError`` 就是重新绑定iteration variables。

.. code-block:: python3

    >>> [i := i+1 for i in range(5)]  # 无效的

但是，更新 iteration variable 将降低可读性并引入错误。即使 Python 3.8 没有实现海象 operator，程序员也应该避免在 scope 中重用 iteration variables。

另一个陷阱是 Python 禁止在 class scope 下的 comprehension 内使用分配 expressions。

.. code-block:: python3

    >>> class Example:
    ...     [(j := i) for i in range(5)] # 无效的
    ...

此限制来自 `bpo-3692`_ 。当 class 声明包含 list comprehension 时，interpreter 的行为是不可预测的。为了避免这种极端情况，在 class 下分配 expression 无效。

.. code-block:: python3

    >>> class Foo:
    ...     a = [1, 2, 3]
    ...     b = [4, 5, 6]
    ...     c = [i for i in zip(a, b)]  # b 被定义
    ...
    >>> class Bar:
    ...     a = [1,2,3]
    ...     b = [4,5,6]
    ...     c = [x * y for x in a for y in b] # b 未定义
    ...
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 4, in Bar
      File "<stdin>", line 4, in <listcomp>
    NameError: name 'b' is not defined

结论（Conclusion）
----------------------------

海象operator（ ``:=`` ）之所以备受争议，是因为代码可读性可能会下降。事实上，在 `mail thread <https://mail.python.org/pipermail/python-ideas/2018-March/049409.html>`_ 的讨论中，PEP 572的作者Christoph Groth就曾考虑过使用" ``=`` "来实现像C/C++一样的内联赋值。在不判断 " ``:=`` " 丑陋的情况下，许多开发人员认为区分 " ``:=`` " 和 " ``=`` " 之间的功能很困难，因为它们服务于相同的目的，但行为并不一致。此外，编写紧凑的代码并没有足够的说服力，因为代码越小并不总是越好。然而，在某些情况下，海象 operator 可以增强可读性（如果您了解如何使用 ``:=`` ）。例如，

.. code-block:: python3

    buf = b""
    while True:
        data = read(1024)
        if not data:
            break
        buf += data

通过使用 ``:=`` ，可以简化前面的示例。

.. code-block:: python3

    buf = b""
    while (data := read(1024)):
        buf += data

`Python document`_ 和 GitHub `issue-8122`_ 提供了许多关于通过 " ``:=`` " 提高代码可读性的好例子。不过，使用海象operator要小心。如果开发人员不知道 scopes，某些情况（例如 ``foo(x := 3, cat='vector')`` ）可能会引入新的错误。尽管PEP 572对于开发人员来说编写有缺陷的代码可能存在风险，但深入理解设计理念和有用的示例将帮助我们在正确的时间使用它编写可读的代码。

参考资料（References）
--------------------------------

1. `PEP 572 - Assignment Expressions`_
2. `What’s New In Python 3.8`_
3. `PEP 572 and decision-making in Python`_
4. `The PEP 572 endgame`_
5. `Use assignment expression in stdlib (combined PR)`_
6. `Improper scope in list comprehension, when used in class declaration`_

.. _PEP 572: https://www.python.org/dev/peps/pep-0572/
.. _PEP 572 - Assignment Expressions: https://www.python.org/dev/peps/pep-0572/
.. _What’s New In Python 3.8: https://docs.python.org/3/whatsnew/3.8.html
.. _PEP 572 and decision-making in Python: https://lwn.net/Articles/757713/
.. _The PEP 572 endgame: https://lwn.net/Articles/759558/
.. _Use assignment expression in stdlib (combined PR): https://github.com/python/cpython/pull/8122/files
.. _improper scope in list comprehension, when used in class declaration: https://bugs.python.org/issue3692
.. _Yoda conditions: https://en.wikipedia.org/wiki/Yoda_conditions
.. _bpo-3692: https://bugs.python.org/issue3692
.. _Python document: https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions
.. _issue-8122: https://github.com/python/cpython/pull/8122/files
