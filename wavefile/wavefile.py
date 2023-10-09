#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Copyright 2012 David García Garzón

This file is part of python-wavefile

python-wavefile is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python-wavefile is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import ctypes
import sys
import warnings
from enum import Enum, IntEnum, IntFlag


from .libsndfile import (
    _lib,
    OPEN_MODES,
    SEEK_MODES,
    FILE_STRINGS,
    FILE_FORMATS,
    COMMANDS,
    SF_INFO,
    SF_FORMAT_INFO,
)

# Vorbis and Flac use utf8.
# WAV/AIFF use ascii, but if chars beyond 127 are found,
# we chose to interpret them as utf8. That migth be a wrong choice.
# Same for writing, if users sets a non ASCII char in tag,
# it will be encoded as utf8 which is a non-standard convention of us.
_tagencoding = 'utf8'

# ascii would be enough for libsndfile error messages but utf8 is wider
_errorencoding = 'utf8'

def _fsencode(filename):
    """Returns the filename encoded as the filesystem requires.
    If the filename is bytes (or old plain strings in Py2),
    the filename is considered already decoded and it is returned
    as is.
    """
    if type(filename) == type(''):
        return filename.encode(sys.getfilesystemencoding())
    return filename # bytes (py3) or str (py2), means already encoded

def _sferrormessage(code):
    """Returns the sndfile error message for the code in proper unicode"""
    return _lib.sf_error_number(code).decode(_errorencoding)

