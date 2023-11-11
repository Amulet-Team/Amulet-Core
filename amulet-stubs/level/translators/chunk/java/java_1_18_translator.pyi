from .java_blockstate_translator import JavaBlockstateTranslator as JavaBlockstateTranslator
from PyMCTranslate import TranslationManager as TranslationManager, Version as Version
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import VersionIdentifierType as VersionIdentifierType

class Java118Translator(JavaBlockstateTranslator):
    @staticmethod
    def is_valid(key): ...
    @staticmethod
    def _unpack_biomes(translation_manager: TranslationManager, version_identifier: VersionIdentifierType, chunk: Chunk): ...
    @staticmethod
    def _pack_biomes(translation_manager: TranslationManager, version_identifier: VersionIdentifierType, chunk: Chunk): ...
export = Java118Translator
