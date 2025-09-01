import subprocess
import sys
import shutil
import os

import pybind11
import amulet.pybind11_extensions
import amulet.io
import amulet.test_utils
import amulet.utils
import amulet.nbt
import amulet.core


def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")


RootDir = os.path.dirname(os.path.dirname(__file__))
TestsDir = os.path.join(RootDir, "tests")


def main() -> None:
    platform_args = []
    if sys.platform == "win32":
        platform_args.extend(["-G", "Visual Studio 17 2022"])
        if sys.maxsize > 2**32:
            platform_args.extend(["-A", "x64"])
        else:
            platform_args.extend(["-A", "Win32"])
        platform_args.extend(["-T", "v143"])

    os.chdir(TestsDir)
    shutil.rmtree(os.path.join(TestsDir, "build", "CMakeFiles"), ignore_errors=True)

    if subprocess.run(["cmake", "--version"]).returncode:
        raise RuntimeError("Could not find cmake")
    if subprocess.run(
        [
            "cmake",
            *platform_args,
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-Dpybind11_DIR={fix_path(pybind11.get_cmake_dir())}",
            f"-Damulet_pybind11_extensions_DIR={fix_path(amulet.pybind11_extensions.__path__[0])}",
            f"-Damulet_io_DIR={fix_path(amulet.io.__path__[0])}",
            f"-Damulet_test_utils_DIR={fix_path(amulet.test_utils.__path__[0])}",
            f"-Damulet_utils_DIR={fix_path(amulet.utils.__path__[0])}",
            f"-Damulet_nbt_DIR={fix_path(amulet.nbt.__path__[0])}",
            f"-Damulet_core_DIR={fix_path(amulet.core.__path__[0])}",
            f"-DCMAKE_INSTALL_PREFIX=install",
            "-B",
            "build",
        ]
    ).returncode:
        raise RuntimeError("Error configuring test-amulet-core")
    if subprocess.run(
        ["cmake", "--build", "build", "--config", "RelWithDebInfo"]
    ).returncode:
        raise RuntimeError("Error building test-amulet-core")
    if subprocess.run(
        ["cmake", "--install", "build", "--config", "RelWithDebInfo"]
    ).returncode:
        raise RuntimeError("Error installing test-amulet-core")


if __name__ == "__main__":
    main()
