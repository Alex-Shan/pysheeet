==================================================================================
Python 面试速查表（Python Interview Cheatsheet）
==================================================================================

.. meta::
    :description lang=zh_CN: 精心策划的 Python 面试问题，每个问题都直接链接到回答该问题的确切速查表部分。涵盖核心语言基础知识、数据结构、functions 和 decorators、iterators 和 generators、OOP 和 dunder methods、并发性和 GIL、asyncio、常见问题、C 扩展、数据库、网络和安全。
    :keywords: Python interview questions, Python cheat sheet, GIL, asyncio, threading, multiprocessing, generators, decorators, closures, mutable default arguments, MRO, metaclasses, dunder methods, slots, dataclass, context managers, descriptors, SQLAlchemy, ctypes, Python C API, Python security

此页面是速查表 rest 的精选、问题索引地图。每个条目都是您可能在 Python 采访中看到的问题，后面跟着一个链接，可直接跳转到回答该问题的笔记部分。它有意成为一个导航层——实际的解释、代码和警告位于链接的部分中。

有两种使用方式：

* **钻主题：** 选择一个组（e.g.*Asyncio*）并走每一个问题。
* **面试前快速回顾：** 阅读问题，对于任何您无法用一两句话自信回答的问题，请点击查看。

Python 语言基础（Python Language Fundamentals）
==================================================================================

* ``from __future__ import ...`` 的作用是什么？未来哪些进口仍然重要？ :ref:`print 函数（Print Function） <notes/basic/python-future:Print Function>` · :ref:`除法（Division） <notes/basic/python-future:Division>` · :ref:`标注（Annotations） <notes/basic/python-future:Annotations>`
* ``Ellipsis`` （ ``...`` ）在现代Python中的用途是什么？ :ref:`省略号（Ellipsis） <notes/basic/python-basic:Ellipsis>`
* ``for`` / ``while`` ``... else`` 子句如何运作？ :ref:`for ... else ... 语句（for ... else ...） <notes/basic/python-basic:for ... else ...>` · :ref:`while ... else ... 语句（while ... else ...） <notes/basic/python-basic:while ... else ...>`
* ``try ... except ... else`` 能做什么普通 ``try ... except`` 不能做的事情？ :ref:`try ... except ... else ... 语句（try ... except ... else ...） <notes/basic/python-basic:try ... except ... else ...>`
* Python 如何处理 Unicode 与 bytes，什么是代码点？ :ref:`字符（Characters） <notes/basic/python-unicode:Characters>` · :ref:`Unicode 代码点（Unicode Code Point） <notes/basic/python-unicode:Unicode Code Point>`

数据结构和集合（Data Structures & Collections）
============================================================================

* list 的 shallow copy 与 deep copy 有什么区别？ :ref:`复制列表：浅复制与深复制（Copy Lists: Shallow vs Deep Copy） <notes/basic/python-list:Copy Lists: Shallow vs Deep Copy>`
* 为什么 ``[[]] * n`` 可能产生意外结果？ :ref:`使用乘法运算符初始化列表（Initialize Lists with Multiplication Operator） <notes/basic/python-list:Initialize Lists with Multiplication Operator>`
* 什么是 list comprehension？generator expression 什么时候更好？ :ref:`使用列表推导式创建列表（Create Lists with List Comprehensions） <notes/basic/python-list:Create Lists with List Comprehensions>`
* 迭代时如何获得 ``(index, value)`` 对？ :ref:`使用 enumerate() 带索引迭代（Iterate with Index Using enumerate()） <notes/basic/python-list:Iterate with Index Using enumerate()>`
* dict 是如何迭代的， ``dict.items()`` / ``dict.keys()`` 返回什么？ :ref:`使用 dict.keys() 获取所有键（Get All Keys with dict.keys() ） <notes/basic/python-dict:Get All Keys with \`\`dict.keys()\`\`>` · :ref:`使用 dict.items() 获取键值对（Get Key-Value Pairs with dict.items() ） <notes/basic/python-dict:Get Key-Value Pairs with \`\`dict.items()\`\`>`
* ``dict.setdefault`` 与 ``collections.defaultdict`` — 哪个适合哪种用例？ :ref:`使用 setdefault() 和 defaultdict 设置默认值（Set Default Values with setdefault() and defaultdict ） <notes/basic/python-dict:Set Default Values with \`\`setdefault()\`\` and \`\`defaultdict\`\`>`
* 如何合并两个dicts（3.9之前和3.9之后）？ :ref:`在 Python 中合并两个字典（Merge Two Dictionaries in Python） <notes/basic/python-dict:Merge Two Dictionaries in Python>`
* 您将如何从头开始实现 LRU cache？ :ref:`使用 OrderedDict 实现 LRU 缓存（Implement LRU Cache with OrderedDict） <notes/basic/python-dict:Implement LRU Cache with OrderedDict>`
* 如何在保留顺序的同时对 list 进行重复数据删除？ :ref:`从列表中删除重复项（Remove Duplicates from a List） <notes/basic/python-set:Remove Duplicates from a List>`
* 什么时候会使用 ``heapq`` 而不是排序？ :ref:`基本堆操作（Basic Heap Operations） <notes/basic/python-heap:Basic Heap Operations>` · :ref:`使用 heapq 实现优先级队列（Implement Priority Queue with heapq ） <notes/basic/python-heap:Implement Priority Queue with \`\`heapq\`\`>`
* 如何使用 dunder methods 模拟类似 dict 的 object？ :ref:`用特殊方法模拟字典（Emulate a Dictionary with Special Methods） <notes/basic/python-dict:Emulate a Dictionary with Special Methods>`

