/**
 * example.cpp - 基本 pybind11 示例
 *
 * 建造：
 *   mkdir build && cd build
 *   cmake .. && make
 *
 * 用法：
 *   >>> import example
 *   >>> example.add(1, 2)
 *   3
 *   >>> example.fib(10)
 *   55
 */
#include <pybind11/pybind11.h>

namespace py = pybind11;

int add(int a, int b) { return a + b; }

unsigned long fib(unsigned long n) {
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);
}

// 大 n 的迭代版本
unsigned long fib_iter(unsigned long n) {
  if (n < 2) return n;
  unsigned long a = 0, b = 1;
  for (unsigned long i = 1; i < n; ++i) {
    unsigned long tmp = a + b;
    a = b;
    b = tmp;
  }
  return b;
}

PYBIND11_MODULE(example, m) {
  m.doc() = "Example pybind11 module with basic functions";

  m.def("add", &add, "Add two integers", py::arg("a"), py::arg("b"));

  m.def("fib", &fib, "Compute Fibonacci number (recursive)", py::arg("n"));

  m.def("fib_iter", &fib_iter, "Compute Fibonacci number (iterative)", py::arg("n"));
}
