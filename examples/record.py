#!/usr/bin/env python

from wavefile import WaveWriter, Format
import numpy as np
import pyaudio, sys

SECONDS = 10
BUFFERSIZE = 512
SAMPLERATE = 48000
NCHANNELS = 2
TITLE = "Some Noise"
ARTIST = "The Artists"

pa = pyaudio.PyAudio()
stream = pa.open(
	format = pyaudio.paFloat32,
	channels = NCHANNELS,
	rate = SAMPLERATE,
	frames_per_buffer = BUFFERSIZE,
	input = True,
)
with WaveWriter('recording.ogg', channels=NCHANNELS, samplerate=SAMPLERATE, format=Format.OGG|Format.VORBIS) as w :
	w.metadata.title = TITLE
	w.metadata.artist = ARTIST

	nbuffers = int(SECONDS*SAMPLERATE/BUFFERSIZE)
	for x in range(nbuffers) :
		data = np.fromstring(data, np.float32)
		data = data.reshape(BUFFERSIZE,NCHANNELS)
		w.write(data.transpose())

stream.close()
pa.terminate()

