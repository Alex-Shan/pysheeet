.. meta::
    :description lang=zh_CN: Python list 速查表涵盖 list 操作、comprehensions、切片、排序、过滤和常见的 list 操作模式以及代码示例
    :keywords: Python, Python3, Python list, Python list cheat sheet, list comprehension, slicing, sorting, filtering, append, extend, iteration

================
列表（List）
================

.. contents:: 目录（Table of Contents）
    :backlinks: none

list 是我们用来存储 objects 的常见数据结构。大多数时候，程序员关心的是获取、设置、搜索、过滤和排序。此外，有时我们会陷入内存管理的常见陷阱。因此，本速查表的主要目标是收集一些常见的操作和陷阱。

Python列表基础知识和常用操作（Python List Basics and Common Operations）
----------------------------------------------------------------------------------------------------------------------

我们可以通过多种方式来操纵Python中的lists。在我们开始学习这些通用操作之前，以下代码片段显示了 lists 最常见的操作。

.. code-block:: python

    >>> a = [1, 2, 3, 4, 5]
    >>> # 包含
    >>> 2 in a
    True
    >>> # 正向 index
    >>> a[0]
    1
    >>> # 负向 index
    >>> a[-1]
    5
    >>> # 切片 list[start:end:step]
    >>> a[1:]
    [2, 3, 4, 5]
    >>> a[1:-1]
    [2, 3, 4]
    >>> a[1:-1:2]
    [2, 4]
    >>> # 反转
    >>> a[::-1]
    [5, 4, 3, 2, 1]
    >>> a[:0:-1]
    [5, 4, 3, 2]
    >>> # 设置 item
    >>> a[0] = 0
    >>> a
    [0, 2, 3, 4, 5]
    >>> # 将 items 附加到 list
    >>> a.append(6)
    >>> a
    [0, 2, 3, 4, 5, 6]
    >>> a.extend([7, 8, 9])
    >>> a
    [0, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> # 删除 item
    >>> del a[-1]
    >>> a
    [0, 2, 3, 4, 5, 6, 7, 8]
    >>> # list comprehension
    >>> b = [x for x in range(3)]
    >>> b
    [0, 1, 2]
    >>> # 添加两个lists
    >>> a + b
    [0, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2]

使用乘法运算符初始化列表（Initialize Lists with Multiplication Operator）
----------------------------------------------------------------------------------------------------------------------

一般来说，如果list expression中的item是immutable object，我们可以通过 ``*`` operator创建list。

.. code-block:: python

    >>> a = [None] * 3
    >>> a
    [None, None, None]
    >>> a[0] = "foo"
    >>> a
    ['foo', None, None]

但是，如果list expression中的item是mutable object，则 ``*`` operator将复制item的引用N次。为了避免这个陷阱，我们应该使用list comprehension来初始化list。

.. code-block:: python

    >>> a = [[]] * 3
    >>> b = [[] for _ in range(3)]
    >>> a[0].append("Hello")
    >>> a
    [['Hello'], ['Hello'], ['Hello']]
    >>> b[0].append("Python")
    >>> b
    [['Python'], [], []]

复制列表：浅复制与深复制（Copy Lists: Shallow vs Deep Copy）
--------------------------------------------------------------------------------------------

将 list 分配给 variable 是一个常见的陷阱。此分配不会将 list 复制到 variable。 variable仅指list并增加list的reference count。

.. code-block:: python

    import sys
    >>> a = [1, 2, 3]
    >>> sys.getrefcount(a)
    2
    >>> b = a
    >>> sys.getrefcount(a)
    3
    >>> b[2] = 123456  # a[2] = 123456
    >>> b
    [1, 2, 123456]
    >>> a
    [1, 2, 123456]

types 副本有两份。第一个称为 *shallow copy* （非 recursive 副本），第二个称为 *deep copy* （recursive 副本）。大多数时候，我们通过shallow copy复制一个list就足够了。但是，如果 list 是嵌套的，我们必须使用 deep copy。

.. code-block:: python

    >>> # shallow copy
    >>> a = [1, 2]
    >>> b = list(a)
    >>> b[0] = 123
    >>> a
    [1, 2]
    >>> b
    [123, 2]
    >>> a = [[1], [2]]
    >>> b = list(a)
    >>> b[0][0] = 123
    >>> a
    [[123], [2]]
    >>> b
    [[123], [2]]
    >>> # deep copy
    >>> import copy
    >>> a = [[1], [2]]
    >>> b = copy.deepcopy(a)
    >>> b[0][0] = 123
    >>> a
    [[1], [2]]
    >>> b
    [[123], [2]]

使用 slice 对象切分列表（Slice Lists with slice Objects）
----------------------------------------------------------------------------------------------

有时，我们的数据可能会连接成一个大段，例如数据包。在这种情况下，我们将使用 ``slice`` objects 来表示数据的 range 作为解释 variables，而不是使用*切片 expressions*。

.. code-block:: python

    >>> icmp = (
    ...     b"080062988e2100005bff49c20005767c"
    ...     b"08090a0b0c0d0e0f1011121314151617"
    ...     b"18191a1b1c1d1e1f2021222324252627"
    ...     b"28292a2b2c2d2e2f3031323334353637"
    ... )
    >>> head = slice(0, 32)
    >>> data = slice(32, len(icmp))
    >>> icmp[head]
    b'080062988e2100005bff49c20005767c'

使用列表推导式创建列表（Create Lists with List Comprehensions）
----------------------------------------------------------------------------------------------------

PEP `202 <https://www.python.org/dev/peps/pep-0202/>`_ 中提出的 `List comprehensions <https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions>`_ 提供了一种优雅的方式来基于另一个 list、序列或某些 object（即 iterable）创建新的 list。另外，有时我们可以用这个expression来代替 ``map`` 和 ``filter`` 。

.. code-block:: python

    >>> [x for x in range(10)]
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> [(lambda x: x**2)(i) for i in range(10)]
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> [x for x in range(10) if x > 5]
    [6, 7, 8, 9]
    >>> [x if x > 5 else 0 for x in range(10)]
    [0, 0, 0, 0, 0, 0, 6, 7, 8, 9]
    >>> [x + 1 if x < 5 else x + 2 if x > 5 else x + 5 for x in range(10)]
    [1, 2, 3, 4, 5, 10, 8, 9, 10, 11]
    >>> [(x, y) for x in range(3) for y in range(2)]
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

将列表解包到变量（Unpack Lists into Variables）
--------------------------------------------------------------------------

有时，我们想将 list 解包为 variables，以使我们的代码变得更具可读性。在这种情况下，我们将 N elements 分配给 N variables，如下例所示。

.. code-block:: python

    >>> arr = [1, 2, 3]
    >>> a, b, c = arr
    >>> a, b, c
    (1, 2, 3)

基于PEP `3132 <https://www.python.org/dev/peps/pep-3132>`_ ，我们可以使用单个星号将N个elements解压到Python 3中小于N的variables的数量。

.. code-block:: python

    >>> arr = [1, 2, 3, 4, 5]
    >>> a, b, *c, d = arr
    >>> a, b, d
    (1, 2, 5)
    >>> c
    [3, 4]

使用 enumerate() 带索引迭代（Iterate with Index Using enumerate()）
--------------------------------------------------------------------------------------------------------------------

``enumerate`` 是内置 function。它帮助我们同时获取indexes（或计数）和elements，而无需使用 ``range(len(list))`` 。更多信息请参见 `Looping Techniques <https://docs.python.org/3/tutorial/datastructures.html#looping-techniques>`_ 。

.. code-block:: python

    >>> for i, v in enumerate(range(3)):
    ...     print(i, v)
    ...
    0 0
    1 1
    2 2
    >>> for i, v in enumerate(range(3), 1): # start = 1
    ...     print(i, v)
    ...
    1 0
    2 1
    3 2

与 zip() 合并列表（Combine Lists with zip()）
----------------------------------------------------------------------------

`zip <https://docs.python.org/3/library/functions.html#zip>`_ 使我们能够一次迭代多个 lists 中包含的 items。每当 lists 之一耗尽时，Iteration 就会停止。因此，iteration 的长度与最短的 list 相同。如果不需要这种行为，我们可以在 **Python 3**中使用 ``itertools.zip_longest`` 或在**Python 2** 中使用 ``itertools.izip_longest`` 。

.. code-block:: python

    >>> a = [1, 2, 3]
    >>> b = [4, 5, 6]
    >>> list(zip(a, b))
    [(1, 4), (2, 5), (3, 6)]
    >>> c = [1]
    >>> list(zip(a, b, c))
    [(1, 4, 1)]
    >>> from itertools import zip_longest
    >>> list(zip_longest(a, b, c))
    [(1, 4, 1), (2, 5, None), (3, 6, None)]


过滤列表项（Filter List Items）
------------------------------------------------

`filter <https://docs.python.org/3/library/functions.html#filter>`_ 是内置的function，帮助我们删除不必要的items。在 **Python 2**中， ``filter`` 返回 list。但是，在**Python 3** 中， ``filter`` 返回 *iterable object*。请注意，*list comprehension* 或 *generator expression* 提供了一种更简洁的方法来删除 items。

.. code-block:: python

    >>> [x for x in range(5) if x > 1]
    [2, 3, 4]
    >>> l = ['1', '2', 3, 'Hello', 4]
    >>> f = lambda x: isinstance(x, int)
    >>> filter(f, l)
    <filter object at 0x10bee2198>
    >>> list(filter(f, l))
    [3, 4]
    >>> list((i for i in l if f(i)))
    [3, 4]

用列表实现堆栈（Implement Stack with List）
--------------------------------------------------------------------

Python 中不需要额外的数据结构 stack，因为 ``list`` 提供了 ``append`` 和 ``pop`` methods，这使我们能够将 list 用作 stack。

.. code-block:: python

    >>> stack = []
    >>> stack.append(1)
    >>> stack.append(2)
    >>> stack.append(3)
    >>> stack
    [1, 2, 3]
    >>> stack.pop()
    3
    >>> stack.pop()
    2
    >>> stack
    [1]

使用 in 运算符检查成员关系（Check Membership with in Operator）
----------------------------------------------------------------------------------------------------

我们可以实现 ``__contains__`` method 来使 class 执行 ``in`` 操作。程序员模拟自定义 classes 的成员资格测试操作是一种常用方法。

.. code-block:: python

    class Stack:

        def __init__(self):
            self.__list = []

        def push(self, val):
            self.__list.append(val)

        def pop(self):
            return self.__list.pop()

        def __contains__(self, item):
            return True if item in self.__list else False

    stack = Stack()
    stack.push(1)
    print(1 in stack)
    print(0 in stack)

例子

.. code-block:: bash

    python stack.py
    True
    False

使用 __getitem__ 和 __setitem__ 访问元素（Access Items with __getitem__ and __setitem__）
----------------------------------------------------------------------------------------------------------------------------------------------------------------

让自定义 classes 像 lists 一样执行 get 和 set 操作很简单。我们可以实现 ``__getitem__`` method 和 ``__setitem__`` method 来使 class 能够检索和覆盖 index 的数据。另外，如果我们想用function、 ``len`` 来计算elements的个数，我们可以实现一个 ``__len__`` method。

.. code-block:: python

    class Stack:

        def __init__(self):
            self.__list = []

        def push(self, val):
            self.__list.append(val)

        def pop(self):
            return self.__list.pop()

        def __repr__(self):
            return "{}".format(self.__list)

        def __len__(self):
            return len(self.__list)

        def __getitem__(self, idx):
            return self.__list[idx]

        def __setitem__(self, idx, val):
            self.__list[idx] = val


    stack = Stack()
    stack.push(1)
    stack.push(2)
    print("stack:", stack)

    stack[0] = 3
    print("stack:", stack)
    print("num items:", len(stack))

例子

.. code-block:: bash

    $ python stack.py
    stack: [1, 2]
    stack: [3, 2]
    num items: 2

使用 __iter__ 进行委托迭代（Delegate Iteration with __iter__）
--------------------------------------------------------------------------------------------------------

如果自定义容器 class 持有 list 并且我们希望迭代在容器上工作，我们可以实现 ``__iter__`` method 将迭代委托给 list。请注意，method、 ``__iter__`` 应该返回 *iterator object*，因此我们不能直接返回 list；否则，Python 引发 ``TypeError`` 。

.. code-block:: python

    class Stack:

        def __init__(self):
            self.__list = []

        def push(self, val):
            self.__list.append(val)

        def pop(self):
            return self.__list.pop()

        def __iter__(self):
            return iter(self.__list)

    stack = Stack()
    stack.push(1)
    stack.push(2)
    for s in stack:
        print(s)

例子

.. code-block:: bash

    $ python stack.py
    1
    2

使用 sort() 和 sorted() 对列表进行排序（Sort Lists with sort() and sorted()）
----------------------------------------------------------------------------------------------------------------------------------

Python list 提供内置的 ``list.sort`` method，无需使用额外的内存即可对 list `in-place <https://en.wikipedia.org/wiki/In-place_algorithm>`_ 进行排序。另外，为了避免与 ``sorted`` 混淆， ``list.sort`` 的return value为 ``None`` ，而function只能用于 ``list`` 。

.. code-block:: python

    >>> l = [5, 4, 3, 2, 1]
    >>> l.sort()
    >>> l
    [1, 2, 3, 4, 5]
    >>> l.sort(reverse=True)
    >>> l
    [5, 4, 3, 2, 1]

``sorted`` function 不会就地修改任何 iterable object。相反，它返回一个新排序的 list。如果某些 list 的 elements 是只读的或 immutable，则使用 ``sorted`` 比 ``list.sort`` 更安全。此外， ``list.sort`` 和 ``sorted`` 之间的另一个区别是 ``sorted`` 接受任何 **iterable对象** 。

.. code-block:: python

    >>> l = [5, 4, 3, 2, 1]
    >>> new = sorted(l)
    >>> new
    [1, 2, 3, 4, 5]
    >>> l
    [5, 4, 3, 2, 1]
    >>> d = {3: 'andy', 2: 'david', 1: 'amy'}
    >>> sorted(d)  # 排序 iterable
    [1, 2, 3]

要对 list 及其 elements 为 tuples 进行排序，使用 ``operator.itemgetter`` 很有帮助，因为它将 key function 分配给 ``sorted`` key parameter。注意key应该是可比的；否则，它将引发 ``TypeError`` 。

.. code-block:: python

    >>> from operator import itemgetter
    >>> l = [('andy', 10), ('david', 8), ('amy', 3)]
    >>> l.sort(key=itemgetter(1))
    >>> l
    [('amy', 3), ('david', 8), ('andy', 10)]

``operator.itemgetter`` 很有用，因为 function 返回 getter method 可适用于其他 objects 和 method ``__getitem__`` 。 例如， 将 list 与其 elements 排序为 dictionary 可以通过使用 ``operator.itemgetter`` 来实现，因为所有 elements 都具有 ``__getitem__`` 。

.. code-block:: python

    >>> from pprint import pprint
    >>> from operator import itemgetter
    >>> l = [
    ...     {'name': 'andy', 'age': 10},
    ...     {'name': 'david', 'age': 8},
    ...     {'name': 'amy', 'age': 3},
    ... ]
    >>> l.sort(key=itemgetter('age'))
    >>> pprint(l)
    [{'age': 3, 'name': 'amy'},
     {'age': 8, 'name': 'david'},
     {'age': 10, 'name': 'andy'}]

如果需要对 list 与其 elements 既不具有可比性又不具有 ``__getitem__`` method 进行排序，则分配自定义的 key function 是可行的。

.. code-block:: python

    >>> class Node(object):
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __repr__(self):
    ...         return f"Node({self.val})"
    ...
    >>> nodes = [Node(3), Node(2), Node(1)]
    >>> nodes.sort(key=lambda x: x.val)
    >>> nodes
    [Node(1), Node(2), Node(3)]
    >>> nodes.sort(key=lambda x: x.val, reverse=True)
    >>> nodes
    [Node(3), Node(2), Node(1)]

可以使用 ``operator.attrgetter`` 来简化上面的代码片段。 function 根据 attribute 的名称返回 attribute getter。注意attribute应该是可比的；否则， ``sorted`` 或 ``list.sort`` 将提高 ``TypeError`` 。

.. code-block:: python

    >>> from operator import attrgetter
    >>> class Node(object):
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __repr__(self):
    ...         return f"Node({self.val})"
    ...
    >>> nodes = [Node(3), Node(2), Node(1)]
    >>> nodes.sort(key=attrgetter('val'))
    >>> nodes
    [Node(1), Node(2), Node(3)]

如果 object 具有 ``__lt__`` method，则意味着 object 具有可比性，并且 ``sorted`` 或 ``list.sort`` 不需要将 key function 输入到其 key parameter。可以直接对 list 或 iterable 序列进行排序。

.. code-block:: python

    >>> class Node(object):
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __repr__(self):
    ...         return f"Node({self.val})"
    ...     def __lt__(self, other):
    ...         return self.val - other.val < 0
    ...
    >>> nodes = [Node(3), Node(2), Node(1)]
    >>> nodes.sort()
    >>> nodes
    [Node(1), Node(2), Node(3)]

如果 object 没有 ``__lt__`` method，则很可能在声明 object 的 class 后修补 method。也就是说，打补丁后，object就变得具有可比性了。

.. code-block:: python

    >>> class Node(object):
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __repr__(self):
    ...         return f"Node({self.val})"
    ...
    >>> Node.__lt__ = lambda s, o: s.val < o.val
    >>> nodes = [Node(3), Node(2), Node(1)]
    >>> nodes.sort()
    >>> nodes
    [Node(1), Node(2), Node(3)]

请注意，Python3 中的 ``sorted`` 或 ``list.sort`` 不支持 ``cmp`` parameter，它是 Python2 中的 **ONLY** 有效的 argument。如果需要使用旧的比较 function、e.g。某些遗留代码， ``functools.cmp_to_key`` 很有用，因为它将比较 function 转换为 key function。

.. code-block:: python

    >>> from functools import cmp_to_key
    >>> class Node(object):
    ...     def __init__(self, val):
    ...         self.val = val
    ...     def __repr__(self):
    ...         return f"Node({self.val})"
    ...
    >>> nodes = [Node(3), Node(2), Node(1)]
    >>> nodes.sort(key=cmp_to_key(lambda x,y: x.val - y.val))
    >>> nodes
    [Node(1), Node(2), Node(3)]

使用 bisect 维护有序列表（Maintain Sorted List with bisect）
----------------------------------------------------------------------------------------------------

`bisect <https://docs.python.org/3/library/bisect.html>`_ module 提供 functions 以按排序顺序维护 list，而无需在每次插入后对 list 进行排序。它使用二分搜索算法，使得大型 lists 的插入高效。

.. code-block:: python

    import bisect

    class Foo(object):
        def __init__(self, k):
            self.k = k

        def __eq__(self, rhs):
            return self.k == rhs.k

        def __ne__(self, rhs):
            return self.k != rhs.k

        def __lt__(self, rhs):
            return self.k < rhs.k

        def __gt__(self, rhs):
            return self.k > rhs.k

        def __le__(self, rhs):
            return self.k <= rhs.k

        def __ge__(self, rhs):
            return self.k >= rhs.k

        def __repr__(self):
            return f"Foo({self.k})"

        def __str__(self):
            return self.__repr__()

    foo = [Foo(1), Foo(3), Foo(2), Foo(0)]
    bar = []
    for x in foo:
        bisect.insort(bar, x)

    print(bar) # [Foo(0)、Foo(1)、Foo(2)、Foo(3)]

正确创建嵌套列表（Create Nested Lists Correctly）
------------------------------------------------------------------------------

创建嵌套lists（2D lists或矩阵）时，我们应该使用list comprehension来确保每个内部list都是一个单独的object。以下代码片段显示了创建 2D list 的正确方法。

.. code-block:: python

    # new a list with size = 3

    >>> [0] * 3
    [0, 0, 0]

    # 新的 2d list，尺寸为 3x3

    >>> [[0] * 3 for _ in range(3)]
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

请注意，我们应该避免通过以下代码片段创建多维 list，因为 list 中的所有 objects 都指向同一地址。

.. code-block:: python

    >>> a = [[0] * 3] * 3
    >>> a
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    >>> a[1][1] = 2
    >>> a
    [[0, 2, 0], [0, 2, 0], [0, 2, 0]]


使用 deque 实现环形缓冲区（Implement Circular Buffer with deque）
------------------------------------------------------------------------------------------------------------

`collections.deque <https://docs.python.org/3/library/collections.html#collections.deque>`_ 是 double-ended queue，支持在两端高效添加和移除 elements。设置 ``maxlen`` 可以创建 circular buffer，在添加新 elements 时自动丢弃旧 elements。

.. code-block:: python

    >>> from collections import deque
    >>> d = deque(maxlen=8)
    >>> for x in range(9):
    ...     d.append(x)
    ...
    >>> d
    deque([1, 2, 3, 4, 5, 6, 7, 8], maxlen=8)

以下示例显示如何使用 ``deque`` 实现类似于 Unix 命令的 ``tail`` function。

.. code-block:: python

    >>> from collections import deque
    >>> def tail(path, n=10):
    ...     with open(path) as f:
    ...         return deque(f, n)
    ...
    >>> tail("/etc/hosts")

将列表拆分为块（Split List into Chunks）
--------------------------------------------------------------

有时，我们需要将 list 拆分为特定大小的较小块。以下 generator function 从 list 生成连续的块。

.. code-block:: python

    >>> def chunk(lst, n):
    ...     for i in range(0, len(lst), n):
    ...         yield lst[i:i+n]
    ...
    >>> a = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(chunk(a, 3))
    [[1, 2, 3], [4, 5, 6], [7, 8]]

使用 itertools.groupby 对连续元素进行分组（Group Consecutive Elements with itertools.groupby）
------------------------------------------------------------------------------------------------------------------------------------------------------------------

`itertools.groupby <https://docs.python.org/3/library/itertools.html#itertools.groupby>`_ 将具有相同 key 的连续 elements 分组到 iterable 中。它对于游程长度 encoding 或对排序数据进行分组很有用。

.. code-block:: python

    >>> import itertools
    >>> s = "AAABBCCCCC"
    >>> for k, v in itertools.groupby(s):
    ...     print(k, list(v))
    ...
    A ['A', 'A', 'A']
    B ['B', 'B']
    C ['C', 'C', 'C', 'C', 'C']

    # 按 key 分组

    >>> x = [('gp1', 'a'), ('gp2', 'b'), ('gp2', 'c')]
    >>> for k, v in itertools.groupby(x, lambda x: x[0]):
    ...     print(k, list(v))
    ...
    gp1 [('gp1', 'a')]
    gp2 [('gp2', 'b'), ('gp2', 'c')]

排序列表中的二分查找（Binary Search in Sorted List）
--------------------------------------------------------------------------------

二分查找是一种在已排序的 list 中查找 item 的有效算法。以下代码片段展示了如何使用 ``bisect_left`` 实现二分搜索。

.. code-block:: python

    >>> def binary_search(arr, x, lo=0, hi=None):
    ...     if not hi: hi = len(arr)
    ...     pos = bisect_left(arr, x, lo, hi)
    ...     return pos if pos != hi and arr[pos] == x else -1
    ...
    >>> a = [1, 1, 1, 2, 3]
    >>> binary_search(a, 1)
    0
    >>> binary_search(a, 2)
    3

使用 bisect_left 查找下界（Find Lower Bound with bisect_left）
------------------------------------------------------------------------------------------------------------

``bisect_left`` 返回可以插入 element 以保持 list 排序的最左边位置。这相当于找到下界。

.. code-block:: python

    >>> import bisect
    >>> a = [1,2,3,3,4,5]
    >>> bisect.bisect_left(a, 3)
    2
    >>> bisect.bisect_left(a, 3.5)
    4

使用 bisect_right 求上界（Find Upper Bound with bisect_right）
--------------------------------------------------------------------------------------------------------------

``bisect_right`` （或 ``bisect`` ）返回可以插入element以保持list排序的最右边位置。这相当于找到上限。

.. code-block:: python

    >>> import bisect
    >>> a = [1,2,3,3,4,5]
    >>> bisect.bisect_right(a, 3)
    4
    >>> bisect.bisect_right(a, 3.5)
    4

按字典顺序对元组排序（Sort Tuples Lexicographically）
----------------------------------------------------------------------------------

默认情况下，Python 按字典顺序比较 tuples 和 lists。这意味着它会比较第一个 elements，如果它们相等，则会比较第二个 elements，依此类推。

.. code-block:: python

    # python compare lists lexicographically

    >>> a = [(1,2), (1,1), (1,0), (2,1)]
    >>> a.sort()
    >>> a
    [(1, 0), (1, 1), (1, 2), (2, 1)]

实现 Trie（前缀树）（Implement Trie (Prefix Tree)）
------------------------------------------------------------------------------------

`Trie <https://en.wikipedia.org/wiki/Trie>`_ （前缀树）是一种树数据结构，用于在strings数据集中高效检索keys。以下代码片段显示了使用 ``defaultdict`` 的紧凑实现。

.. code-block:: python

    >>> from functools import reduce
    >>> from collections import defaultdict
    >>> Trie = lambda: defaultdict(Trie)
    >>> prefixes = ['abc', 'de', 'g']
    >>> trie = Trie()
    >>> end = True
    >>> for p in prefixes:
    ...     reduce(dict.__getitem__, p, trie)[end] = p
    ...

    # 搜索前缀

    >>> def find(trie, word):
    ...     curr = trie
    ...     for c in word:
    ...         if c not in curr:
    ...             return False
    ...         curr = curr[c]
    ...     return True
    ...
    >>> find(trie, "abcdef")
    False
    >>> find(trie, "abc")
    True
    >>> find(trie, "ab")
    True

    # 搜索词

    >>> def find(trie, p):
    ...     curr = trie
    ...     for c in p:
    ...         if c not in curr or True in curr:
    ...             break
    ...         curr = curr[c]
    ...     return True if True in curr else False
    ...
    >>> find(trie, "abcdef")
    True
    >>> find(trie, "abc")
    True
    >>> find(trie, "ab")
    False
