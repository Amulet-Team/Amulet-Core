from setuptools import setup, find_packages, Extension
import versioneer
import numpy
import sysconfig
from distutils import ccompiler
import sys
import pybind11
import glob
import os
import re

if (sysconfig.get_config_var("CXX") or ccompiler.get_default_compiler()).split()[
    0
] == "msvc":
    CompileArgs = ["/std:c++20"]
else:
    CompileArgs = ["-std=c++20"]

if sys.platform == "darwin":
    CompileArgs.append("-mmacosx-version-min=10.13")


# TODO: Would it be better to compile a shared library and link against that?
def find_pybind_extensions(src_dir: str) -> list[Extension]:
    extensions = list[Extension]()
    for cpp_path in glob.glob(os.path.join(glob.escape(src_dir), "**", "*.cpp"), recursive=True):
        with open(cpp_path) as f:
            src = f.read()
            match = re.search(r"PYBIND11_MODULE\((?P<module>[a-zA-Z0-9]+), m\)", src)
            if match:
                module = match.group("module")
                assert os.path.splitext(os.path.basename(cpp_path))[0] == module, f"module name must match file name. {cpp_path}"
                package = os.path.relpath(os.path.dirname(cpp_path), src_dir).replace(os.sep, ".")
                if package:
                    module = f"{package}.{module}"
                extra_sources = [
                    os.path.join(src_dir, match.group("src")) for match in re.finditer(r"//include (?P<src>[a-zA-Z0-9/]+\.cpp)", src)
                ]
                extensions.append(
                    Extension(
                        name=module,
                        sources=[cpp_path, *extra_sources],
                        extra_compile_args=CompileArgs
                    )
                )

    return extensions


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    include_dirs=["src", numpy.get_include(), pybind11.get_include()],
    packages=find_packages(),
    ext_modules=find_pybind_extensions("src"),
)
