.. meta::
    :description lang=zh_CN: Python 堆和优先级 queue 速查表涵盖 heapq module 操作、堆排序算法、使用自定义比较器的优先级 queue 实现以及实际示例
    :keywords: Python, Python Cheat Sheet, heap, heapq, priority queue, heap sort, min heap, max heap, Python heapq, nlargest, nsmallest

==============
堆（Heap）
==============

.. contents:: 目录（Table of Contents）
    :backlinks: none

heapq module 提供堆 queue 算法的实现，也称为优先级 queue 算法。堆是二叉树，其中每个父节点的 value 小于或等于其任何子节点（最小堆）。本速查表涵盖了堆操作，包括堆排序、优先级 queues、合并排序 iterables 以及有效查找 n 个最大或最小的 elements。

源代码可在 `GitHub <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/heap.py>`_ 上获取。

参考资料（References）
--------------------------------

- `heapq — Heap queue algorithm <https://docs.python.org/3/library/heapq.html>`_
- `queue.PriorityQueue <https://docs.python.org/3/library/queue.html#queue.PriorityQueue>`_

基本堆操作（Basic Heap Operations）
--------------------------------------------------------

``heapq`` module 提供 functions 来创建和操作堆。使用 ``heapify`` 在 O(n) 时间内将 list 就地转换为堆。使用 ``heappush`` 和 ``heappop`` 添加和删除 elements，同时维护堆 property。

.. code-block:: python

    >>> import heapq
    >>> # 将 list 就地转换为堆
    >>> h = [5, 1, 3, 2, 6]
    >>> heapq.heapify(h)
    >>> h[0]  # 根处最小的 element
    1
    >>> # 推入和弹出
    >>> heapq.heappush(h, 0)
    >>> heapq.heappop(h)
    0
    >>> # 一次操作即可推送和弹出
    >>> heapq.heappushpop(h, 4)  # 推入 4，然后弹出最小的
    1
    >>> # 一次操作即可弹出和推送
    >>> heapq.heapreplace(h, 0)  # 弹出最小的，然后压入 0
    2

使用 ``heapq`` 实现堆排序（Implement Heap Sort with ``heapq`` ）
--------------------------------------------------------------------------------------------------------------

堆排序的工作原理是将所有 elements 推入堆中，然后将它们一一弹出。由于堆维护最小堆 property，因此 elements 按排序顺序出现。时间复杂度为O(n log n)。

.. code-block:: python

    >>> import heapq
    >>> a = [5, 1, 3, 2, 6]
    >>> h = []
    >>> for x in a:
    ...     heapq.heappush(h, x)
    ...
    >>> x = [heapq.heappop(h) for _ in range(len(a))]
    >>> x
    [1, 2, 3, 5, 6]

更有效的方法是使用 ``heapify`` 就地转换 list：

.. code-block:: python

    >>> import heapq
    >>> def heap_sort(items):
    ...     h = items.copy()
    ...     heapq.heapify(h)
    ...     return [heapq.heappop(h) for _ in range(len(h))]
    ...
    >>> heap_sort([5, 1, 3, 2, 6])
    [1, 2, 3, 5, 6]

实现最大堆（Implement Max Heap）
--------------------------------------------------

Python的 ``heapq`` 仅提供最小堆。要实现最大堆，请在压入时对 values 取反，并在弹出时再次取反。

.. code-block:: python

    >>> import heapq
    >>> # 使用否定的最大堆
    >>> h = []
    >>> for x in [5, 1, 3, 2, 6]:
    ...     heapq.heappush(h, -x)
    ...
    >>> [-heapq.heappop(h) for _ in range(len(h))]
    [6, 5, 3, 2, 1]

对于自定义objects，通过反向比较实现 ``__lt__`` ：

.. code-block:: python

    import heapq

    class MaxHeapItem:
        def __init__(self, val):
            self.val = val

        def __lt__(self, other):
            return self.val > other.val  # 反转最大堆

    h = []
    for x in [5, 1, 3]:
        heapq.heappush(h, MaxHeapItem(x))

    print(heapq.heappop(h).val)  # 5（最大）

使用 ``heapq`` 实现优先级队列（Implement Priority Queue with ``heapq`` ）
----------------------------------------------------------------------------------------------------------------------------

优先级 queue processes elements 基于其优先级而不是插入顺序。使用 tuples ``(priority, value)`` ，其中数字越低表示优先级越高。

.. code-block:: python

    >>> import heapq
    >>> pq = []
    >>> heapq.heappush(pq, (2, "medium"))
    >>> heapq.heappush(pq, (1, "high"))
    >>> heapq.heappush(pq, (3, "low"))
    >>> [heapq.heappop(pq) for _ in range(len(pq))]
    [(1, 'high'), (2, 'medium'), (3, 'low')]

