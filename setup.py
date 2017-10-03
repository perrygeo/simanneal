#!/usr/bin/env/python
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

# Parse the version from the fiona module.
with open('simanneal/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

setup(
    name='simanneal',
    version=version,
    description='Simulated Annealing in Python',
    license='ISC',
    author='Matthew Perry',
    author_email='perrygeo@gmail.com',
    url='https://github.com/perrygeo/simanneal',
    long_description=LONG_DESCRIPTION,
    packages=['simanneal', 'simanneal.tests'],
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],)
