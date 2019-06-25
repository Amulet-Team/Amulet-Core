import sys
import os

from setuptools import setup, find_packages

#import version

import numpy

include_dirs = [numpy.get_include()]

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

packs = find_packages("src", include=['amulet*',])

print(packs)

setup(
    name="amulet",
    version="0.0.0",
    packages=packs,
    package_dir={'':"src"},
    include_dirs=include_dirs,
    include_package_data=True
)