#!/usr/bin/env/python
import sys
import os
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESCRIPTION = """simanneal is a python implementation of the 
simulated annealing discrete optimization 
teechnique. It is useful for findy close-to-optimal solutions amongst 
extremely large (but finite) set of potential configurations.
"""

setup(name='simanneal',
      version='0.1',
      description='Simulated Annealing in Python',
      license='BSD',
      author='Matthew Perry',
      author_email='perrygeo@gmail.com',
      url='https://github.com/perrygeo/simanneal',
      long_description=LONG_DESCRIPTION,
      packages=['simanneal'],
      install_requires=[],
)
