.. meta::
    :description lang=zh_CN: 从 Python 学习现代 C++ 语法 - Python 和 C++ 代码片段的并排比较
    :keywords: C++, Python, C++11, C++14, C++17, C++20, modern C++, syntax comparison, learn C++

============================================================================
从 Python 学习 C++（Learn C++ from Python）
============================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

现代 C++（C++11、C++14、C++17、C++20）已发展到包含使其在语法上与 Python 相似的功能，从而使 Python 开发人员更容易进行过渡。本综合指南提供了 Python 和现代 C++ 代码片段之间的并排比较和 1-1 映射，涵盖 variables、数据结构、functions、lambdas、classes 和算法等基本编程概念。

无论您是 Python 开发人员，希望学习 C++ 来优化性能、系统编程，还是扩展您的编程技能，本教程都会演示如何将熟悉的 Python 模式转换为现代 C++ 语法。许多流行的框架（例如 PyTorch、TensorFlow 和 NumPy）都使用 C++ 扩展来执行性能关键型操作，特别是在深度学习、LLM 训练和 CUDA GPU 编程中。了解 C++ 使您能够编写自定义扩展、优化瓶颈并为这些高性能 libraries 做出贡献。

要了解有关 C++ 编程的更多信息，请参阅此 `C++ cheatsheet <https://cppcheatsheet.com/>`_ 以获取更多参考和最佳实践。

**完整的工作示例：** 请参阅 `cpp_from_py.cpp <https://github.com/crazyguitar/pysheeet/blob/master/src/cpp_from_python/cpp_from_py.cpp>`_ 以获取带有集成 Google 测试套件的可运行代码。每个 function 都包含显示等效 Python 代码的 Doxygen 注释。

你好世界（Hello World）
----------------------------------

任何语言的传统第一个程序。 Python 和 C++ 都可以将文本打印到 console，但 C++ 需要包括 iostream library 和主 function。

**Python**

.. code-block:: python

    print("Hello, World!")

**C++**

.. code-block:: cpp

    #include <iostream>

    int main() {
        std::cout << "Hello, World!" << std::endl;
        return 0;
    }

变量（Variables）
--------------------------

现代 C++ 支持使用 ``auto`` 关键字进行自动 type 推理，使 variable 声明与 Python 一样简洁。 compiler 从初始化 values 推导出 types。

**Python**

.. code-block:: python

    x = 10
    y = 3.14
    name = "Alice"
    is_valid = True

**C++**

.. code-block:: cpp

    auto x = 10;
    auto y = 3.14;
    auto name = "Alice";
    auto is_valid = true;

列表和向量（Lists and Vectors）
------------------------------------------------

Python lists 和 C++ 向量是可以增长和收缩的动态 arrays。两者都支持索引、附加 elements 和查询大小。 C++ 向量需要指定 element type，但现代 C++ 可以从初始化中推断出来。

**Python**

.. code-block:: python

    numbers = [1, 2, 3, 4, 5]
    numbers.append(6)
    print(numbers[0])
    print(len(numbers))

**C++**

.. code-block:: cpp

    #include <vector>

    std::vector<int> numbers = {1, 2, 3, 4, 5};
    numbers.push_back(6);
    std::cout << numbers[0] << std::endl;
    std::cout << numbers.size() << std::endl;

数组切片和访问（Array Slicing and Access）
------------------------------------------------------------------

Python 支持带有负 indices 和 ranges 的强大切片语法。 C++ 没有内置切片，但您可以使用 iterators 或创建子向量。负索引需要从末尾开始手动计算。

**Python**

