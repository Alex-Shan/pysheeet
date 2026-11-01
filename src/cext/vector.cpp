/**
 * vector.cpp - pybind11 class 绑定示例
 *
 * 演示：
 *   - Class 与构造函数绑定
 *   - 读/写properties
 *   - Methods
 *   - Operator 过载
 *   - __repr__ 打印精美
 *
 * 用法：
 *   >>> from vector import Vector2D
 *   >>> v1 = Vector2D(3, 4)
 *   >>> v1.length()
 *   5.0
 *   >>> v2 = Vector2D(1, 2)
 *   >>> v3 = v1 + v2
 *   >>> v3
 *   Vector2D(4.0, 6.0)
 */
#include <pybind11/pybind11.h>

#include <cmath>
#include <sstream>

namespace py = pybind11;

class Vector2D {
 public:
  double x, y;

  Vector2D(double x = 0, double y = 0) : x(x), y(y) {}

  double length() const { return std::sqrt(x * x + y * y); }

  double dot(const Vector2D& other) const { return x * other.x + y * other.y; }

  Vector2D normalized() const {
    double len = length();
    if (len == 0) return Vector2D(0, 0);
    return Vector2D(x / len, y / len);
  }

  Vector2D operator+(const Vector2D& other) const { return Vector2D(x + other.x, y + other.y); }

  Vector2D operator-(const Vector2D& other) const { return Vector2D(x - other.x, y - other.y); }

  Vector2D operator*(double scalar) const { return Vector2D(x * scalar, y * scalar); }

  bool operator==(const Vector2D& other) const { return x == other.x && y == other.y; }

  std::string repr() const {
    std::ostringstream oss;
    oss << "Vector2D(" << x << ", " << y << ")";
    return oss.str();
  }
};

PYBIND11_MODULE(vector, m) {
  m.doc() = "2D Vector class example";

  py::class_<Vector2D>(m, "Vector2D")
      .def(py::init<double, double>(), py::arg("x") = 0, py::arg("y") = 0)
      .def_readwrite("x", &Vector2D::x)
      .def_readwrite("y", &Vector2D::y)
      .def("length", &Vector2D::length, "Return vector length")
      .def("dot", &Vector2D::dot, "Dot product with another vector")
      .def("normalized", &Vector2D::normalized, "Return unit vector")
      .def("__add__", &Vector2D::operator+)
      .def("__sub__", &Vector2D::operator-)
      .def("__mul__", &Vector2D::operator*)
      .def("__eq__", &Vector2D::operator==)
      .def("__repr__", &Vector2D::repr);
}
