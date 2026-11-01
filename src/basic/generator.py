"""Python Generator Examples

Source code for docs/notes/basic/python-generator.rst
"""

import inspect
from contextlib import contextmanager
from types import GeneratorType

import pytest


# Generator Function
def simple_gen():
    """Simple generator yielding values."""
    yield 1
    yield 2
    yield 3


def countdown(n: int):
    """Countdown generator."""
    while n > 0:
        yield n
        n -= 1


def fibonacci(n: int):
    """Generate fibonacci sequence."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def infinite_counter(start: int = 0):
    """Infinite counter generator."""
    n = start
    while True:
        yield n
        n += 1


# Generator Expression
def gen_expr_sum(n: int) -> int:
    """Sum using generator expression."""
    return sum(x**2 for x in range(n))


# 发送 Values
def accumulator():
    """Accumulator that receives values via send."""
    total = 0
    while True:
        value = yield total
        if value is not None:
            total += value


# Generator 带返回
def average():
    """Calculate average, return via StopIteration."""
    total = 0.0
    count = 0
    while True:
        value = yield
        if value is None:
            break
        total += value
        count += 1
    return total / count if count else 0


# 产量来自
def chain(*iterables):
    """Chain multiple iterables."""
    for it in iterables:
        yield from it


def flatten(nested):
    """Flatten nested lists."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


# Iterable Class
class Range:
    """Custom range class using generator."""

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __iter__(self):
        n = self.start
        while n < self.end:
            yield n
            n += 1

    def __reversed__(self):
        n = self.end - 1
        while n >= self.start:
            yield n
            n -= 1


# 管道
def filter_positive(nums):
    """Filter positive numbers."""
    for n in nums:
        if n > 0:
            yield n


def double(nums):
    """Double each number."""
    for n in nums:
        yield n * 2


def read_lines(lines):
    """Strip whitespace from lines."""
    for line in lines:
        yield line.strip()


def filter_comments(lines):
    """Filter out comment lines."""
    for line in lines:
        if not line.startswith("#"):
            yield line


# 抛出并关闭
def gen_with_exception():
    """Generator that handles exceptions."""
    try:
        yield 1
        yield 2
    except ValueError:
        yield "caught"


def gen_with_cleanup():
    """Generator with cleanup in finally."""
    try:
        yield 1
        yield 2
    finally:
        pass  # 清理工作会在这里进行


# Context Manager
@contextmanager
def capture_output():
    """Context manager using generator."""
    output = []
    yield output


# 测试
class TestGeneratorBasics:
    def test_simple_gen(self):
        assert list(simple_gen()) == [1, 2, 3]

    def test_countdown(self):
        assert list(countdown(3)) == [3, 2, 1]

    def test_fibonacci(self):
        assert list(fibonacci(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    def test_infinite_counter(self):
        from itertools import islice

        assert list(islice(infinite_counter(), 5)) == [0, 1, 2, 3, 4]
        assert list(islice(infinite_counter(10), 3)) == [10, 11, 12]


class TestGeneratorExpression:
    def test_gen_expr_sum(self):
        assert gen_expr_sum(5) == 0 + 1 + 4 + 9 + 16

    def test_unpack(self):
        g = (x for x in range(3))
        assert [*g] == [0, 1, 2]

    def test_unpack_multiple(self):
        g1 = (x for x in range(2))
        g2 = (x**2 for x in range(2))
        assert [*g1, *g2] == [0, 1, 0, 1]


class TestSend:
    def test_accumulator(self):
        acc = accumulator()
        assert next(acc) == 0
        assert acc.send(10) == 10
        assert acc.send(20) == 30
        assert acc.send(5) == 35


class TestGeneratorReturn:
    def test_average(self):
        g = average()
        next(g)
        g.send(10)
        g.send(20)
        g.send(30)
        try:
            g.send(None)
        except StopIteration as e:
            assert e.value == 20.0


class TestYieldFrom:
    def test_chain(self):
        assert list(chain([1, 2], [3, 4])) == [1, 2, 3, 4]

    def test_flatten(self):
        assert list(flatten([1, [2, [3, 4], 5], 6])) == [1, 2, 3, 4, 5, 6]


class TestIterableClass:
    def test_range(self):
        assert list(Range(1, 5)) == [1, 2, 3, 4]

    def test_reversed_range(self):
        assert list(reversed(Range(1, 5))) == [4, 3, 2, 1]


class TestPipeline:
    def test_pipeline(self):
        nums = [-1, 2, -3, 4, 5]
        result = list(double(filter_positive(nums)))
        assert result == [4, 8, 10]

    def test_text_pipeline(self):
        data = ["  hello  ", "# comment", "  world  "]
        result = list(filter_comments(read_lines(data)))
        assert result == ["hello", "world"]


class TestThrowClose:
    def test_throw(self):
        g = gen_with_exception()
        assert next(g) == 1
        assert g.throw(ValueError) == "caught"

    def test_close(self):
        g = gen_with_cleanup()
        assert next(g) == 1
        g.close()  # 不应该提高


class TestGeneratorState:
    def test_states(self):
        def gen():
            yield 1

        g = gen()
        assert inspect.getgeneratorstate(g) == "GEN_CREATED"
        next(g)
        assert inspect.getgeneratorstate(g) == "GEN_SUSPENDED"
        try:
            next(g)
        except StopIteration:
            pass
        assert inspect.getgeneratorstate(g) == "GEN_CLOSED"


class TestGeneratorType:
    def test_isinstance(self):
        def gen():
            yield 1

        assert isinstance(gen(), GeneratorType)
        assert not isinstance([1, 2, 3], GeneratorType)


class TestContextManager:
    def test_capture(self):
        with capture_output() as out:
            out.append("test")
        assert out == ["test"]


# 总理 Generator
def prime(n: int):
    """Generate n prime numbers."""
    p = 2
    while n > 0:
        for x in range(2, p):
            if p % x == 0:
                break
        else:
            yield p
            n -= 1
        p += 1


# Closure 使用 Generator
def closure_gen(start: int = 0):
    """Closure implemented as generator."""
    x = start
    while True:
        x += 1
        yield x


# 简单的调度程序
def fib(n: int) -> int:
    """Fibonacci for scheduler example."""
    if n <= 2:
        return 1
    return fib(n - 1) + fib(n - 2)


def g_fib(n: int):
    """Generator yielding fibonacci numbers."""
    for x in range(1, n + 1):
        yield fib(x)


def run_scheduler(tasks: list) -> list:
    """Simple round-robin scheduler."""
    from collections import deque

    q = deque(tasks)
    results = []
    while q:
        try:
            t = q.popleft()
            results.append(next(t))
            q.append(t)
        except StopIteration:
            results.append("done")
    return results


# Compiler 组件
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])


