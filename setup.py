#!/usr/bin/python
from distutils.core import setup

readme = """
'wavefile' python module to read and write audio files.
It is a pythonic wrapper to the sndfile library featuring:
* Attribute access to format, channels, length, sample rate...
* Numpy interface using in place arrays (optimal for block processing)
* Works as context manager
* Different objects for reading and writing (no modes, consistent interface)
* Shortened constants accessing for formats and the like
* Matlab like whole file interface (not recommended but convenient)

You can find the latest version at:
https://github.com/vokimon/python-wavefile
"""

setup(
	name = "wavefile",
	version = "1.2~git",
	description = "Pythonic wave file reader and writer",
	author = "David Garcia Garzon",
	author_email = "voki@canvoki.net",
	url = 'https://github.com/vokimon/python-wavefile',
	long_description = readme,
	license = 'GNU General Public License v3 or later (GPLv3+)',
	packages=[
		'wavefile',
		],
	scripts=[
#		'audio.py',
		],
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Multimedia',
		'Topic :: Scientific/Engineering',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: OS Independent',
	],
	)

