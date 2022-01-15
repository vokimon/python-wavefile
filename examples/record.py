#!/usr/bin/env python

### Record example (using pyaudio)

from wavefile import WaveWriter, Format
import numpy as np
import pyaudio, sys

SECONDS = 10
BUFFERSIZE = 512
SAMPLERATE = 48000
NCHANNELS = 2
TITLE = "Some Noise"
ARTIST = "The Artists"
NBUFFERS = int(SECONDS*SAMPLERATE/BUFFERSIZE)

pa = pyaudio.PyAudio()
with WaveWriter('recording.ogg', channels=NCHANNELS, samplerate=SAMPLERATE, format=Format.OGG|Format.VORBIS) as w:

	w.metadata.title = TITLE
	w.metadata.artist = ARTIST

	stream = pa.open(
		format = pyaudio.paFloat32,
		channels = NCHANNELS,
		rate = SAMPLERATE,
		frames_per_buffer = BUFFERSIZE,
		input = True,
	)

	for x in range(NBUFFERS):
		data = stream.read(BUFFERSIZE)
		data = np.fromstring(data, np.float32)
		data = data.reshape(BUFFERSIZE,NCHANNELS)
		w.write(data.transpose())

		sys.stdout.write("."); sys.stdout.flush()

	stream.close()

pa.terminate()

# vim: noet ts=4 sw=4
