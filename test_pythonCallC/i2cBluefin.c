#include <Python.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <stdio.h>
/*
 * Function to be called from Python
 */
static PyObject* mls_i2c_open_device(PyObject* self, PyObject* args)
{
	int result;
	char filename[40];
	unsigned char addr;
	unsigned char port;
	int file;
	result = PyArg_ParseTuple(args, "bb", &port, &addr);

	sprintf(filename,"/dev/i2c-%d", port);
	if(result == 0)
	{
		return Py_BuildValue("i", -1);	//error
	}

	printf("\nfilename = %s, address=0x%x\n", filename, addr);

	if((file = open(filename, O_RDWR)) < 0)
	{
		printf("Failed to open the bus.");
		return Py_BuildValue("i", -2);	//error
	}

	if(ioctl(file, I2C_SLAVE,  addr) < 0)
	{
		printf("Failed to accquire bus access and/or talk to slave.\n");		
		return Py_BuildValue("i", -3);	//error
	}
	printf("i2cBluefin: file = %d\n", file);
	return Py_BuildValue("i", file);
}
#if 0
static PyObject* mls_i2c_write_data(PyObject* self, PyObject* args)
{
	int result, i;
	int file;
	unsigned char *data_out;
	unsigned char nbytes;
	
	result = PyArg_ParseTuple(args, "iii" , &file, &data_out, &nbytes);
	printf("ls_i2c_write_data: file = %d\n", file);
	//printf("mls Register: ");
	//for(i = 0; i < nbytes; i++)
	//{
		printf("aaa  %d  %d\n", data_out[0], nbytes);
	//}

	if(write(file, data_out, nbytes) != nbytes)
	{
		printf("Error writing data");
		return Py_BuildValue("i", 1);
	}
	return Py_BuildValue("i", 0);
}
static PyObject* mls_i2c_write_data(PyObject* self, PyObject* args)
{
	int result, i;
	int file;
	unsigned char *data_out;
	unsigned char nbytes;
	PyObject *py_tuple;
	int length;
	
	result = PyArg_ParseTuple(args, "iO" , &file, &py_tuple);
	printf("mls_i2c_write_data: file = %d\n", file);
	nbytes = PyTuple_Size(py_tuple);
	length = nbytes;
	data_out = malloc(nbytes);
	printf("Parsing argument with length = %d\n", nbytes);
	while(length--)
	{
		data_out[length] = (int) PyInt_AsLong(PyTuple_GetItem(py_tuple, length));
	}
	printf("mls Register: ");
	for(i = 0; i < nbytes; i++)
	{
		printf("aaa  %d", data_out[i]);
	}

	if(write(file, data_out, nbytes) != nbytes)
	{
		printf("Error writing data");
		return Py_BuildValue("i", 1);
	}
	return Py_BuildValue("i", 0);
}


static PyObject* mls_i2c_write_data(PyObject* self, PyObject* args)
{
	int result, i;
	unsigned char data_out[200];
	unsigned char nbytes;
	
	result = PyArg_ParseTuple(args, "sb", &data_out, &nbytes);
	printf("mls_i2c_write_data: file = %d\n", file);
	printf("Parsing argument with length = %d\n", nbytes);
	for(i = 0; i < nbytes; i++)
	{
		printf("  %d", data_out[i]);
	}
	//printf("\n");

	if(write(file, data_out, nbytes) != nbytes)
	{
		printf("Error writing data");
		return Py_BuildValue("i", 1);
	}
	return Py_BuildValue("i", 0);
}
#else
static PyObject* mls_i2c_write_data(PyObject* self, PyObject* args)
{
	int result, i;
	unsigned char *data_out;
	unsigned char nbytes;
	PyObject *py_tuple, *item;
	int length;
	int file;
	result = PyArg_ParseTuple(args, "ibO" , &file, &nbytes, &py_tuple);
	//printf("mls_i2c_write_data: file = %d\n", file);
	//nbytes = PyList_Size(py_tuple);
	//printf("Parsing argument with length = %d\n", nbytes);
	length = nbytes;
	data_out = malloc(nbytes);
	for(i = 0; i < nbytes; i++)
	{
		item = PyList_GetItem(py_tuple, i);
		data_out[i] = (unsigned char)PyInt_AsLong(item);
		Py_INCREF(item);
	}
	//printf("mls Register: ");
	//for(i = 0; i < nbytes; i++)
	//{
	//	printf("%d  ", data_out[i]);
	//}
	//printf("\n");

	if(write(file, data_out, nbytes) != nbytes)
	{
		printf("Error writing data");
		return Py_BuildValue("i", 1);
	}
	return Py_BuildValue("i", 0);
}

#endif
static PyObject* mls_i2c_read_data(PyObject* self, PyObject* args)
{
	int result;
	int file;
	unsigned char* data;
	int nbytes;
	unsigned char i, length = 0;
	PyObject * data_out;
	PyObject* buffer = PyList_New(0);

	result = PyArg_ParseTuple(args, "ii", &file, &nbytes);
	if(result == 0)
	{
		printf("Error when parse argument");
		return Py_BuildValue("i", 1);	//error
	}
	
	data = malloc(sizeof(char) * nbytes);	//
	length = read(file, data, nbytes);
	if(length != nbytes)
	{
		printf("Error reading %d bytes. Expect: %d\n", length, nbytes);
	}
	for(i = 0; i < nbytes; i++)
	{
		//printf("%x  ", data[i]);
		PyList_Append(buffer, PyInt_FromSize_t((size_t) data[i]));
	}
	//printf("\n");
	
	data_out = Py_BuildValue("Si", buffer, nbytes);
	
	free(data);
	return data_out;
}


static PyObject* mls_i2c_close_device(PyObject* self, PyObject* args)
{
	int result;
	int file;

	result = PyArg_ParseTuple(args, "i", &file);

	close(file);
	return Py_BuildValue("i", 0);
}


static PyObject* mls_i2c_sleep_ms(PyObject* self, PyObject* args)
{
	int result;
	int ms;

	result = PyArg_ParseTuple(args, "i", &ms);

	usleep(ms * 1000);
	return Py_BuildValue("i", 0);
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef myModule_methods[] = {
	{"mls_i2c_open_device", 	mls_i2c_open_device, 		METH_VARARGS},
	{"mls_i2c_write_data",		mls_i2c_write_data,		METH_VARARGS},
	{"mls_i2c_read_data",		mls_i2c_read_data,		METH_VARARGS},
	{"mls_i2c_close_device", 	mls_i2c_close_device, 		METH_VARARGS},
	{"mls_i2c_sleep_ms",		mls_i2c_sleep_ms,		METH_VARARGS},
	{NULL, NULL}
};

/*
 * Python calls this to let us initialize our module
 */
void initi2cBluefin()
{
  (void) Py_InitModule("i2cBluefin", myModule_methods);
}
