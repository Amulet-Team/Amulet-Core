import os
import subprocess
import sys
from pathlib import Path
import platform
import datetime
from tempfile import TemporaryDirectory

from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext

from packaging.version import Version

import versioneer

import requirements

if (
    os.environ.get("AMULET_FREEZE_COMPILER", None)
    and sys.platform == "darwin"
    and platform.machine() != "arm64"
):
    raise Exception("The MacOS frozen build must be created on arm64")


def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")


cmdclass: dict[str, type[Command]] = versioneer.get_cmdclass()


class CMakeBuild(cmdclass.get("build_ext", build_ext)):
    def build_extension(self, ext):
        import pybind11
        import amulet.pybind11_extensions
        import amulet.io
        import amulet.nbt

        ext_dir = (
            (Path.cwd() / self.get_ext_fullpath("")).parent.resolve()
            / "amulet"
            / "core"
        )
        core_src_dir = (
            Path.cwd() / "src" / "amulet" / "core" if self.editable_mode else ext_dir
        )

        platform_args = []
        if sys.platform == "win32":
            platform_args.extend(["-G", "Visual Studio 17 2022"])
            if sys.maxsize > 2**32:
                platform_args.extend(["-A", "x64"])
            else:
                platform_args.extend(["-A", "Win32"])
            platform_args.extend(["-T", "v143"])
        elif sys.platform == "darwin":
            if platform.machine() == "arm64":
                platform_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64")

        if subprocess.run(["cmake", "--version"]).returncode:
            raise RuntimeError("Could not find cmake")
        with TemporaryDirectory() as tempdir:
            if subprocess.run(
                [
                    "cmake",
                    *platform_args,
                    f"-DPYTHON_EXECUTABLE={sys.executable}",
                    f"-Dpybind11_DIR={fix_path(pybind11.get_cmake_dir())}",
                    f"-Damulet_pybind11_extensions_DIR={fix_path(amulet.pybind11_extensions.__path__[0])}",
                    f"-Damulet_io_DIR={fix_path(amulet.io.__path__[0])}",
                    f"-Damulet_nbt_DIR={fix_path(amulet.nbt.__path__[0])}",
                    f"-Damulet_core_DIR={fix_path(core_src_dir)}",
                    f"-DAMULET_CORE_EXT_DIR={fix_path(ext_dir)}",
                    f"-DCMAKE_INSTALL_PREFIX=install",
                    "-B",
                    tempdir,
                ]
            ).returncode:
                raise RuntimeError("Error configuring amulet-core")
            if subprocess.run(
                ["cmake", "--build", tempdir, "--config", "Release"]
            ).returncode:
                raise RuntimeError("Error building amulet-core")
            if subprocess.run(
                ["cmake", "--install", tempdir, "--config", "Release"]
            ).returncode:
                raise RuntimeError("Error installing amulet-core")


cmdclass["build_ext"] = CMakeBuild


def _get_version() -> str:
    version_str: str = versioneer.get_version()

    if os.environ.get("AMULET_FREEZE_COMPILER", None):
        date_format = "%y%m%d%H%M%S"
        try:
            with open("build/timestamp.txt", "r") as f:
                timestamp = datetime.datetime.strptime(f.read(), date_format)
        except Exception:
            timestamp = datetime.datetime(1, 1, 1)
        if datetime.timedelta(minutes=10) < datetime.datetime.now() - timestamp:
            timestamp = datetime.datetime.now()
            os.makedirs("build", exist_ok=True)
            with open("build/timestamp.txt", "w") as f:
                f.write(timestamp.strftime(date_format))

        version = Version(version_str)
        epoch = f"{version.epoch}!" if version.epoch else ""
        release = ".".join(map(str, version.release))
        pre = "".join(map(str, version.pre)) if version.is_prerelease else ""
        post = f".post{timestamp.strftime(date_format)}"
        local = f"+{version.local}" if version.local else ""
        version_str = f"{epoch}{release}{pre}{post}{local}"

    return version_str


setup(
    version=_get_version(),
    cmdclass=cmdclass,
    ext_modules=[Extension("amulet.core._amulet_core", [])]
    * (not os.environ.get("AMULET_SKIP_COMPILE", None)),
    install_requires=requirements.get_runtime_dependencies(),
)
