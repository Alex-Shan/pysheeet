.. meta::
    :description lang=zh_CN: Python C/C++ 扩展教程，涵盖用于高性能本机代码的 pybind11、ctypes、cffi、Cython 和 Python C API
    :keywords: Python, Python3, pybind11, ctypes, cffi, Cython, C extension, C API, native code, performance, NumPy, shared library

扩展（Extension）
==========================

Python 的灵活性是以性能为代价的。当您需要数值计算、系统接口或包装现有 C/C++ libraries 的速度时，本机扩展可以弥补这一差距。本节涵盖多种方法：

- **ctypes** - Standard library FFI 用于调用 C functions 无需编译
- **Python C API** - 具有最大控制的传统方法（遗留）
- **pybind11** （推荐用于 C++） - 具有自动 type 转换的简洁 C++11 语法，由 PyTorch、TensorFlow 和 SciPy 使用
- **cffi** - 具有 PyPy 兼容性的 ctypes 的更清洁替代品
- **Cython** - 类似 Python 的语法，可编译为 C 以进行逐步优化

对于大多数包装 C++ 代码的新项目，建议选择 pybind11。要在没有构建步骤的情况下调用现有 C libraries，请使用 ctypes 或 cffi。

.. toctree::
   :maxdepth: 1

   python-ctypes
   python-capi
   python-cext-modern
   cpp-from-python
