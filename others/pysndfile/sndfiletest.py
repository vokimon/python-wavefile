#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import sndfile
import os
import numpy

class sndfileTests(unittest.TestCase) :	
	def setUp(self) :
		"Set up data for test"

	def tearDown(self) :
		"Clean up test generated changes"
		for filename in [
				"test.wav",
				"test.au",
				"test.aiff"
				] :
			if not os.access(filename, os.R_OK) : continue
			os.remove(filename)


	def test_readFile_whenDoesNotExist(self) :
		try :
			sndfile.sndfile("notexisting.wav","r")
			self.fail("Should have thrown an exception")
		except sndfile.IOException, e :
			self.assertEqual(("System error : No such file or directory.",), e.args)

	def test_readFile_whenMalformed(self) :
		waveoutput = open("test.wav", "w")
		print >> waveoutput, "This is not a wav"
		waveoutput.close()
		try :
			sndfile.sndfile("test.wav","r")
			self.fail("Should have thrown an exception")
		except sndfile.IOException, e :
			self.assertEqual(("File contains data in an unknown format.",), e.args)

	# DGG: If constructor does not complain, try using sf_format_check first
	# DGG: sndfile.WAV and so on, should be defined, like IsInput in pyjack

	def test_writeFile_closing(self) :
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.close()
		self.assertEqual(True, os.access("test.wav", os.R_OK))

	def _test_writeFile_withBadParameters(self) :
		try :
			wavoutput = sndfile.sndfile("test.wav","w", format=sndfile.WAV|sndfile.VORBIS )
			self.fail("Should have thrown an exception")
		except sndfile.UnsupportedFormatException, e :
			self.assertEqual("TODO: Lo que devuelva sf_strerror", e.args)

	def test_headerReadAndWrite_byDefault(self) :
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav","r")
		self.assertEqual(sndfile.WAV | sndfile.PCM16, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_settingChannels(self) :
		wavoutput = sndfile.sndfile("test.wav","w", channels=2)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav","r")
		self.assertEqual(sndfile.WAV| sndfile.PCM16, wavinput.getFormat())
		self.assertEqual(2, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_settingSampleRate(self) :
		wavoutput = sndfile.sndfile("test.wav","w", samplerate=22050)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav","r")
		self.assertEqual(sndfile.WAV | sndfile.PCM16, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(22050, wavinput.getSampleRate())

	def test_headerReadAndWrite_settingFormat(self) :
		wavoutput = sndfile.sndfile("test.wav","w", format= sndfile.WAV | sndfile.PCM24)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav","r")
		self.assertEqual(sndfile.WAV | sndfile.PCM24, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_settingEverything(self) :
		wavoutput = sndfile.sndfile("test.wav","w", format= sndfile.WAV | sndfile.PCM24, channels = 2, samplerate = 22050)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav","r")
		self.assertEqual(sndfile.WAV | sndfile.PCM24, wavinput.getFormat())
		self.assertEqual(2, wavinput.getChannels())
		self.assertEqual(22050, wavinput.getSampleRate())

	def test_Metadata_settingArtist(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("artist", "Testing the Artist")
		self.assertEqual("Testing the Artist", wavoutput.getString("artist"))
		wavoutput.close()

	def test_Metadata_settingTitle(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("title", "Testing the Title")
		self.assertEqual("Testing the Title", wavoutput.getString("title"))
		wavoutput.close()

	def test_Metadata_settingDate(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("date", "15-04-2010")
		self.assertEqual("15-04-2010", wavoutput.getString("date"))
		wavoutput.close()

	def test_Metadata_settingComment(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("comment", "Adding a comment")
		self.assertEqual("Adding a comment", wavoutput.getString("comment"))
		wavoutput.close()

	def test_Metadata_settingCopyright(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("copyright", "Testing the copyright")
		self.assertEqual("Testing the copyright", wavoutput.getString("copyright"))
		wavoutput.close()

	def test_Metadata_settingSoftware(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		wavoutput.setString("software", "Python/C API")
		self.assertEqual("Python/C API (libsndfile-1.0.20)", wavoutput.getString("software"))
		wavoutput.close()

	def test_Metadata_settingTagNotSupported(self):
		wavoutput = sndfile.sndfile("test.wav","w")
		try :
			wavoutput.setString("TagNotSupported", "Trying to throw an exception")
			self.fail("Should have thrown an exception")
		except sndfile.TagNotSupported, e :
			self.assertEqual(("setString error : Tag not supported by sndfile.",), e.args)
			wavoutput.close()

	def test_headerReadAndWrite_settingAIFFformat(self) :
		wavoutput = sndfile.sndfile("test.aiff","w", format= sndfile.AIFF | sndfile.PCM32)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.aiff","r")
		self.assertEqual(sndfile.AIFF | sndfile.PCM32, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_settingAUformat(self) :
		wavoutput = sndfile.sndfile("test.au","w", format= sndfile.AU | sndfile.FLOAT)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.au","r")
		self.assertEqual(sndfile.AU | sndfile.FLOAT, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_byDefaultChangingExtension(self) :
		wavoutput = sndfile.sndfile("test.aiff","w")
		wavoutput.close()
		wavinput = sndfile.sndfile("test.aiff","r")
		self.assertEqual(sndfile.AIFF | sndfile.PCM16, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	def test_headerReadAndWrite_byDefaultChangingExtensionToAU(self) :
		wavoutput = sndfile.sndfile("test.au","w")
		wavoutput.close()
		wavinput = sndfile.sndfile("test.au","r")
		self.assertEqual(sndfile.AU | sndfile.PCM16, wavinput.getFormat())
		self.assertEqual(1, wavinput.getChannels())
		self.assertEqual(44100, wavinput.getSampleRate())

	# TODO: Specifying an extension not matching the format
	# TODO: Ni format ni extension reconocida

	def test_readWriteToOneChannel(self):
		wavoutput = sndfile.sndfile("test.wav", "w")
		seconds = 10
		wav = numpy.ones((1, 44100 * seconds))
		wav[0,:]*=.6
		wavoutput.write(wav)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav", "r")
		result = numpy.zeros((1, 44100 * seconds))
		self.assertEqual(1 * 44100 * seconds , wavinput.read(result)) #Number of items: CHANNELS * SAMPLERATE * SECONDS
		self.assertEqual(wav.all() , result.all())
		# Issues
		# pot not omplir el buffer: sndfile suporta aquest cas, simplement retorna el numero de frames que ha escrit al buffer
		# llegir mes d'un buffer
		# buffer creat per omplir, canals incorrectes
		# buffer creat per dump, canals incorrectes
	def test_readWriteTwoChannels(self):
		wavoutput = sndfile.sndfile("test.wav", "w", channels=2)
		seconds = 60
		wav = numpy.ones((2, 44100 * seconds))
		wav[0,:]*=.6
		wav[1,:]*=.3
		wavoutput.write(wav)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav", "r")
		result = numpy.zeros((2, 44100 * seconds))
		self.assertEqual(2 * 44100 * seconds , wavinput.read(result))
		self.assertEqual(wav.all() , result.all())

	def test_writeReadGetFrames(self):
		wavoutput = sndfile.sndfile("test.wav", "w", channels=2)
		seconds = 60
		frames =  wavoutput.getSampleRate() * seconds
		wav = numpy.ones((wavoutput.getChannels(), frames))
		wav[0,:]*=.6
		wav[1,:]*=.3
		wavoutput.write(wav)
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav", "r")
		self.assertEqual(frames , wavinput.getFrames())

	def test_writeReadFourChannelsCreatingBufferWithFileInfo(self):
		channels = 4
		wavoutput = sndfile.sndfile("test.wav", "w", channels=channels)
		seconds = 60
		frames =  wavoutput.getSampleRate() * seconds
		wav = numpy.ones((channels, frames))
		wav[0,:]*=.8
		wav[1,:]*=.6
		wav[1,:]*=.4
		wav[1,:]*=.2
		self.assertEqual(channels * frames , wavoutput.write(wav))
		wavoutput.close()
		wavinput = sndfile.sndfile("test.wav", "r")
		result = numpy.zeros((wavinput.getChannels(), wavinput.getFrames())) #With this, we make sure that the buffer will hold all the data
		self.assertEqual(channels * frames, wavinput.read(result))
		self.assertEqual(wav.all() , result.all())

	# DGG: Afegeix els formats que hi ha
	# DGG: Later test the previous functionality but with dictionary interface: __getitem__, __setitem__...
	# DGG: Later test writting and reading a data block as floats (numpy), to check the interleaving, just write a sequence
	# DGG: Test what happens when writing a numpy array does not match the channels
	# DGG: Then, if you want to support many data formats, and figure out how, try it (the important ones are floats, anyway)
	# DGG: Then test a couple of convenience functions to write 
	#	data, format, samplerate = sndfile.waveread(filename)
	#	sndfile.wavewrite(filename, data, format=..., samplerate=...)

if __name__ == "__main__" :
	unittest.main()


