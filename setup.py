import os
import subprocess
import sys
from pathlib import Path
import re
import requirements

from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext
from packaging.version import Version

import versioneer

def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")

dependencies = requirements.get_fixed_runtime_dependencies()
setup_args = {}

def add_cpp_dependency(lib_name: str, version_str: str) -> None:
    version = Version(version_str)
    if version.is_prerelease:
        # Breaking API changes can be made between pre-release versions. Pin to this exact release.
        dependencies.append(f"{lib_name}=={version_str}")
    else:
        # Major - breaking API change. Dependents must be updated and recompiled.
        major = version.major
        # Minor - backwards compatible API change. Dependents must be recompiled.
        minor = version.minor
        # Patch - API unchanged. Dependents must be recompiled.
        patch = version.micro
        # Fix - API unchanged. Dependents do not need to be recompiled.
        dependencies.append(f"{lib_name}~={major}.{minor}.{patch}.0")

def add_default_requirements():
    dependencies.append(
        f"amulet-compiler-version{requirements.AMULET_COMPILER_VERSION_REQUIREMENT}"
    )
    dependencies.append(f"amulet_nbt{requirements.AMULET_NBT_REQUIREMENT}")

if os.environ.get("AMULET_FREEZE_COMPILER", None):
    try:
        import amulet_compiler_version
        import amulet.nbt
    except ImportError:
        add_default_requirements()
    else:
        dependencies.append(
            f"amulet-compiler-version=={amulet_compiler_version.__version__}"
        )

        def add_dependency(lib_name: str, version_str: str) -> None:
            version = Version(version_str)
            if version.is_prerelease:
                # Breaking ABI changes can be made between pre-release versions.
                # Pin to this exact release.
                dependencies.append(f"{lib_name}=={version_str}")
            else:
                # Breaking ABI changes can be made in major and minor changes.
                # Require the same major and minor version.
                match = re.fullmatch(
                    r"(?P<major>\d+)(\.(?P<minor>\d+)(\.(?P<patch>\d+))?)?", version_str
                )
                if match is None:
                    raise RuntimeError(
                        f"Unsupported version number {lib_name}=={version_str}"
                    )
                major = match.group("major")
                minor = match.group("minor") or 0
                patch = match.group("patch") or 0
                dependencies.append(f"{lib_name}~={major}.{minor}.{patch}")

        add_dependency("amulet_nbt", amulet.nbt.__version__)

        setup_args["options"] = {
            "bdist_wheel": {
                "build_number": f"1.{amulet_compiler_version.compiler_id}.{amulet_compiler_version.compiler_version}"
            }
        }
else:
    add_default_requirements()


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

        if subprocess.run(
            [
                "cmake",
                *platform_args,
                f"-DPYTHON_EXECUTABLE={sys.executable}",
                f"-Dpybind11_DIR={pybind11.get_cmake_dir().replace(os.sep, '/')}",
                f"-Damulet_pybind11_extensions_DIR={fix_path(amulet.pybind11_extensions.__path__[0])}",
                f"-Damulet_io_DIR={fix_path(amulet.io.__path__[0])}",
                f"-Damulet_nbt_DIR={fix_path(amulet.nbt.__path__[0])}",
                f"-Damulet_core_DIR={fix_path(core_src_dir)}",
                f"-DAMULET_CORE_EXT_DIR={fix_path(ext_dir)}",
                f"-DCMAKE_INSTALL_PREFIX=install",
                "-B",
                "build",
            ]
        ).returncode:
            raise RuntimeError("Error configuring amulet_core")
        if subprocess.run(
            ["cmake", "--build", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_core")
        if subprocess.run(
            ["cmake", "--install", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_core")


cmdclass["build_ext"] = CMakeBuild


setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    ext_modules=[Extension("amulet.core._amulet_core", [])],
    install_requires=dependencies,
    **setup_args,
)
