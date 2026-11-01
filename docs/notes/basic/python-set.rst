.. meta::
    :description lang=zh_CN: Python set 速查表涵盖 set comprehensions、set 操作（并、交、差），删除重复项、子集、超集和 frozenset 以及代码示例
    :keywords: Python, Python3, Python set, Python set cheat sheet, set comprehension, set operations, union, intersection, difference, symmetric difference, frozenset, subset, superset

==============
集合（Set）
==============

.. contents:: 目录（Table of Contents）
    :backlinks: none

Sets是Python中唯一的elements的无序collections。它们为成员资格测试提供 O(1) 平均时间复杂度，并支持数学 set 运算，例如并集、交集和差集。本速查表涵盖了 set comprehensions、常见 set 操作、唯一 lists 和 immutable frozenset type。

源代码可在 `GitHub <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/set.py>`_ 上获取。

参考资料（References）
--------------------------------

- `Set Types — set, frozenset <https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset>`_
- `Sets <https://docs.python.org/3/tutorial/datastructures.html#sets>`_

创建一个集合（Create a Set）
----------------------------------------

使用大括号 ``{}`` 或 ``set()`` 构造函数创建 sets。请注意，空花括号 ``{}`` 创建 dict，而不是 set。

.. code-block:: python

    >>> s = {1, 2, 3}
    >>> s
    {1, 2, 3}
    >>> s = set([1, 2, 2, 3])
    >>> s
    {1, 2, 3}
    >>> empty = set()  # 不是 {}
    >>> type(empty)
    <class 'set'>

使用集合推导式创建集合（Create Sets with Set Comprehension）
----------------------------------------------------------------------------------------------

与 list comprehensions 一样，set comprehensions 提供了创建 sets 的简洁方法。该语法使用大括号 ``{}`` 而不是方括号。

.. code-block:: python

    >>> a = [1, 2, 5, 6, 6, 6, 7]
    >>> s = {x for x in a}
    >>> s
    {1, 2, 5, 6, 7}
    >>> s = {x for x in a if x > 3}
    >>> s
    {5, 6, 7}
    >>> s = {x ** 2 for x in range(5)}
    >>> s
    {0, 1, 4, 9, 16}

从列表中删除重复项（Remove Duplicates from a List）
--------------------------------------------------------------------------------

将 list 转换为 set 会自动删除重复的 elements。这是 sets 最常见的用例之一。

.. code-block:: python

    >>> a = [1, 2, 2, 2, 3, 4, 5, 5]
    >>> list(set(a))
    [1, 2, 3, 4, 5]

要保留原始顺序，请使用 ``dict.fromkeys()`` (Python 3.7+)：

.. code-block:: python

    >>> a = [3, 1, 2, 1, 3, 2]
    >>> list(dict.fromkeys(a))
    [3, 1, 2]

向集合添加元素（Add Items to a Set）
------------------------------------------------------

使用 ``add()`` 添加单个 element，或使用 ``update()`` 添加多个 elements。

.. code-block:: python

    >>> s = {1, 2, 3}
    >>> s.add(4)
    >>> s
    {1, 2, 3, 4}
    >>> s.update([5, 6, 7])
    >>> s
    {1, 2, 3, 4, 5, 6, 7}
    >>> s |= {8, 9}  # 与更新相同
    >>> s
    {1, 2, 3, 4, 5, 6, 7, 8, 9}

从集合移除元素（Remove Items from a Set）
----------------------------------------------------------------

使用 ``remove()`` 删除 element（如果未找到，则引发 KeyError），或使用 ``discard()`` 删除而不会出现错误。使用 ``pop()`` 删除任意 element。

.. code-block:: python

    >>> s = {1, 2, 3, 4, 5}
    >>> s.remove(3)
    >>> s
    {1, 2, 4, 5}
    >>> s.discard(10)  # 如果没有找到则没有错误
    >>> s.pop()  # 删除任意element
    1
    >>> s.clear()  # 全部删除
    >>> s
    set()

使用 ``|`` 运算符求并集（Union with ``|`` Operator）
------------------------------------------------------------------------------------

两个 sets 的并集包含来自两个 sets 的所有 elements。使用 ``|`` operator 或 ``union()`` method。

.. code-block:: python

    >>> a = {1, 2, 3}
    >>> b = {3, 4, 5}
    >>> a | b
    {1, 2, 3, 4, 5}
    >>> a.union(b)
    {1, 2, 3, 4, 5}
    >>> a | b | {6, 7}  # 多个 sets
    {1, 2, 3, 4, 5, 6, 7}

使用 ``&`` 运算符求交集（Intersection with ``&`` Operator）
--------------------------------------------------------------------------------------------------

两个sets的交集仅包含两个sets中都存在的elements。使用 ``&`` operator 或 ``intersection()`` method。

.. code-block:: python

    >>> a = {1, 2, 3, 4}
    >>> b = {3, 4, 5, 6}
    >>> a & b
    {3, 4}
    >>> a.intersection(b)
    {3, 4}