.. code-block:: python

    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    print(numbers[0])
    print(numbers[-1])
    print(numbers[2:5])
    print(numbers[:3])
    print(numbers[7:])
    print(numbers[::2])
    print(numbers[::-1])

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> numbers = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    std::cout << numbers[0] << std::endl;
    std::cout << numbers[numbers.size() - 1] << std::endl;

    std::vector<int> slice1(numbers.begin() + 2, numbers.begin() + 5);
    std::vector<int> slice2(numbers.begin(), numbers.begin() + 3);
    std::vector<int> slice3(numbers.begin() + 7, numbers.end());

    std::vector<int> every_second;
    for (size_t i = 0; i < numbers.size(); i += 2) {
        every_second.push_back(numbers[i]);
    }

    std::vector<int> reversed(numbers.rbegin(), numbers.rend());

字典与映射（Dictionaries and Maps）
--------------------------------------------------------

Python 中的 Dictionaries 和 C++ 中的映射存储 key-value 对。两者都允许使用括号表示法进行插入、查找和修改。 C++ 映射保持 keys 排序，而 Python dicts 保持插入顺序 (Python 3.7+)。

**Python**

.. code-block:: python

    ages = {"Alice": 30, "Bob": 25}
    ages["Charlie"] = 35
    print(ages["Alice"])

**C++**

.. code-block:: cpp

    #include <map>
    #include <string>

    std::map<std::string, int> ages = {{"Alice", 30}, {"Bob", 25}};
    ages["Charlie"] = 35;
    std::cout << ages["Alice"] << std::endl;

For循环（For Loop）
------------------------------

两种语言都支持传统计数 loops 和基于 range 的 iteration。基于 C++ range 的 loops (C++11) 提供类似于 Python 的 for-in loops 的语法，使得容器上的 iteration 更具可读性。

**Python**

.. code-block:: python

    for i in range(5):
        print(i)

    for item in [1, 2, 3]:
        print(item)

**C++**

.. code-block:: cpp

    for (int i = 0; i < 5; i++) {
        std::cout << i << std::endl;
    }

    for (auto item : {1, 2, 3}) {
        std::cout << item << std::endl;
    }

While 循环（While Loop）
----------------------------------------

而loops只要条件为true就执行。 Python 和 C++ 之间的语法几乎相同，其中 C++ 需要条件周围的括号和主体的大括号。

**Python**

.. code-block:: python

    i = 0
    while i < 5:
        print(i)
        i += 1

**C++**

.. code-block:: cpp

    int i = 0;
    while (i < 5) {
        std::cout << i << std::endl;
        i++;
    }

if-else 条件语句（If-Else）
------------------------------------------

有条件statements控制程序流程基于boolean expressions。 C++ 需要将条件括起来并使用大括号作为块，而 Python 使用缩进。两者都支持 elif/else if 的链式条件。

**Python**

.. code-block:: python

    x = 10
    if x > 5:
        print("Greater")
    elif x == 5:
        print("Equal")
    else:
        print("Less")

**C++**

.. code-block:: cpp

    auto x = 10;
    if (x > 5) {
        std::cout << "Greater" << std::endl;
    } else if (x == 5) {
        std::cout << "Equal" << std::endl;
    } else {
        std::cout << "Less" << std::endl;
    }

函数（Functions）
--------------------------

Functions封装了可重用的代码。现代 C++ 支持尾随返回 type 语法 (-> type)，类似于 Python 的 type hints。当 function 主体很简单时，auto 关键字允许 type 推断返回 types。

**Python**

.. code-block:: python

    def add(a, b):
        return a + b

    result = add(3, 5)

**C++**

.. code-block:: cpp

    auto add(int a, int b) -> int {
        return a + b;
    }

    auto result = add(3, 5);

Lambda 函数（Lambda Functions）
------------------------------------------------------

Lambda functions 是匿名 functions，可以从周围的 scope 捕获 variables。 Python和C++都支持lambdas，使得函数式编程模式成为可能。 C++ lambdas 可以指定捕获模式（通过 value，通过参考），以更好地控制 variable 的寿命和性能。

**Python**

