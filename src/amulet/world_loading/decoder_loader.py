from __future__ import annotations

import glob
import importlib
import json
import os

from typing import Tuple, Type, AbstractSet, Dict

from .decoders.decoder import Decoder
from ..api import paths
from ..api.errors import DecoderLoaderNoneMatched

_loaded_decoders: Dict[str, Decoder] = {}
_has_loaded_decoders = False

SUPPORTED_DECODER_VERSION = 0
SUPPORTED_META_VERSION = 0


def _find_decoders(search_directory: str = None):
    global _has_loaded_decoders

    if not search_directory:
        search_directory = paths.DECODERS_DIR

    directories = glob.iglob(os.path.join(search_directory, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "decoder.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            decoder_info = json.load(fp)

        if decoder_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable decoder located in "{d}" due to unsupported meta version'
            )
            continue

        if decoder_info["decoder"]["decoder_version"] != SUPPORTED_DECODER_VERSION:
            print(
                f"[Error] Couldn't enable decoder \"{decoder_info['decoder']['id']}\" due to unsupported decoder version"
            )
            continue

        spec = importlib.util.spec_from_file_location(
            decoder_info["decoder"]["entry_point"],
            os.path.join(d, decoder_info["decoder"]["entry_point"] + ".py"),
        )
        modu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "DECODER_CLASS"):
            print(
                f"[Error] Decoder \"{decoder_info['decoder']['id']}\" is missing the DECODER_CLASS attribute"
            )
            continue

        _loaded_decoders[decoder_info["decoder"]["id"]] = modu.DECODER_CLASS()

        if __debug__:
            print(
                f"[Debug] Enabled decoder \"{decoder_info['decoder']['id']}\", version {decoder_info['decoder']['wrapper_version']}"
            )

    _has_loaded_decoders = True


def reload(search_directory: str = None):
    """
    Reloads all decoders in the given directory

    :param search_directory: The directory to search for, defaults to :py:data:`api.paths.FORMATS_DIR`
    """
    _loaded_decoders.clear()
    _find_decoders(search_directory)


def get_all_loaded_decoders() -> AbstractSet[str]:
    """
    :return: The identifiers of all loaded decoders
    """
    if not _has_loaded_decoders:
        _find_decoders()
    return _loaded_decoders.keys()


def get_decoder(decoder_id: str) -> Type:
    """
    Gets the class for the decoder with the given ``decoder_id``

    :param decoder_id: The decoder qid for the desired loaded decoder
    :return: The class for the decoder
    """
    if not _has_loaded_decoders:
        _find_decoders()
    return _loaded_decoders[decoder_id]


def identify(identifier: Tuple) -> str:
    if not _has_loaded_decoders:
        _find_decoders()

    for decoder_name, decoder_instance in _loaded_decoders.items():
        if decoder_instance.identify(identifier):
            return decoder_name

    raise DecoderLoaderNoneMatched("Could not find a matching decoder loader")


if __name__ == "__main__":
    import time

    _find_decoders()
    print(_loaded_decoders)
    time.sleep(1)
    reload()
    print(_loaded_decoders)