函数和装饰器（Functions & Decorators）
============================================================

* ``*args`` 和 ``**kwargs`` 到底做了什么？如何转发它们？ :ref:`可变参数 *args 与 **kwargs （Variable Arguments *args and **kwargs ） <notes/basic/python-func:Variable Arguments \`\`*args\`\` and \`\`**kwargs\`\`>` · :ref:`解包参数（Unpack Arguments） <notes/basic/python-func:Unpack Arguments>`
* keyword-only arguments 与 positional-only arguments 有何区别？ :ref:`仅关键字参数（Keyword-Only Arguments） <notes/basic/python-func:Keyword-Only Arguments>` · :ref:`仅位置参数（Positional-Only Arguments） <notes/basic/python-func:Positional-Only Arguments>`
* 什么是 closure，它捕获什么？ :ref:`闭包（Closure） <notes/basic/python-func:Closure>`
* decorators 如何工作？如何编写接收 arguments 的 decorator？ :ref:`装饰器（Decorator） <notes/basic/python-func:Decorator>` · :ref:`带参数的装饰器（Decorator with Arguments） <notes/basic/python-func:Decorator with Arguments>`
* ``functools.lru_cache`` 与 ``functools.partial`` — 它们的作用是什么？ :ref:`使用 lru_cache 缓存（Cache with lru_cache ） <notes/basic/python-func:Cache with \`\`lru_cache\`\`>` · :ref:`偏函数（Partial Functions） <notes/basic/python-func:Partial Functions>`
* ``functools.singledispatch`` 如何实现function重载？ :ref:`singledispatch - 函数重载（ singledispatch - Function Overloading） <notes/basic/python-func:\`\`singledispatch\`\` - Function Overloading>`

迭代器和生成器（Iterators & Generators）
==============================================================

* Generator function 与 generator expression — 每个惯用语是什么时候？ :ref:`生成器函数与生成器表达式（Generator Function vs Generator Expression） <notes/basic/python-generator:Generator Function vs Generator Expression>`
* 如何将 value 发送到正在运行的 generator 中？ :ref:`将值发送到生成器（Send Values to Generator） <notes/basic/python-generator:Send Values to Generator>`
* ``yield from`` 有什么作用，它是如何组成generators的？ :ref:`yield from 表达式（yield from Expression） <notes/basic/python-generator:yield from Expression>` · :ref:`带返回值的 yield from（yield from with Return） <notes/basic/python-generator:yield from with Return>`
* 如何使用 generator method 构建 iterable class？ :ref:`通过生成器的可迭代类（Iterable Class via Generator） <notes/basic/python-generator:Iterable Class via Generator>`
* 如何使用 ``@contextmanager`` 将 context manager 实现为 generator？ :ref:`通过生成器进行上下文管理（Context Manager via Generator） <notes/basic/python-generator:Context Manager via Generator>` · :ref:`@contextmanager 的作用（What @contextmanager Does） <notes/basic/python-generator:What \`\`@contextmanager\`\` Does>`
* 什么是异步 generator，它与普通 generator 有何不同？ :ref:`异步生成器 (Python 3.6+)（Async Generator (Python 3.6+)） <notes/basic/python-generator:Async Generator (Python 3.6+)>`

