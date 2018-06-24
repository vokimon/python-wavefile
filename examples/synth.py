#!/usr/bin/env python

### Writting example

from wavefile import WaveWriter, Format
import numpy as np

BUFFERSIZE = 512
NCHANNELS = 2
TITLE = "Some Noise"
ARTIST = "The Artists"

with WaveWriter('synth.ogg',
		channels=NCHANNELS,
		format=Format.OGG|Format.VORBIS,
		) as w :
	w.metadata.title = "Some Noise"
	w.metadata.artist = "The Artists"
	data = np.zeros((NCHANNELS,BUFFERSIZE), np.float32)
	for x in range(256) :
		# First channel: Saw wave sweep
		data[0,:] = (x*np.arange(BUFFERSIZE, dtype=np.float32)%BUFFERSIZE/BUFFERSIZE)
		# Second channel: Modulated square wave
		data[1,BUFFERSIZE-x*2:] =  1
		data[1,:BUFFERSIZE-x*2] = -1
		# Write it down
		w.write(data)

