"""Python Function Examples

Source code for docs/notes/basic/python-func.rst
"""

from functools import lru_cache, partial, reduce, singledispatch, wraps

import pytest


# Default Arguments
def greet(name: str, greeting: str = "Hello") -> str:
    """Greet with optional greeting."""
    return f"{greeting}, {name}!"


def good_default(items=None):
    """Correct way to use mutable default."""
    if items is None:
        items = []
    items.append(1)
    return items


# Variable Arguments
def sum_all(*args) -> int:
    """Sum all positional arguments."""
    return sum(args)


def format_info(**kwargs) -> str:
    """Format keyword arguments."""
    return ", ".join(f"{k}={v}" for k, v in kwargs.items())


def mixed_args(a, b=None, *args, **kwargs):
    """Function with mixed argument types."""
    return {"a": a, "b": b, "args": args, "kwargs": kwargs}


# 仅关键字 Arguments
def keyword_only(a, b, *, kw):
    """Function with keyword-only argument."""
    return a + b + kw


def keyword_only_default(a, *, kw=10):
    """Keyword-only with default value."""
    return a + kw


# 仅位置 Arguments (Python 3.8+)
def positional_only(a, b, /, c):
    """Function with positional-only arguments."""
    return a + b + c


def combined_args(a, /, b, *, c):
    """Positional-only and keyword-only combined."""
    return a + b + c


# Lambda
square = lambda x: x**2
add = lambda a, b: a + b
max_val = lambda a, b: a if a > b else b


# Closure
def make_multiplier(n: int):
    """Create a multiplier function."""

    def multiplier(x: int) -> int:
        return x * n

    return multiplier


def make_counter():
    """Create a counter with mutable state."""
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


# Generator
def fibonacci(n: int):
    """Generate fibonacci sequence."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# Decorator
def log_calls(func):
    """Decorator that logs function calls."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)

    wrapper.call_count = 0
    return wrapper


# Decorator 与 Arguments
def repeat(times: int):
    """Decorator that repeats function calls."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


# Class Decorator
class CountCalls:
    """Decorator class that counts calls."""

    def __init__(self, func):
        self.func = func
        self.count = 0
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)


# Cache
@lru_cache(maxsize=None)
def fib_cached(n: int) -> int:
    """Fibonacci with caching."""
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


# 部分的
def power(base: int, exponent: int) -> int:
    """Raise base to exponent."""
    return base**exponent


square_partial = partial(power, exponent=2)
cube_partial = partial(power, exponent=3)


# 单次调度
@singledispatch
def process(arg):
    """Generic function with type dispatch."""
    return f"Default: {arg}"


@process.register(int)
def _(arg):
    return f"Integer: {arg * 2}"


@process.register(list)
def _(arg):
    return f"List with {len(arg)} items"


# 可调用 Class
class Adder:
    """Callable class that adds a fixed value."""

    def __init__(self, n: int):
        self.n = n

    def __call__(self, x: int) -> int:
        return self.n + x


# 高阶 functions
def apply_twice(func, x):
    """Apply function twice."""
    return func(func(x))


# 测试
class TestDefaultArguments:
    def test_default(self):
        assert greet("Alice") == "Hello, Alice!"

    def test_custom(self):
        assert greet("Bob", "Hi") == "Hi, Bob!"

    def test_mutable_default(self):
        assert good_default() == [1]
        assert good_default() == [1]  # 不是 [1, 1]


class TestVariableArguments:
    def test_args(self):
        assert sum_all(1, 2, 3, 4, 5) == 15

    def test_kwargs(self):
        result = format_info(name="Alice", age=30)
        assert "name=Alice" in result
        assert "age=30" in result

    def test_mixed(self):
        result = mixed_args(1, 2, 3, 4, x=5)
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["args"] == (3, 4)
        assert result["kwargs"] == {"x": 5}


class TestKeywordOnly:
    def test_keyword_only(self):
        assert keyword_only(1, 2, kw=3) == 6

    def test_keyword_only_default(self):
        assert keyword_only_default(5) == 15
        assert keyword_only_default(5, kw=20) == 25


class TestPositionalOnly:
    def test_positional_only(self):
        assert positional_only(1, 2, 3) == 6
        assert positional_only(1, 2, c=3) == 6

    def test_combined(self):
        assert combined_args(1, 2, c=3) == 6
        assert combined_args(1, b=2, c=3) == 6


class TestLambda:
    def test_square(self):
        assert square(5) == 25

    def test_add(self):
        assert add(2, 3) == 5

    def test_conditional(self):
        assert max_val(3, 5) == 5
        assert max_val(7, 2) == 7


class TestClosure:
    def test_multiplier(self):
        double = make_multiplier(2)
        triple = make_multiplier(3)
        assert double(5) == 10
        assert triple(5) == 15

    def test_counter(self):
        counter = make_counter()
        assert counter() == 1
        assert counter() == 2
        assert counter() == 3


class TestGenerator:
    def test_fibonacci(self):
        assert list(fibonacci(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


class TestDecorator:
    def test_log_calls(self):
        @log_calls
        def example():
            return "result"

        example()
        example()
        assert example.call_count == 2
        assert example.__name__ == "example"

    def test_repeat(self):
        counter = {"count": 0}

        @repeat(3)
        def increment():
            counter["count"] += 1

        increment()
        assert counter["count"] == 3


class TestClassDecorator:
    def test_count_calls(self):
        @CountCalls
        def example():
            return "result"

        example()
        example()
        assert example.count == 2


class TestCache:
    def test_fib_cached(self):
        fib_cached.cache_clear()
        assert fib_cached(10) == 55
        assert fib_cached(20) == 6765
        info = fib_cached.cache_info()
        assert info.hits > 0


class TestPartial:
    def test_square(self):
        assert square_partial(5) == 25

    def test_cube(self):
        assert cube_partial(5) == 125


class TestSingledispatch:
    def test_default(self):
        assert process("hello") == "Default: hello"

    def test_int(self):
        assert process(5) == "Integer: 10"

    def test_list(self):
        assert process([1, 2, 3]) == "List with 3 items"


class TestCallable:
    def test_adder(self):
        add_five = Adder(5)
        assert add_five(10) == 15
        assert callable(add_five)


class TestHigherOrder:
    def test_apply_twice(self):
        assert apply_twice(lambda x: x * 2, 3) == 12

    def test_map(self):
        assert list(map(square, [1, 2, 3])) == [1, 4, 9]

    def test_filter(self):
        assert list(filter(lambda x: x > 2, [1, 2, 3, 4])) == [3, 4]

    def test_reduce(self):
        assert reduce(lambda x, y: x + y, [1, 2, 3, 4, 5]) == 15
        assert reduce(lambda x, y: x * y, [1, 2, 3, 4, 5]) == 120
