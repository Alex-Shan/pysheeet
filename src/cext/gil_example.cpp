/**
 * gil_example.cpp - GIL 发布示例
 *
 * 演示：
 *   - 为 CPU 密集型工作发布 GIL
 *   - 允许Python threads并行运行
 *   - 需要时重新获取GIL
 *
 * 用法：
 *   >>> from gil_example import slow_operation, fib_nogil
 *   >>> import threading
 *   >>> # These run in parallel because GIL is released
 *   >>> threads = [threading.Thread(target=slow_operation, args=(1,)) for _ in range(3)]
 */
#include <pybind11/pybind11.h>

#include <chrono>
#include <functional>
#include <thread>

namespace py = pybind11;

// 释放GIL的缓慢操作
void slow_operation(int seconds) {
  // 睡觉时释放GIL
  py::gil_scoped_release release;
  std::this_thread::sleep_for(std::chrono::seconds(seconds));
}

// CPU 密集斐波那契，无 GIL
unsigned long fib_nogil(unsigned long n) {
  // 发布GIL用于CPU工作
  py::gil_scoped_release release;

  std::function<unsigned long(unsigned long)> fib_impl;
  fib_impl = [&](unsigned long n) -> unsigned long {
    if (n < 2) return n;
    return fib_impl(n - 1) + fib_impl(n - 2);
  };
  return fib_impl(n);
}

// 显示 GIL 重新获取的示例
void call_python_callback(py::function callback, const std::string& msg) {
  // 发布 GIL 进行一些工作
  {
    py::gil_scoped_release release;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }
  // GIL在这里自动重新获取
  // 现在可以安全拨打 Python
  callback(msg);
}

PYBIND11_MODULE(gil_example, m) {
  m.doc() = "GIL release examples for parallel execution";

  m.def("slow_operation", &slow_operation, "Sleep for N seconds (releases GIL)", py::arg("seconds"));

  m.def("fib_nogil", &fib_nogil, "Compute Fibonacci without holding GIL", py::arg("n"));

  m.def("call_python_callback", &call_python_callback, "Call Python function after releasing GIL", py::arg("callback"), py::arg("msg"));
}
