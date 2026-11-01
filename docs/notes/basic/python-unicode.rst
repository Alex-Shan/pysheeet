.. meta::
    :description lang=zh_CN: Python Unicode 教程涵盖 string encoding、decoding、UTF-8、ASCII、bytes 转换以及 Python 3 中的字符处理
    :keywords: Python, Python3, Unicode, UTF-8, encoding, decoding, bytes, string, ASCII, character, codec

======================================
Unicode 字符（Unicode）
======================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

本速查表的主要目标是收集一些与 Unicode 相关的常见片段。在Python 3中，strings用Unicode代替bytes表示。更多信息请参见 PEP `3100 <https://www.python.org/dev/peps/pep-3100>`_

**ASCII**代码是定义字符数字代码的最著名的标准。数字values原本只定义了128个字符，所以ASCII只包含控制码、数字、小写字母、大写字母等。但是，这不足以我们表示世界各地存在的重音字符、汉字或表情符号等字符。因此，开发了**Unicode** 来解决这个问题。它定义了*代码点*来表示各种字符，例如ASCII，但字符数最多为1,111,998。

字符串（String）
----------------------

在 Python 2 中，strings 表示为 *bytes*，而不是 *Unicode*。 Python提供string的不同types，例如Unicode、string、原始string等。在这种情况下，如果我们想声明一个 Unicode string，我们为 string literals 添加 ``u`` 前缀。

.. code-block:: python

    >>> s = 'Café'  # byte string
    >>> s
    'Caf\xc3\xa9'
    >>> type(s)
    <type 'str'>
    >>> u = u'Café' # unicode string
    >>> u
    u'Caf\xe9'
    >>> type(u)
    <type 'unicode'>

在 Python 3 中，strings 以*Unicode* 表示。如果我们想表示 byte string，我们为 string literals 添加 ``b`` 前缀。请注意，早期的 Python 版本 (3.0-3.2) 不支持 ``u`` 前缀。为了减轻从 Python 2 迁移 Unicode 感知应用程序的痛苦，Python 3.3 再次支持 string literals 的 ``u`` 前缀。更多信息请参见 PEP `414 <https://www.python.org/dev/peps/pep-0414>`_

.. code-block:: python

    >>> s = 'Café'
    >>> type(s)
    <class 'str'>
    >>> s
    'Café'
    >>> s.encode('utf-8')
    b'Caf\xc3\xa9'
    >>> s.encode('utf-8').decode('utf-8')
    'Café'

字符（Characters）
----------------------------

Python 2 将所有 string 字符视为 bytes。在这种情况下，strings 的长度可能不等于字符数。例如， ``Café`` 的长度是 5，而不是 4，因为 ``é`` 被编码为 2 bytes 字符。

.. code-block:: python

    >>> s= 'Café'
    >>> print([_c for _c in s])
    ['C', 'a', 'f', '\xc3', '\xa9']
    >>> len(s)
    5
    >>> s = u'Café'
    >>> print([_c for _c in s])
    [u'C', u'a', u'f', u'\xe9']
    >>> len(s)
    4

Python 3 将所有 string 字符作为 Unicode 代码点。 string 的长度始终等于字符数。

.. code-block:: python

    >>> s = 'Café'
    >>> print([_c for _c in s])
    ['C', 'a', 'f', 'é']
    >>> len(s)
    4
    >>> bs = bytes(s, encoding='utf-8')
    >>> print(bs)
    b'Caf\xc3\xa9'
    >>> len(bs)
    5

移植unicode(s, 'utf-8')（Porting unicode(s, 'utf-8')）
----------------------------------------------------------------------------------------------------

`unicode() <https://docs.python.org/2.7/library/functions.html#unicode>`_ 内置 function 在 Python 3 中被删除，那么转换 expression ``unicode(s, 'utf-8')`` 以便它在 Python 2 和 3 中工作的最佳方法是什么？

在 Python 2 中：

.. code-block:: python

    >>> s = 'Café'
    >>> unicode(s, 'utf-8')
    u'Caf\xe9'
    >>> s.decode('utf-8')
    u'Caf\xe9'
    >>> unicode(s, 'utf-8') == s.decode('utf-8')
    True

在 Python 3 中：

.. code-block:: python

    >>> s = 'Café'
    >>> s.decode('utf-8')
    AttributeError: 'str' object has no attribute 'decode'

所以，真正的答案是……

