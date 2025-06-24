from typing import Union, Mapping

from setuptools import build_meta
from setuptools.build_meta import *

import requirements


def get_requires_for_build_wheel(
    config_settings: Union[Mapping[str, Union[str, list[str], None]], None] = None,
) -> list[str]:
    return [
        *build_meta.get_requires_for_build_wheel(config_settings),
        "wheel",
        *requirements.get_build_dependencies(),
    ]


def get_requires_for_build_editable(
    config_settings: Union[Mapping[str, Union[str, list[str], None]], None] = None,
) -> list[str]:
    return [
        *build_meta.get_requires_for_build_editable(config_settings),
        *requirements.get_build_dependencies(),
    ]
