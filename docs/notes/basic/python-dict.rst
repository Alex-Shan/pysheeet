.. meta::
    :description lang=zh_CN: Python dictionary 速查表涵盖创建、操作、合并、comprehensions、defaultdict、OrderedDict 和 LRU cache 以及代码示例
    :keywords: Python, Python3, Python dictionary, Python dict cheat sheet, dict, hashmap, key-value pairs, defaultdict, OrderedDict, dictionary comprehension, LRU cache, dict methods

============================
字典（Dictionary）
============================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Dictionaries 是 Python 最强大且最常用的数据结构之一。它们存储 key-value 对，并提供 O(1) 查找、插入和删除的平均时间复杂度。自 Python 3.7 起，dictionaries 将插入顺序保持为语言功能。本速查表涵盖了基本的 dictionary 操作，从基本操作到高级模式，例如使用 special methods 模拟 dictionary 行为以及实现 LRU（最近最少使用）cache。

源代码可在 `GitHub <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/dict.py>`_ 上获取。

参考资料（References）
--------------------------------

- `Mapping Types — dict <https://docs.python.org/3/library/stdtypes.html#mapping-types-dict-frozendict>`_
- `collections — Container datatypes <https://docs.python.org/3/library/collections.html>`_
- `PEP 584：为 dict 添加 Union Operators <https://www.python.org/dev/peps/pep-0584/>`_

使用 ``dict.keys()`` 获取所有键（Get All Keys with ``dict.keys()`` ）
------------------------------------------------------------------------------------------------------------------------

``keys()`` method 返回包含所有 dictionary keys 的视图​​ object。在 Python 3 中，这是反映 dictionary 更改的动态视图。

.. code-block:: python

    >>> a = {"1":1, "2":2, "3":3}
    >>> b = {"2":2, "3":3, "4":4}
    >>> a.keys()
    ['1', '3', '2']

使用 ``dict.items()`` 获取键值对（Get Key-Value Pairs with ``dict.items()`` ）
------------------------------------------------------------------------------------------------------------------------------------------

``items()`` method 将 key-value 对返回为 tuples，这对于同时迭代 keys 和 values 非常有用。

.. code-block:: python

    >>> a = {"1":1, "2":2, "3":3}
    >>> a.items()

查找字典之间的公共键（Find Common Keys Between Dictionaries）
--------------------------------------------------------------------------------------------------

查找多个dictionaries中存在的keys是一个常见的操作。使用 set 交集是最有效的方法。

.. code-block:: python

    >>> a = {"1":1, "2":2, "3":3}
    >>> b = {"2":2, "3":3, "4":4}
    >>> [_ for _ in a.keys() if _ in b.keys()]
    ['3', '2']
    >>> # 更好的方法
    >>> c = set(a).intersection(set(b))
    >>> list(c)
    ['3', '2']
    >>> # 或者
    >>> [_ for _ in a if _ in b]
    ['3', '2']
    [('1', 1), ('3', 3), ('2', 2)]

使用 ``setdefault()`` 和 ``defaultdict`` 设置默认值（Set Default Values with ``setdefault()`` and ``defaultdict`` ）
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

使用 dictionaries 时，您经常需要将 set 默认为 values，以弥补缺少的 keys。 Python为此提供了 ``setdefault()`` 和 ``collections.defaultdict`` 。

.. code-block:: python

    >>> # 直观但不推荐
    >>> d = {}
    >>> key = "foo"
    >>> if key not in d:
    ...     d[key] = []
    ...

    # using d.setdefault(key[, default])
    >>> d = {}
    >>> key = "foo"
    >>> d.setdefault(key, [])
    []
    >>> d[key] = 'bar'
    >>> d
    {'foo': 'bar'}

    # 使用collections.defaultdict
    >>> from collections import defaultdict
    >>> d = defaultdict(list)
    >>> d["key"]
    []
    >>> d["foo"]
    []
    >>> d["foo"].append("bar")
    >>> d
    defaultdict(<class 'list'>, {'key': [], 'foo': ['bar']})

如果 *key* 不在 dictionary 中， ``dict.setdefault(key[, default])`` 返回其默认值 value。但是，如果 key 存在于 dictionary 中，则 function 将返回其 value。

.. code-block:: python

    >>> d = {}
    >>> d.setdefault("key", [])
    []
    >>> d["key"] = "bar"
    >>> d.setdefault("key", [])
    'bar'

使用 ``dict.update()`` 更新字典（Update Dictionary with ``dict.update()`` ）
----------------------------------------------------------------------------------------------------------------------------------------

``update()`` method 将另一个 dictionary 合并到当前 dictionary。第二个 dictionary 中的 keys 会覆盖第一个 dictionary 中已有的 keys。