Unicode 代码点（Unicode Code Point）
--------------------------------------------------------------

`ord <https://docs.python.org/3/library/functions.html#ord>`_ 是一个强大的内置 function，用于从给定字符获取 Unicode 代码点。因此，如果我们想检查字符的 Unicode 代码点，我们可以使用 ``ord`` 。

.. code-block:: python

    >>> s = u'Café'
    >>> for _c in s: print('U+%04x' % ord(_c))
    ...
    U+0043
    U+0061
    U+0066
    U+00e9
    >>> u = '中文'
    >>> for _c in u: print('U+%04x' % ord(_c))
    ...
    U+4e2d
    U+6587


编码（Encoding）
------------------------

*Unicode 代码点* 传输到 *byte string* 称为 encoding。

.. code-block:: python

    >>> s = u'Café'
    >>> type(s.encode('utf-8'))
    <class 'bytes'>

解码（Decoding）
------------------------

*byte string* 传输到 *Unicode 代码点* 称为 decoding。

.. code-block:: python

    >>> s = bytes('Café', encoding='utf-8')
    >>> s.decode('utf-8')
    'Café'

Unicode 规范化（Unicode Normalization）
--------------------------------------------------------------------

有些字符可以用两种相似的形式来表示。例如，字符 ``é`` 可以写为 ``e ́`` （规范分解）或 ``é`` （规范组合）。在这种情况下，当我们比较两个 strings 时，即使它们看起来很相似，我们也可能会得到意想不到的结果。因此，我们可以规范化一个Unicode表单来解决这个问题。

.. code-block:: python

    # python 3
    >>> u1 = 'Café'       # unicode string
    >>> u2 = 'Cafe\u0301'
    >>> u1, u2
    ('Café', 'Café')
    >>> len(u1), len(u2)
    (4, 5)
    >>> u1 == u2
    False
    >>> u1.encode('utf-8') # 得到 u1 byte string
    b'Caf\xc3\xa9'
    >>> u2.encode('utf-8') # 得到 u2 byte string
    b'Cafe\xcc\x81'
    >>> from unicodedata import normalize
    >>> s1 = normalize('NFC', u1)  # 获取 u1 NFC 格式
    >>> s2 = normalize('NFC', u2)  # 获取 u2 NFC 格式
    >>> s1 == s2
    True
    >>> s1.encode('utf-8'), s2.encode('utf-8')
    (b'Caf\xc3\xa9', b'Caf\xc3\xa9')
    >>> s1 = normalize('NFD', u1)  # 获取 u1 NFD 格式
    >>> s2 = normalize('NFD', u2)  # 获取 u2 NFD 格式
    >>> s1, s2
    ('Café', 'Café')
    >>> s1 == s2
    True
    >>> s1.encode('utf-8'), s2.encode('utf-8')
    (b'Cafe\xcc\x81', b'Cafe\xcc\x81')


避免 ``UnicodeDecodeError`` （Avoid ``UnicodeDecodeError`` ）
------------------------------------------------------------------------------------------------------------------

当 byte strings 无法从 decode 转换为 Unicode 代码点时，Python 会升高 `UnicodeDecodeError` 。如果我们想避免这个 exception，我们可以将 *replace*、*backslashreplace* 或 *ignore* 传递给 `decode <https://docs.python.org/3/library/stdtypes.html#bytes.decode>`_ 中的错误 argument。

.. code-block:: python

    >>> u = b"\xff"
    >>> u.decode('utf-8', 'strict')
        Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
    >>> # 使用 U+FFFD、REPLACEMENT CHARACTER
    >>> u.decode('utf-8', "replace")
    '\ufffd'
    >>> # 插入 \xNN escape 序列
    >>> u.decode('utf-8', "backslashreplace")
    '\\xff'
    >>> # 将该字符保留在 Unicode 结果之外
    >>> u.decode('utf-8', "ignore")
    ''

长字符串（Long String）
----------------------------------

以下代码片段显示了在 Python 中声明多行 string 的常见方法。

.. code-block:: python

    # 原厂长string
    s = 'This is a very very very long python string'

    # 带有转义反斜杠的单引号
    s = "This is a very very very " \
        "long python string"

    # 使用括号
    s = (
        "This is a very very very "
        "long python string"
    )

    # 使用 ``+``
    s = (
        "This is a very very very " +
        "long python string"
    )

    # 使用带有转义反斜杠的三引号
    s = '''This is a very very very \
    long python string'''
