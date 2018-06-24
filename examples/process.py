#!/usr/bin/env python

### Processing example

import sys
from wavefile import WaveReader, WaveWriter

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

# vim: noet ts=4 sw=4
