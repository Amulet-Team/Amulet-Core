import sys
import os

from setuptools import setup, find_packages

import numpy

include_dirs = [numpy.get_include()]

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from amulet import version

packs = find_packages(
    "src", include=["amulet*"], exclude=["*.command_line", "*.command_line.*"]
)

requirements_fp = open("./requirements.txt")

required_packages = requirements_fp.readlines()

requirements_fp.close()

setup(
    name="amulet",
    version=".".join(map(str, version.VERSION_NUMBER)),
    packages=packs,
    package_dir={"": "src"},
    include_dirs=include_dirs,
    include_package_data=True,
    install_requires=required_packages,
)
