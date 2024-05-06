from __future__ import annotations

from typing import Tuple, Optional, Any

from amulet_nbt import (
    CompoundTag,
    ByteTag,
    IntTag,
    ListTag,
    FloatTag,
)
from amulet.player import Player
from amulet.api.chunk import Chunk

from amulet.api.data_types import (
    VersionNumberTuple,
    Dimension,
    AnyNDArray,
)
from amulet.api.wrapper import WorldFormatWrapper

from .interface.chunk.leveldb_chunk_versions import (
    game_to_chunk_version,
)
from .dimension import ChunkData
from .interface.chunk import BaseLevelDBInterface, get_interface

OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"


class LevelDBFormat(WorldFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the Bedrock world format.
    """

    def _get_interface(
        self, raw_chunk_data: Optional[Any] = None
    ) -> BaseLevelDBInterface:
        return get_interface(self._get_interface_key(raw_chunk_data))

    def _get_interface_key(self, raw_chunk_data: Optional[ChunkData] = None) -> int:
        if raw_chunk_data:
            if b"," in raw_chunk_data:
                chunk_version = raw_chunk_data[b","][0]
            else:
                chunk_version = raw_chunk_data.get(b"v", b"\x00")[0]
        else:
            chunk_version = game_to_chunk_version(
                self.max_world_version[1],
                self.root_tag.compound.get_compound("experiments", CompoundTag())
                .get_byte("caves_and_cliffs", ByteTag())
                .py_int,
            )
        return chunk_version

    def _decode(
        self,
        interface: BaseLevelDBInterface,
        dimension: Dimension,
        cx: int,
        cz: int,
        raw_chunk_data: Any,
    ) -> Tuple[Chunk, AnyNDArray]:
        bounds = self.bounds(dimension).bounds
        return interface.decode(cx, cz, raw_chunk_data, (bounds[0][1], bounds[1][1]))

    def _encode(
        self,
        interface: BaseLevelDBInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ) -> Any:
        bounds = self.bounds(dimension).bounds
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            (bounds[0][1], bounds[1][1]),
        )

    def _load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        player_nbt = self._get_raw_player_data(player_id).compound
        dimension = player_nbt["DimensionId"]
        if isinstance(dimension, IntTag) and IntTag(0) <= dimension <= IntTag(2):
            dimension_str = {
                0: OVERWORLD,
                1: THE_NETHER,
                2: THE_END,
            }[dimension.py_int]
        else:
            dimension_str = OVERWORLD

        # get the players position
        pos_data = player_nbt.get("Pos")
        if (
            isinstance(pos_data, ListTag)
            and len(pos_data) == 3
            and pos_data.list_data_type == FloatTag.tag_id
        ):
            position = tuple(map(float, pos_data))
            position = tuple(
                p if -100_000_000 <= p <= 100_000_000 else 0.0 for p in position
            )
        else:
            position = (0.0, 0.0, 0.0)

        # get the players rotation
        rot_data = player_nbt.get("Rotation")
        if (
            isinstance(rot_data, ListTag)
            and len(rot_data) == 2
            and rot_data.list_data_type == FloatTag.tag_id
        ):
            rotation = tuple(map(float, rot_data))
            rotation = tuple(
                p if -100_000_000 <= p <= 100_000_000 else 0.0 for p in rotation
            )
        else:
            rotation = (0.0, 0.0)

        return Player(
            player_id,
            dimension_str,
            position,
            rotation,
        )
