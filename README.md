python-wavefile
===============

Pythonic libsndfile wrapper to read and write audio files.

Features
--------

* Attribute access for format, channels, length, sample rate...
* Numpy interface using in-place arrays (optimal for block processing)
* Real multichannel (not just mono/stereo)
* Separate classes for reading and writing, so that available operations are consistent with the mode.
* Writer and reader objects work as context managers for [RAII idiom](http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization)
* Shortened constant names for formats (Using scopes instead of prefixes)
* Matlab like whole-file interface (not recommended in production code but quite convenient for quick scripting)
* No module compilation required (wraps the dll using ctypes)
* Works both for Python3 >= 3.3 and Python2 >= 2.6

You can find the latest version at:
https://github.com/vokimon/python-wavefile

Wish list
---------

* Use file name extension to deduce main format, if not specified
* Use main format to deduce subformat, if not specified
* Separate Formats scope into Formats, Subformats and Endianess
* Expose descriptive strings for formats
* Exposing sndfile command API
* Handling properly unicode in text strings (now considers them UTF-8, which is not always true)
* Handling properly different physical numpy layouts: use a view, assert or reshape

Installation
------------

### Using PyPi

```bash
pypi-install wavefile
```

### From sources

A setup.py script is provided so the common procedure for
installing python packages in you platfrom will work.
For example in Debian/Ubuntu systems:
```bash
sudo python setup install
```
And for per-user installation:
```bash
python setup install --home=~/local
```
provided that you have PTYHON_PATH set properly.

Copying the wavefile directory to your project is also ok.


Examples
--------

### Writting example

```python
from wavefile import WaveWriter, Format
import numpy as np

with WaveWriter('synth.ogg', channels=2, format=Format.OGG|Format.VORBIS) as w :
	w.metadata.title = "Some Noise"
	w.metadata.artist = "The Artists"
	data = np.zeros((2,512), np.float32)
	for x in xrange(100) :
		data[0,:] = (x*np.arange(512, dtype=np.float32)%512/512)
		data[1,512-x:] =  1
		data[1,:512-x] = -1
		w.write(data)
```

### Playback example (using pyaudio)

```python
import pyaudio, sys
from wavefile import WaveReader

p = pyaudio.PyAudio()
with WaveReader(sys.argv[1]) as r :

	# Print info
	print "Title:", r.metadata.title
	print "Artist:", r.metadata.artist
	print "Channels:", r.channels
	print "Format: 0x%x"%r.format
	print "Sample Rate:", r.samplerate

	# open pyaudio stream
	stream = p.open(
			format = pyaudio.paFloat32,
			channels = r.channels,
			rate = r.samplerate,
			frames_per_buffer = 512,
			output = True)

	# iterator interface (reuses one array)
	# beware of the frame size, not always 512, but 512 at least
	for frame in r.read_iter(size=512) :
		stream.write(frame, frame.shape[1])
		sys.stdout.write("."); sys.stdout.flush()

	stream.close()
```

### Processing example

```python
import sys
from wavefile import WaveReader, WaveWriter

with WaveReader(sys.argv[1]) as r :
	with WaveWriter(
			'output.wav',
			channels=r.channels,
			samplerate=r.samplerate,
			) as w :
		w.metadata.title = r.metadata.title + " II"
		w.metadata.artist = r.metadata.artist

		for data in r.read_iter(size=512) :
			sys.stdout.write("."); sys.stdout.flush()
			w.write(.8*data)
```

While read_iter is simpler and recommended,
you can still use the read function,
which is closer to the C one.

```python
import sys, numpy as np
from wavefile import WaveReader, WaveWriter

with WaveReader(sys.argv[1]) as r :
	with WaveWriter(
			'output.wav',
			channels=r.channels,
			samplerate=r.samplerate,
			) as w :
		w.metadata.title = r.metadata.title + " II"
		w.metadata.artist = r.metadata.artist

		data = np.zeros((r.channels,512), np.float32, order='F')
		nframes = r.read(data)
		while nframes :
			sys.stdout.write("."); sys.stdout.flush()
			w.write(.8*data[:,:nframes])
			nframes = r.read(data)
```

Notice that with ```read``` you have to reallocate the data yourself,
the loop structure is somewhat more complex,
and you have to slice to the actual ```nframes``` because
the last block usually does not have the size you asked for.
```read_iter``` simplifies the code by transparently
allocating the data block for you, reusing it for each block
and slicing it when the last incomplete block arrives.


Existing alternatives (what i like and dislike)
-----------------------------------------------

This is 'yet another' wrapper for sndfile.
A lot of them appeared just because the standard
'wave' module is quite limited on what and how it does.
But none of the wrappers I found around fully suit my
needs and that's because I wrote this small and incomplete one,
to fit my needs.
So this is a summary of what I found, just in case it is useful to anyone.

- Standard 'wave' module:
	- http://docs.python.org/library/wave.html
	- I think this is the main reason why there are many
	  wrappers around. The standard module to do wave file
	  loading is crap.
	- Based on sndfile but it just writes .wav files.
	- It lacks support for floating point samples, patch provided
	  but ignored see http://bugs.python.org/issue1144504
	- unreadable getX() methods instead of properties.
	- no numpy integration
	- generators, context managers... what?
	- no whole-file shortcuts provided

- scikits.audiolab
	- git clone https://github.com/cournape/audiolab
	- Cython based + python layer
	- Dual interface: matlab like and OO
	- Property accessors to samplerate...
	- Numpy integration
	- Inplace processing
	- Not in Ubuntu
	- Within a big library

- pysndfile
	- http://savannah.nongnu.org/projects/pysndfile/
	- Swig based wrapper.
	- Direct lib library + python object wrappers
	- Unusable because it is not finished (empty read/write methods in wrapper!)

- libsndfile-python
	- http://code.google.com/p/libsndfile-python/
	- svn checkout http://libsndfile-python.googlecode.com/svn/trunk/ libsndfile-python-read-only
	- Implemented in CPython
	- numpy support
	- cpython purely wraps the library
	- wrappers build the interface
	- double layered lib and pythonic interface (not that pythonic but supports numpy)
	- Implements 'command' sndfile interface

- libsndfilectypes
	- http://code.google.com/p/pyzic/wiki/LibSndFilectypes
	- ctypes based wrapper: no compilation required
	- numpy supported
	- Windows only setup (fixable)
	- Long access to constants
	- Not inplace read (creates an array every time)


python-wavefile reuses most of the libsndfilectypes ctypes wrapper,
as not requiring module compilation was seen as a good point.
A pythonic layer was added on the top of it.



Version history
---------------

### 1.2

- Seek implemented
- Removed some error handling that aborted program execution
- Removed alien reference code in 'other' folder

### 1.1

- Python 3 support
- Support for unicode filenames

### 1.0

- First version