.. code-block:: python

    square = lambda x: x * x
    print(square(5))

    numbers = [1, 2, 3, 4]
    squared = list(map(lambda x: x * x, numbers))

    # 捕获variables
    multiplier = 10
    multiply = lambda x: x * multiplier
    print(multiply(5))

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    auto square = [](int x) { return x * x; };
    std::cout << square(5) << std::endl;

    std::vector<int> numbers = {1, 2, 3, 4};
    std::vector<int> squared;
    std::transform(numbers.begin(), numbers.end(),
                   std::back_inserter(squared),
                   [](int x) { return x * x; });

    // 通过 value [=] 或通过引用 [&] 捕获 variables
    int multiplier = 10;
    auto multiply = [multiplier](int x) { return x * multiplier; };
    std::cout << multiply(5) << std::endl;

Lambda 捕获模式（Lambda Capture Modes）
------------------------------------------------------------------

C++ lambdas 提供对如何从封闭的 scope 捕获 variables 的显式控制。这比 Python 的隐式 closure 行为更明确，并且允许通过在复制 values 或使用引用之间进行选择来进行优化。

**Python**

.. code-block:: python

    x = 10
    y = 20

    # 隐式捕获 x 和 y
    add_xy = lambda z: x + y + z
    print(add_xy(5))

**C++**

.. code-block:: cpp

    int x = 10;
    int y = 20;

    // value 捕获
    auto add_xy_val = [x, y](int z) { return x + y + z; };
    std::cout << add_xy_val(5) << std::endl;

    // 通过引用捕获
    auto add_xy_ref = [&x, &y](int z) { return x + y + z; };

    // value 捕获全部
    auto add_all_val = [=](int z) { return x + y + z; };

    // 通过引用捕获所有内容
    auto add_all_ref = [&](int z) { return x + y + z; };

列表推导式（List Comprehension）
--------------------------------------------------

Python 的 list comprehensions 提供了用于创建 lists 的简洁语法。 C++ 没有直接语法，但您可以使用 loops 或 STL 算法（例如 std::transform 和 std::copy_if）获得类似的结果。

**Python**

.. code-block:: python

    squares = [x * x for x in range(10)]
    evens = [x for x in range(10) if x % 2 == 0]

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> squares;
    for (int x = 0; x < 10; x++) {
        squares.push_back(x * x);
    }

    std::vector<int> evens;
    for (int x = 0; x < 10; x++) {
        if (x % 2 == 0) {
            evens.push_back(x);
        }
    }

字符串操作（String Operations）
------------------------------------------------

两种语言都提供丰富的 string 操作功能。在串联方面，C++ strings 是 mutable，类似于 Python strings，但单个字符访问的工作原理类似。 C++ 需要显式转换 functions 以进行大小写更改。

**Python**

.. code-block:: python

    s = "Hello"
    s += " World"
    print(len(s))
    print(s[0])
    print(s.upper())

**C++**

.. code-block:: cpp

    #include <string>
    #include <algorithm>

    std::string s = "Hello";
    s += " World";
    std::cout << s.size() << std::endl;
    std::cout << s[0] << std::endl;

    std::string upper = s;
    std::transform(upper.begin(), upper.end(), upper.begin(), ::toupper);
    std::cout << upper << std::endl;

类（Classes）
--------------------

面向 Object 的编程在两种语言中的工作方式类似。 C++ 需要显式访问说明符（公共、私有）和构造函数初始化 lists。两者都支持成员 variables 和 methods，其中 C++ 使用 :: 进行 scope 分辨率。

**Python**

.. code-block:: python

    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

        def greet(self):
            return f"Hello, I'm {self.name}"

    p = Person("Alice", 30)
    print(p.greet())

**C++**

.. code-block:: cpp

    #include <string>

    class Person {
    public:
        std::string name;
        int age;

        Person(std::string name, int age) : name(name), age(age) {}

        std::string greet() {
            return "Hello, I'm " + name;
        }
    };

    Person p("Alice", 30);
    std::cout << p.greet() << std::endl;

可选值（Optional Values）
----------------------------------------

