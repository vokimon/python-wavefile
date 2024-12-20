# Version history

## 1.6.3 2024-12-04

- Migrated to pyproject.toml
- Using `packaging` instead deprecated `pkg_resources`
- Dropped travis ci support

## 1.6.2 2023-10-10

- Temptative support for freebsd

## 1.6.1 2023-10-10

- Build fixes

## 1.6.0 2023-10-10

- Dropped Python<3.8
- Incorporated enums for all the new formats supported by sndfile up to 1.0.31
  - Containers: mp3, opus
  - Encodings: NMS ADPCM, MPEGx Layerx
- Experimental: Api to enumerate, check and describe formats
- Added `Writer.seek` method
- Added example for whole-file load/save
- wavefile.save accepts 1D mono data for convenience
- PR#23 Incorrect implementation of saveWave method. Fixes #20. Thanks Sravan Patibandla (pbskumar)!
  - This will render some client code failing. But I applied it since
    it is coherent to have the same layout on saving and loading.
    Client code should now transpose the numpy matrix when saving with wavefile.save()

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



