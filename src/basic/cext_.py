"""
Tests for C extension examples (ctypes and cffi).

These tests demonstrate calling C code from Python without
requiring compilation of pybind11/Cython modules.
"""

import ctypes
import math
import os
import platform
import subprocess
import tempfile

import pytest


# 如果没有 C compiler 可用，则跳过所有测试
def has_c_compiler():
    """Check if gcc or clang is available."""
    for compiler in ["gcc", "clang", "cc"]:
        try:
            result = subprocess.run(
                [compiler, "--version"], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


requires_compiler = pytest.mark.skipif(
    not has_c_compiler(), reason="No C compiler available"
)


class TestCtypesBasic:
    """Test ctypes with standard library functions."""

    def test_libc_strlen(self):
        """Test calling strlen from libc."""
        if platform.system() == "Darwin":
            libc = ctypes.CDLL("libc.dylib")
        elif platform.system() == "Linux":
            libc = ctypes.CDLL("libc.so.6")
        else:
            pytest.skip("Unsupported platform")

        libc.strlen.argtypes = [ctypes.c_char_p]
        libc.strlen.restype = ctypes.c_size_t

        result = libc.strlen(b"hello")
        assert result == 5

    def test_libc_abs(self):
        """Test calling abs from libc."""
        if platform.system() == "Darwin":
            libc = ctypes.CDLL("libc.dylib")
        elif platform.system() == "Linux":
            libc = ctypes.CDLL("libc.so.6")
        else:
            pytest.skip("Unsupported platform")

        assert libc.abs(-42) == 42
        assert libc.abs(42) == 42

    def test_math_sqrt(self):
        """Test calling sqrt from libm."""
        if platform.system() == "Darwin":
            libm = ctypes.CDLL("libm.dylib")
        elif platform.system() == "Linux":
            libm = ctypes.CDLL("libm.so.6")
        else:
            pytest.skip("Unsupported platform")

        libm.sqrt.argtypes = [ctypes.c_double]
        libm.sqrt.restype = ctypes.c_double

        result = libm.sqrt(16.0)
        assert abs(result - 4.0) < 1e-10


class TestCtypesStructures:
    """Test ctypes with structures."""

    def test_simple_structure(self):
        """Test creating and using a ctypes Structure."""

        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0

        # 手动计算距离
        distance = math.sqrt(p.x**2 + p.y**2)
        assert abs(distance - 5.0) < 1e-10

    def test_nested_structure(self):
        """Test nested structures."""

        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

        class Rectangle(ctypes.Structure):
            _fields_ = [("top_left", Point), ("bottom_right", Point)]

        rect = Rectangle(Point(0, 10), Point(10, 0))
        assert rect.top_left.x == 0
        assert rect.top_left.y == 10
        assert rect.bottom_right.x == 10
        assert rect.bottom_right.y == 0

    def test_array_in_structure(self):
        """Test arrays within structures."""

        class Data(ctypes.Structure):
            _fields_ = [("values", ctypes.c_int * 5), ("count", ctypes.c_int)]

        d = Data()
        d.count = 5
        for i in range(5):
            d.values[i] = i * 10

        assert list(d.values) == [0, 10, 20, 30, 40]
        assert d.count == 5


class TestCtypesPointers:
    """Test ctypes pointer operations."""

    def test_pointer_to_int(self):
        """Test pointer to integer."""
        value = ctypes.c_int(42)
        ptr = ctypes.pointer(value)
        assert ptr.contents.value == 42

        # 通过指针修改
        ptr.contents.value = 100
        assert value.value == 100

    def test_byref(self):
        """Test byref for passing by reference."""
        value = ctypes.c_int(42)
        # byref 创建一个轻量级指针用于传递给 C functions
        ref = ctypes.byref(value)
        # byref 返回 CArgObject，而不是完整指针
        assert ref is not None


@requires_compiler
class TestCtypesCustomLibrary:
    """Test ctypes with custom compiled C code."""

    @pytest.fixture
    def fib_library(self, tmp_path):
        """Compile a simple Fibonacci library."""
        c_code = """
        unsigned long fib(unsigned long n) {
            if (n < 2) return n;
            return fib(n - 1) + fib(n - 2);
        }

        int add(int a, int b) {
            return a + b;
        }

        double multiply(double a, double b) {
            return a * b;
        }
        """

        c_file = tmp_path / "fib.c"
        c_file.write_text(c_code)

        if platform.system() == "Darwin":
            lib_file = tmp_path / "libfib.dylib"
            cmd = [
                "clang",
                "-shared",
                "-fPIC",
                "-o",
                str(lib_file),
                str(c_file),
            ]
        else:
            lib_file = tmp_path / "libfib.so"
            cmd = ["gcc", "-shared", "-fPIC", "-o", str(lib_file), str(c_file)]

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            pytest.skip(f"Compilation failed: {result.stderr.decode()}")

        lib = ctypes.CDLL(str(lib_file))

        # Set 最多 function 签名
        lib.fib.argtypes = [ctypes.c_ulong]
        lib.fib.restype = ctypes.c_ulong

        lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.add.restype = ctypes.c_int

        lib.multiply.argtypes = [ctypes.c_double, ctypes.c_double]
        lib.multiply.restype = ctypes.c_double

        return lib

    def test_fib(self, fib_library):
        """Test Fibonacci function."""
        assert fib_library.fib(0) == 0
        assert fib_library.fib(1) == 1
        assert fib_library.fib(10) == 55
        assert fib_library.fib(20) == 6765

    def test_add(self, fib_library):
        """Test add function."""
        assert fib_library.add(1, 2) == 3
        assert fib_library.add(-5, 10) == 5
        assert fib_library.add(0, 0) == 0

    def test_multiply(self, fib_library):
        """Test multiply function with doubles."""
        assert abs(fib_library.multiply(2.5, 4.0) - 10.0) < 1e-10
        assert abs(fib_library.multiply(-1.5, 2.0) - (-3.0)) < 1e-10


class TestCffi:
    """Test cffi if available."""

    @pytest.fixture
    def cffi_available(self):
        """Check if cffi is installed."""
        try:
            import cffi

            return cffi.FFI()
        except ImportError:
            pytest.skip("cffi not installed")

    def test_cffi_libc(self, cffi_available):
        """Test cffi with libc."""
        ffi = cffi_available

        ffi.cdef("""
            int abs(int x);
            size_t strlen(const char *s);
        """)

        if platform.system() == "Darwin":
            libc = ffi.dlopen("libc.dylib")
        elif platform.system() == "Linux":
            libc = ffi.dlopen("libc.so.6")
        else:
            pytest.skip("Unsupported platform")

        assert libc.abs(-42) == 42
        assert libc.strlen(b"hello") == 5

    def test_cffi_math(self, cffi_available):
        """Test cffi with libm."""
        ffi = cffi_available

        ffi.cdef("""
            double sqrt(double x);
            double pow(double x, double y);
        """)

        if platform.system() == "Darwin":
            libm = ffi.dlopen("libm.dylib")
        elif platform.system() == "Linux":
            libm = ffi.dlopen("libm.so.6")
        else:
            pytest.skip("Unsupported platform")

        assert abs(libm.sqrt(16.0) - 4.0) < 1e-10
        assert abs(libm.pow(2.0, 10.0) - 1024.0) < 1e-10


class TestPythonPerformance:
    """Test pure Python implementations for comparison."""

    def test_python_fib(self):
        """Test pure Python Fibonacci."""

        def fib(n):
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)

        assert fib(0) == 0
        assert fib(1) == 1
        assert fib(10) == 55
        assert fib(20) == 6765

    def test_python_fib_iterative(self):
        """Test iterative Fibonacci (faster)."""

        def fib_iter(n):
            if n < 2:
                return n
            a, b = 0, 1
            for _ in range(n - 1):
                a, b = b, a + b
            return b

        assert fib_iter(0) == 0
        assert fib_iter(1) == 1
        assert fib_iter(10) == 55
        assert fib_iter(50) == 12586269025

    def test_python_fib_memoized(self):
        """Test memoized Fibonacci."""
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def fib_memo(n):
            if n < 2:
                return n
            return fib_memo(n - 1) + fib_memo(n - 2)

        assert fib_memo(0) == 0
        assert fib_memo(1) == 1
        assert fib_memo(10) == 55
        assert fib_memo(50) == 12586269025
