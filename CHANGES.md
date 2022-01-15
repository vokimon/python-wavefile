# Version history

## Unreleased

- Incorporated all the new formats from sndfile 1.0.31
	- Containers: mp3, opus
	- Encodings: NMS ADPCM, MPEG
- Added `Writer.seek` method

## 1.5

- MacOSX support
- Fix: Genere string accesses the proper id (closes #18)
- PyAudio an optional dependency (just used by examples)
- New stuff from libsndfile 1.0.26 included

## 1.4

- Works with Python 3.0 to 3.2, patch from j3ffhubb
- Works on cygwin, patch from j3ffhubb
- Added readf/writef functions, patch from Tim Langlois
- Ctypes backend clean up, removing lot of legacy code
- Using libsndfile soname (runtime packages) instead of link name (development)
- Tests can be run from setup
- Travis support

## 1.3

- Fix: Whole-file interface works again, regression tests added
- Added a helper script to run tests in Py2 and Py3
- Using utf8 for tags

## 1.2

- Seek implemented
- Removed some error handling that aborted program execution
- Removed alien reference code in 'other' folder

## 1.1

- Python 3 support
- Support for unicode filenames

## 1.0

- First version



