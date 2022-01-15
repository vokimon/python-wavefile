#!/usr/bin/env python

### Playback example (using pyaudio)

import pyaudio, sys
from wavefile import WaveReader

BUFFERSIZE = 512

pa = pyaudio.PyAudio()
with WaveReader(sys.argv[1]) as r:

	# Print info
	print("Title: {}".format(r.metadata.title))
	print("Artist: {}".format(r.metadata.artist))
	print("Channels: {}".format(r.channels))
	print("Format: 0x{:x}".format(r.format))
	print("Sample Rate: {}".format(r.samplerate))

	# open pyaudio stream
	stream = pa.open(
		format = pyaudio.paFloat32,
		channels = r.channels,
		rate = r.samplerate,
		frames_per_buffer = BUFFERSIZE,
		output = True,
		)

	# iterator interface (reuses one array)
	# beware of the frame size, not always BUFFERSIZE, but BUFFERSIZE at least
	for frame in r.read_iter(size=BUFFERSIZE):
		stream.write(frame.flatten(), frame.shape[1])

		sys.stdout.write("."); sys.stdout.flush()

	stream.close()

pa.terminate()

# vim: noet ts=4 sw=4
