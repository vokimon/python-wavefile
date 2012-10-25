python-wavefile
===============

'wavefile' python module to read and write audio files.
It is a pythonic wrapper to the sndfile library featuring:
* Attribute access to format, channels, length, sample rate...
* Numpy interface using in place arrays (optimal for block processing)
* Works as context manager
* Different objects for reading and writing (no modes, consistent interface)
* Shortened constants accessing for formats and the like
* Matlab like whole file interface (not recommended but convenient)

You can find the latest version at:
https://github.com/vokimon/python-wavefile

TODO:
* Handling properly different physical numpy layouts: use a view, assert or reshape
* sndfile command interface
* Seeking
* Use file name extension to deduce main format, if not specified
* Use main format to deduce subformat if not specified
* Providing strings for formats

Installation
------------

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
and slicing it as you get the data.


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
	- wrappers around. The standard module to do wave file
	- loading is crap.

	- Based on sndfile but it just writes .wav files.
	- It lacks support for floating point samples, patch provided
	  but ignored see http://bugs.python.org/issue1144504
	- unreadable getX() methods instead of properties.
	- no numpy integration
	- no whole file shortcuts

- scikits.audiolab
	- git clone https://github.com/cournape/audiolab
	- Cython based + python layer
	- Dual interface: matlab like and OO
	- Property accessors to samplerate...
	- Numpy integration
	- Inplace processing?
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
	- ctypes based wrapper
	- No compilation required
	- numpy supported
	- Windows only setup (fixable)
	- Long access to constants
	- Not inplace read (creates an array every time)




