#!/bin/bash

python2 test/wavefileTest.py && 
python3 test/wavefileTest.py && 
echo SUCCESS!!!  ||
echo FAILED

