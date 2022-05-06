from __future__ import annotations

from amulet.api.wrapper import EntityIDType, EntityCoordType
from .base_leveldb_interface import (
    BaseLevelDBInterface,
)


class LevelDB0Interface(BaseLevelDBInterface):

    chunk_version = 0

    def __init__(self):
        super().__init__()

        self._set_feature("finalised_state", "int0-2")

        self._set_feature("data_2d", "height512|biome256")

        self._set_feature("block_entities", "31list")
        self._set_feature("block_entity_format", EntityIDType.str_id)
        self._set_feature("block_entity_coord_format", EntityCoordType.xyz_int)

        self._set_feature("entities", "32list")
        self._set_feature("entity_format", EntityIDType.int_id)
        self._set_feature("entity_coord_format", EntityCoordType.Pos_list_float)

        self._set_feature("terrain", "30array")


export = LevelDB0Interface