class Format(IntFlag):
    """Represents an audio file format.
    A full format specification can be constructed by bitwise 'or' of three components:
    a major format, meaning the container file format,
    a subtype, usually the internal audio encoding,
    and an endianess.
    Components can be obtained by bitwise 'and' operator with TYPEMASK, SUBMASK and ENDMASK.
    """

    @property
    def description(self):
        """A textual description for the format"""

        details = self.info()
        return ' '.join(
            details.get(attr, None)
            for attr in ['name', 'subtype']
            if details.get(attr, None)
        )

    @property
    def extension(self):
        """The common extension for the major format or None"""

        details = self.info()
        return details.get('extension',None)

    def isSupported(self):
        """True if the combination of major, subtype and mask is supported by the library."""

        return _lib.sf_format_check(SF_INFO(
            frames=1000, # whatever
            samplerate=44100, # whatever
            channels=2, # whatever
            format=self.value,
        ))

    def info(self):
        return formatDescription(self.value)

    @classmethod
    def common(cls):
        return commonFormats()

    @classmethod
    def all(cls):
        return allFormats()

    @classmethod
    def major(cls):
        return majorFormats()

    @classmethod
    def subtypes(cls):
        return subtypeFormats()


    WAV    = 0x010000    # Microsoft WAV format (little endian default).
    AIFF   = 0x020000    # Apple/SGI AIFF format (big endian).
    AU     = 0x030000    # Sun/NeXT AU format (big endian).
    RAW    = 0x040000    # RAW PCM data.
    PAF    = 0x050000    # Ensoniq PARIS file format.
    SVX    = 0x060000    # Amiga IFF / SVX8 / SV16 format.
    NIST   = 0x070000    # Sphere NIST format.
    VOC    = 0x080000    # VOC files.
    IRCAM  = 0x0A0000    # Berkeley/IRCAM/CARL
    W64    = 0x0B0000    # Sonic Foundry's 64 bit RIFF/WAV
    MAT4   = 0x0C0000    # Matlab (tm) V4.2 / GNU Octave 2.0
    MAT5   = 0x0D0000    # Matlab (tm) V5.0 / GNU Octave 2.1
    PVF    = 0x0E0000    # Portable Voice Format
    XI     = 0x0F0000    # Fasttracker 2 Extended Instrument
    HTK    = 0x100000    # HMM Tool Kit format
    SDS    = 0x110000    # Midi Sample Dump Standard
    AVR    = 0x120000    # Audio Visual Research
    WAVEX  = 0x130000    # MS WAVE with WAVEFORMATEX
    SD2    = 0x160000    # Sound Designer 2
    FLAC   = 0x170000    # FLAC lossless file format
    CAF    = 0x180000    # Core Audio File format
    WVE    = 0x190000    # Psion WVE format
    OGG    = 0x200000    # Xiph OGG container
    MPC2K  = 0x210000    # Akai MPC 2000 sampler
    RF64   = 0x220000    # RF64 WAV file
    MPEG   = 0x230000    # MPEG-1/2 audio stream

    # Subtypes from here on.

    PCM_S8       = 0x0001  # Signed 8 bit data
    PCM_16       = 0x0002  # Signed 16 bit data
    PCM_24       = 0x0003  # Signed 24 bit data
    PCM_32       = 0x0004  # Signed 32 bit data

    PCM_U8       = 0x0005  # Unsigned 8 bit data (WAV and RAW only)

    FLOAT        = 0x0006  # 32 bit float data
    DOUBLE       = 0x0007  # 64 bit float data

    ULAW         = 0x0010  # U-Law encoded
    ALAW         = 0x0011  # A-Law encoded
    IMA_ADPCM    = 0x0012  # IMA ADPCM
    MS_ADPCM     = 0x0013  # Microsoft ADPCM

    GSM610       = 0x0020  # GSM 6.10 encoding
    VOX_ADPCM    = 0x0021  # OKI / Dialogix ADPCM
    NMS_ADPCM_16 = 0x0022  # 16kbs NMS G721-variant encoding.
    NMS_ADPCM_24 = 0x0023  # 24kbs NMS G721-variant encoding.
    NMS_ADPCM_32 = 0x0024  # 32kbs NMS G721-variant encoding.

    G721_32      = 0x0030  # 32kbs G721 ADPCM encoding
    G723_24      = 0x0031  # 24kbs G723 ADPCM encoding
    G723_40      = 0x0032  # 40kbs G723 ADPCM encoding

    DWVW_12      = 0x0040  # 12 bit Delta Width Variable Word encoding
    DWVW_16      = 0x0041  # 16 bit Delta Width Variable Word encoding
    DWVW_24      = 0x0042  # 24 bit Delta Width Variable Word encoding
    DWVW_N       = 0x0043  # N bit Delta Width Variable Word encoding

    DPCM_8       = 0x0050  # 8 bit differential PCM (XI only)
    DPCM_16      = 0x0051  # 16 bit differential PCM (XI only)

    VORBIS       = 0x0060  # Xiph Vorbis encoding
    OPUS         = 0x0064  # Xiph/Skype Opus encoding.

    ALAC_16      = 0x0070  # Apple Lossless Audio Codec (16 bit)
    ALAC_20      = 0x0071  # Apple Lossless Audio Codec (20 bit)
    ALAC_24      = 0x0072  # Apple Lossless Audio Codec (24 bit)
    ALAC_32      = 0x0073  # Apple Lossless Audio Codec (32 bit)

    MPEG_LAYER_I   = 0x0080 # MPEG-1 Audio Layer I.
    MPEG_LAYER_II  = 0x0081 # MPEG-1 Audio Layer II.
    MPEG_LAYER_III = 0x0082 # MPEG-2 Audio Layer III.

    # Endian-ness options.

    ENDIAN_FILE    = 0x00000000    # Default file endian-ness.
    ENDIAN_LITTLE  = 0x10000000    # Force little endian-ness.
    ENDIAN_BIG     = 0x20000000    # Force big endian-ness.
    ENDIAN_CPU     = 0x30000000    # Force CPU endian-ness.

    SUBMASK  = 0x0000FFFF
    TYPEMASK = 0x0FFF0000
    ENDMASK  = 0x30000000

class Seek(int, Enum):
    SET = SEEK_MODES.SF_SEEK_SET # Relative to the begining of the file
    CUR = SEEK_MODES.SF_SEEK_CUR # Relative to the last read frame
    END = SEEK_MODES.SF_SEEK_END # Relative to the end of the file


class WaveMetadata(object):
    strings = dict((
        (
            k[len('SF_STR_'):].lower(),
            getattr(FILE_STRINGS,k)
        )
        for k in dir(FILE_STRINGS)
        if k.startswith('SF_STR_')
    ))

    __slots__ = list(strings.keys()) + [
        '_sndfile',
    ]

    def __init__(self, sndfile):
        self._sndfile = sndfile

    def __dir__(self):
        return [s for s in self.strings if s]

    def __getattr__(self, name):
        if name not in self.strings:
            raise AttributeError(name)
        stringid = self.strings[name]
        value = _lib.sf_get_string(self._sndfile, stringid)
        if value is None: return None
        return value.decode(_tagencoding)

    def __setattr__(self, name, value):
        if name not in self.strings:
            return object.__setattr__(self, name, value)

        stringid = self.strings[name]
        error = _lib.sf_set_string(self._sndfile, stringid, value.encode(_tagencoding))
        if error: print(ValueError(
            name,
            error, _sferrormessage(error)))

    def __iter__(self):
        for k, i in self.strings.items():
            value = _lib.sf_get_string(self._sndfile, i)
            if value is None: continue
            yield k, value.decode(_tagencoding)

