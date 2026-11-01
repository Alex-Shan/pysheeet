/* 简单的 C 扩展 module 演示了 Python C API 基础知识。 */
#include <Python.h>

PyDoc_STRVAR(doc_mod, "Simple example C extension module.\n");
PyDoc_STRVAR(doc_hello, "hello() -> str\n\nReturn a greeting string.");
PyDoc_STRVAR(doc_add, "add(a, b) -> int\n\nAdd two integers.");
PyDoc_STRVAR(doc_fib, "fib(n) -> int\n\nCompute Fibonacci number.");

static PyObject* hello(PyObject* self) { return PyUnicode_FromString("Hello from C!"); }

static PyObject* add(PyObject* self, PyObject* args) {
  long a, b;
  if (!PyArg_ParseTuple(args, "ll", &a, &b)) {
    return NULL;
  }
  return PyLong_FromLong(a + b);
}

static unsigned long fib_impl(unsigned long n) {
  if (n < 2) return n;
  return fib_impl(n - 1) + fib_impl(n - 2);
}

static PyObject* fib(PyObject* self, PyObject* args) {
  unsigned long n;
  if (!PyArg_ParseTuple(args, "k", &n)) {
    return NULL;
  }
  return PyLong_FromUnsignedLong(fib_impl(n));
}

static PyMethodDef methods[] = {
    {"hello", (PyCFunction)hello, METH_NOARGS, doc_hello},
    {"add", (PyCFunction)add, METH_VARARGS, doc_add},
    {"fib", (PyCFunction)fib, METH_VARARGS, doc_fib},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "simple", doc_mod, -1, methods};

PyMODINIT_FUNC PyInit_simple(void) { return PyModule_Create(&module); }
