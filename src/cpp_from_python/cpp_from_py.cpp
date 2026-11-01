/*
 * 从 Python 学习 C++ - 现代 C++ 示例和测试
 *
 * 演示现代 C++ 语法以及 Doxygen 注释中的 Python 等效项。
 * 构建： mkdir 构建 && cd 构建 && cmake .. && make
 * 测试：进行测试
 */

#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <numeric>
#include <optional>
#include <memory>
#include <tuple>
#include <functional>
#include <gtest/gtest.h>

/**
 * @brief 打印 hello world 消息
 *
 * Python 等效项：
 * @代码{.py}
 * print("Hello, World!")
 * @结束代码
 */
void hello_world() {
    std::cout << "Hello, World!" << std::endl;
}

/**
 * @brief 使用 auto 关键字演示自动 type 推理
 *
 * Python 等效项：
 * @代码{.py}
 * x = 10
 * y = 3.14
 * name = "Alice"
 * is_valid = True
 * @结束代码
 */
void variables() {
    auto x = 10;
    auto y = 3.14;
    auto name = "Alice";
    auto is_valid = true;
}

/**
 * @brief 创建和操作向量（动态 arrays）
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4, 5]
 * numbers.append(6)
 * print(numbers[0])
 * print(len(numbers)）
 * @结束代码
 */
std::vector<int> lists_and_vectors() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    numbers.push_back(6);
    return numbers;
}

/**
 * @brief 演示 array 切片和访问模式
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
 * print(numbers[0])
 * print(numbers[-1])
 * print(numbers[2:5])
 * print(numbers[:3])
 * print(numbers[7:])
 * print(numbers[::2])
 * print(numbers[::-1])
 * @结束代码
 */
std::vector<int> array_slicing() {
    std::vector<int> numbers = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    // 切片[2:5]
    std::vector<int> slice(numbers.begin() + 2, numbers.begin() + 5);

    // 每秒 element [::2]
    std::vector<int> every_second;
    for (size_t i = 0; i < numbers.size(); i += 2) {
        every_second.push_back(numbers[i]);
    }

    // 反转[::-1]
    std::vector<int> reversed(numbers.rbegin(), numbers.rend());

    return reversed;
}

/**
 * @brief 使用 key-value 存储的映射
 *
 * Python 等效项：
 * @代码{.py}
 * ages = {"Alice": 30, "Bob": 25}
 * 年龄["Charlie"] = 35
 * print(ages["Alice"])
 * @结束代码
 */
std::map<std::string, int> dictionaries_and_maps() {
    std::map<std::string, int> ages = {{"Alice", 30}, {"Bob", 25}};
    ages["Charlie"] = 35;
    return ages;
}

/**
 * @brief Range 基于 loops
 *
 * Python 等效项：
 * @代码{.py}
 * for i in range(5):
 *     print(i)
 *
 * for item in [1, 2, 3]:
 *     print(item)
 * @结束代码
 */
void for_loop() {
    for (int i = 0; i < 5; i++) {
        // 传统型 loop
    }

    for (auto item : {1, 2, 3}) {
        // 基于Range的loop
    }
}

/**
 * @brief 添加两个数字
 *
 * Python 等效项：
 * @代码{.py}
 * def add(a, b):
 *     返回 a + b
 *
 * result = add(3, 5)
 * @结束代码
 */
auto add(int a, int b) -> int {
    return a + b;
}

/**
 * @brief Lambda function 计算数字的平方
 *
 * Python 等效项：
 * @代码{.py}
 * square = lambda x: x * x
 * print(square(5)）
 *
 * numbers = [1, 2, 3, 4]
 * squared = list(map(lambda x: x * x, numbers))
 *
 * multiplier = 10
 * multiply = lambda x: x * multiplier
 * print(multiply(5)）
 * @结束代码
 */
std::function<int(int)> create_square_lambda() {
    return [](int x) { return x * x; };
}

/**
 * @brief Lambda 与 variable 捕获
 *
 * Python 等效项：
 * @代码{.py}
 * multiplier = 10
 * multiply = lambda x: x * multiplier
 * @结束代码
 */
std::function<int(int)> create_multiply_lambda(int multiplier) {
    return [multiplier](int x) { return x * multiplier; };
}

/**
 * @brief 使用 lambda 变换向量
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4]
 * squared = list(map(lambda x: x * x, numbers))
 * @结束代码
 */
std::vector<int> transform_with_lambda(const std::vector<int>& numbers) {
    std::vector<int> squared;
    std::transform(numbers.begin(), numbers.end(),
                   std::back_inserter(squared),
                   [](int x) { return x * x; });
    return squared;
}