查找列表之间的共同元素（Find Common Elements Between Lists）
----------------------------------------------------------------------------------------------

寻找两个lists之间的公共items是set交集的实际应用。

.. code-block:: python

    >>> a = [1, 1, 2, 3]
    >>> b = [3, 5, 5, 6]
    >>> list(set(a) & set(b))
    [3]

使用 ``-`` 运算符求差集（Difference with ``-`` Operator）
----------------------------------------------------------------------------------------------

两个 sets 的 difference 包含存在于第一个 set、但不存在于第二个 set 的 elements。使用 ``-`` operator 或 ``difference()`` method。

.. code-block:: python

    >>> a = {1, 2, 3, 4}
    >>> b = {3, 4, 5, 6}
    >>> a - b
    {1, 2}
    >>> b - a
    {5, 6}

使用 ``^`` 运算符的对称差（Symmetric Difference with ``^`` Operator）
--------------------------------------------------------------------------------------------------------------------

对称差异包含位于任一 set 中的 elements，但不在两者中。使用 ``^`` operator 或 ``symmetric_difference()`` method。

.. code-block:: python

    >>> a = {1, 2, 3}
    >>> b = {3, 4, 5}
    >>> a ^ b
    {1, 2, 4, 5}

使用 ``<=`` 运算符检查子集（Check Subset with ``<=`` Operator）
--------------------------------------------------------------------------------------------------------

使用 ``<=`` 或 ``issubset()`` 检查一个set的所有elements是否在另一个中。使用 ``<`` 为真子集（子集但不相等）。

.. code-block:: python

    >>> a = {1, 2}
    >>> b = {1, 2, 3, 4}
    >>> a <= b  # a 是 b 的子集
    True
    >>> a < b   # a 是真子集
    True
    >>> a <= a  # 等于 sets
    True
    >>> a < a   # 不是真子集
    False

使用 ``>=`` 运算符检查超集（Check Superset with ``>=`` Operator）
------------------------------------------------------------------------------------------------------------

使用 ``>=`` 或 ``issuperset()`` 检查一个 set 是否包含另一个 set 的全部 elements。

.. code-block:: python

    >>> a = {1, 2, 3, 4}
    >>> b = {1, 2}
    >>> a >= b  # a 是 b 的超集
    True
    >>> a > b   # a 是真超集
    True

检查不相交集（Check Disjoint Sets）
------------------------------------------------------

如果两个 sets 没有共同的 elements，则它们是不相交的。使用 ``isdisjoint()`` 进行检查。

.. code-block:: python

    >>> a = {1, 2, 3}
    >>> b = {4, 5, 6}
    >>> a.isdisjoint(b)
    True
    >>> c = {3, 4, 5}
    >>> a.isdisjoint(c)
    False

成员关系测试（Membership Testing）
----------------------------------------------------

Sets 为成员资格测试提供 O(1) 平均时间复杂度，使其比 lists 执行此操作要快得多。

.. code-block:: python

    >>> s = {1, 2, 3, 4, 5}
    >>> 3 in s
    True
    >>> 10 in s
    False
    >>> 10 not in s
    True

Frozenset - 不可变集（Frozenset - Immutable Set）
--------------------------------------------------------------------------------------

``frozenset`` 是 set 的 immutable 版本。它可以用作 dictionary key 或用作另一个 set 的 element。

.. code-block:: python

    >>> fs = frozenset([1, 2, 3])
    >>> fs
    frozenset({1, 2, 3})
    >>> fs.add(4)  # 引发属性错误
    AttributeError: 'frozenset' object has no attribute 'add'

使用 frozenset 作为 dictionary key：

.. code-block:: python

    >>> d = {frozenset([1, 2]): "a", frozenset([3, 4]): "b"}
    >>> d[frozenset([1, 2])]
    'a'

在 set 中使用 frozenset：

.. code-block:: python

    >>> s = {frozenset([1, 2]), frozenset([3, 4])}
    >>> frozenset([1, 2]) in s
    True

集合操作总结（Set Operations Summary）
------------------------------------------------------------

.. code-block:: python

    # 创建
    s = {1, 2, 3}           # literal
    s = set([1, 2, 3])      # 来自 iterable
    s = {x for x in range(5)}  # comprehension

    # 添加/删除
    s.add(x)                # 添加单个element
    s.update([x, y])        # 添加多个elements
    s.remove(x)             # 删除（如果丢失则出现KeyError）
    s.discard(x)            # 删除（如果丢失则不会出错）
    s.pop()                 # 删除任意element
    s.clear()               # 全部删除

    # Set 操作
    a | b                   # 联盟
    a & b                   # 路口
    a - b                   # 不同之处
    a ^ b                   # 对称差异

    # 比较
    a <= b                  # 子集
    a < b                   # 真子集
    a >= b                  # 超集
    a > b                   # 真超集
    a.isdisjoint(b)         # 不常见 elements

    # 会员资格
    x in s                  # O(1) 查找
    x not in s
