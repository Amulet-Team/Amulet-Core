from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.chunk import Chunk
from amulet.api.data_types import (
    VersionIdentifierType,
)

if TYPE_CHECKING:
    from PyMCTranslate import Version, TranslationManager

from .java_blockstate_translator import JavaBlockstateTranslator


class Java118Translator(JavaBlockstateTranslator):
    # TODO: move this logic into the interface

    @staticmethod
    def is_valid(key):
        return key[0] == "java" and 2836 <= key[1]

    @staticmethod
    def _unpack_biomes(
        translation_manager: "TranslationManager",
        version_identifier: VersionIdentifierType,
        chunk: Chunk,
    ):
        pass

    @staticmethod
    def _pack_biomes(
        translation_manager: "TranslationManager",
        version_identifier: VersionIdentifierType,
        chunk: Chunk,
    ):
        pass


export = Java118Translator
