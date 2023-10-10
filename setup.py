#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

readme = """
Pythonic libsndfile wrapper to read and write audio files.

Features
--------

- Writer and reader objects are context managers
- Format, channels, length, sample rate... are accessed as properties as well as text strings
- Real multichannel (not just mono/stereo)
- All libsndfile formats supported, floating point encodings by default
- Numpy based interface
- Generators for block by block reading
- Reading reuses the same data block to avoid many data allocations
- Shortened constant names for formats (Using scopes instead of prefixes)
- Matlab-like whole-file interface (not recommended in production code but quite convenient for quick scripting)
- Transparent UTF-8 handling for filenames and text strings
- No module compilation required (wraps the dll using ctypes)
- Works both for Python3 >= 3.8

You can find the latest version at:
https://github.com/vokimon/python-wavefile
"""

setup(
    name = "wavefile",
    version = '1.6.2',
    description = "Pythonic wave file reader and writer",
    author = "David Garcia Garzon",
    author_email = "voki@canvoki.net",
    url = 'https://github.com/vokimon/python-wavefile',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    license = 'GNU General Public License v3 or later (GPLv3+)',
    packages=find_packages(exclude=['*_test']),
    install_requires=[
        'numpy',
    ],
    test_suite='test',
    tests_require='PyAudio',
    extras_require={
        "examples": "PyAudio"
    },
    classifiers = [
        'Programming Language :: Python',
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