def tokenize(text: str):
    """Tokenize arithmetic expression."""
    tokens = [
        r"(?P<NUMBER>\d+)",
        r"(?P<PLUS>\+)",
        r"(?P<MINUS>-)",
        r"(?P<TIMES>\*)",
        r"(?P<DIVIDE>/)",
        r"(?P<WS>\s+)",
    ]
    lex = re.compile("|".join(tokens))
    scan = lex.scanner(text)
    return (
        Token(m.lastgroup, m.group())
        for m in iter(scan.match, None)
        if m.lastgroup != "WS"
    )


class Node:
    _fields = []

    def __init__(self, *args):
        for attr, value in zip(self._fields, args):
            setattr(self, attr, value)


class Number(Node):
    _fields = ["value"]


class BinOp(Node):
    _fields = ["op", "left", "right"]


def parse(toks):
    """Parse tokens into AST."""
    lookahead, current = next(toks, None), None

    def accept(*toktypes):
        nonlocal lookahead, current
        if lookahead and lookahead.type in toktypes:
            current, lookahead = lookahead, next(toks, None)
            return True

    def expr():
        left = term()
        while accept("PLUS", "MINUS"):
            left = BinOp(current.value, left)
            left.right = term()
        return left

    def term():
        left = factor()
        while accept("TIMES", "DIVIDE"):
            left = BinOp(current.value, left)
            left.right = factor()
        return left

    def factor():
        if accept("NUMBER"):
            return Number(int(current.value))
        raise SyntaxError()

    return expr()


import types


class NodeVisitor:
    """Visitor using generators for stack-based evaluation."""

    def visit(self, node):
        stack = [self.genvisit(node)]
        ret = None
        while stack:
            try:
                node = stack[-1].send(ret)
                stack.append(self.genvisit(node))
                ret = None
            except StopIteration as e:
                stack.pop()
                ret = e.value
        return ret

    def genvisit(self, node):
        ret = getattr(self, "visit_" + type(node).__name__)(node)
        if isinstance(ret, types.GeneratorType):
            ret = yield from ret
        return ret


class Evaluator(NodeVisitor):
    """Evaluate AST using generator-based visitor."""

    def visit_Number(self, node):
        return node.value

    def visit_BinOp(self, node):
        leftval = yield node.left
        rightval = yield node.right
        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
        }
        return ops[node.op](leftval, rightval)


def evaluate(exp: str):
    """Evaluate arithmetic expression."""
    toks = tokenize(exp)
    tree = parse(toks)
    return Evaluator().visit(tree)


# 用于比较的异步 Iterator
class AsyncIter:
    """Async iterator for performance comparison."""

    def __init__(self, n):
        self._n = n

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._n == 0:
            raise StopAsyncIteration
        self._n -= 1
        return self._n


async def agen(n: int):
    """Async generator for performance comparison."""
    for i in range(n):
        yield i


# 附加测试
class TestPrime:
    def test_prime(self):
        assert list(prime(5)) == [2, 3, 5, 7, 11]


class TestClosure:
    def test_closure_gen(self):
        g = closure_gen(5566)
        assert next(g) == 5567
        assert next(g) == 5568
        assert next(g) == 5569


class TestScheduler:
    def test_round_robin(self):
        results = run_scheduler([g_fib(3), g_fib(3)])
        assert results == [1, 1, 1, 1, 2, 2, "done", "done"]


class TestCompiler:
    def test_tokenize(self):
        tokens = list(tokenize("2 + 3"))
        assert tokens[0] == Token("NUMBER", "2")
        assert tokens[1] == Token("PLUS", "+")
        assert tokens[2] == Token("NUMBER", "3")

    def test_evaluate_simple(self):
        assert evaluate("2 + 3") == 5
        assert evaluate("2 * 3") == 6
        assert evaluate("10 - 4") == 6
        assert evaluate("8 / 2") == 4.0

    def test_evaluate_complex(self):
        assert evaluate("2 * 3 + 5") == 11
        assert evaluate("2 + 3 * 5") == 17
        assert evaluate("2 * 3 + 5 / 2") == 8.5


class TestAsyncGen:
    def test_async_iter(self):
        import asyncio

        async def collect():
            return [x async for x in agen(5)]

        assert asyncio.run(collect()) == [0, 1, 2, 3, 4]

    def test_async_iter_class(self):
        import asyncio

        async def collect():
            return [x async for x in AsyncIter(5)]

        assert asyncio.run(collect()) == [4, 3, 2, 1, 0]
