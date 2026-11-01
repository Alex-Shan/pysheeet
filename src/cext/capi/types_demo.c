/* 演示 C API 中的 Python types 操作。 */
#include <Python.h>

/* List 操作 */
static PyObject* list_demo(PyObject* self) {
  PyObject* list = PyList_New(0);
  PyList_Append(list, PyLong_FromLong(1));
  PyList_Append(list, PyLong_FromLong(2));
  PyList_Append(list, PyLong_FromLong(3));
  return list;
}

static PyObject* list_sum(PyObject* self, PyObject* args) {
  PyObject* list;
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &list)) {
    return NULL;
  }
  long sum = 0;
  Py_ssize_t len = PyList_Size(list);
  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject* item = PyList_GetItem(list, i); /* 借用的参考文献 */
    sum += PyLong_AsLong(item);
  }
  return PyLong_FromLong(sum);
}

/* 使用 iterator 协议迭代 list */
static PyObject* iter_list(PyObject* self, PyObject* args) {
  PyObject *list, *iter, *item;
  if (!PyArg_ParseTuple(args, "O", &list)) {
    return NULL;
  }
  iter = PyObject_GetIter(list);
  if (!iter) return NULL;

  PyObject* result = PyList_New(0);
  while ((item = PyIter_Next(iter)) != NULL) {
    PyObject* doubled = PyLong_FromLong(PyLong_AsLong(item) * 2);
    PyList_Append(result, doubled);
    Py_DECREF(doubled);
    Py_DECREF(item);
  }
  Py_DECREF(iter);
  return result;
}

/* Dict 操作 */
static PyObject* dict_demo(PyObject* self) {
  PyObject* dict = PyDict_New();
  PyDict_SetItemString(dict, "name", PyUnicode_FromString("Python"));
  PyDict_SetItemString(dict, "version", PyLong_FromLong(3));
  return dict;
}

static PyObject* dict_get(PyObject* self, PyObject* args) {
  PyObject* dict;
  const char* key;
  if (!PyArg_ParseTuple(args, "O!s", &PyDict_Type, &dict, &key)) {
    return NULL;
  }
  PyObject* value = PyDict_GetItemString(dict, key); /* 借用的参考文献 */
  if (!value) {
    Py_RETURN_NONE;
  }
  Py_INCREF(value);
  return value;
}

/* 迭代dict */
static PyObject* iter_dict(PyObject* self, PyObject* args) {
  PyObject* dict;
  if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict)) {
    return NULL;
  }
  PyObject* result = PyList_New(0);
  PyObject *key, *value;
  Py_ssize_t pos = 0;
  while (PyDict_Next(dict, &pos, &key, &value)) {
    PyObject* pair = PyTuple_Pack(2, key, value);
    PyList_Append(result, pair);
    Py_DECREF(pair);
  }
  return result;
}

/* Tuple 操作 */
static PyObject* tuple_demo(PyObject* self) { return Py_BuildValue("(isd)", 1, "hello", 3.14); }

static PyObject* tuple_unpack(PyObject* self, PyObject* args) {
  int a;
  const char* b;
  double c;
  if (!PyArg_ParseTuple(args, "(isd)", &a, &b, &c)) {
    return NULL;
  }
  return Py_BuildValue("{s:i,s:s,s:d}", "int", a, "str", b, "float", c);
}

/* Set 操作 */
static PyObject* set_demo(PyObject* self) {
  PyObject* set = PySet_New(NULL);
  PySet_Add(set, PyLong_FromLong(1));
  PySet_Add(set, PyLong_FromLong(2));
  PySet_Add(set, PyLong_FromLong(2)); /* 重复的被忽略 */
  PySet_Add(set, PyLong_FromLong(3));
  return set;
}

static PyObject* set_contains(PyObject* self, PyObject* args) {
  PyObject *set, *item;
  if (!PyArg_ParseTuple(args, "OO", &set, &item)) {
    return NULL;
  }
  int result = PySet_Contains(set, item);
  if (result == -1) return NULL;
  return PyBool_FromLong(result);
}

/* String 操作 */
static PyObject* str_demo(PyObject* self) {
  PyObject* s1 = PyUnicode_FromString("Hello");
  PyObject* s2 = PyUnicode_FromString(" World");
  PyObject* result = PyUnicode_Concat(s1, s2);
  Py_DECREF(s1);
  Py_DECREF(s2);
  return result;
}

static PyObject* str_format(PyObject* self, PyObject* args) {
  const char* name;
  int age;
  if (!PyArg_ParseTuple(args, "si", &name, &age)) {
    return NULL;
  }
  return PyUnicode_FromFormat("%s is %d years old", name, age);
}

/* Bytes 操作 */
static PyObject* bytes_demo(PyObject* self) { return PyBytes_FromString("hello bytes"); }

static PyObject* bytes_len(PyObject* self, PyObject* args) {
  PyObject* bytes;
  if (!PyArg_ParseTuple(args, "S", &bytes)) {
    return NULL;
  }
  return PyLong_FromSsize_t(PyBytes_Size(bytes));
}

static PyMethodDef methods[] = {
    {"list_demo", (PyCFunction)list_demo, METH_NOARGS, "Create a list [1,2,3]"},
    {"list_sum", (PyCFunction)list_sum, METH_VARARGS, "Sum list elements"},
    {"iter_list", (PyCFunction)iter_list, METH_VARARGS, "Double each element"},
    {"dict_demo", (PyCFunction)dict_demo, METH_NOARGS, "Create a dict"},
    {"dict_get", (PyCFunction)dict_get, METH_VARARGS, "Get dict value by key"},
    {"iter_dict", (PyCFunction)iter_dict, METH_VARARGS, "Get dict items as list"},
    {"tuple_demo", (PyCFunction)tuple_demo, METH_NOARGS, "Create a tuple"},
    {"tuple_unpack", (PyCFunction)tuple_unpack, METH_VARARGS, "Unpack tuple"},
    {"set_demo", (PyCFunction)set_demo, METH_NOARGS, "Create a set"},
    {"set_contains", (PyCFunction)set_contains, METH_VARARGS, "Check set membership"},
    {"str_demo", (PyCFunction)str_demo, METH_NOARGS, "Concat strings"},
    {"str_format", (PyCFunction)str_format, METH_VARARGS, "Format string"},
    {"bytes_demo", (PyCFunction)bytes_demo, METH_NOARGS, "Create bytes"},
    {"bytes_len", (PyCFunction)bytes_len, METH_VARARGS, "Get bytes length"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "types_demo", "Python types in C API", -1, methods};

PyMODINIT_FUNC PyInit_types_demo(void) { return PyModule_Create(&module); }
