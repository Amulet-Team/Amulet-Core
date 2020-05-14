from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.base_leveldb_interface import (
    BaseLevelDBInterface,
)


class LevelDB0Interface(BaseLevelDBInterface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 0
        self.features["finalised_state"] = "int0-2"

        self.features["data_2d"] = "unused_height512|biome256"

        self.features["block_entities"] = "31list"
        self.features["block_entity_format"] = "str-id"
        self.features["block_entity_coord_format"] = "xyz-int"

        self.features["entities"] = "32list"
        self.features["entity_format"] = "int-id"
        self.features["entity_coord_format"] = "Pos-list-float"

        self.features["terrain"] = "30array"


INTERFACE_CLASS = LevelDB0Interface