/**
 * @brief List comprehension 等效项
 *
 * Python 等效项：
 * @代码{.py}
 * squares = [x * x for x in range(10)]
 * evens = [x for x in range(10) if x % 2 == 0]
 * @结束代码
 */
std::vector<int> list_comprehension() {
    std::vector<int> evens;
    for (int x = 0; x < 10; x++) {
        if (x % 2 == 0) {
            evens.push_back(x);
        }
    }
    return evens;
}

/**
 * @brief String 连接和操作
 *
 * Python 等效项：
 * @代码{.py}
 * s = "Hello"
 * s += " World"
 * print(len(s)）
 * print(s[0])
 * @结束代码
 */
std::string string_operations() {
    std::string s = "Hello";
    s += " World";
    return s;
}

/**
 * @brief Person class 与构造函数和 method
 *
 * Python 等效项：
 * @代码{.py}
 * class Person:
 *     def __init__(self, name, age):
 *         self.name = name
 *         self.age = age
 *
 *     def greet(self):
 *         return f"你好，我是{self.name}"
 *
 * p = Person("Alice", 30)
 * print(p.greet()）
 * @结束代码
 */
class Person {
public:
    std::string name;
    int age;

    Person(std::string name, int age);
    std::string greet() const;
};

Person::Person(std::string n, int a) : name(n), age(a) {}

std::string Person::greet() const {
    return "Hello, I'm " + name;
}

/**
 * @brief 可选的 value 处理
 *
 * Python 等效项：
 * @代码{.py}
 * def find_value(key):
 *     data = {"a": 1, "b": 2}
 *     return data.get(key)
 *
 * result = find_value("a")
 * if result is not None:
 *     print(result)
 * @结束代码
 */
std::optional<int> find_value(const std::string& key) {
    std::map<std::string, int> data = {{"a", 1}, {"b", 2}};
    auto it = data.find(key);
    if (it != data.end()) {
        return it->second;
    }
    return std::nullopt;
}

/**
 * @brief Tuple 使用结构化绑定进行解包
 *
 * Python 等效项：
 * @代码{.py}
 * point = (10, 20)
 * x, y = point
 * print(x, y)
 * @结束代码
 */
std::tuple<int, int> create_tuple() {
    return std::make_tuple(10, 20);
}

/**
 * @brief 从向量中过滤偶数
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4, 5]
 * evens = list(filter(lambda x: x % 2 == 0, numbers))
 * @结束代码
 */
std::vector<int> filter_evens(const std::vector<int>& numbers) {
    std::vector<int> evens;
    std::copy_if(numbers.begin(), numbers.end(),
                 std::back_inserter(evens),
                 [](int x) { return x % 2 == 0; });
    return evens;
}

/**
 * @brief 检查是否有 element 满足条件
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4, 5]
 * has_even = any(x % 2 == 0 for x in numbers)
 * @结束代码
 */
bool has_even(const std::vector<int>& numbers) {
    return std::any_of(numbers.begin(), numbers.end(),
                       [](int x) { return x % 2 == 0; });
}

/**
 * @brief 检查是否所有 elements 满足条件
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4, 5]
 * all_positive = all(x > 0 for x in numbers)
 * @结束代码
 */
bool all_positive(const std::vector<int>& numbers) {
    return std::all_of(numbers.begin(), numbers.end(),
                       [](int x) { return x > 0; });
}

/**
 * @brief 对向量进行适当排序
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [3, 1, 4, 1, 5]
 * numbers.sort()
 * @结束代码
 */
std::vector<int> sort_vector(std::vector<int> numbers) {
    std::sort(numbers.begin(), numbers.end());
    return numbers;
}

/**
 * @brief 找到最小值 element
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [3, 1, 4, 1, 5]
 * print(min(numbers)）
 * @结束代码
 */
int find_min(const std::vector<int>& numbers) {
    return *std::min_element(numbers.begin(), numbers.end());
}

/**
 * @brief 总结所有 elements
 *
 * Python 等效项：
 * @代码{.py}
 * numbers = [1, 2, 3, 4, 5]
 * total = sum(numbers)
 * @结束代码
 */
int sum_vector(const std::vector<int>& numbers) {
    return std::accumulate(numbers.begin(), numbers.end(), 0);
}

/**
 * @brief Function 和 default argument
 *
 * Python 等效项：
 * @代码{.py}
 * def greet(name, greeting="Hello"):
 *     return f"{问候语}，{名字}"
 *
 * print(greet("Alice")）
 * print(greet("Bob", "Hi")）
 * @结束代码
 */
std::string greet(const std::string& name, const std::string& greeting = "Hello") {
    return greeting + ", " + name;
}

