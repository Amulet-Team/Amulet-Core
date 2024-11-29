import os
import subprocess
import sys
from pathlib import Path
import pybind11

from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext

import versioneer
import pybind11_extensions
import amulet_nbt
import leveldb


# https://github.com/pybind/cmake_example/blob/master/setup.py
class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


cmdclass: dict[str, type[Command]] = versioneer.get_cmdclass()


class CMakeBuild(cmdclass.get("build_ext", build_ext)):
    def build_extension(self, ext):
        ext_fullpath = Path.cwd() / self.get_ext_fullpath("")
        src_dir = ext_fullpath.parent.resolve()

        platform_args = []
        if sys.platform == "win32":
            platform_args.extend(["-G", "Visual Studio 17 2022"])
            if sys.maxsize > 2**32:
                platform_args.extend(["-A", "x64"])
            else:
                platform_args.extend(["-A", "Win32"])
            platform_args.extend(["-T", "v143"])

        if subprocess.run(
            [
                "cmake",
                *platform_args,
                f"-DPYTHON_EXECUTABLE={sys.executable}",
                f"-Dpybind11_DIR={pybind11.get_cmake_dir().replace(os.sep, '/')}",
                f"-Dpybind11_extensions_DIR={pybind11_extensions.__path__[0].replace(os.sep, '/')}",
                f"-Damulet_nbt_DIR={amulet_nbt.__path__[0].replace(os.sep, '/')}",
                f"-Dleveldb_mcpe_DIR={leveldb.__path__[0].replace(os.sep, '/')}",
                f"-DCMAKE_INSTALL_PREFIX=install",
                f"-DSRC_INSTALL_DIR={src_dir}",
                "-B",
                "build",
            ]
        ).returncode:
            raise RuntimeError("Error configuring amulet_nbt")
        if subprocess.run(
            ["cmake", "--build", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_nbt")
        if subprocess.run(
            ["cmake", "--install", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_nbt")


cmdclass["build_ext"] = CMakeBuild


setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    ext_modules=[CMakeExtension("amulet._amulet")],
)
