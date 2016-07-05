#include <Python.h>
#include <fcntl.h>
#include <stdio.h>

static PyObject* mlsPrintSomething(PyObject* self, PyObject* args)
{
	printf("Hello world :v \r\n");
	return Py_BuildValue("i", 0);
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef printSomething_methods[] = {
	{"mlsPrintSomething", 	mlsPrintSomething, 		METH_VARARGS},
	{NULL, NULL}
};

/*
 * Python calls this to let us initialize our module
 */
void initprintSomething()
{
  (void) Py_InitModule("printSomething", printSomething_methods);
}