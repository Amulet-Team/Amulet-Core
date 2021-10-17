from typing import List
from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob
import pkg_resources
import versioneer
import numpy


PROJECT_PREFIX = "amulet"


def load_requirements(path: str) -> List[str]:
    requirements = []
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if line and line[0] != "#":
                if line.startswith("-r "):
                    requirements += load_requirements(line[3:])
                else:
                    requirements.append(str(pkg_resources.Requirement.parse(line)))
    return requirements


required_packages = load_requirements("requirements.txt")

ext = []
pyx_path = f"{PROJECT_PREFIX}/**/*.pyx"
if next(glob.iglob(pyx_path, recursive=True), None):
    # This throws an error if it does not match any files
    ext += cythonize(
        pyx_path,
        language_level=3,
        annotate=True,
    )

setup(
    version=versioneer.get_version(),
    install_requires=required_packages,
    packages=find_packages(),
    include_package_data=True,
    cmdclass=versioneer.get_cmdclass(),
    ext_modules=ext,
    include_dirs=[numpy.get_include()],
)
