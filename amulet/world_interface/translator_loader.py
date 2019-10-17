from __future__ import annotations

import glob
import importlib
import json
import os

from typing import Tuple, AbstractSet, Dict

from .translators.translator import Translator
from ..api import paths
from ..api.errors import TranslatorLoaderNoneMatched

_loaded_translators: Dict[str, Translator] = {}
_has_loaded_translators = False

SUPPORTED_TRANSLATOR_VERSION = 0
SUPPORTED_META_VERSION = 0


def _find_translators(search_directory: str = None):
    global _has_loaded_translators

    if not search_directory:
        search_directory = paths.TRANSLATORS_DIR

    directories = glob.iglob(os.path.join(search_directory, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "translator.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            translator_info = json.load(fp)

        if translator_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable translator located in "{d}" due to unsupported meta version'
            )
            continue

        if (
            translator_info["translator"]["translator_version"]
            != SUPPORTED_TRANSLATOR_VERSION
        ):
            print(
                f"[Error] Couldn't enable translator \"{translator_info['translator']['id']}\" due to unsupported translator version"
            )
            continue

        spec = importlib.util.spec_from_file_location(
            translator_info["translator"]["entry_point"],
            os.path.join(d, translator_info["translator"]["entry_point"] + ".py"),
        )
        modu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "TRANSLATOR_CLASS"):
            print(
                f"[Error] Translator \"{translator_info['translator']['id']}\" is missing the TRANSLATOR_CLASS attribute"
            )
            continue

        _loaded_translators[
            translator_info["translator"]["id"]
        ] = modu.TRANSLATOR_CLASS()

        if __debug__:
            print(
                f"[Debug] Enabled translator \"{translator_info['translator']['id']}\", version {translator_info['translator']['wrapper_version']}"
            )

    _has_loaded_translators = True


def reload(search_directory: str = None):
    """
    Reloads all translators in the given directory

    :param search_directory: The directory to search for, defaults to :py:data:`api.paths.FORMATS_DIR`
    """
    _loaded_translators.clear()
    _find_translators(search_directory)


def get_all_loaded_translators() -> AbstractSet[str]:
    """
    :return: The identifiers of all loaded translators
    """
    if not _has_loaded_translators:
        _find_translators()
    return _loaded_translators.keys()


def get_translator(identifier: Tuple) -> Translator:
    """
    Gets the class for the translator with the given ``translator_id``

    :param identifier: The translator identifier for the desired loaded translator
    :return: The class for the translator
    """
    translator_id = _identify(identifier)
    return _loaded_translators[translator_id]


def _identify(identifier: Tuple) -> str:
    if not _has_loaded_translators:
        _find_translators()

    for translator_name, translator_instance in _loaded_translators.items():
        if translator_instance.identify(identifier):
            return translator_name

    raise TranslatorLoaderNoneMatched("Could not find a matching translator loader")


if __name__ == "__main__":
    import time

    _find_translators()
    print(_loaded_translators)
    time.sleep(1)
    reload()
    print(_loaded_translators)