class WaveWriter(object):
    def __init__(self,
                filename,
                samplerate = 44100,
                channels = 1,
                format = Format.WAV | Format.FLOAT,
                ):

        self._info = SF_INFO(
                samplerate = samplerate,
                channels = channels,
                format = format
            )
        self._sndfile = _lib.sf_open(_fsencode(filename), OPEN_MODES.SFM_WRITE, self._info)
        if _lib.sf_error(self._sndfile):
            raise IOError("Error opening '%s': %s"%(
                filename, _sferrormessage(_lib.sf_error(self._sndfile))))
        assert self._sndfile, "Null sndfile handle but no error status"
        self._metadata = WaveMetadata(self._sndfile)

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()
        if value: raise

    def close(self):
        _lib.sf_close( self._sndfile)

    @property
    def metadata(self):
        return self._metadata

    def write(self, data):
        channels, nframes = data.shape
        data = data.ravel('F')
        assert channels == self._info.channels
        if data.dtype==np.float64:
            return _lib.sf_writef_double(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), nframes)
        if data.dtype==np.float32:
            return _lib.sf_writef_float(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), nframes)
        if data.dtype==np.int16:
            return _lib.sf_writef_short(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), nframes)
        if data.dtype==np.int32:
            return _lib.sf_writef_int(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), nframes)
        raise TypeError("Please choose a correct dtype")

    def seek(self, frames, whence=Seek.SET):
        """Moves the current multisample frame to be read/written.
        This movement can be absolute position (whence=Seek.SET)
        relative to the current position (whence=Seek.CUR)
        or relative to the end (whence=Seek.END).
        Returns absolute seek position or -1 if out of scope.
        """
        return _lib.sf_seek(self._sndfile, frames, whence)

class WaveReader(object):
    def __init__(
        self,
        filename,
        samplerate = 0,
        channels = 0,
        format = 0,
    ):

        self._info = SF_INFO(
            samplerate = samplerate,
            channels = channels,
            format = format
        )
        self._sndfile = _lib.sf_open(_fsencode(filename), OPEN_MODES.SFM_READ, self._info)
        if _lib.sf_error(self._sndfile):
            raise IOError("Error opening '%s': %s"%(
                filename, _sferrormessage(_lib.sf_error(self._sndfile))))
        assert self._sndfile, "Null sndfile handle but no error status"
        self._metadata = WaveMetadata(self._sndfile)

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()
        if value: raise

    def close(self):
        _lib.sf_close( self._sndfile)

    @property
    def metadata(self):
        return self._metadata

    @property
    def channels(self): return self._info.channels

    @property
    def format(self): return self._info.format

    @property
    def samplerate(self): return self._info.samplerate

    @property
    def frames(self): return self._info.frames

    # TODO: Untested
    @property
    def byterate(self):
        return _lib.sf_current_byterate(self._sndfile)

    def read_iter(self, size=512, buffer=None):
        data = buffer
        if data is None:
            data = self.buffer(size)
        else:
            assert buffer.shape[0] == self.channels
            size = buffer.shape[1]
        nframes = self.read(data)
        while nframes:
            yield data[:,:nframes]
            nframes = self.read(data)

    def buffer(self, size, dtype=np.float32):
        """Provides a properly constructed buffer to read data"""
        return np.zeros((self.channels, size), dtype, order='F')

    def read(self, data):
        channels, frames = data.shape
        assert channels == self.channels, \
            "Buffer has room for %i channels, wave file has %i channels"%(
                channels, self.channels)
        assert data.strides[0]*channels == data.strides[1], \
            "Buffer storage be column-major order. Consider using buffer(size)"
        if data.dtype==np.float64:
            return _lib.sf_readf_double(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), frames)
        if data.dtype==np.float32:
            return _lib.sf_readf_float(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), frames)
        if data.dtype==np.int16:
            return _lib.sf_readf_short(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), frames)
        if data.dtype==np.int32:
            return _lib.sf_readf_int(self._sndfile, data.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), frames)
        raise TypeError("Please choose a correct dtype")

    def seek(self, frames, whence=Seek.SET):
        """Moves the current multisample frame to be read/written.
        This movement can be absolute position (whence=Seek.SET)
        relative to the current position (whence=Seek.CUR)
        or relative to the end (whence=Seek.END).
        Returns absolute seek position or -1 if out of scope.
        """
        return _lib.sf_seek(self._sndfile, frames, whence)

