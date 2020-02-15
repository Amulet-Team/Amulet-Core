from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.base_leveldb_interface import (
    BaseLevelDBInterface
)


class LevelDB4Interface(BaseLevelDBInterface):
    def __init__(self):
        BaseLevelDBInterface.__init__(self)

        self.features["chunk_version"] = 4
        self.features["finalised_state"] = "int0-2"

        self.features["data_2d"] = "unused_height512|biome256"

        self.features["block_entities"] = "31list"
        self.features["block_entity_format"] = "str-id"
        self.features["block_entity_coord_format"] = "xyz-int"

        self.features["entities"] = "32list"
        self.features["entity_format"] = "int-id"
        self.features["entity_coord_format"] = "Pos-list-float"

        self.features["terrain"] = "2farray"


INTERFACE_CLASS = LevelDB4Interface
