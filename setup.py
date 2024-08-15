from setuptools import setup, Extension
import versioneer
import sysconfig
from distutils import ccompiler
import sys
import pybind11
import glob
import os
import amulet_nbt

if (sysconfig.get_config_var("CXX") or ccompiler.get_default_compiler()).split()[
    0
] == "msvc":
    CompileArgs = ["/std:c++20"]
else:
    CompileArgs = ["-std=c++20"]

if sys.platform == "darwin":
    CompileArgs.append("-mmacosx-version-min=10.13")


# TODO: Would it be better to compile a shared library and link against that?


AmuletNBTLib = (
    "amulet_nbt",
    dict(
        sources=glob.glob(
            os.path.join(glob.escape(amulet_nbt.get_source()), "**", "*.cpp"),
            recursive=True,
        ),
        include_dirs=[amulet_nbt.get_include()],
        cflags=CompileArgs,
    ),
)

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    libraries=[AmuletNBTLib],
    ext_modules=[
        Extension(
            name="amulet.__init__",
            sources=glob.glob("src/**/*.cpp", recursive=True),
            include_dirs=[
                pybind11.get_include(),
                amulet_nbt.get_include(),
                "src",
            ],
            libraries=["amulet_nbt"],
            define_macros=[("PYBIND11_DETAILED_ERROR_MESSAGES", None)],
            extra_compile_args=CompileArgs,
        ),
    ]
)
