#include <Python.h>
#include <numpy/arrayobject.h>
#include <sndfile.h>
#include <iostream>

static PyObject *SndfileIOException = NULL;
static PyObject *SndfileTagNotSupportedException = NULL;

typedef struct {
	PyObject_HEAD
	SNDFILE * handle;
	SF_INFO sfinfo;
} pysndfile;

static void pysndfile_dealloc(pysndfile* self)
{
	self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
pysndfile_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	pysndfile *self = (pysndfile *)type->tp_alloc(type, 0);
	if (self == NULL) return NULL;

	return (PyObject *)self;
}

std::string getExtension(const char * filename)
{
	int len = strlen(filename);
	int pos = 0;
	for(int i = 0; i < len; i++)
	{
		if(filename[i] == '.')
		{
			pos = i;
			break;
		}
	}
	std::string extension(filename,pos + 1, (strlen(filename)-1));
	return extension;
}

static int
pysndfile_init(PyObject *self, PyObject *args, PyObject *kwds) {
	const char *filename;
	const char *mode;
	int channels = 0;
	int samplerate = 0;
	int format = 0;
	pysndfile * object = (pysndfile*)self;

	static char *kwlist[] = {"filename", "mode", "format", "channels", "samplerate", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ss|iii", kwlist, &filename, &mode, &format, &channels, &samplerate))
		return -1;

	memset(&object->sfinfo, 0, sizeof(SF_INFO));
	int modeFlag = SFM_READ;
	std::string extension = getExtension(filename);
	if (mode==std::string("w")) 
	{
		modeFlag = SFM_WRITE;
		object->sfinfo.channels = channels == 0 ? 1 : channels;
		object->sfinfo.samplerate = samplerate == 0 ? 44100 : samplerate;
		if ( extension == "wav" )
			object->sfinfo.format = format == 0 ? SF_FORMAT_WAV | SF_FORMAT_PCM_16 : format;
		else if ( extension == "aiff" )
			object->sfinfo.format = format == 0 ? SF_FORMAT_AIFF | SF_FORMAT_PCM_16 : format;
		else if ( extension == "au" )
			object->sfinfo.format = format == 0 ? SF_FORMAT_AU | SF_FORMAT_PCM_16 : format;
	}
	object->handle = sf_open(filename, modeFlag, &object->sfinfo);
	if (sf_error(object->handle))
	{
		PyErr_SetString(SndfileIOException, sf_strerror(object->handle));
		return -1;
	}

	return 1;
}

static PyObject *
close(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	sf_close(object->handle);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
getChannels(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	return Py_BuildValue("i", object->sfinfo.channels);
}

static PyObject *
getSampleRate(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	return Py_BuildValue("i", object->sfinfo.samplerate);
}

static PyObject *
getFormat(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	return Py_BuildValue("i", object->sfinfo.format);
}

static PyObject *
getFrames(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	return Py_BuildValue("i", object->sfinfo.frames);
}

static PyObject *
setString(PyObject * self, PyObject *args)
{
	const char * stringName;
	const char * stringValue;
	pysndfile * object = (pysndfile*)self;
	
	if (!PyArg_ParseTuple(args, "ss", &stringName, &stringValue))
        return NULL;
	
	if ( !strcmp(stringName, "artist") )
	{
		sf_set_string(object->handle, SF_STR_ARTIST, stringValue);
		return Py_None;
	}
	if ( !strcmp(stringName, "title") )
	{
		sf_set_string(object->handle, SF_STR_TITLE, stringValue);
		return Py_None;
	}
	if ( !strcmp(stringName, "date") )
	{
		sf_set_string(object->handle, SF_STR_DATE, stringValue);
		return Py_None;
	}
	if ( !strcmp(stringName, "comment") )
	{
		sf_set_string(object->handle, SF_STR_COMMENT, stringValue);
		return Py_None;
	}
	if ( !strcmp(stringName, "copyright") )
	{
		sf_set_string(object->handle, SF_STR_COPYRIGHT, stringValue);
		return Py_None;
	}
	if ( !strcmp(stringName, "software") )
	{
		sf_set_string(object->handle, SF_STR_SOFTWARE, stringValue);
		return Py_None;
	}
	PyErr_SetString(SndfileTagNotSupportedException, "setString error : Tag not supported by sndfile.");
	return NULL;
}

static PyObject *
getString(PyObject * self, PyObject *args)
{
	const char * stringName;
	pysndfile * object = (pysndfile*)self;

	if (!PyArg_ParseTuple(args, "s", &stringName))
		return NULL;

	if ( !strcmp(stringName, "artist") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_ARTIST));
	if ( !strcmp(stringName, "title") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_TITLE));
	if ( !strcmp(stringName, "date") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_DATE));
	if ( !strcmp(stringName, "comment") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_COMMENT));
	if ( !strcmp(stringName, "copyright") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_COPYRIGHT));
	if ( !strcmp(stringName, "software") )
		return Py_BuildValue("s", sf_get_string(object->handle, SF_STR_SOFTWARE));
	return Py_None;
}

