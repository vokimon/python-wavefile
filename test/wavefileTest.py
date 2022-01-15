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

from wavefile import *
import unittest
import numpy as np
from numpy.testing import assert_equal as np_assert_equal, assert_almost_equal as np_assert_almost_equal

class LibSndfileTest(unittest.TestCase):

	def setUp(self):
		self.filestoremove = []
		self.sfversion = wavefile._lib.sf_version_string().decode()

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
		return np.sin( np.linspace(0, 2*np.pi*f*samples/samplerate, samples))[:,np.newaxis]

	def counter(self, samples=400):
		return np.arange(samples)[:,np.newaxis].T*1.0

	def channels(self, *args):
		return np.hstack(args).T

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
		if self.sfversion != 'libsndfile-1.0.25':
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
		if self.sfversion != 'libsndfile-1.0.25':
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
			pos = r.seek(0, Seek.SET)
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

	def test_save(self):
		samplerate = 44100
		data = self.fourSinusoids(samples=400)
		wavefile.save("file.wav", data, samplerate=samplerate)
		readsamplerate, readdata = wavefile.load("file.wav")
		np_assert_almost_equal(readdata, data, decimal=7)
		self.assertEqual(readsamplerate, samplerate)

	def test_save_slice(self):
		samplerate = 44100
		data = self.fourSinusoids(samples=400)
		data = np.ascontiguousarray(data)
		wavefile.save("file.wav", data[::2], samplerate=samplerate)
		readsamplerate, readdata = wavefile.load("file.wav")
		np_assert_almost_equal(readdata, data[::2], decimal=7)
		self.assertEqual(readsamplerate, samplerate)

	def test_save_asCOrder(self):
		samplerate = 44100
		data = self.fourSinusoids(samples=400)
		data = np.ascontiguousarray(data)
		wavefile.save("file.wav", data, samplerate=samplerate)
		readsamplerate, readdata = wavefile.load("file.wav")
		np_assert_almost_equal(readdata, data, decimal=7)
		self.assertEqual(readsamplerate, samplerate)


if __name__ == '__main__':
	import sys
	Runner = unittest.TextTestRunner
	from colour_runner.runner import ColourTextTestRunner as Runner
	sys.exit(unittest.main(), testRunner=Runner())



