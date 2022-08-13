from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob
import versioneer
import numpy

ext = []
pyx_path = f"amulet/**/*.pyx"
if next(glob.iglob(pyx_path, recursive=True), None):
    # This throws an error if it does not match any files
    ext += cythonize(
        pyx_path,
        language_level=3,
        annotate=True,
    )

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    include_dirs=[numpy.get_include()],
    packages=find_packages(),
    ext_modules=ext,
)
