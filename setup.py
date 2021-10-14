from typing import List
from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob
import shutil
import versioneer
import numpy

# there were issues with other builds carrying over their cache
for d in glob.glob("*.egg-info"):
    shutil.rmtree(d)


def load_requirements(path: str) -> List[str]:
    requirements = []
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("git+") or line.startswith("https:"):
                continue
            elif line.startswith("-r "):
                requirements += load_requirements(line[3:])
            else:
                requirements.append(line)
    return requirements


required_packages = load_requirements("./requirements.txt")

ext = []
if next(glob.iglob("amulet/**/*.pyx", recursive=True), None):
    # This throws an error if it does not match any files
    ext += cythonize(
        "amulet/**/*.pyx",
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