.. code-block:: python

    >>> a = {"1":1, "2":2, "3":3}
    >>> b = {"2":2, "3":3, "4":4}
    >>> a.update(b)
    >>> a
    {'1': 1, '3': 3, '2': 2, '4': 4}

在 Python 中合并两个字典（Merge Two Dictionaries in Python）
----------------------------------------------------------------------------------------------------

有多种方法可以合并 dictionaries，具体取决于您的 Python 版本。 Python 3.9+ 还支持 ``|`` operator 进行 dictionary 合并。

Python 3.4 或更低

.. code-block:: python

    >>> a = {"x": 55, "y": 66}
    >>> b = {"a": "foo", "b": "bar"}
    >>> c = a.copy()
    >>> c.update(b)
    >>> c
    {'y': 66, 'x': 55, 'b': 'bar', 'a': 'foo'}


Python 3.5 或以上

.. code-block:: python

    >>> a = {"x": 55, "y": 66}
    >>> b = {"a": "foo", "b": "bar"}
    >>> c = {**a, **b}
    >>> c
    {'x': 55, 'y': 66, 'a': 'foo', 'b': 'bar'}

用特殊方法模拟字典（Emulate a Dictionary with Special Methods）
--------------------------------------------------------------------------------------------------------

您可以通过实现 special methods 来创建类似 dictionary 的 objects： ``__getitem__`` 、 ``__setitem__`` 、 ``__delitem__`` 、 ``__contains__`` 和 ``__iter__`` 。

.. code-block:: python

    >>> class EmuDict(object):
    ...   def __init__(self, dict_):
    ...     self._dict = dict_
    ...   def __repr__(self):
    ...     return "EmuDict: " + repr(self._dict)
    ...   def __getitem__(self, key):
    ...     return self._dict[key]
    ...   def __setitem__(self, key, val):
    ...     self._dict[key] = val
    ...   def __delitem__(self, key):
    ...     del self._dict[key]
    ...   def __contains__(self, key):
    ...     return key in self._dict
    ...   def __iter__(self):
    ...     return iter(self._dict.keys())
    ...
    >>> _ = {"1":1, "2":2, "3":3}
    >>> emud = EmuDict(_)
    >>> emud  # __repr__
    EmuDict: {'1': 1, '2': 2, '3': 3}
    >>> emud['1']  # __getitem__
    1
    >>> emud['5'] = 5  # __setitem__
    >>> emud
    EmuDict: {'1': 1, '2': 2, '3': 3, '5': 5}
    >>> del emud['2']  # __delitem__
    >>> emud
    EmuDict: {'1': 1, '3': 3, '5': 5}
    >>> for _ in emud:
    ...     print(emud[_], end=' ')  # __iter__
    ... else:
    ...     print()
    ...
    1 3 5
    >>> '1' in emud  # __contains__
    True

使用 OrderedDict 实现 LRU 缓存（Implement LRU Cache with OrderedDict）
----------------------------------------------------------------------------------------------------------------------------

当 LRU（最近最少使用）cache 已满时，将逐出最近最少访问的 items。 ``OrderedDict.move_to_end()`` 使实施变得简单。

.. code-block:: python

	from collections import OrderedDict


	class LRU(object):
		def __init__(self, maxsize=128):
			self._maxsize = maxsize
			self._cache = OrderedDict()

		def get(self, k):
			if k not in self._cache:
				return None

			self._cache.move_to_end(k)
			return self._cache[k]

		def put(self, k, v):
			if k in self._cache:
				self._cache.move_to_end(k)
			self._cache[k] = v
			if len(self._cache) > self._maxsize:
				self._cache.popitem(last=False)

		def __str__(self):
			return str(self._cache)

		def __repr__(self):
			return self.__str__()

请注意，dictionaries 保留 Python 3.7 的插入顺序。而且，更新key不会影响订单。因此，dictionary 也可以模拟 LRU cache，这与使用 OrderedDict 类似。

.. code-block:: python

	class LRU(object):
		def __init__(self, maxsize=128):
			self._maxsize = maxsize
			self._cache = {}

		def get(self, k):
			if k not in self._cache:
				return None

			self.move_to_end(k)
			return self._cache[k]

		def put(self, k, v):
			if k in self._cache:
				self.move_to_end(k)
			self._cache[k] = v
			if len(self._cache) > self._maxsize:
				self.pop()

		def pop(self):
			it = iter(self._cache.keys())
			del self._cache[next(it)]

		def move_to_end(self, k):
			if k not in self._cache:
				return
			v = self._cache[k]
			del self._cache[k]
			self._cache[k] = v

		def __str__(self):
			return str(self._cache)

		def __repr__(self):
			return self.__str__()
