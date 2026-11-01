/* 在 Python C API 中演示 argument 解析。 */
#include <Python.h>

/* METH_NOARGS - 无 arguments */
static PyObject* no_args(PyObject* self) { Py_RETURN_NONE; }

/* METH_O - 单 object argument */
static PyObject* single_arg(PyObject* self, PyObject* arg) { return Py_BuildValue("O", arg); }

/* METH_VARARGS - positional arguments */
static PyObject* pos_args(PyObject* self, PyObject* args) {
  PyObject *x = NULL, *y = NULL;
  if (!PyArg_ParseTuple(args, "OO", &x, &y)) {
    return NULL;
  }
  return Py_BuildValue("OO", x, y);
}

/* METH_VARARGS | METH_KEYWORDS - keyword arguments */
static PyObject* kw_args(PyObject* self, PyObject* args, PyObject* kwargs) {
  static char* keywords[] = {"x", "y", "z", NULL};
  PyObject *x = NULL, *y = NULL, *z = Py_None;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO|O", keywords, &x, &y, &z)) {
    return NULL;
  }
  return Py_BuildValue("OOO", x, y, z);
}

/* 解析具体types */
static PyObject* typed_args(PyObject* self, PyObject* args) {
  int i;
  double d;
  const char* s;

  if (!PyArg_ParseTuple(args, "ids", &i, &d, &s)) {
    return NULL;
  }
  return Py_BuildValue("{s:i,s:d,s:s}", "int", i, "double", d, "str", s);
}

static PyMethodDef methods[] = {
    {"no_args", (PyCFunction)no_args, METH_NOARGS, "No arguments"},
    {"single_arg", (PyCFunction)single_arg, METH_O, "Single argument"},
    {"pos_args", (PyCFunction)pos_args, METH_VARARGS, "Positional arguments"},
    {"kw_args", (PyCFunction)kw_args, METH_VARARGS | METH_KEYWORDS, "Keyword arguments"},
    {"typed_args", (PyCFunction)typed_args, METH_VARARGS, "Typed arguments"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "args", "Argument parsing examples", -1, methods};

PyMODINIT_FUNC PyInit_args(void) { return PyModule_Create(&module); }
