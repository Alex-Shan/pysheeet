/* 演示 Python C API 中的 exception 处理。 */
#include <Python.h>

static PyObject* FooError;

/* 升内置exception */
static PyObject* raise_value_error(PyObject* self) {
  PyErr_SetString(PyExc_ValueError, "This is a ValueError");
  return NULL;
}

/* 加高定制exception */
static PyObject* raise_foo_error(PyObject* self) {
  PyErr_SetString(FooError, "This is a custom FooError");
  return NULL;
}

/* 使用 string 格式进行提升 */
static PyObject* raise_with_format(PyObject* self, PyObject* args) {
  int code;
  if (!PyArg_ParseTuple(args, "i", &code)) {
    return NULL;
  }
  PyErr_Format(PyExc_RuntimeError, "Error code: %d", code);
  return NULL;
}

/* 检查并传播exception */
static PyObject* divide(PyObject* self, PyObject* args) {
  double a, b;
  if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
    return NULL;
  }
  if (b == 0.0) {
    PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
    return NULL;
  }
  return PyFloat_FromDouble(a / b);
}

static PyMethodDef methods[] = {
    {"raise_value_error", (PyCFunction)raise_value_error, METH_NOARGS, NULL},
    {"raise_foo_error", (PyCFunction)raise_foo_error, METH_NOARGS, NULL},
    {"raise_with_format", (PyCFunction)raise_with_format, METH_VARARGS, NULL},
    {"divide", (PyCFunction)divide, METH_VARARGS, "Divide a by b"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "errors", "Exception handling examples", -1, methods};

PyMODINIT_FUNC PyInit_errors(void) {
  PyObject* m = PyModule_Create(&module);
  if (!m) return NULL;

  FooError = PyErr_NewException("errors.FooError", NULL, NULL);
  Py_INCREF(FooError);
  PyModule_AddObject(m, "FooError", FooError);
  return m;
}