类与面向对象编程（Classes & OOP）
==============================================

* ``__new__`` 与 ``__init__`` — 各自何时运行？ :ref:`__new__ 与 __init__ 对比（__new__ vs __init__） <notes/basic/python-object:__new__ vs __init__>`
* ``__str__`` 与 ``__repr__`` — 谁叫哪个？ :ref:`__str__ 和 __repr__（__str__ and __repr__） <notes/basic/python-object:__str__ and __repr__>`
* 描述符协议如何工作？ :ref:`描述符协议（Descriptor Protocol） <notes/basic/python-object:Descriptor Protocol>`
* 什么是 context manager 协议（ ``__enter__`` / ``__exit__`` ）？ :ref:`上下文管理器协议（Context Manager Protocol） <notes/basic/python-object:Context Manager Protocol>`
* ``@staticmethod`` 与 ``@classmethod`` — 何时使用哪个？ :ref:`@staticmethod 和 @classmethod（@staticmethod and @classmethod） <notes/basic/python-object:@staticmethod and @classmethod>`
* 什么是MRO，C3线性化如何解决钻石问题？ :ref:`菱形继承问题（MRO）（The Diamond Problem (MRO)） <notes/basic/python-object:The Diamond Problem (MRO)>`
* 什么时候应该定义 ``__slots__`` ？ :ref:`使用__slots__（Using __slots__） <notes/basic/python-object:Using __slots__>`
* 如何在运行时使用 ``type(...)`` 定义 class？ :ref:`使用 type() 声明类（Declare Class with type()） <notes/basic/python-object:Declare Class with type()>`
* 什么是 abstract base classes， ``abc`` 如何强制执行它们？ :ref:`带有 abc 的抽象基类（Abstract Base Classes with abc） <notes/basic/python-object:Abstract Base Classes with abc>`
* 如何实现可调用的 object？ :ref:`可使用 __call__ 调用（Callable with __call__） <notes/basic/python-object:Callable with __call__>`
* 与普通的 getter/setter 相比， ``@property`` 能为您带来什么？ :ref:`@property 装饰器（@property Decorator） <notes/basic/python-object:@property Decorator>`

并发（Concurrency）
==============================

* 什么是 GIL，它如何影响 CPU 绑定与 I/O 绑定代码？ :ref:`了解 GIL（Understanding the GIL） <notes/concurrency/python-threading:Understanding the GIL>`
* 线程与 multiprocessing — 您什么时候会分别使用它们？ :ref:`创建线程（Creating Threads） <notes/concurrency/python-threading:Creating Threads>` · :ref:`创建进程（Creating Processes） <notes/concurrency/python-multiprocessing:Creating Processes>`
* ``Lock`` vs ``RLock`` — 有什么区别？ :ref:`锁定 - 互斥（Lock - Mutual Exclusion） <notes/concurrency/python-threading:Lock - Mutual Exclusion>` · :ref:`RLock - 可重入锁（RLock - Reentrant Lock） <notes/concurrency/python-threading:RLock - Reentrant Lock>`
* 如何与 ``Event`` 、 ``Condition`` 或 ``Barrier`` 同步？ :ref:`事件 - 线程信号（Event - Thread Signaling） <notes/concurrency/python-threading:Event - Thread Signaling>` · :ref:`条件 - 复杂同步（Condition - Complex Synchronization） <notes/concurrency/python-threading:Condition - Complex Synchronization>` · :ref:`屏障 - 同步点（Barrier - Synchronization Point） <notes/concurrency/python-threading:Barrier - Synchronization Point>`
* 您将如何使用 ``queue.Queue`` 构建生产者-消费者管道？ :ref:`带队列的生产者-消费者（Producer-Consumer with Queue） <notes/concurrency/python-threading:Producer-Consumer with Queue>`
* 什么是 deadlock？如何预防？ :ref:`死锁示例及预防（Deadlock Example and Prevention） <notes/concurrency/python-threading:Deadlock Example and Prevention>`
* 如何跨 processes（Queue、管道、Value、管理器）共享状态？ :ref:`使用 Queue 共享数据（Sharing Data with Queue） <notes/concurrency/python-multiprocessing:Sharing Data with Queue>` · :ref:`使用 Value 与 Array 共享内存（Shared Memory with Value and Array） <notes/concurrency/python-multiprocessing:Shared Memory with Value and Array>` · :ref:`使用 Manager 共享复杂对象（Manager for Complex Shared Objects） <notes/concurrency/python-multiprocessing:Manager for Complex Shared Objects>`
* ``ThreadPoolExecutor`` 与 ``ProcessPoolExecutor`` — 您如何选择？ :ref:`ThreadPoolExecutor 基础知识（ThreadPoolExecutor Basics） <notes/concurrency/python-futures:ThreadPoolExecutor Basics>` · :ref:`ProcessPoolExecutor 基础知识（ProcessPoolExecutor Basics） <notes/concurrency/python-futures:ProcessPoolExecutor Basics>`
* 当许多期货完成时，您如何得出 process 的结果？ :ref:`按完成顺序处理结果（Processing Results as They Complete） <notes/concurrency/python-futures:Processing Results as They Complete>`