对于自定义 objects，实现 ``__lt__`` method 来定义比较行为：

.. code-block:: python

    import heapq

    class Task:
        def __init__(self, priority, name):
            self.priority = priority
            self.name = name

        def __lt__(self, other):
            return self.priority < other.priority

        def __repr__(self):
            return f"Task({self.priority}, {self.name!r})"

    h = []
    heapq.heappush(h, Task(3, "low"))
    heapq.heappush(h, Task(1, "high"))
    heapq.heappush(h, Task(2, "medium"))

    while h:
        print(heapq.heappop(h))
    # Task(1, 'high')
    # Task(2, 'medium')
    # Task(3, 'low')

查找 K 个最大或最小元素（Find K Largest or Smallest Elements）
----------------------------------------------------------------------------------------------------

``nlargest`` 和 ``nsmallest`` functions 有效地找到 k 个最大或最小的 elements。当 k 相对于 list 大小较小时，它们比排序更有效。

.. code-block:: python

    >>> import heapq
    >>> nums = [5, 1, 8, 3, 9, 2, 7]
    >>> heapq.nsmallest(3, nums)
    [1, 2, 3]
    >>> heapq.nlargest(3, nums)
    [9, 8, 7]

使用 ``key`` parameter 从 complex objects 中提取比较 keys：

.. code-block:: python

    >>> import heapq
    >>> data = [
    ...     {'name': 'Alice', 'score': 85},
    ...     {'name': 'Bob', 'score': 92},
    ...     {'name': 'Charlie', 'score': 78},
    ... ]
    >>> heapq.nlargest(2, data, key=lambda x: x['score'])
    [{'name': 'Bob', 'score': 92}, {'name': 'Alice', 'score': 85}]

合并有序可迭代对象（Merge Sorted Iterables）
------------------------------------------------------------------

``merge`` function 将多个排序输入合并为一个排序输出。它返回 iterator，使其对于大型数据集而言具有内存效率。

.. code-block:: python

    >>> import heapq
    >>> a = [1, 3, 5, 7]
    >>> b = [2, 4, 6, 8]
    >>> c = [0, 9, 10]
    >>> list(heapq.merge(a, b, c))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

使用 ``key`` 和 ``reverse`` parameters 进行自定义合并：

.. code-block:: python

    >>> import heapq
    >>> # 按降序合并
    >>> a = [5, 3, 1]
    >>> b = [6, 4, 2]
    >>> list(heapq.merge(a, b, reverse=True))
    [6, 5, 4, 3, 2, 1]

维护固定大小的堆（Maintain a Fixed-Size Heap）
------------------------------------------------------------------------

要维护固定大小 k 的堆（e.g.，跟踪顶部 k elements），请使用 ``heappushpop`` 或在每次推送后检查大小。

.. code-block:: python

    >>> import heapq
    >>> def top_k(items, k):
    ...     """Keep track of k largest elements using min-heap."""
    ...     h = []
    ...     for x in items:
    ...         if len(h) < k:
    ...             heapq.heappush(h, x)
    ...         elif x > h[0]:
    ...             heapq.heapreplace(h, x)
    ...     return sorted(h, reverse=True)
    ...
    >>> top_k([5, 1, 8, 3, 9, 2, 7, 4, 6], 3)
    [9, 8, 7]

带索引跟踪的堆（Heap with Index Tracking）
------------------------------------------------------------------

当您需要更新堆中的优先级时，请使用 dictionary 来跟踪 element 位置或将条目标记为无效。

.. code-block:: python

    import heapq

    class IndexedHeap:
        def __init__(self):
            self.heap = []
            self.entry_finder = {}
            self.REMOVED = '<removed>'

        def push(self, item, priority):
            if item in self.entry_finder:
                self.remove(item)
            entry = [priority, item]
            self.entry_finder[item] = entry
            heapq.heappush(self.heap, entry)

        def remove(self, item):
            entry = self.entry_finder.pop(item)
            entry[-1] = self.REMOVED

        def pop(self):
            while self.heap:
                priority, item = heapq.heappop(self.heap)
                if item is not self.REMOVED:
                    del self.entry_finder[item]
                    return item
            raise KeyError('pop from empty heap')

    # 用法
    h = IndexedHeap()
    h.push('task1', 3)
    h.push('task2', 1)
    h.push('task1', 0)  # 更新优先级
    print(h.pop())  # 任务1（现在优先级为0）