TEST(BasicTest, AddFunction) {
    EXPECT_EQ(add(3, 5), 8);
    EXPECT_EQ(add(0, 0), 0);
    EXPECT_EQ(add(-1, 1), 0);
}

TEST(VectorTest, ListsAndVectors) {
    auto vec = lists_and_vectors();
    EXPECT_EQ(vec.size(), 6);
    EXPECT_EQ(vec[0], 1);
    EXPECT_EQ(vec[5], 6);
}

TEST(VectorTest, ArraySlicing) {
    auto reversed = array_slicing();
    EXPECT_EQ(reversed.size(), 10);
    EXPECT_EQ(reversed[0], 9);
    EXPECT_EQ(reversed[9], 0);
}

TEST(MapTest, DictionariesAndMaps) {
    auto ages = dictionaries_and_maps();
    EXPECT_EQ(ages["Alice"], 30);
    EXPECT_EQ(ages["Bob"], 25);
    EXPECT_EQ(ages["Charlie"], 35);
}

TEST(LambdaTest, SquareLambda) {
    auto square = create_square_lambda();
    EXPECT_EQ(square(5), 25);
    EXPECT_EQ(square(0), 0);
    EXPECT_EQ(square(-3), 9);
}

TEST(LambdaTest, MultiplyLambda) {
    auto multiply = create_multiply_lambda(10);
    EXPECT_EQ(multiply(5), 50);
    EXPECT_EQ(multiply(0), 0);
}

TEST(LambdaTest, TransformWithLambda) {
    std::vector<int> numbers = {1, 2, 3, 4};
    auto squared = transform_with_lambda(numbers);
    EXPECT_EQ(squared.size(), 4);
    EXPECT_EQ(squared[0], 1);
    EXPECT_EQ(squared[1], 4);
    EXPECT_EQ(squared[2], 9);
    EXPECT_EQ(squared[3], 16);
}

TEST(VectorTest, ListComprehension) {
    auto evens = list_comprehension();
    EXPECT_EQ(evens.size(), 5);
    EXPECT_EQ(evens[0], 0);
    EXPECT_EQ(evens[4], 8);
}

TEST(StringTest, StringOperations) {
    auto str = string_operations();
    EXPECT_EQ(str, "Hello World");
    EXPECT_EQ(str.size(), 11);
}

TEST(ClassTest, PersonClass) {
    Person p("Alice", 30);
    EXPECT_EQ(p.name, "Alice");
    EXPECT_EQ(p.age, 30);
    EXPECT_EQ(p.greet(), "Hello, I'm Alice");
}

TEST(OptionalTest, FindValue) {
    auto result = find_value("a");
    ASSERT_TRUE(result.has_value());
    EXPECT_EQ(result.value(), 1);

    auto missing = find_value("z");
    EXPECT_FALSE(missing.has_value());
}

TEST(TupleTest, CreateTuple) {
    auto [x, y] = create_tuple();
    EXPECT_EQ(x, 10);
    EXPECT_EQ(y, 20);
}

TEST(AlgorithmTest, FilterEvens) {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    auto evens = filter_evens(numbers);
    EXPECT_EQ(evens.size(), 2);
    EXPECT_EQ(evens[0], 2);
    EXPECT_EQ(evens[1], 4);
}

TEST(AlgorithmTest, HasEven) {
    std::vector<int> with_even = {1, 2, 3};
    std::vector<int> without_even = {1, 3, 5};
    EXPECT_TRUE(has_even(with_even));
    EXPECT_FALSE(has_even(without_even));
}

TEST(AlgorithmTest, AllPositive) {
    std::vector<int> all_pos = {1, 2, 3};
    std::vector<int> has_neg = {1, -2, 3};
    EXPECT_TRUE(all_positive(all_pos));
    EXPECT_FALSE(all_positive(has_neg));
}

TEST(AlgorithmTest, SortVector) {
    std::vector<int> unsorted = {3, 1, 4, 1, 5};
    auto sorted = sort_vector(unsorted);
    EXPECT_EQ(sorted[0], 1);
    EXPECT_EQ(sorted[4], 5);
}

TEST(AlgorithmTest, FindMin) {
    std::vector<int> numbers = {3, 1, 4, 1, 5};
    EXPECT_EQ(find_min(numbers), 1);
}

TEST(AlgorithmTest, SumVector) {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    EXPECT_EQ(sum_vector(numbers), 15);
}

TEST(FunctionTest, DefaultArguments) {
    EXPECT_EQ(greet("Alice"), "Hello, Alice");
    EXPECT_EQ(greet("Bob", "Hi"), "Hi, Bob");
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
