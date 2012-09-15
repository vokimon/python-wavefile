#!/usr/bin/python
import numpy as np
import ctypes


from libsndfile import _lib

from libsndfile import OPEN_MODES, SEEK_MODES, SF_INFO

class Format :
	WAV    = 0x010000	# Microsoft WAV format (little endian default).
	AIFF   = 0x020000	# Apple/SGI AIFF format (big endian).
	AU     = 0x030000	# Sun/NeXT AU format (big endian).
	RAW    = 0x040000	# RAW PCM data.
	PAF    = 0x050000	# Ensoniq PARIS file format.
	SVX    = 0x060000	# Amiga IFF / SVX8 / SV16 format.
	NIST   = 0x070000	# Sphere NIST format.
	VOC    = 0x080000	# VOC files.
	IRCAM  = 0x0A0000	# Berkeley/IRCAM/CARL
	W64    = 0x0B0000	# Sonic Foundry's 64 bit RIFF/WAV
	MAT4   = 0x0C0000	# Matlab (tm) V4.2 / GNU Octave 2.0
	MAT5   = 0x0D0000	# Matlab (tm) V5.0 / GNU Octave 2.1
	PVF    = 0x0E0000	# Portable Voice Format
	XI     = 0x0F0000	# Fasttracker 2 Extended Instrument
	HTK    = 0x100000	# HMM Tool Kit format
	SDS    = 0x110000	# Midi Sample Dump Standard
	AVR    = 0x120000	# Audio Visual Research
	WAVEX  = 0x130000	# MS WAVE with WAVEFORMATEX
	SD2    = 0x160000	# Sound Designer 2
	FLAC   = 0x170000	# FLAC lossless file format
	CAF    = 0x180000	# Core Audio File format
	WVE    = 0x190000	# Psion WVE format
	OGG    = 0x200000	# Xiph OGG container
	MPC2K  = 0x210000	# Akai MPC 2000 sampler
	RF64   = 0x220000	# RF64 WAV file

	# Subtypes from here on.

	PCM_S8     = 0x0001	# Signed 8 bit data
	PCM_16     = 0x0002	# Signed 16 bit data
	PCM_24     = 0x0003	# Signed 24 bit data
	PCM_32     = 0x0004	# Signed 32 bit data

	PCM_U8     = 0x0005	# Unsigned 8 bit data (WAV and RAW only)

	FLOAT      = 0x0006	# 32 bit float data
	DOUBLE     = 0x0007	# 64 bit float data

	ULAW       = 0x0010	# U-Law encoded.
	ALAW       = 0x0011	# A-Law encoded.
	IMA_ADPCM  = 0x0012	# IMA ADPCM.
	MS_ADPCM   = 0x0013	# Microsoft ADPCM.

	GSM610     = 0x0020	# GSM 6.10 encoding.
	VOX_ADPCM  = 0x0021	# OKI / Dialogix ADPCM

	G721_32    = 0x0030	# 32kbs G721 ADPCM encoding.
	G723_24    = 0x0031	# 24kbs G723 ADPCM encoding.
	G723_40    = 0x0032	# 40kbs G723 ADPCM encoding.

	DWVW_12    = 0x0040	# 12 bit Delta Width Variable Word encoding.
	DWVW_16    = 0x0041	# 16 bit Delta Width Variable Word encoding.
	DWVW_24    = 0x0042	# 24 bit Delta Width Variable Word encoding.
	DWVW_N     = 0x0043	# N bit Delta Width Variable Word encoding.

	DPCM_8     = 0x0050	# 8 bit differential PCM (XI only)
	DPCM_16    = 0x0051	# 16 bit differential PCM (XI only)

	VORBIS     = 0x0060	# Xiph Vorbis encoding.

	# Endian-ness options.

	ENDIAN_FILE    = 0x00000000    # Default file endian-ness.
	ENDIAN_LITTLE  = 0x10000000    # Force little endian-ness.
	ENDIAN_BIG     = 0x20000000    # Force big endian-ness.
	ENDIAN_CPU     = 0x30000000    # Force CPU endian-ness.

	SUBMASK  = 0x0000FFFF
	TYPEMASK = 0x0FFF0000
	ENDMASK  = 0x30000000