Python 使用 None 来表示缺失的 values，而 C++ (C++17+) 为 type 安全可选 values 提供 std::optional。这可以防止空指针错误，并使 type 系统中显式缺少 value。

**Python**

.. code-block:: python

    def find_value(key):
        data = {"a": 1, "b": 2}
        return data.get(key)

    result = find_value("a")
    if result is not None:
        print(result)

**C++**

.. code-block:: cpp

    #include <optional>
    #include <map>

    std::optional<int> find_value(std::string key) {
        std::map<std::string, int> data = {{"a", 1}, {"b", 2}};
        auto it = data.find(key);
        if (it != data.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    auto result = find_value("a");
    if (result.has_value()) {
        std::cout << result.value() << std::endl;
    }

智能指针（Smart Pointers）
----------------------------------------

Python 与 garbage collection 自动处理内存。 C++ 智能指针 (C++11+) 通过 RAII 提供自动内存管理。 unique_ptr 确保单一所有权，而 shared_ptr 允许多个拥有者使用 reference counting。

**Python**

.. code-block:: python

    class Resource:
        def __init__(self, name):
            self.name = name

    resource = Resource("data")

**C++**

.. code-block:: cpp

    #include <memory>

    class Resource {
    public:
        std::string name;
        Resource(std::string name) : name(name) {}
    };

    auto resource = std::make_unique<Resource>("data");
    auto shared = std::make_shared<Resource>("data");

文件输入/输出（File I/O）
----------------------------------

**Python**

.. code-block:: python

    with open("file.txt", "r") as f:
        content = f.read()

    with open("file.txt", "w") as f:
        f.write("Hello")

**C++**

.. code-block:: cpp

    #include <fstream>
    #include <string>

    std::ifstream file("file.txt");
    std::string content((std::istreambuf_iterator<char>(file)),
                        std::istreambuf_iterator<char>());

    std::ofstream out("file.txt");
    out << "Hello";

异常处理（Exception Handling）
------------------------------------------------

两种语言都支持 try-catch exception 处理以进行错误管理。 C++ 使用类型化的 exceptions 并要求在 catch 块中显式 exception types。

**Python**

.. code-block:: python

    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        print(f"Error: {e}")
    finally:
        print("Cleanup")

**C++**

.. code-block:: cpp

    #include <exception>

    try {
        if (divisor == 0) {
            throw std::runtime_error("Division by zero");
        }
        result = 10 / divisor;
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
    }

元组（Tuples）
--------------------

Tuples 将多个 values 组合在一起。 C++17 引入了结构化绑定，允许与 Python 类似的 tuple 解包，从而可以轻松返回和解构多个 values。

**Python**

.. code-block:: python

    point = (10, 20)
    x, y = point
    print(x, y)

**C++**

.. code-block:: cpp

    #include <tuple>

    auto point = std::make_tuple(10, 20);
    auto [x, y] = point;
    std::cout << x << " " << y << std::endl;

枚举（Enumerate）
--------------------------

Python 的 enumerate 在 iteration 期间提供 index-value 对。 C++ 没有直接等效项，但您可以使用传统索引 loops 获得相同的结果。

**Python**

.. code-block:: python

    items = ["a", "b", "c"]
    for i, item in enumerate(items):
        print(i, item)

**C++**

.. code-block:: cpp

    #include <vector>
    #include <string>

    std::vector<std::string> items = {"a", "b", "c"};
    for (size_t i = 0; i < items.size(); i++) {
        std::cout << i << " " << items[i] << std::endl;
    }

filter 与 map（Filter and Map）
--------------------------------------------------------

Python 的过滤器和映射 functions 将转换应用于序列。 C++ 通过 STL 算法（如 ``std::copy_if`` 和 ``std::transform`` ）提供等效功能。

**Python**

.. code-block:: python

    numbers = [1, 2, 3, 4, 5]
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    doubled = list(map(lambda x: x * 2, numbers))

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> numbers = {1, 2, 3, 4, 5};

    std::vector<int> evens;
    std::copy_if(numbers.begin(), numbers.end(),
                 std::back_inserter(evens),
                 [](int x) { return x % 2 == 0; });

    std::vector<int> doubled;
    std::transform(numbers.begin(), numbers.end(),
                   std::back_inserter(doubled),
                   [](int x) { return x * 2; });

any 与 all（Any and All）
--------------------------------------------

检查序列中的任何或所有 elements 是否满足条件。 C++ 为这些常见操作提供了 ``std::any_of`` 和 ``std::all_of`` 算法。

**Python**

.. code-block:: python

    numbers = [1, 2, 3, 4, 5]
    has_even = any(x % 2 == 0 for x in numbers)
    all_positive = all(x > 0 for x in numbers)

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> numbers = {1, 2, 3, 4, 5};

    bool has_even = std::any_of(numbers.begin(), numbers.end(),
                                 [](int x) { return x % 2 == 0; });

    bool all_positive = std::all_of(numbers.begin(), numbers.end(),
                                     [](int x) { return x > 0; });

排序（Sorting）
----------------------

按升序或降序对序列进行排序。两种语言都提供就地排序以及通过自定义比较 functions 创建排序副本的能力。

**Python**

.. code-block:: python

    numbers = [3, 1, 4, 1, 5]
    numbers.sort()

    sorted_nums = sorted(numbers, reverse=True)

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> numbers = {3, 1, 4, 1, 5};
    std::sort(numbers.begin(), numbers.end());

    std::vector<int> sorted_nums = numbers;
    std::sort(sorted_nums.begin(), sorted_nums.end(), std::greater<int>());

最小值和最大值（Min and Max）
----------------------------------------

查找序列中的最小值和最大值 values。 C++ 使用基于 iterator 的算法返回 iterators，需要取消引用才能获得实际的 values。

**Python**

.. code-block:: python

    numbers = [3, 1, 4, 1, 5]
    print(min(numbers))
    print(max(numbers))

**C++**

.. code-block:: cpp

    #include <vector>
    #include <algorithm>

    std::vector<int> numbers = {3, 1, 4, 1, 5};
    std::cout << *std::min_element(numbers.begin(), numbers.end()) << std::endl;
    std::cout << *std::max_element(numbers.begin(), numbers.end()) << std::endl;

求和（Sum）
--------------

计算序列中所有 elements 的总和。 C++ 使用来自数字 library 的 ``std::accumulate`` ，它还可以执行其他归约操作。

**Python**

.. code-block:: python

    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)

**C++**

.. code-block:: cpp

    #include <vector>
    #include <numeric>

    std::vector<int> numbers = {1, 2, 3, 4, 5};
    int total = std::accumulate(numbers.begin(), numbers.end(), 0);

zip 操作（Zip）
----------------------

并行迭代多个序列。 Python的zip是内置的，而C++需要手动基于index的iteration才能达到相同的结果。

**Python**

.. code-block:: python

    names = ["Alice", "Bob"]
    ages = [30, 25]
    for name, age in zip(names, ages):
        print(name, age)

**C++**

.. code-block:: cpp

    #include <vector>
    #include <string>

    std::vector<std::string> names = {"Alice", "Bob"};
    std::vector<int> ages = {30, 25};

    for (size_t i = 0; i < std::min(names.size(), ages.size()); i++) {
        std::cout << names[i] << " " << ages[i] << std::endl;
    }

默认参数（Default Arguments）
----------------------------------------------

Functions 可以具有默认的 parameter values，在未提供 arguments 时使用。两种语言都使用类似的语法支持此功能。

**Python**

.. code-block:: python

    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}"

    print(greet("Alice"))
    print(greet("Bob", "Hi"))

**C++**

.. code-block:: cpp

    #include <string>

    std::string greet(std::string name, std::string greeting = "Hello") {
        return greeting + ", " + name;
    }

    std::cout << greet("Alice") << std::endl;
    std::cout << greet("Bob", "Hi") << std::endl;
