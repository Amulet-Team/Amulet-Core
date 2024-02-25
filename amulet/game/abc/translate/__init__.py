"""
A package to support translating block and entity data between versions.
Everything that is not imported into this module is an implementation detail.
"""

from ._translator import (
    BlockToUniversalTranslator,
    BlockFromUniversalTranslator,
    EntityToUniversalTranslator,
    EntityFromUniversalTranslator,
    load_json_block_translations,
)
