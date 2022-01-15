# Pending tasks

## Wish list

- Smart format chooser
    - Use file name extension to deduce main format, if not specified
    - Use main format to deduce subformat, if not specified
- Format enumeration
    - Separate Formats scope into Formats, Subformats and Endianess
    - Expose format description strings at the API
- Exposing sndfile command API
- `mv test/wavefileTest.py wavefile/wavefile_test.py`
- pathlib support


## Test Coverage

- [ ] list of available strings (dir)
- [ ] write in format float32
- [ ] write in format int16
- [ ] write in format int32
- [ ] write seek
- [ ] reader bitrate property
- [ ] `read_iter` with a given buffer proper size
- [ ] `read_iter` with a given buffer bad size
- [ ] read in format float64
- [ ] read in format int16
- [ ] read in format int32
- [x] `loadWave` longer than 512
- [x] `saveWave` longer than 512