异步编程（Asyncio）
==========================

* 当您拨打 ``asyncio.run(coro())`` 时实际上会发生什么？ :ref:`使用 asyncio.run 运行协程（Running Coroutines with asyncio.run） <notes/asyncio/python-asyncio-basic:Running Coroutines with asyncio.run>`
* ``asyncio.create_task`` 与直接等待 coroutine — 有什么区别？ :ref:`创建和管理任务（Creating and Managing Tasks） <notes/asyncio/python-asyncio-basic:Creating and Managing Tasks>`
* ``asyncio.gather`` 和 ``asyncio.wait`` 有什么区别？ :ref:`收集多个协程（Gathering Multiple Coroutines） <notes/asyncio/python-asyncio-basic:Gathering Multiple Coroutines>` · :ref:`等待首个任务完成（Waiting for First Completed） <notes/asyncio/python-asyncio-basic:Waiting for First Completed>`
* 如何对 awaitable 进行时间限制？ :ref:`带超时限制的等待（Waiting with Timeout） <notes/asyncio/python-asyncio-basic:Waiting with Timeout>`
* 什么是异步 context manager，如何编写？ :ref:`异步上下文管理器（Asynchronous Context Managers） <notes/asyncio/python-asyncio-basic:Asynchronous Context Managers>` · :ref:`使用 @asynccontextmanager（Using @asynccontextmanager） <notes/asyncio/python-asyncio-basic:Using @asynccontextmanager>`
* 如何从异步 function 调用阻塞代码而不阻塞 loop？ :ref:`在执行器中运行阻塞代码（Running Blocking Code in Executor） <notes/asyncio/python-asyncio-basic:Running Blocking Code in Executor>`
* 您如何处理 exceptions 内部提出的任务？ :ref:`任务中的异常处理（Exception Handling in Tasks） <notes/asyncio/python-asyncio-basic:Exception Handling in Tasks>`
* 如何对 asyncio 中的并发进行速率限制？ :ref:`用于速率限制的信号量（Semaphores for Rate Limiting） <notes/asyncio/python-asyncio-advanced:Semaphores for Rate Limiting>`
* asyncio 中的正常关机是什么？ :ref:`平稳关闭（Graceful Shutdown） <notes/asyncio/python-asyncio-advanced:Graceful Shutdown>`
* 从概念上讲，什么是 coroutine 以及 event loop 如何驱动它？ :ref:`什么是协程？（What is a Coroutine?） <notes/asyncio/python-asyncio-guide:What is a Coroutine?>` · :ref:`事件循环（Event Loop） <notes/asyncio/python-asyncio-guide:Event Loop>`

常见问题（Common Gotchas）
========================================

* 为什么使用 mutable default argument ( ``def f(x=[])`` ) 很危险？ :ref:`默认参数（Default Arguments） <notes/basic/python-func:Default Arguments>`

C 扩展和互操作（C Extensions & Interop）
================================================================

