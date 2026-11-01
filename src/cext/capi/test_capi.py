"""Tests for Python C API extension examples."""

import pytest
import sys
import os

# 将构建目录添加到路径
build_dir = os.path.join(os.path.dirname(__file__), "build")
for d in os.listdir(build_dir) if os.path.exists(build_dir) else []:
    path = os.path.join(build_dir, d)
    if os.path.isdir(path) and path not in sys.path:
        sys.path.insert(0, path)


class TestSimple:
    """Test simple module."""

    def test_hello(self):
        import simple

        assert simple.hello() == "Hello from C!"

    def test_add(self):
        import simple

        assert simple.add(1, 2) == 3
        assert simple.add(-5, 10) == 5

    def test_fib(self):
        import simple

        assert simple.fib(0) == 0
        assert simple.fib(1) == 1
        assert simple.fib(10) == 55
        assert simple.fib(20) == 6765


class TestArgs:
    """Test argument parsing module."""

    def test_no_args(self):
        import args

        assert args.no_args() is None

    def test_single_arg(self):
        import args

        assert args.single_arg(42) == 42
        assert args.single_arg("hello") == "hello"

    def test_pos_args(self):
        import args

        assert args.pos_args(1, 2) == (1, 2)
        assert args.pos_args("a", "b") == ("a", "b")

    def test_kw_args(self):
        import args

        assert args.kw_args(1, 2) == (1, 2, None)
        assert args.kw_args(1, 2, 3) == (1, 2, 3)
        assert args.kw_args(x=1, y=2, z=3) == (1, 2, 3)

    def test_typed_args(self):
        import args

        result = args.typed_args(42, 3.14, "hello")
        assert result == {"int": 42, "double": 3.14, "str": "hello"}


class TestGil:
    """Test GIL handling module."""

    def test_fib_no_gil(self):
        import gil

        assert gil.fib_no_gil(10) == 55
        assert gil.fib_no_gil(20) == 6765


class TestErrors:
    """Test exception handling module."""

    def test_raise_value_error(self):
        import errors

        with pytest.raises(ValueError, match="This is a ValueError"):
            errors.raise_value_error()

    def test_raise_foo_error(self):
        import errors

        with pytest.raises(errors.FooError, match="This is a custom FooError"):
            errors.raise_foo_error()

    def test_raise_with_format(self):
        import errors

        with pytest.raises(RuntimeError, match="Error code: 42"):
            errors.raise_with_format(42)

    def test_divide(self):
        import errors

        assert errors.divide(10.0, 2.0) == 5.0
        with pytest.raises(ZeroDivisionError):
            errors.divide(1.0, 0.0)


class TestTypesDemo:
    """Test Python types manipulation."""

    def test_list_demo(self):
        import types_demo

        assert types_demo.list_demo() == [1, 2, 3]

    def test_list_sum(self):
        import types_demo

        assert types_demo.list_sum([1, 2, 3, 4]) == 10

    def test_iter_list(self):
        import types_demo

        assert types_demo.iter_list([1, 2, 3]) == [2, 4, 6]

    def test_dict_demo(self):
        import types_demo

        assert types_demo.dict_demo() == {"name": "Python", "version": 3}

    def test_dict_get(self):
        import types_demo

        d = {"a": 1, "b": 2}
        assert types_demo.dict_get(d, "a") == 1
        assert types_demo.dict_get(d, "c") is None

    def test_iter_dict(self):
        import types_demo

        d = {"x": 1, "y": 2}
        result = types_demo.iter_dict(d)
        assert set(result) == {("x", 1), ("y", 2)}

    def test_tuple_demo(self):
        import types_demo

        assert types_demo.tuple_demo() == (1, "hello", 3.14)

    def test_tuple_unpack(self):
        import types_demo

        result = types_demo.tuple_unpack((42, "test", 2.5))
        assert result == {"int": 42, "str": "test", "float": 2.5}

    def test_set_demo(self):
        import types_demo

        assert types_demo.set_demo() == {1, 2, 3}

    def test_set_contains(self):
        import types_demo

        s = {1, 2, 3}
        assert types_demo.set_contains(s, 2) is True
        assert types_demo.set_contains(s, 5) is False

    def test_str_demo(self):
        import types_demo

        assert types_demo.str_demo() == "Hello World"

    def test_str_format(self):
        import types_demo

        assert types_demo.str_format("Alice", 30) == "Alice is 30 years old"

    def test_bytes_demo(self):
        import types_demo

        assert types_demo.bytes_demo() == b"hello bytes"

    def test_bytes_len(self):
        import types_demo

        assert types_demo.bytes_len(b"hello") == 5
