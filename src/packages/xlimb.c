#include <Python.h>
#include <stdio.h>
#include "helper.h"
#include "polygon.h"
/* #include "bullet.h" */



static PyObject* distance(PyObject *self, PyObject *args)
{
    float x1, y1, x2, y2;
    if (!PyArg_ParseTuple(args, "(ff)(ff)", &x1, &y1, &x2, &y2)) {
        return NULL;
    }
    return PyFloat_FromDouble(helper_distance(x1, y1, x2, y2));
}

static PyObject* resolve_line(PyObject *self, PyObject *args)
{
    double x1, y1, x2, y2;
    double result[2];
    if (!PyArg_ParseTuple(args, "(dd)(dd)", &x1, &y1, &x2, &y2)) {
        return NULL;
    }


    helper_resolve_line(x1, y1, x2, y2, result);
    if (result == 0 && result == 0){
        return Py_BuildValue("(ss)", NULL, NULL);
    }else{
        return Py_BuildValue("dd", result[0], result[0]);
    }
}


static PyObject* get_polygon_idx_collision(PyObject *self, PyObject *args)
{
    double x, y; 
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) {
        return NULL;
    }

    return Py_BuildValue("i", polygon_get_polygon_idx_collision(x, y));
}

/* static PyObject* calculate_position(PyObject *self, PyObject *args) */
/* { */
    /* double FRAME_INTERVAL;  */
    /* PyObject * obj; */

    /* if (!PyArg_ParseTuple(args, "dO", &FRAME_INTERVAL, &obj)) { */
        /* return NULL; */
    /* } */
    /* bullet_calculate_position(FRAME_INTERVAL, obj); */
    /* return Py_BuildValue("s", NULL); */
/* } */

static PyMethodDef xlimb_helper_methods[] = { 
    {"distance", distance, METH_VARARGS, "docs"},
    {"resolve_line", resolve_line, METH_VARARGS, "docs"},
    {"get_polygon_idx_collision",  get_polygon_idx_collision, METH_VARARGS, "docs"},
    /* {"calculate_position",  calculate_position, METH_VARARGS, "docs"}, */
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef xlimb_helper_definition = { 
    PyModuleDef_HEAD_INIT,
    "xlimb",
    "docs",
    -1, 
    xlimb_helper_methods
};

PyMODINIT_FUNC PyInit_xlimb_helper(void)
{
    Py_Initialize();
    return PyModule_Create(&xlimb_helper_definition);
}
