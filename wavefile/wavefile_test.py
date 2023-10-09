#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from __future__ import unicode_literals
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),"../"))

from . import wavefile
import unittest
import numpy as np
from numpy.testing import (
    assert_almost_equal as np_assert_almost_equal,
)

def v(versiontext):
    import pkg_resources
    return pkg_resources.parse_version(versiontext)

class WavefileTest(unittest.TestCase):

    def setUp(self):
        self.filestoremove = []
        import pkg_resources
        self.sfversion = wavefile._lib.sf_version_string().decode()
        self.version = v(self.sfversion[len('libsndfile-'):])

    def tearDown(self):
        import os
        for file in self.filestoremove:
            if os.access(file, os.F_OK):
                os.remove(file)

    def toRemove(self, file):
        self.filestoremove.append(file)

    def savewav(self, data, filename, samplerate):
        import os
        assert not os.access(filename, os.F_OK), "Test temporary file already existed: %s"%filename
        import wavefile
        with wavefile.WaveWriter(
                filename,
                samplerate=samplerate,
                channels=data.shape[1]
                ) as writer:
            writer.write(data.ravel("C").reshape(data.shape))
        self.toRemove(filename)

    def writeFile(self, name, content):
        f = open(name,'w')
        self.toRemove(name)
        f.write(content)
        f.close()

    def display(self, file):
        import os
        os.system("sweep '%s'"%file)

    def sinusoid(self, samples=400, f=440, samplerate=44100):
        return np.sin( np.linspace(0, 2*np.pi*f*samples/samplerate, samples))[np.newaxis,:]

    def counter(self, samples=400):
        return np.arange(samples)[np.newaxis,:]*1.0

    def channels(self, *args):
        return np.vstack(args)

    def stereoSinusoids(self, samples=400):
        return self.channels(
            self.sinusoid(samples, 440),
            self.sinusoid(samples, 880),
            )

    def fourSinusoids(self, samples=400):
        return self.channels(
            self.sinusoid(samples, 880),
            self.sinusoid(samples, 440),
            self.sinusoid(samples, 220),
            self.sinusoid(samples, 110),
        )


    def test_sinusoid(self):
        self.assertEqual(self.sinusoid(600).shape, (1,600))

    def test_channels(self):
        self.assertEqual(self.fourSinusoids(600).shape, (4,600))

    def test_reader_withMissingFile(self):
        try:
            r = wavefile.WaveReader("notexisting.wav")
            self.fail("Exception expected")
        except IOError as e:
            self.assertEqual( (
                "Error opening 'notexisting.wav': System error.",
            ), e.args)

    def test_reader_withWrongfile(self):
        self.writeFile("badfile.wav","Bad content")
        try:
            r = wavefile.WaveReader("badfile.wav")
            self.fail("Exception expected")
        except IOError as e:
            self.assertIn(e.args[0], [
                "Error opening 'badfile.wav': File contains data in an unknown format.", # libsndfile 1.0.28
                "Error opening 'badfile.wav': Format not recognised.", # libsndfile > 1.0.30
            ])

    def test_writter_withWrongPath(self):
        try:
            w = wavefile.WaveWriter("/badpath/file.wav")
            self.fail("Exception expected")
        except IOError as e:
            self.assertEqual( (
                "Error opening '/badpath/file.wav': System error.",
            ), e.args)

    def test_readed_generatedByWaveWriter(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav")
        r = wavefile.WaveReader("file.wav")

    def test_format_byDefault(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav")
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(
            hex(
                wavefile.Format.WAV |
                wavefile.Format.FLOAT |
                0),
            hex(r.format))

    def test_format_whenOgg(self):
        self.toRemove("file.ogg")
        w = wavefile.WaveWriter("file.ogg",
            format= wavefile.Format.OGG | wavefile.Format.VORBIS)
        w.close()
        r = wavefile.WaveReader("file.ogg")
        self.assertEqual(
            hex(
                wavefile.Format.OGG |
                wavefile.Format.VORBIS |
                0),
            hex(r.format))

    def test_channels_byDefault(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav")
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(1, r.channels)

    def test_channels_set(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav", channels=4)
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(4, r.channels)
        r.close()

    def test_samplerate_byDefault(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav")
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(44100, r.samplerate)
        r.close()

    def test_sampelrate_set(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav", samplerate=22050)
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(22050, r.samplerate)
        r.close()

    def test_metadata_default(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav", samplerate=22050)
        w.close()
        r = wavefile.WaveReader("file.wav")
        self.assertEqual(None, r.metadata.title)
        self.assertEqual(None, r.metadata.copyright)
        self.assertEqual(None, r.metadata.software)
        self.assertEqual(None, r.metadata.artist)
        self.assertEqual(None, r.metadata.comment)
        self.assertEqual(None, r.metadata.date)
        self.assertEqual(None, r.metadata.album)
        self.assertEqual(None, r.metadata.license)
        self.assertEqual(None, r.metadata.tracknumber)
        self.assertEqual(None, r.metadata.genre)
        r.close()

    def test_metadata_illegalAttribute(self):
        self.toRemove("file.wav")
        w = wavefile.WaveWriter("file.wav", samplerate=22050)
        w.close()
        r = wavefile.WaveReader("file.wav")
        try:
            self.assertEqual(None, r.metadata.illegalAttribute)
            self.fail("Exception expected")
        except AttributeError as e:
            self.assertEqual( (
                "illegalAttribute",
            ), e.args)
        r.close()


    def write3Channels(self):
        self.saw = np.linspace(0,1,10).astype(np.float32)
        self.sin = np.sin(2*np.pi*self.saw).astype(np.float32)
        self.sqr = np.concatenate((np.ones(5), -np.ones(5))).astype(np.float32)
        self.input = np.array([self.saw, self.sin, self.sqr]).T.copy()
        wavefile.save("file.wav", self.input, 44100)

    def test_metadata_set(self):
        self.toRemove("file.ogg")
        w = wavefile.WaveWriter("file.ogg",
            format=wavefile.Format.OGG|wavefile.Format.VORBIS)
        w.metadata.title = 'mytitle'
        w.metadata.copyright = 'mycopyright'
        w.metadata.software = 'mysoftware'
        w.metadata.artist = 'myartist'
        w.metadata.comment = 'mycomment'
        w.metadata.date = 'mydate'
        w.metadata.album = 'myalbum'
        w.metadata.license = 'mylicense'
        w.metadata.tracknumber = '77'
        w.metadata.genre = 'mygenre'
        w.close()
        r = wavefile.WaveReader("file.ogg")
        self.assertEqual("mytitle", r.metadata.title)
        self.assertEqual("mycopyright", r.metadata.copyright)
        self.assertEqual("mysoftware ({0})".format(self.sfversion),
            r.metadata.software)
        self.assertEqual("myartist", r.metadata.artist)
        self.assertEqual("mycomment", r.metadata.comment)
        self.assertEqual("mydate", r.metadata.date)
        self.assertEqual("myalbum", r.metadata.album)
        self.assertEqual("mylicense", r.metadata.license)
        if self.version > v('1.0.25'):
            self.assertEqual("77", r.metadata.tracknumber)
            self.assertEqual("mygenre", r.metadata.genre)
        r.close()

    def test_metadata_iter(self):
        self.toRemove("file.ogg")
        w = wavefile.WaveWriter("file.ogg",
            format=wavefile.Format.OGG|wavefile.Format.VORBIS)
        w.metadata.title = 'mytitle'
        w.metadata.copyright = 'mycopyright'
        w.metadata.software = 'mysoftware'
        w.metadata.artist = 'myartist'
        w.metadata.comment = 'mycomment'
        w.metadata.date = 'mydate'
        w.metadata.album = 'myalbum'
        w.metadata.license = 'mylicense'
        w.metadata.tracknumber = '77'
        w.metadata.genre = 'mygenre'
        w.close()
        r = wavefile.WaveReader("file.ogg")
        strings = dict(r.metadata)
        expected = dict(
            title = 'mytitle',
            copyright = 'mycopyright',
            software = 'mysoftware ({0})'.format(self.sfversion),
            artist = 'myartist',
            comment = 'mycomment',
            date = 'mydate',
            album = 'myalbum',
            license = 'mylicense',
            )
        if self.version > v('1.0.25'):
            expected.update(
                tracknumber='77',
                genre='mygenre',
                )
        self.assertEqual(strings, expected)
        r.close()

    def writeWav(self, filename, data):
        self.toRemove(filename)
        with wavefile.WaveWriter(filename, channels=data.shape[0]) as w:
            w.write(data)


    def test_read(self):
        data = self.fourSinusoids(samples=400)
        self.writeWav("file.wav", data)
        with wavefile.WaveReader("file.wav") as r:
            readdata = np.zeros((4, 1000), np.float32, order='F')
            size = r.read(readdata)
            self.assertEqual(size, 400)
            np_assert_almost_equal(readdata[:,:size], data, decimal=7)

    def test_read_withRowMajorArrays(self):
        data = self.fourSinusoids(samples=400)
        self.writeWav("file.wav", data)
        with wavefile.WaveReader("file.wav") as r:
            try:
                readdata = np.zeros((4, 1000), np.float32)
                size = r.read(readdata)
                self.fail("Exception expedted")
            except AssertionError as e:
                self.assertEqual(
                    ("Buffer storage be column-major order. Consider using buffer(size)",),
                    e.args
                    )

    def test_read_badChannels(self):
        data = self.fourSinusoids(samples=400)
        self.writeWav("file.wav", data)
        with wavefile.WaveReader("file.wav") as r:
            try:
                readdata = np.zeros((2, 1000), np.float32, order='F')
                size = r.read(readdata)
                self.fail("Exception expedted")
            except Exception as e:
                self.assertEqual(
                    ("Buffer has room for 2 channels, wave file has 4 channels",),
                    e.args
                    )

    def test_readIter(self):
        blockSize = 100
        data = self.fourSinusoids(samples=400)
        self.writeWav("file.wav", data)
        with wavefile.WaveReader("file.wav") as r:
            for i, readdata in enumerate(r.read_iter(blockSize)):
                np_assert_almost_equal(data[:,i*blockSize:(i+1)*blockSize],readdata)
        self.assertEqual(3, i)

    def test_readIter_nonExactBlock(self):
        blockSize = 100
        data = self.fourSinusoids(samples=410)
        self.writeWav("file.wav", data)
        with wavefile.WaveReader("file.wav") as r:
            for i, readdata in enumerate(r.read_iter(blockSize)):
                np_assert_almost_equal(
                    data[:,i*blockSize:i*blockSize+readdata.shape[1]],
                    readdata)
        self.assertEqual(4, i)


    def test_write_unicodeFilename(self):
        data = self.fourSinusoids(samples=400)
        self.writeWav("file€.wav", data)

        self.assertTrue("file€.wav" in os.listdir('.'))

    def test_write_unicodeFilename_koreanCodepage(self):
        # Should work in windows if your code page is Korean (cp1252) and fail with any other
        data = self.fourSinusoids(samples=400)
        self.writeWav("언어.wav", data)

        self.assertTrue("언어.wav" in os.listdir('.'))

    def test_write_unicodeFilename_multipleCodePage(self):
        # Should fail (by now) in windows which ever you code page is
        data = self.fourSinusoids(samples=400)
        self.writeWav("语言Языку.wav", data)

        self.assertTrue("语言Языку.wav" in os.listdir(u'.'))

    def test_write_decodedFilenames(self):
        data = self.fourSinusoids(samples=400)
        encoded = "file€.wav".encode(sys.getfilesystemencoding())
        self.writeWav(encoded, data)

        self.assertTrue("file€.wav" in os.listdir(u'.'))

    def test_counterHelper(self):
        blockSize = 10
        data = self.counter(samples=400)
        self.writeWav("file.wav", data)
        firstSamples = []
        with wavefile.WaveReader("file.wav") as r:
            for i, readdata in enumerate(r.read_iter(blockSize)):
                firstSample = int(round(readdata[0][0]))
                firstSamples.append(firstSample)
        self.assertEqual(list(range(0,400,10)), firstSamples)

    def seekTestHelper(self, frames, whence, expectedFrame, expectedSeq):
        """After reading the frames block starting at 40,
        do a seek of 'frames' frames relative to the 'whence'
        and check that seek returns expectedFrame, and that the final
        sequence is 'expectedSeq' """

        blockSize = 10
        data = self.counter(samples=100)
        self.writeWav("file.wav", data)
        firstSamples = []
        with wavefile.WaveReader("file.wav") as r:
            for i, readdata in enumerate(r.read_iter(blockSize)):
                firstSample = int(round(readdata[0][0]))
                if firstSample == 40 and 40 not in firstSamples:
                    pos = r.seek(frames, whence)
                    self.assertEqual(expectedFrame, pos)
                firstSamples.append(firstSample)
        self.assertEqual(expectedSeq, firstSamples)

    def test_seek_absoluteForward(self):
        self.seekTestHelper(
            55, wavefile.Seek.SET, 55,
            list(range(0,50,10))+list(range(55,100,10)))

    def test_seek_absoluteBackward(self):
        self.seekTestHelper(
            35, wavefile.Seek.SET, 35,
            list(range(0,50,10))+list(range(35,100,10)))

    def test_seek_absoluteNegative(self):
        self.seekTestHelper(
            -35, wavefile.Seek.SET, -1,
            list(range(0,100,10)))

    def test_seek_absoluteToTheEnd_nextReadJustFinishes(self):
        self.seekTestHelper(
            100, wavefile.Seek.SET, 100,
            list(range(0,50,10)))

    def test_seek_absoluteBeyondEnd(self):
        self.seekTestHelper(
            101, wavefile.Seek.SET, -1,
            list(range(0,100,10)))

    def test_seek_absoluteAtStart(self):
        self.seekTestHelper(
            0, wavefile.Seek.SET, 0,
            list(range(0,50,10))+list(range(0,100,10)))

    def test_seek_relativeForward(self):
        self.seekTestHelper(
            +32, wavefile.Seek.CUR, 82,
            list(range(0,50,10))+list(range(82,100,10)))

    def test_seek_relativeBackward(self):
        self.seekTestHelper(
            -32, wavefile.Seek.CUR, 18,
            list(range(0,50,10))+list(range(18,100,10)))

    def test_seek_relativeBackwardTooMuch(self):
        self.seekTestHelper(
            -51, wavefile.Seek.CUR, -1,
            list(range(0,100,10)))

    def test_seek_relativeForwardTooMuch(self):
        self.seekTestHelper(
            +51, wavefile.Seek.CUR, -1,
            list(range(0,100,10)))

    def test_seek_relativeAtEnd(self):
        self.seekTestHelper(
            +50, wavefile.Seek.CUR, 100,
            list(range(0,50,10)))

    def test_seek_fromEndBack(self):
        self.seekTestHelper(
            -20, wavefile.Seek.END, 80,
            list(range(0,50,10))+list(range(80,100,10)))

    def test_seek_fromEndToTheBegining(self):
        self.seekTestHelper(
            -100, wavefile.Seek.END, 0,
            list(range(0,50,10))+list(range(0,100,10)))

    def test_seek_fromEndBackTooMuch(self):
        self.seekTestHelper(
            -101, wavefile.Seek.END, -1,
            list(range(0,100,10)))

    def test_seek_fromEndStay(self):
        self.seekTestHelper(
            0, wavefile.Seek.END, 100,
            list(range(0,50,10)))

    def test_seek_fromEndForwardFails(self):
        self.seekTestHelper(
            1, wavefile.Seek.END, -1,
            list(range(0,100,10)))

    def test_seek_toResetFileReading(self):
        blockSize = 10
        data = self.counter(samples=100)
        self.writeWav("file.wav", data)
        firstSamples = []
        with wavefile.WaveReader("file.wav") as r:
            for i, readdata in enumerate(r.read_iter(blockSize)):
                firstSample = int(round(readdata[0][0]))
                firstSamples.append(firstSample)
            pos = r.seek(0, wavefile.Seek.SET)
            for i, readdata in enumerate(r.read_iter(blockSize)):
                firstSample = int(round(readdata[0][0]))
                firstSamples.append(firstSample)
        self.assertEqual(list(range(0,100,10))*2, firstSamples)

    def test_load(self):
        data = self.fourSinusoids(samples=400)
        self.writeWav("file.wav", data)
        readsamplerate, readdata = wavefile.load("file.wav")
        np_assert_almost_equal(readdata, data, decimal=7)
        self.assertEqual(readsamplerate, 44100)

    def test_load_longer(self):
        data = self.fourSinusoids(samples=600) # > 512
        self.writeWav("file.wav", data)
        readsamplerate, readdata = wavefile.load("file.wav")
        np_assert_almost_equal(readdata, data, decimal=7)
        self.assertEqual(readsamplerate, 44100)

    def assertLoadWav(self, filename,
            expectedData=None,
            expectedSamplerate=44100,
            expectedShape=None
    ):
        samplerate, data = wavefile.load("file.wav")
        if expectedShape is not None:
            self.assertEqual(data.shape, expectedShape)
        if expectedData is not None:
            np_assert_almost_equal(expectedData, data, decimal=7)
        self.assertEqual(expectedSamplerate, samplerate)

    def test_save(self):
        data = self.fourSinusoids(samples=400)
        wavefile.save("file.wav", data, samplerate=44100)
        self.assertLoadWav("file.wav", data)

    def test_save_slice(self):
        data = self.fourSinusoids(samples=400)
        #data = np.ascontiguousarray(data)
        wavefile.save("file.wav", data[:,::2], samplerate=44100)
        self.assertLoadWav('file.wav', data[:,::2])

    def test_save_longerThanAFrame(self):
        data = self.fourSinusoids(samples=600) # >512
        wavefile.save("file.wav", data, samplerate=44100)
        self.assertLoadWav('file.wav', data)

    def test_save_asCOrder(self):
        data = self.fourSinusoids(samples=400)
        data = np.ascontiguousarray(data)
        wavefile.save("file.wav", data, samplerate=44100)
        self.assertLoadWav('file.wav', data)

    def test_save_swappedAxis_fixesThem_deprecated(self):
        data = self.fourSinusoids(samples=400)
        frameFirst = np.ascontiguousarray(data.T)
        wavefile.save("file.wav", frameFirst, samplerate=44100)
        self.assertLoadWav('file.wav', data)

    @unittest.skipIf(sys.version_info < (3,2), "Warning assertions introduced in 3.2")
    def test_save_swappedAxis_deprecationWarning(self):
        data = self.fourSinusoids(samples=400)
        frameFirst = np.ascontiguousarray(data.T)
        with self.assertWarnsRegex(DeprecationWarning,
            "First dimension should be the channel."
        ):
            wavefile.save("file.wav", frameFirst, samplerate=44100)

    def test_save_monoInSingleDimension_forConvenience(self):
        data = self.sinusoid(samples=400, f=440)[0]
        self.assertEqual(data.shape, (400,))
        wavefile.save("file.wav", data, samplerate=44100)
        # Read still provides the channel dimension
        self.assertLoadWav('file.wav', data.reshape((1,400)))


class Format_Test(unittest.TestCase):

    def setUp(self):
        import pkg_resources
        self.sfversion = wavefile._lib.sf_version_string().decode()
        self.version = v(self.sfversion[len('libsndfile-'):])
        self.maxDiff = None

    def assertFormatListEqual(self, data, expected):
        rendered = ''.join(
            """{format:08x}: "{name}"{formatedExtension}\n""".format(
                    formatedExtension = " ({extension})".format(**item) if item['extension'] else "",
                    **item
                )
            for item in sorted(data, key=lambda x: x['format'])
        )
        self.maxDiff = None
        self.assertMultiLineEqual(rendered, expected)

    def test_commonFormats(self):
        formats = wavefile.commonFormats()
        self.assertFormatListEqual(formats,
            """00010002: "WAV (Microsoft 16 bit PCM)" (wav)\n"""
            """00010005: "WAV (Microsoft 8 bit PCM)" (wav)\n"""
            """00010006: "WAV (Microsoft 32 bit float)" (wav)\n"""
            """00010012: "WAV (Microsoft 4 bit IMA ADPCM)" (wav)\n"""
            """00010013: "WAV (Microsoft 4 bit MS ADPCM)" (wav)\n"""
            """00020001: "AIFF (Apple/SGI 8 bit PCM)" (aiff)\n"""
            """00020002: "AIFF (Apple/SGI 16 bit PCM)" (aiff)\n"""
            """00020006: "AIFF (Apple/SGI 32 bit float)" (aifc)\n"""
            """00030002: "AU (Sun/Next 16 bit PCM)" (au)\n"""
            """00030010: "AU (Sun/Next 8-bit u-law)" (au)\n"""
            """00040021: "OKI Dialogic VOX ADPCM" (vox)\n"""
            + (
            """00170002: "FLAC 16 bit" (flac)\n"""
                if self.version>=v('1.0.18') else ""
            )
            +
            """00180002: "CAF (Apple 16 bit PCM)" (caf)\n"""
            """00180070: "CAF (Apple 16 bit ALAC)" (caf)\n"""
            + (
            """00200060: "Ogg Vorbis (Xiph Foundation)" (ogg)\n"""
                if self.version>=v('1.0.31') else ""
            )
            + (
            """00200060: "Ogg Vorbis (Xiph Foundation)" (oga)\n"""
                if v('1.0.31')>self.version>=v('1.0.18') else "")
            + (
            """00200064: "Ogg Opus (Xiph Foundation)" (opus)\n"""
                if self.version>=v('1.0.29') else "")
            + (
            """00230082: "MPEG Layer 3" (mp3)\n"""
                if self.version>v('1.0.31') else "")
        )


    def test_majorFormats(self):
        formats = wavefile.majorFormats()
        self.assertFormatListEqual(formats, ""
            """00010000: "WAV (Microsoft)" (wav)\n"""
            """00020000: "AIFF (Apple/SGI)" (aiff)\n"""
            """00030000: "AU (Sun/NeXT)" (au)\n"""
            """00040000: "RAW (header-less)" (raw)\n"""
            """00050000: "PAF (Ensoniq PARIS)" (paf)\n"""
            """00060000: "IFF (Amiga IFF/SVX8/SV16)" (iff)\n"""
            """00070000: "WAV (NIST Sphere)" (wav)\n"""
            """00080000: "VOC (Creative Labs)" (voc)\n"""
            """000a0000: "SF (Berkeley/IRCAM/CARL)" (sf)\n"""
            """000b0000: "W64 (SoundFoundry WAVE 64)" (w64)\n"""
            """000c0000: "MAT4 (GNU Octave 2.0 / Matlab 4.2)" (mat)\n"""
            """000d0000: "MAT5 (GNU Octave 2.1 / Matlab 5.0)" (mat)\n"""
            """000e0000: "PVF (Portable Voice Format)" (pvf)\n"""
            """000f0000: "XI (FastTracker 2)" (xi)\n"""
            """00100000: "HTK (HMM Tool Kit)" (htk)\n"""
            """00110000: "SDS (Midi Sample Dump Standard)" (sds)\n"""
            """00120000: "AVR (Audio Visual Research)" (avr)\n"""
            """00130000: "WAVEX (Microsoft)" (wav)\n"""
            """00160000: "SD2 (Sound Designer II)" (sd2)\n"""
            """00170000: "FLAC (Free Lossless Audio Codec)" (flac)\n"""
            """00180000: "CAF (Apple Core Audio File)" (caf)\n"""
            """00190000: "WVE (Psion Series 3)" (wve)\n"""
            """00200000: "OGG (OGG Container format)" (oga)\n"""
            """00210000: "MPC (Akai MPC 2k)" (mpc)\n"""
            """00220000: "RF64 (RIFF 64)" (rf64)\n"""
            + (
            """00230000: "MPEG-1/2 Audio" (m1a)\n"""
                if self.version > v('1.0.31') else "")

        )

    def test_subtypeFormats(self):
        formats = wavefile.subtypeFormats()
        self.assertFormatListEqual(formats, ""
            """00000001: "Signed 8 bit PCM"\n"""
            """00000002: "Signed 16 bit PCM"\n"""
            """00000003: "Signed 24 bit PCM"\n"""
            """00000004: "Signed 32 bit PCM"\n"""
            """00000005: "Unsigned 8 bit PCM"\n"""
            """00000006: "32 bit float"\n"""
            """00000007: "64 bit float"\n"""
            """00000010: "U-Law"\n"""
            """00000011: "A-Law"\n"""
            """00000012: "IMA ADPCM"\n"""
            """00000013: "Microsoft ADPCM"\n"""
            """00000020: "GSM 6.10"\n"""
            """00000021: "VOX ADPCM" (vox)\n"""
            + (
            """00000022: "16kbs NMS ADPCM"\n"""
            """00000023: "24kbs NMS ADPCM"\n"""
            """00000024: "32kbs NMS ADPCM"\n"""
                if self.version>=v('1.0.29') else "")
            +
            """00000030: "32kbs G721 ADPCM"\n"""
            """00000031: "24kbs G723 ADPCM"\n"""
            + (
            """00000032: "40kbs G723 ADPCM"\n"""
                if self.version>=v('1.0.29') else "")
            +
            """00000040: "12 bit DWVW"\n"""
            """00000041: "16 bit DWVW"\n"""
            """00000042: "24 bit DWVW"\n"""
            """00000050: "8 bit DPCM"\n"""
            """00000051: "16 bit DPCM"\n"""
            + (
            """00000060: "Vorbis"\n"""
                if self.version>=v('1.0.18') else "")
            + (
            """00000064: "Opus"\n"""
                if self.version>=v('1.0.29') else "")
            +
            """00000070: "16 bit ALAC"\n"""
            """00000071: "20 bit ALAC"\n"""
            """00000072: "24 bit ALAC"\n"""
            """00000073: "32 bit ALAC"\n"""
            + (
            """00000080: "MPEG Layer I" (mp1)\n"""
            """00000081: "MPEG Layer II" (mp2)\n"""
            """00000082: "MPEG Layer III" (mp3)\n"""
                if self.version>v('1.0.31') else "")

        )

    def test_formatDescription_full(self):
        self.assertEqual(
            wavefile.formatDescription(
                wavefile.Format.WAV | wavefile.Format.PCM_16
            ), dict(
                format=0x00010000,
                name="WAV (Microsoft)",
                subtype="Signed 16 bit PCM",
                extension="wav",
            )
        )

    def test_formatDescription_major(self):
        self.assertEqual(
            wavefile.formatDescription(
                wavefile.Format.WAV
            ), dict(
                format=0x00010000,
                name="WAV (Microsoft)",
                # no subtype
                extension="wav",
            )
        )

    def test_formatDescription_subtype(self):
        self.assertEqual(
            wavefile.formatDescription(
                wavefile.Format.PCM_16
            ), dict(
                # no format
                # no name
                subtype="Signed 16 bit PCM",
                # no extension
            )
        )

    def test_checkFormat_whenCompatible(self):
        self.assertTrue(wavefile.checkFormat(
            wavefile.Format.WAV | wavefile.Format.PCM_16))

    def test_checkFormat_whenIncompatible(self):
        self.assertFalse(wavefile.checkFormat(
            wavefile.Format.WAV | wavefile.Format.PCM_S8))

    def test_allFormats(self):
        formats = wavefile.allFormats()
        self.assertFormatListEqual(formats, ""
            """00010002: "WAV (Microsoft) Signed 16 bit PCM" (wav)\n"""
            """00010003: "WAV (Microsoft) Signed 24 bit PCM" (wav)\n"""
            """00010004: "WAV (Microsoft) Signed 32 bit PCM" (wav)\n"""
            """00010005: "WAV (Microsoft) Unsigned 8 bit PCM" (wav)\n"""
            """00010006: "WAV (Microsoft) 32 bit float" (wav)\n"""
            """00010007: "WAV (Microsoft) 64 bit float" (wav)\n"""
            """00010010: "WAV (Microsoft) U-Law" (wav)\n"""
            """00010011: "WAV (Microsoft) A-Law" (wav)\n"""
            """00010012: "WAV (Microsoft) IMA ADPCM" (wav)\n"""
            """00010013: "WAV (Microsoft) Microsoft ADPCM" (wav)\n"""
            + (
            """00010082: "WAV (Microsoft) MPEG Layer III" (wav)\n"""
                if self.version>v('1.0.31') else "")
            +
            """00020001: "AIFF (Apple/SGI) Signed 8 bit PCM" (aiff)\n"""
            """00020002: "AIFF (Apple/SGI) Signed 16 bit PCM" (aiff)\n"""
            """00020003: "AIFF (Apple/SGI) Signed 24 bit PCM" (aiff)\n"""
            """00020004: "AIFF (Apple/SGI) Signed 32 bit PCM" (aiff)\n"""
            """00020005: "AIFF (Apple/SGI) Unsigned 8 bit PCM" (aiff)\n"""
            """00020006: "AIFF (Apple/SGI) 32 bit float" (aiff)\n"""
            """00020007: "AIFF (Apple/SGI) 64 bit float" (aiff)\n"""
            """00020010: "AIFF (Apple/SGI) U-Law" (aiff)\n"""
            """00020011: "AIFF (Apple/SGI) A-Law" (aiff)\n"""
            """00020012: "AIFF (Apple/SGI) IMA ADPCM" (aiff)\n"""
            """00030001: "AU (Sun/NeXT) Signed 8 bit PCM" (au)\n"""
            """00030002: "AU (Sun/NeXT) Signed 16 bit PCM" (au)\n"""
            """00030003: "AU (Sun/NeXT) Signed 24 bit PCM" (au)\n"""
            """00030004: "AU (Sun/NeXT) Signed 32 bit PCM" (au)\n"""
            """00030006: "AU (Sun/NeXT) 32 bit float" (au)\n"""
            """00030007: "AU (Sun/NeXT) 64 bit float" (au)\n"""
            """00030010: "AU (Sun/NeXT) U-Law" (au)\n"""
            """00030011: "AU (Sun/NeXT) A-Law" (au)\n"""
            """00040001: "RAW (header-less) Signed 8 bit PCM" (raw)\n"""
            """00040002: "RAW (header-less) Signed 16 bit PCM" (raw)\n"""
            """00040003: "RAW (header-less) Signed 24 bit PCM" (raw)\n"""
            """00040004: "RAW (header-less) Signed 32 bit PCM" (raw)\n"""
            """00040005: "RAW (header-less) Unsigned 8 bit PCM" (raw)\n"""
            """00040006: "RAW (header-less) 32 bit float" (raw)\n"""
            """00040007: "RAW (header-less) 64 bit float" (raw)\n"""
            """00040010: "RAW (header-less) U-Law" (raw)\n"""
            """00040011: "RAW (header-less) A-Law" (raw)\n"""
            """00050001: "PAF (Ensoniq PARIS) Signed 8 bit PCM" (paf)\n"""
            """00050002: "PAF (Ensoniq PARIS) Signed 16 bit PCM" (paf)\n"""
            """00050003: "PAF (Ensoniq PARIS) Signed 24 bit PCM" (paf)\n"""
            """00070001: "WAV (NIST Sphere) Signed 8 bit PCM" (wav)\n"""
            """00070002: "WAV (NIST Sphere) Signed 16 bit PCM" (wav)\n"""
            """00070003: "WAV (NIST Sphere) Signed 24 bit PCM" (wav)\n"""
            """00070004: "WAV (NIST Sphere) Signed 32 bit PCM" (wav)\n"""
            """00070010: "WAV (NIST Sphere) U-Law" (wav)\n"""
            """00070011: "WAV (NIST Sphere) A-Law" (wav)\n"""
            """00080002: "VOC (Creative Labs) Signed 16 bit PCM" (voc)\n"""
            """00080005: "VOC (Creative Labs) Unsigned 8 bit PCM" (voc)\n"""
            """00080010: "VOC (Creative Labs) U-Law" (voc)\n"""
            """00080011: "VOC (Creative Labs) A-Law" (voc)\n"""
            """000a0002: "SF (Berkeley/IRCAM/CARL) Signed 16 bit PCM" (sf)\n"""
            """000a0004: "SF (Berkeley/IRCAM/CARL) Signed 32 bit PCM" (sf)\n"""
            """000a0006: "SF (Berkeley/IRCAM/CARL) 32 bit float" (sf)\n"""
            """000a0010: "SF (Berkeley/IRCAM/CARL) U-Law" (sf)\n"""
            """000a0011: "SF (Berkeley/IRCAM/CARL) A-Law" (sf)\n"""
            """000b0002: "W64 (SoundFoundry WAVE 64) Signed 16 bit PCM" (w64)\n"""
            """000b0003: "W64 (SoundFoundry WAVE 64) Signed 24 bit PCM" (w64)\n"""
            """000b0004: "W64 (SoundFoundry WAVE 64) Signed 32 bit PCM" (w64)\n"""
            """000b0005: "W64 (SoundFoundry WAVE 64) Unsigned 8 bit PCM" (w64)\n"""
            """000b0006: "W64 (SoundFoundry WAVE 64) 32 bit float" (w64)\n"""
            """000b0007: "W64 (SoundFoundry WAVE 64) 64 bit float" (w64)\n"""
            """000b0010: "W64 (SoundFoundry WAVE 64) U-Law" (w64)\n"""
            """000b0011: "W64 (SoundFoundry WAVE 64) A-Law" (w64)\n"""
            """000b0012: "W64 (SoundFoundry WAVE 64) IMA ADPCM" (w64)\n"""
            """000b0013: "W64 (SoundFoundry WAVE 64) Microsoft ADPCM" (w64)\n"""
            """000c0002: "MAT4 (GNU Octave 2.0 / Matlab 4.2) Signed 16 bit PCM" (mat)\n"""
            """000c0004: "MAT4 (GNU Octave 2.0 / Matlab 4.2) Signed 32 bit PCM" (mat)\n"""
            """000c0006: "MAT4 (GNU Octave 2.0 / Matlab 4.2) 32 bit float" (mat)\n"""
            """000c0007: "MAT4 (GNU Octave 2.0 / Matlab 4.2) 64 bit float" (mat)\n"""
            """000d0002: "MAT5 (GNU Octave 2.1 / Matlab 5.0) Signed 16 bit PCM" (mat)\n"""
            """000d0004: "MAT5 (GNU Octave 2.1 / Matlab 5.0) Signed 32 bit PCM" (mat)\n"""
            """000d0005: "MAT5 (GNU Octave 2.1 / Matlab 5.0) Unsigned 8 bit PCM" (mat)\n"""
            """000d0006: "MAT5 (GNU Octave 2.1 / Matlab 5.0) 32 bit float" (mat)\n"""
            """000d0007: "MAT5 (GNU Octave 2.1 / Matlab 5.0) 64 bit float" (mat)\n"""
            """000e0001: "PVF (Portable Voice Format) Signed 8 bit PCM" (pvf)\n"""
            """000e0002: "PVF (Portable Voice Format) Signed 16 bit PCM" (pvf)\n"""
            """000e0004: "PVF (Portable Voice Format) Signed 32 bit PCM" (pvf)\n"""
            """00120001: "AVR (Audio Visual Research) Signed 8 bit PCM" (avr)\n"""
            """00120002: "AVR (Audio Visual Research) Signed 16 bit PCM" (avr)\n"""
            """00120005: "AVR (Audio Visual Research) Unsigned 8 bit PCM" (avr)\n"""
            """00130002: "WAVEX (Microsoft) Signed 16 bit PCM" (wav)\n"""
            """00130003: "WAVEX (Microsoft) Signed 24 bit PCM" (wav)\n"""
            """00130004: "WAVEX (Microsoft) Signed 32 bit PCM" (wav)\n"""
            """00130005: "WAVEX (Microsoft) Unsigned 8 bit PCM" (wav)\n"""
            """00130006: "WAVEX (Microsoft) 32 bit float" (wav)\n"""
            """00130007: "WAVEX (Microsoft) 64 bit float" (wav)\n"""
            """00130010: "WAVEX (Microsoft) U-Law" (wav)\n"""
            """00130011: "WAVEX (Microsoft) A-Law" (wav)\n"""
            """00160001: "SD2 (Sound Designer II) Signed 8 bit PCM" (sd2)\n"""
            """00160002: "SD2 (Sound Designer II) Signed 16 bit PCM" (sd2)\n"""
            """00160003: "SD2 (Sound Designer II) Signed 24 bit PCM" (sd2)\n"""
            """00160004: "SD2 (Sound Designer II) Signed 32 bit PCM" (sd2)\n"""
            + (
            """00170001: "FLAC (Free Lossless Audio Codec) Signed 8 bit PCM" (flac)\n"""
            """00170002: "FLAC (Free Lossless Audio Codec) Signed 16 bit PCM" (flac)\n"""
            """00170003: "FLAC (Free Lossless Audio Codec) Signed 24 bit PCM" (flac)\n"""
                if self.version>=v('1.0.18') else "")
            +
            """00180001: "CAF (Apple Core Audio File) Signed 8 bit PCM" (caf)\n"""
            """00180002: "CAF (Apple Core Audio File) Signed 16 bit PCM" (caf)\n"""
            """00180003: "CAF (Apple Core Audio File) Signed 24 bit PCM" (caf)\n"""
            """00180004: "CAF (Apple Core Audio File) Signed 32 bit PCM" (caf)\n"""
            """00180006: "CAF (Apple Core Audio File) 32 bit float" (caf)\n"""
            """00180007: "CAF (Apple Core Audio File) 64 bit float" (caf)\n"""
            """00180010: "CAF (Apple Core Audio File) U-Law" (caf)\n"""
            """00180011: "CAF (Apple Core Audio File) A-Law" (caf)\n"""
            """00180070: "CAF (Apple Core Audio File) 16 bit ALAC" (caf)\n"""
            """00180071: "CAF (Apple Core Audio File) 20 bit ALAC" (caf)\n"""
            """00180072: "CAF (Apple Core Audio File) 24 bit ALAC" (caf)\n"""
            """00180073: "CAF (Apple Core Audio File) 32 bit ALAC" (caf)\n"""
            + (
            """00200060: "OGG (OGG Container format) Vorbis" (oga)\n"""
                if self.version>=v('1.0.18') else "")
            + (
            """00200064: "OGG (OGG Container format) Opus" (oga)\n"""
                if self.version>=v('1.0.29') else "")
            +
            """00210002: "MPC (Akai MPC 2k) Signed 16 bit PCM" (mpc)\n"""
            """00220002: "RF64 (RIFF 64) Signed 16 bit PCM" (rf64)\n"""
            """00220003: "RF64 (RIFF 64) Signed 24 bit PCM" (rf64)\n"""
            """00220004: "RF64 (RIFF 64) Signed 32 bit PCM" (rf64)\n"""
            """00220005: "RF64 (RIFF 64) Unsigned 8 bit PCM" (rf64)\n"""
            """00220006: "RF64 (RIFF 64) 32 bit float" (rf64)\n"""
            """00220007: "RF64 (RIFF 64) 64 bit float" (rf64)\n"""
            """00220010: "RF64 (RIFF 64) U-Law" (rf64)\n"""
            """00220011: "RF64 (RIFF 64) A-Law" (rf64)\n"""
            + (
            """00230080: "MPEG-1/2 Audio MPEG Layer I" (m1a)\n"""
            """00230081: "MPEG-1/2 Audio MPEG Layer II" (m1a)\n"""
            """00230082: "MPEG-1/2 Audio MPEG Layer III" (m1a)\n"""
                if self.version>v('1.0.31') else "")
        )

    def test_format_description_major(self):
        f = wavefile.Format.WAV
        self.assertEqual(f.description, "WAV (Microsoft)")

    def test_format_name_full(self):
        f = wavefile.Format.WAV | wavefile.Format.PCM_16
        self.assertEqual(f.description, "WAV (Microsoft) Signed 16 bit PCM")

    def test_format_name_subtype(self):
        f = wavefile.Format.PCM_16
        self.assertEqual(f.description, "Signed 16 bit PCM")

    def test_format_extension_major(self):
        f = wavefile.Format.WAV
        self.assertEqual(f.extension, 'wav')

    def test_format_extension_full(self):
        f = wavefile.Format.WAV | wavefile.Format.PCM_16
        self.assertEqual(f.extension, 'wav')

    def test_format_extension_subtype(self):
        f = wavefile.Format.PCM_16
        self.assertEqual(f.extension, None)

    def test_format_isSupported_existing(self):
        f = wavefile.Format.WAV | wavefile.Format.PCM_16
        self.assertTrue(f.isSupported())

    def test_format_isSupported_incompatible(self):
        f = wavefile.Format.WAV | wavefile.Format.PCM_S8
        self.assertFalse(f.isSupported())

    def test_info_full(self):
        f = wavefile.Format.WAV | wavefile.Format.PCM_16
        self.assertEqual( f.info(), dict(
            format=0x00010000,
            name="WAV (Microsoft)",
            subtype="Signed 16 bit PCM",
            extension="wav",
        ))

    def test_info_major(self):
        f = wavefile.Format.WAV
        self.assertEqual( f.info(), dict(
            format=0x00010000,
            name="WAV (Microsoft)",
            # no subtype
            extension="wav",
        ))

    def test_info_subtype(self):
        f = wavefile.Format.PCM_16
        self.assertEqual( f.info(), dict(
            # no format
            # no name
            subtype="Signed 16 bit PCM",
            # no extension
        ))

    def test_info_subtype_badone(self):
        f = wavefile.Format(0x29) # Not existing as 2022-01-18
        with self.assertRaises(ValueError) as ctx:
            f.info()
        self.assertEqual(format(ctx.exception),
            "41"
        )

    def test_info_major_badone(self):
        f = wavefile.Format(0x290000) # Not existing as 2022-01-18
        with self.assertRaises(ValueError) as ctx:
            f.info()
        self.assertEqual(format(ctx.exception),
            "2686976"
        )


    def test_format_all__equal_allFormats(self):
        self.assertEqual(
            list(wavefile.Format.all()),
            list(wavefile.allFormats()),
        )

    def test_format_common__equal_commonFormats(self):
        self.assertEqual(
            list(wavefile.Format.common()),
            list(wavefile.commonFormats()),
        )

    def test_format_major__equal_majorFormats(self):
        self.assertEqual(
            list(wavefile.Format.major()),
            list(wavefile.majorFormats()),
        )

    def test_format_subtypes__equal_subtypesFormats(self):
        self.assertEqual(
            list(wavefile.Format.subtypes()),
            list(wavefile.subtypeFormats()),
        )


