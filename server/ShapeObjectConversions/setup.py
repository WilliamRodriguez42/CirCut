from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np

NB_COMPILE_JOBS = 12

extensions = [
	Extension('gtso', ['gtso.pyx'], include_dirs=[np.get_include()]),
	Extension('etso', ['etso.pyx'], include_dirs=[np.get_include()])
]

setup(
	ext_modules = cythonize(extensions, annotate=True, language_level="3")
)