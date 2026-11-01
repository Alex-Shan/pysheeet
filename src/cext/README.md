<a id="pybind11-c-extension-examples"></a>

# pybind11 C++ 扩展示例（pybind11 C++ Extension Examples）

该目录包含演示 pybind11 绑定的 C++ 源文件。

<a id="prerequisites"></a>

## 先决条件（Prerequisites）

```bash
pip install pybind11 numpy
```

<a id="building-with-cmake"></a>

## 使用 CMake 构建（Building with CMake）

```bash
mkdir build && cd build
cmake ..
make
```

编译后的modules会在 `build/` 目录下。

<a id="building-with-setuppy-alternative"></a>

## 使用 setup.py 构建（替代）（Building with setup.py (Alternative)）

```bash
pip install .
```

<a id="examples"></a>

## 示例（Examples）

<a id="examplecpp"></a>

### example.cpp 用法（example.cpp）
基本 function 绑定（加法、斐波那契）。

```python
>>> import example
>>> example.add(1, 2)
3
>>> example.fib(10)
55
```

<a id="vectorcpp"></a>

### vector.cpp 用法（vector.cpp）
Class 与 operators 和 properties 结合。

```python
>>> from vector import Vector2D
>>> v = Vector2D(3, 4)
>>> v.length()
5.0
>>> v2 = v + Vector2D(1, 1)
>>> v2
Vector2D(4.0, 5.0)
```

<a id="numpy_examplecpp"></a>

### numpy_example.cpp 用法（numpy_example.cpp）
NumPy array 操作（零拷贝）。

```python
>>> import numpy as np
>>> from numpy_example import multiply_inplace
>>> arr = np.array([1.0, 2.0, 3.0])
>>> multiply_inplace(arr, 2.0)
>>> arr
array([2., 4., 6.])
```

<a id="gil_examplecpp"></a>

### gil_example.cpp 用法（gil_example.cpp）
GIL 发布用于并行执行。

```python
>>> from gil_example import fib_nogil
>>> import threading
>>> # 由于 GIL 已发布，并行运行
>>> threads = [threading.Thread(target=fib_nogil, args=(30,)) for _ in range(4)]
```

<a id="fibc"></a>

### fib.c 用法（fib.c）
纯 C library 用于 ctypes/cffi 示例。

```bash
# 编译
gcc -shared -fPIC -o libfib.so fib.c      # Linux
clang -shared -fPIC -o libfib.dylib fib.c # macOS
```

```python
>>> import ctypes
>>> lib = ctypes.CDLL("./libfib.so")
>>> lib.fib(10)
55
```