def load(filename):
    with WaveReader(filename) as r:
        blockSize = 512
        data = r.buffer(r.frames)
        fullblocks = r.frames // blockSize
        lastBlockSize = r.frames % blockSize
        for i in range(fullblocks):
            readframes = r.read(data[:,i*blockSize:(i+1)*blockSize])
            assert readframes == blockSize
        if lastBlockSize:
            readframes = r.read(data[:,fullblocks*blockSize:])
            assert readframes == lastBlockSize
        return r.samplerate, data

def save(filename, data, samplerate, verbose=False):
    """
    Given save the audio data, having shape (channels, frames),
    and stores as a sound file.
    For convenience you can also provide a mono in (channels,) shape.
    """
    if verbose: print("Saving wave file:",filename)

    # Mono convenience
    if len(data.shape) == 1:
        data = data.reshape((1,data.shape[0]))

    channels, frames = data.shape

    # TODO: Deprecate this compat code
    if channels>frames and frames>0: # heuristic to detect inverted dims
        warnings.warn(
            "First dimension should be the channel. "
            "Transposing but next version, python-wavefile 1.7, will not.",
            DeprecationWarning
        )
        data = data.T
        channels, frames = data.shape

    blockSize = 512
    fullblocks = frames // blockSize
    lastBlockSize = frames % blockSize
    with WaveWriter(filename, channels=channels, samplerate=samplerate) as w:
        for i in range(fullblocks):
            w.write(data[:,blockSize*i:blockSize*(i+1)])
        if lastBlockSize:
            w.write(data[:,fullblocks*blockSize:])

# For the mathlab nostalgic
loadWave=load
saveWave=save

def _command(commandCode, data, sf=None):
    sf = sf or ctypes.c_void_p(0)
    return _lib.sf_command(sf, commandCode, ctypes.byref(data), ctypes.sizeof(data))

def _getFormatList(counterCommand, getterCommand):
    n = ctypes.c_int()
    _command(counterCommand, n)
    for i in range(n.value):
        info = SF_FORMAT_INFO(format=i)
        _command(getterCommand, info)
        item = dict(
            format=info.format,
            name=info.name.decode(),
            extension=info.extension and info.extension.decode(),
        )
        yield item

def commonFormats():
    return _getFormatList(
        COMMANDS.SFC_GET_SIMPLE_FORMAT_COUNT,
        COMMANDS.SFC_GET_SIMPLE_FORMAT)

def majorFormats():
    return _getFormatList(
        COMMANDS.SFC_GET_FORMAT_MAJOR_COUNT,
        COMMANDS.SFC_GET_FORMAT_MAJOR)

def subtypeFormats():
    return _getFormatList(
        COMMANDS.SFC_GET_FORMAT_SUBTYPE_COUNT,
        COMMANDS.SFC_GET_FORMAT_SUBTYPE)

def allFormats():
    majors = majorFormats()
    minors = list(subtypeFormats())
    return (
        dict(
            format = major['format'] | minor['format'],
            name = major['name'] + " " + minor['name'],
            extension = major['extension'],
        )
        for major in majors
        for minor in minors
        if checkFormat(major['format'] | minor['format'])
    )


def checkFormat(format):
    return _lib.sf_format_check(SF_INFO(
        frames=1000, # whatever
        samplerate=44100, # whatever
        channels=2, # whatever
        format=format,
    ))

def formatDescription(code):
    result = {}
    sf = ctypes.c_void_p(0)
    minor = None
    minorCode = code & FILE_FORMATS.SF_FORMAT_SUBMASK
    if minorCode:
        info = SF_FORMAT_INFO(format=minorCode)
        error = _command(COMMANDS.SFC_GET_FORMAT_INFO, info)
        if error:
            raise ValueError(code)

        result.update(
            subtype = info.name.decode()
        )

    if code & FILE_FORMATS.SF_FORMAT_TYPEMASK:
        info = SF_FORMAT_INFO(format=code)
        error = _command(COMMANDS.SFC_GET_FORMAT_INFO, info)
        if error:
            raise ValueError(code)
        result.update(
            format=info.format,
            name=info.name.decode(),
            extension=info.extension and info.extension.decode(),
        )
    return result or None


# vim: et ts=4 sw=4
