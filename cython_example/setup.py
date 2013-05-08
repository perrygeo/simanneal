from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

ext = Extension(
    "cy_anneal", ["cy_anneal.pyx"],
    include_dirs = [numpy.get_include()],
    # adding openmp arguments for openmp variant (not required normally)
    #extra_compile_args=['-fopenmp'],
    #extra_link_args=['-fopenmp']
)

setup(
    ext_modules=[ext],
    cmdclass = {'build_ext': build_ext}
)

# python setup_cython.py build_ext --inplace