static PyObject *
write(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	PyArrayObject *PyBuffer;

	if (!PyArg_ParseTuple(args, "O", &PyBuffer))
		return NULL;	

	double * buffer = new double[PyArray_DIM(PyBuffer, 0) * PyArray_DIM(PyBuffer, 1)];
	int k = 0;
	for (int j = 0 ; j < PyArray_DIM(PyBuffer, 1) ; j++)
	{
		for(int i = 0; i < PyArray_DIM(PyBuffer, 0); ++i)
		{
			buffer[k] = *(double *) PyArray_GETPTR2(PyBuffer, i, j);
			k++;
		}
	}
	int items = sf_write_double(object->handle, buffer, PyArray_DIM(PyBuffer, 0) * PyArray_DIM(PyBuffer, 1));
	delete [] buffer;
	return Py_BuildValue("i", items);
}

static PyObject *
read(PyObject * self, PyObject *args)
{
	pysndfile * object = (pysndfile*)self;
	PyArrayObject *PyBuffer;
	int channels = object->sfinfo.channels;
	int frames = object->sfinfo.frames;

	if (!PyArg_ParseTuple(args, "O", &PyBuffer))
		return NULL;

	//Getting the data from the SNDFILE
	double * buffer = new double[channels * frames];
	int items = sf_read_double(object->handle, buffer, channels * frames);
	//Moving it to the PyArray object passed
	int k = 0;
	for (int j = 0 ; j < frames ; j++)
	{
		for(int i = 0; i < channels; ++i)
		{
			*(double *) PyArray_GETPTR2(PyBuffer, i, j) = buffer[k];
			k++;
		}
	}
	delete [] buffer;
	return Py_BuildValue("i", items);
}

static PyMethodDef pysndfile_methods[] = {
	{"getFormat", getFormat, METH_VARARGS, 
		"Returns the format of the file"},
	{"getSampleRate", getSampleRate, METH_VARARGS, 
		"Returns the sample rate"},
	{"getChannels", getChannels, METH_VARARGS, 
		"Returns the number of channels"},
	{"getFrames", getFrames, METH_VARARGS, 
		"Returns the number of frames"},
	{"close", close, METH_VARARGS, 
		"Closes the file"},
	{"setString", setString, METH_VARARGS, 
		"Sets a string in the file"},
	{"getString", getString, METH_VARARGS, 
		"Returns a string from the file"},
	{"write", write, METH_VARARGS, 
		"Writes buffer data to the sound file."},
	{"read", read, METH_VARARGS, 
		"Reads the data from the sound file to a buffer."},
	{NULL, NULL}
};

static PyTypeObject pysndfileType = {
	PyObject_HEAD_INIT(NULL)
	0,                         /*ob_size*/
	"sndfile.sndfile",         /*tp_name*/
	sizeof(pysndfile),         /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)pysndfile_dealloc, /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,                         /*tp_compare*/
	0,                         /*tp_repr*/
	0,                         /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"API Sndfile",             /* tp_doc */
	0,                         /* tp_traverse */
	0,                         /* tp_clear */
	0,                         /* tp_richcompare */
	0,                         /* tp_weaklistoffset */
	0,                         /* tp_iter */
	0,                         /* tp_iternext */
	pysndfile_methods,         /* tp_methods */
	0,                         /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	pysndfile_init,            /* tp_init */
	0,                         /* tp_alloc */
	pysndfile_new,             /* tp_new */
};

PyMODINIT_FUNC
initsndfile(void)
{
	PyObject *m, *d;
	if (PyType_Ready(&pysndfileType) < 0)
		return;

	m = Py_InitModule3("sndfile", pysndfile_methods, "API Sndfile.");
	if (m == NULL)
		return;

	d = PyModule_GetDict(m);
	if (d == NULL)
		return;

	/* EXCEPCIONS */
	SndfileIOException = PyErr_NewException("sndfile.IOException", NULL, NULL);
	SndfileTagNotSupportedException = PyErr_NewException("sndfile.TagNotSupported", NULL, NULL);
	PyDict_SetItemString(d, "IOException", SndfileIOException);
	PyDict_SetItemString(d, "TagNotSupported", SndfileTagNotSupportedException);
	/* FORMATS */
	PyDict_SetItemString(d, "WAV", Py_BuildValue("i", SF_FORMAT_WAV));
	PyDict_SetItemString(d, "AIFF", Py_BuildValue("i", SF_FORMAT_AIFF));
	PyDict_SetItemString(d, "AU", Py_BuildValue("i", SF_FORMAT_AU));
	/* Formats Subtypes */
	PyDict_SetItemString(d, "PCM8", Py_BuildValue("i", SF_FORMAT_PCM_S8));
	PyDict_SetItemString(d, "PCM16", Py_BuildValue("i", SF_FORMAT_PCM_16));
	PyDict_SetItemString(d, "PCM24", Py_BuildValue("i", SF_FORMAT_PCM_24));
	PyDict_SetItemString(d, "PCM32", Py_BuildValue("i", SF_FORMAT_PCM_32));
	PyDict_SetItemString(d, "FLOAT", Py_BuildValue("i", SF_FORMAT_FLOAT));
	PyDict_SetItemString(d, "DOUBLE", Py_BuildValue("i", SF_FORMAT_DOUBLE));

	Py_INCREF(&pysndfileType);
	PyModule_AddObject(m, "sndfile", (PyObject *)&pysndfileType);
}

