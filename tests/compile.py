import subprocess
import sys
import shutil
import os
import importlib.util

import pybind11


def get_package_path(name: str) -> str:
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise RuntimeError(f"Could not find {name}")
        module_path = spec.origin
        if module_path is None:
            raise RuntimeError(f"Could not find {name}")
        if not module_path.endswith("__init__.py"):
            raise RuntimeError(f"{name} is not a package.")
        return os.path.dirname(module_path).replace(os.sep, "/")
    except:
        print(f"Failed finding {name}. Falling back to importing.")
        return importlib.import_module(name).__path__[0].replace(os.sep, "/")


def main() -> None:
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
            f"-Dpybind11_extensions_DIR={get_package_path('pybind11_extensions')}",
            f"-Damulet_io_DIR={get_package_path("amulet.io")}",
            f"-Damulet_nbt_DIR={get_package_path('amulet.nbt')}",
            f"-Damulet_core_DIR={get_package_path('amulet')}",
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
