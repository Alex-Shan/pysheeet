"""
Tests for pybind11 C++ extension modules.

Run from src/cext directory:
    python -m pytest test_cext.py -v

Build first:
    mkdir build && cd build && cmake .. && make
"""

import sys
import threading
from datetime import datetime

import pytest

# 尝试导入编译好的modules（conftest.py的路径set）
try:
    import example

    HAS_EXAMPLE = True
except ImportError:
    HAS_EXAMPLE = False

try:
    import vector

    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False

try:
    import numpy as np
    import numpy_example

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import gil_example

    HAS_GIL = True
except ImportError:
    HAS_GIL = False


@pytest.mark.skipif(not HAS_EXAMPLE, reason="example module not built")
class TestExample:
    """Test basic pybind11 functions."""

    def test_add(self):
        assert example.add(1, 2) == 3
        assert example.add(-5, 10) == 5
        assert example.add(0, 0) == 0

    def test_fib(self):
        assert example.fib(0) == 0
        assert example.fib(1) == 1
        assert example.fib(10) == 55
        assert example.fib(20) == 6765

    def test_fib_iter(self):
        assert example.fib_iter(0) == 0
        assert example.fib_iter(1) == 1
        assert example.fib_iter(10) == 55
        assert example.fib_iter(50) == 12586269025


@pytest.mark.skipif(not HAS_VECTOR, reason="vector module not built")
class TestVector:
    """Test Vector2D class binding."""

    def test_constructor(self):
        v = vector.Vector2D()
        assert v.x == 0
        assert v.y == 0

        v = vector.Vector2D(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_length(self):
        v = vector.Vector2D(3, 4)
        assert abs(v.length() - 5.0) < 1e-10

        v = vector.Vector2D(0, 0)
        assert v.length() == 0

    def test_dot(self):
        v1 = vector.Vector2D(1, 2)
        v2 = vector.Vector2D(3, 4)
        assert v1.dot(v2) == 11  # 1*3 + 2*4

    def test_normalized(self):
        v = vector.Vector2D(3, 4)
        n = v.normalized()
        assert abs(n.length() - 1.0) < 1e-10

    def test_add(self):
        v1 = vector.Vector2D(1, 2)
        v2 = vector.Vector2D(3, 4)
        v3 = v1 + v2
        assert v3.x == 4
        assert v3.y == 6

    def test_sub(self):
        v1 = vector.Vector2D(5, 7)
        v2 = vector.Vector2D(2, 3)
        v3 = v1 - v2
        assert v3.x == 3
        assert v3.y == 4

    def test_mul(self):
        v = vector.Vector2D(2, 3)
        v2 = v * 2.0
        assert v2.x == 4
        assert v2.y == 6

    def test_eq(self):
        v1 = vector.Vector2D(1, 2)
        v2 = vector.Vector2D(1, 2)
        v3 = vector.Vector2D(1, 3)
        assert v1 == v2
        assert not (v1 == v3)

    def test_repr(self):
        v = vector.Vector2D(3, 4)
        assert "Vector2D" in repr(v)
        assert "3" in repr(v)
        assert "4" in repr(v)


@pytest.mark.skipif(not HAS_NUMPY, reason="numpy_example module not built")
class TestNumPy:
    """Test NumPy integration."""

    def test_multiply_inplace(self):
        arr = np.array([1.0, 2.0, 3.0])
        numpy_example.multiply_inplace(arr, 2.0)
        np.testing.assert_array_equal(arr, [2.0, 4.0, 6.0])

    def test_add_arrays(self):
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])
        result = numpy_example.add_arrays(a, b)
        np.testing.assert_array_equal(result, [5.0, 7.0, 9.0])

    def test_add_arrays_length_mismatch(self):
        a = np.array([1.0, 2.0])
        b = np.array([1.0, 2.0, 3.0])
        with pytest.raises(RuntimeError):
            numpy_example.add_arrays(a, b)

    def test_matrix_sum(self):
        mat = np.array([[1.0, 2.0], [3.0, 4.0]])
        assert numpy_example.matrix_sum(mat) == 10.0

    def test_square(self):
        arr = np.array([1.0, 2.0, 3.0])
        result = numpy_example.square(arr)
        np.testing.assert_array_equal(result, [1.0, 4.0, 9.0])


@pytest.mark.skipif(not HAS_GIL, reason="gil_example module not built")
class TestGIL:
    """Test GIL release functionality."""

    def test_fib_nogil(self):
        result = gil_example.fib_nogil(20)
        assert result == 6765

    def test_slow_operation_parallel(self):
        """Test that slow_operation releases GIL allowing parallel execution."""
        results = []
        start = datetime.now()

        def worker(n):
            results.append(n)
            gil_example.slow_operation(1)

        threads = [
            threading.Thread(target=worker, args=(i,)) for i in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = (datetime.now() - start).total_seconds()
        # 如果 GIL 已发布，所有 3 个操作应在约 1 秒内完成
        # 如果持有 GIL，大约需要 3 秒
        assert elapsed < 2.0, f"Took {elapsed}s, GIL may not be released"
        assert len(results) == 3

    def test_callback(self):
        """Test calling Python callback from C++."""
        results = []

        def callback(msg):
            results.append(msg)

        gil_example.call_python_callback(callback, "hello")
        assert results == ["hello"]
