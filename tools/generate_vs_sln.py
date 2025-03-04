import sys
import subprocess
import os
import shutil

import pybind11
import pybind11_extensions
import amulet_nbt
import leveldb


def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")


RootDir = fix_path(os.path.dirname(os.path.dirname(__file__)))


def main():
    platform_args = []
    if sys.platform == "win32":
        platform_args.extend(["-G", "Visual Studio 17 2022"])
        if sys.maxsize > 2**32:
            platform_args.extend(["-A", "x64"])
        else:
            platform_args.extend(["-A", "Win32"])
        platform_args.extend(["-T", "v143"])

    os.chdir(RootDir)
    shutil.rmtree("build/CMakeFiles", ignore_errors=True)

    if subprocess.run(
        [
            "cmake",
            *platform_args,
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-Dpybind11_DIR={fix_path(pybind11.get_cmake_dir())}",
            f"-Dpybind11_extensions_DIR={fix_path(pybind11_extensions.__path__[0])}",
            f"-Damulet_nbt_DIR={fix_path(amulet_nbt.__path__[0])}",
            f"-Dleveldb_mcpe_DIR={fix_path(leveldb.__path__[0])}",
            f"-DCMAKE_INSTALL_PREFIX=install",
            f"-DSRC_INSTALL_DIR=src",
            "-B",
            "build",
        ]
    ).returncode:
        raise RuntimeError("Error configuring amulet_core")


if __name__ == "__main__":
    main()
