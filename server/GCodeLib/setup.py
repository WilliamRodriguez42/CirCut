from distutils.core import setup
from Cython.Build import cythonize

NB_COMPILE_JOBS = 12

setup(
	ext_modules = cythonize("GCode.pyx", annotate=True)
)