class WaveMetadata(object) :
	strings = [
		'title',
		'copyright',
		'software',
		'artist',
		'comment',
		'date',
		'album',
		'license',
		'tracknumber',
		'genre',
	]
	__slots__ = strings + [
		'_sndfile',
		]

	def __init__(self, sndfile) :
		self._sndfile = sndfile

	def __dir__(self) :
		return self.strings

	def __getattr__(self, name) :
		if name not in self.strings :
			raise AttributeError(name)
		stringid = self.strings.index(name)+1
		return _lib.sf_get_string(self._sndfile, stringid)

	def __setattr__(self, name, value) :
		if name not in self.strings :
			return object.__setattr__(self, name, value)

		stringid = self.strings.index(name)+1
		error = _lib.sf_set_string(self._sndfile, stringid, value)
		if error : print ValueError(
			self.strings[stringid],
			error, _lib.sf_error_number(error))

class WaveWriter(object) :
	def __init__(self,
				filename,
				samplerate = 44100,
				channels = 1,
				format = Format.WAV | Format.FLOAT,
				) :

		self._info = SF_INFO(
				samplerate = samplerate,
				channels = channels,
				format = format
			)
		self._sndfile = _lib.sf_open(filename, OPEN_MODES.SFM_WRITE, self._info)
		self._metadata = WaveMetadata(self._sndfile)

	def __enter__(self) :
		return self
	def __exit__(self, type, value, traceback) :
		_lib.sf_close( self._sndfile)
		if value: raise

	@property
	def metadata(self) :
		return self._metadata

	def write(self, data) :
		nframes, channels = data.shape
		assert channels == self._info.channels
		if data.dtype==np.float64 :
			return _lib.sf_writef_double(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), nframes)
		elif data.dtype==np.float32 :
			return _lib.sf_writef_float(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), nframes)
		elif data.dtype==np.int16 :
			return _lib.sf_writef_short(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), nframes)
		elif data.dtype==np.int32 :
			return _lib.sf_writef_int(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), nframes)
		else:
			raise TypeError("Please choose a correct dtype")


class WaveReader(object) :
	def __init__(self,
				filename,
				samplerate = 0,
				channels = 0,
				format = 0,
				) :

		self._info = SF_INFO(
				samplerate = samplerate,
				channels = channels,
				format = format
			)
		self._sndfile = _lib.sf_open(filename, OPEN_MODES.SFM_READ, self._info)
		self._metadata = WaveMetadata(self._sndfile)

	def __enter__(self) :
		return self
	def __exit__(self, type, value, traceback) :
		_lib.sf_close( self._sndfile)
		if value: raise

	@property
	def metadata(self) :
		return self._metadata

	@property
	def channels(self) : return self._info.channels
	@property
	def format(self) : return self._info.format
	@property
	def samplerate(self) : return self._info.samplerate
	@property
	def frames(self) : return self._info.frames

	def read(self, data) :
		assert data.shape[1] == self.channels
		if data.dtype==np.float64 :
			return _lib.sf_readf_double(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), data.shape[0])
		elif data.dtype==np.float32 :
			return _lib.sf_readf_float(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), data.shape[0])
		elif data.dtype==np.int16 :
			return _lib.sf_readf_short(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), data.shape[0])
		elif data.dtype==np.int32 :
			return _lib.sf_readf_int(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), data.shape[0])
		else:
			raise TypeError("Please choose a correct dtype")


if __name__ == '__main__' :

	with WaveWriter('lala.ogg', channels=2, format=Format.OGG|Format.VORBIS) as w :
		# TODO: Metadata is not working!
		w.metadata.title = "La casa perdida"
		w.metadata.artist = "Me"
		data = np.zeros((512,2), np.float32)
		for x in xrange(100) :
			data[:,0] = (x*np.arange(512, dtype=np.float32)%512/512)
			data[512-x:,1] =  1
			data[:512-x,1] = -1
			w.write(data)

	import sys
	import pyaudio
	p = pyaudio.PyAudio()
	with WaveReader(sys.argv[1], channels=2) as r :
		# open stream
		stream = p.open(
				format = pyaudio.paFloat32,
				channels = r.channels,
				rate = r.samplerate,
				frames_per_buffer = 512,
				output = True)
		with WaveWriter('Elvis-float.wav', channels=r.channels, samplerate=r.samplerate) as w :
			data = np.zeros((512,r.channels), np.float32)
			nframes = r.read(data)
			print "Title:", r.metadata.title
			print "Artist:", r.metadata.artist
			print "Channels:", r.channels
			print "Format: 0x%x"%r.format
			print "Sample Rate:", r.samplerate
			while nframes :
				sys.stdout.write(".")
				sys.stdout.flush()
				stream.write(data[:nframes,:], nframes)
				w.write(data[:nframes]*.8)
				nframes = r.read(data)
	stream.close()





