from typing import Union, Mapping
import os

AMULET_COMPILER_VERSION_REQUIREMENT = "==1.3.0"
# AMULET_NBT_REQUIREMENT = "~=4.0"
AMULET_NBT_REQUIREMENT = "==4.0a19"
AMULET_PYBIND11_EXTENSIONS_REQUIREMENT = "==1.0a0"
AMULET_IO_VERSION_REQUIREMENT = "==1.0a1"

_compile_dependencies: dict[str, str] = {
    "wheel": "",
    "pybind11[global]": "==2.13.6",
    "amulet_pybind11_extensions": AMULET_PYBIND11_EXTENSIONS_REQUIREMENT,
    "amulet_nbt": AMULET_NBT_REQUIREMENT,
    "amulet_io": AMULET_IO_VERSION_REQUIREMENT
}

fixed_runtime_dependencies_data: dict[str, str] = {
    "amulet-compiler-target": "==1.0",
    "numpy": "~=2.0",
    "portalocker": "~=2.4",
    "platformdirs": "~=3.1",
    "pillow": "~=10.0",
    "amulet_runtime_final": "~=1.1",
}


def get_compile_dependencies_data(
    config_settings: Union[Mapping[str, Union[str, list[str], None]], None] = None,
) -> dict[str, str]:
    reqs = _compile_dependencies.copy()
    if (
        config_settings and config_settings.get("AMULET_FREEZE_COMPILER")
    ) or os.environ.get("AMULET_FREEZE_COMPILER", None):
        reqs["amulet-compiler-version"] = (
            "@git+https://github.com/Amulet-Team/Amulet-Compiler-Version.git@1.0"
        )
    return reqs


def get_compile_dependencies(
    config_settings: Union[Mapping[str, Union[str, list[str], None]], None] = None,
) -> list:
    return [
        f"{k}{v}" for k, v in get_compile_dependencies_data(config_settings).items()
    ]


def get_fixed_runtime_dependencies() -> list[str]:
    return [f"{k}{v}" for k, v in fixed_runtime_dependencies_data.items()]