* 如何使用 CPython C API 编写 C 扩展 module？ :ref:`简单的 C 扩展（Simple C Extension） <notes/extension/python-capi:Simple C Extension>` · :ref:`解析参数（Parse Arguments） <notes/extension/python-capi:Parse Arguments>`
* 您如何以及为何以 C 扩展形式发布 GIL？ :ref:`释放 GIL（Release the GIL） <notes/extension/python-capi:Release the GIL>`
* 如何调入与 ``ctypes`` 共享的 library？ :ref:`加载共享库（Loading Shared Libraries） <notes/extension/python-ctypes:Loading Shared Libraries>` · :ref:`基本类型映射（Basic Type Mapping） <notes/extension/python-ctypes:Basic Type Mapping>`

联网（Networking）
============================

* 如何将主机名解析为 Python 中的 IP？ :ref:`获取地址信息（DNS 解析）（Get Address Info (DNS Resolution)） <notes/network/python-socket:Get Address Info (DNS Resolution)>`
* 网络 byte 订单 — 您何时以及为何需要 ``htons`` / ``ntohs`` ？ :ref:`网络字节顺序转换（Network Byte Order Conversion） <notes/network/python-socket:Network Byte Order Conversion>`
* 如何构建最小的 TLS echo 服务器和客户端？ :ref:`简单 TLS Echo 服务器（Simple TLS Echo Server） <notes/network/python-socket-ssl:Simple TLS Echo Server>` · :ref:`TLS 客户端（TLS Client） <notes/network/python-socket-ssl:TLS Client>`
* 什么是双向 TLS (mTLS)，为什么服务需要它？ :ref:`双向 TLS（mTLS）（Mutual TLS (mTLS)） <notes/network/python-socket-ssl:Mutual TLS (mTLS)>`

数据库（Databases）
============================

* SQLAlchemy 引擎实际上包含什么？连接如何工作？ :ref:`创建引擎（Create an Engine） <notes/database/python-sqlalchemy:Create an Engine>` · :ref:`数据库 URL 格式（Database URL Format） <notes/database/python-sqlalchemy:Database URL Format>`
* 如何使用 parameters 安全地运行原始 SQL？ :ref:`连接并执行原始 SQL（Connect and Execute Raw SQL） <notes/database/python-sqlalchemy:Connect and Execute Raw SQL>`
* SQLAlchemy 中的交易 — 谁提交、何时提交？ :ref:`事务管理（Transaction Management） <notes/database/python-sqlalchemy:Transaction Management>`
* 核心与 ORM — ORM 在上面添加了什么？ :ref:`使用声明性基础定义模型（Define Models with Declarative Base） <notes/database/python-sqlalchemy-orm:Define Models with Declarative Base>` · :ref:`会话基础知识（Session Basics） <notes/database/python-sqlalchemy-orm:Session Basics>`

安全与加密（Security & Crypto）
================================================

* 要避免哪些常见的加密错误？ :ref:`常见错误（不要这样做）（Common Mistakes (Don't Do This)） <notes/security/python-crypto:Common Mistakes (Don't Do This)>` · :ref:`安全检查表（Security Checklist） <notes/security/python-crypto:Security Checklist>`
* 为什么您应该选择 ``secrets`` 而不是 ``random`` 作为代币？ :ref:`安全随机生成（Secure Random Generation） <notes/security/python-crypto:Secure Random Generation>` · :ref:`弱随机数生成（Weak Random Number Generation） <notes/security/python-vulnerability:Weak Random Number Generation>`
* 什么是定时攻击？如何防御定时攻击？ :ref:`对字符串比较的计时攻击（Timing Attacks on String Comparison） <notes/security/python-vulnerability:Timing Attacks on String Comparison>`
* SQL 注入是如何在 Python 中发生的，如何预防？ :ref:`SQL 注入（SQL Injection） <notes/security/python-vulnerability:SQL Injection>`

参见（See Also）
========================

如果上述问题没有得到解答，那么顶级 indices 是最好的下一站：

* :doc:`../basic/index` — Python 核心语言和数据结构
* :doc:`../concurrency/index` — 螺纹、multiprocessing、期货
* :doc:`../asyncio/index` — Asyncio 和异步模式
* :doc:`../network/index` — Sockets 和 SSL/TLS
* :doc:`../database/index` — SQLAlchemy 内核和 ORM
* :doc:`../security/index` — 密码学和常见漏洞
* :doc:`../extension/index` — C 扩展和 FFI
