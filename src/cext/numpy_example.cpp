/**
 * numpy_example.cpp - pybind11 NumPy 集成
 *
 * 演示：
 *   - 接受NumPy arrays
 *   - 就地修改arrays（零拷贝）
 *   - 返回新的 arrays
 *   - 2D array 操作
 *
 * 用法：
 *   >>> import numpy as np
 *   >>> from numpy_example import multiply_inplace, add_arrays, matrix_sum
 *   >>> arr = np.array([1.0, 2.0, 3.0])
 *   >>> multiply_inplace(arr, 2.0)
 *   >>> arr
 *   array([2., 4., 6.])
 */
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <stdexcept>

namespace py = pybind11;

// 就地修改array（无复制）
void multiply_inplace(py::array_t<double> arr, double factor) {
  auto buf = arr.mutable_unchecked<1>();
  for (py::ssize_t i = 0; i < buf.shape(0); i++) {
    buf(i) *= factor;
  }
}

// 返回新的 array
py::array_t<double> add_arrays(py::array_t<double> a, py::array_t<double> b) {
  auto buf_a = a.unchecked<1>();
  auto buf_b = b.unchecked<1>();

  if (buf_a.shape(0) != buf_b.shape(0)) {
    throw std::runtime_error("Arrays must have same length");
  }

  auto result = py::array_t<double>(buf_a.shape(0));
  auto buf_r = result.mutable_unchecked<1>();

  for (py::ssize_t i = 0; i < buf_a.shape(0); i++) {
    buf_r(i) = buf_a(i) + buf_b(i);
  }
  return result;
}

// 将所有 elements 以 2D array 形式求和
double matrix_sum(py::array_t<double> mat) {
  auto buf = mat.unchecked<2>();
  double sum = 0;
  for (py::ssize_t i = 0; i < buf.shape(0); i++) {
    for (py::ssize_t j = 0; j < buf.shape(1); j++) {
      sum += buf(i, j);
    }
  }
  return sum;
}

// Element方向正方形
py::array_t<double> square(py::array_t<double> arr) {
  auto buf = arr.unchecked<1>();
  auto result = py::array_t<double>(buf.shape(0));
  auto buf_r = result.mutable_unchecked<1>();

  for (py::ssize_t i = 0; i < buf.shape(0); i++) {
    buf_r(i) = buf(i) * buf(i);
  }
  return result;
}

PYBIND11_MODULE(numpy_example, m) {
  m.doc() = "NumPy integration examples";

  m.def("multiply_inplace", &multiply_inplace, "Multiply array elements by factor in-place", py::arg("arr"), py::arg("factor"));

  m.def("add_arrays", &add_arrays, "Add two arrays element-wise", py::arg("a"), py::arg("b"));

  m.def("matrix_sum", &matrix_sum, "Sum all elements in 2D array", py::arg("mat"));

  m.def("square", &square, "Square each element", py::arg("arr"));
}
