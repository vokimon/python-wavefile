#!/usr/bin/env python

# Whole file reading and writing. Quite convenient
# for quick scripts is not recommended for large files.
# For long term scripts having efficiency concerns,
# please consider more efficient block by block processing.

import wavefile
import numpy as np

# Lets setup some synthesis audio:

def sinusoid(samples, f, samplerate=44100):
    return np.sin(np.linspace(0, 2*np.pi*f*samples/samplerate, samples))[:,np.newaxis]

def channels(*args):
    return np.hstack(args).T

audio = channels(
    sinusoid(100000,  440),
    sinusoid(100000,  880),
    sinusoid(100000, 1760),
)

# This is how you save it
wavefile.save("sinusoid.wav", audio, 44100)

# And this is how you load it again
loadedsamplerate, loaded = wavefile.load("sinusoid.wav")


print("Loaded audio has shape", loaded.shape)

channel1, channel2, channel3 = loaded




