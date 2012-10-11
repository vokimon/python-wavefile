#!/usr/bin/python
from distutils.core import setup, Extension

setup(
	name = "wavefile",
	version = "1.0",
	description = "Pythonic wave file reader and writer",
	author = "David Garcia Garzon",
	author_email = "voki@canvoki.net",
	url = 'https://github.com/vokimon/python-wavefile',
	packages=[
		'wavefile',
		],
	)

