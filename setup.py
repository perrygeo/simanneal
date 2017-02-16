#!/usr/bin/env/python
import sys
import os
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESCRIPTION = """`simanneal` is a python implementation of the
[simulated annealing optimization](http://en.wikipedia.org/wiki/Simulated_annealing) technique.

Simulated annealing is used to find a close-to-optimal solution among an
extremely large (but finite) set of potential solutions. It is particularly
useful for [combinatorial optimization](http://en.wikipedia.org/wiki/Combinatorial_optimization)
problems defined by complex objective functions that rely on external data.
"""

setup(name='simanneal',
      version='0.3.1',
      description='Simulated Annealing in Python',
      license='BSD',
      author='Matthew Perry',
      author_email='perrygeo@gmail.com',
      url='https://github.com/perrygeo/simanneal',
      long_description=LONG_DESCRIPTION,
      packages=['simanneal'],
      install_requires=[],
)
