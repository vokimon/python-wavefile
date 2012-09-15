#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

import sys

require = ['numpy']

if sys.version_info < (2, 5):
  require.append('ctypes')


setup(name='libsndfilectypes',
      version='1.0',
      description='A wrapper around libsndfile using ctypes',
      author='Timothe Faudot',
      #author_email='',
      url='http://code.google.com/p/pyzic/wiki/LibSndFilectypes',
      download_url='http://code.google.com/p/pyzic/downloads/list',
      packages=['libsndfilectypes'],
      data_files = [
                    ("./Lib/site-packages/libsndfilectypes", ["libsndfilectypes/libsndfile-1.dll"]),
                ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Scientific/Engineering',
          ],
      requires=require
     )
