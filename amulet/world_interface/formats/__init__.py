from __future__ import annotations

import glob
import json
import os
import numpy

from typing import Dict, AbstractSet, Tuple, Any
from importlib.util import spec_from_file_location, module_from_spec

from ...api.block import BlockManager
from ...api.chunk import Chunk
from ...api.errors import FormatLoaderNoneMatched
from .. import interfaces, translators
import PyMCTranslate

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

_loaded_formats: Dict[str, Format] = {}
_has_loaded_formats = False

FORMATS_DIRECTORY = os.path.dirname(__file__)


def _find_formats():
    global _has_loaded_formats

    directories = glob.iglob(os.path.join(FORMATS_DIRECTORY, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "format.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            format_info = json.load(fp)

        if format_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable format located in "{d}" due to unsupported meta version'
            )
            continue

        if format_info["format"]["format_version"] != SUPPORTED_FORMAT_VERSION:
            print(
                f"[Error] Couldn't enable format \"{format_info['format']['id']}\" due to unsupported format version"
            )
            continue

        spec = spec_from_file_location(
            format_info["format"]["entry_point"],
            os.path.join(d, format_info["format"]["entry_point"] + ".py"),
        )

        modu = module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "FORMAT_CLASS"):
            print(
                f"[Error] Format \"{format_info['format']['id']}\" is missing the FORMAT_CLASS attribute"
            )
            continue

        _loaded_formats[format_info["format"]["id"]] = modu.FORMAT_CLASS

        if __debug__:
            print(
                f"[Debug] Enabled format \"{format_info['format']['id']}\", version {format_info['format']['wrapper_version']}"
            )

    _has_loaded_formats = True


def reload():
    """Reloads all formats"""
    _loaded_formats.clear()
    _find_formats()


def get_all_formats() -> AbstractSet[str]:
    """
    :return: The names of all loaded formats
    """
    if not _has_loaded_formats:
        _find_formats()
    return _loaded_formats.keys()


def get_format(format_id: str) -> Format:
    """
    Gets the module for the format with the given ``format_id``

    :param format_id: The id for the desired loaded format
    :return: The module object for the format
    """
    if not _has_loaded_formats:
        _find_formats()
    if format_id not in _loaded_formats:
        raise FormatLoaderNoneMatched("Could not find a matching format loader")
    return _loaded_formats[format_id]


def identify(directory: str) -> str:
    """
    Identifies the format the world is in.

    Note: Since Minecraft Java versions below 1.12 lack version identifiers, they
    will always be loaded with 1.12 definitions and always be identified as "java_1_12"

    :param directory: The directory of the world
    :return: The version definitions name for the world and the format loader that would be used
    """
    if not _has_loaded_formats:
        _find_formats()

    for format_name, format_class in _loaded_formats.items():
        if format_class.is_valid(directory):
            return format_name

    raise FormatLoaderNoneMatched("Could not find a matching format loader")


class Format:
    def __init__(self, directory: str):
        self._directory = directory
        self.translation_manager = PyMCTranslate.new_translation_manager()

    def max_world_version(self) -> Tuple:
        raise NotImplemented

    def load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager
    ) -> Chunk:
        return self._load_chunk(cx, cz, global_palette)

    def _load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager, recurse: bool = True
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self._get_raw_chunk_data(cx, cz)
        interface = self._get_interface(raw_chunk_data)
        # get the translator for the given version
        translator = interface.get_translator(raw_chunk_data)

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = interface.decode(raw_chunk_data)

        # set up a callback that translator can use to get chunk data
        # TODO: perhaps find a way so that this does not need to load the whole chunk
        if recurse:
            def callback(x, z):
                palette = BlockManager()
                chunk = self._load_chunk(cx + x, cz + z, palette, False)  # TODO: this will also translate the chunk
                return chunk, palette

        else:
            callback = None

        # translate the data to universal format
        chunk, chunk_palette = translator.to_universal(self.translation_manager, chunk, chunk_palette, callback, recurse)

        # convert the block numerical ids from local chunk palette to global palette
        chunk_to_global = numpy.array([global_palette.get_add_block(block) for _, block in chunk_palette.items()])
        chunk._blocks = chunk_to_global[chunk.blocks]
        return chunk

    def save_chunk(self, chunk: Chunk, palette: BlockManager, interface_id: str, translator_id: str):
        """
        Saves a universal amulet.api.chunk.Chunk object using the given interface and translator.

        TODO: This changes the chunk and palette to only include blocks used in the chunk, translates them with the translator,
        and then calls the interface passing in the translator. It then calls _put_encoded to store the data returned by the interface

        The passed ids will be send to interfaces.get_interface, *not* .identify.
        """
        raise NotImplementedError()

    def _save_chunk_data(self, cx: int, cz: int, data: Any):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(self, cx: int, cz: int) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        raise NotImplementedError()

    def _get_interface(self, raw_chunk_data=None) -> interfaces.Interface:
        raise NotImplementedError

    @staticmethod
    def is_valid(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()


if __name__ == "__main__":
    import time

    _find_formats()
    print(_loaded_formats)
    time.sleep(1)
    reload()
    print(_loaded_formats)
