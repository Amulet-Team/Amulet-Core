import subprocess
import sys
import shutil
import os

import pybind11
import pybind11_extensions

import amulet_nbt
import leveldb
import amulet


def main():
    os.chdir(os.path.dirname(__file__))

    if os.path.isdir("build/CMakeFiles"):
        shutil.rmtree("build/CMakeFiles")

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
            f"-Damulet_core_DIR={amulet.__path__[0].replace(os.sep, '/')}",
            f"-DCMAKE_INSTALL_PREFIX={os.path.join(os.path.dirname(__file__), 'test_amulet').replace(os.sep, '/')}",
            "-B",
            "build",
        ]
    ).returncode:
        raise RuntimeError("Error configuring test_amulet")
    if subprocess.run(
        ["cmake", "--build", "build", "--config", "RelWithDebInfo"]
    ).returncode:
        raise RuntimeError("Error installing test_amulet")
    if subprocess.run(
        ["cmake", "--install", "build", "--config", "RelWithDebInfo"]
    ).returncode:
        raise RuntimeError("Error installing test_amulet")


if __name__ == "__main__":
    main()
