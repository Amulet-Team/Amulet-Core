from typing import Any, List, Dict, Tuple, Optional, TYPE_CHECKING, Iterable, Union

from amulet.api.data_types import (
    Dimension,
    PlatformType,
    ChunkCoordinates,
    AnyNDArray,
    VersionNumberTuple,
)
from amulet.api.wrapper import FormatWrapper
from amulet.api.errors import ChunkDoesNotExist, PlayerDoesNotExist
from amulet.api.player import Player
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup
from amulet.api import wrapper as api_wrapper

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface


class VoidFormatWrapper(FormatWrapper[VersionNumberTuple]):
    """
    A custom :class:`FormatWrapper` class that has no associated data.

    This is just to make the :class:`ImmutableStructure` class happy since it requires a :class:`FormatWrapper` class.

    All methods effectively do nothing.
    """

    def __init__(self, path: str):
        super().__init__(path)
        self._platform = "Unknown Platform"
        self._version = (0, 0, 0)

    @property
    def level_name(self) -> str:
        return "Void"

    @staticmethod
    def is_valid(path: str) -> bool:
        return False

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {}

    @property
    def dimensions(self) -> List[Dimension]:
        return ["main"]

    @property
    def can_add_dimension(self) -> bool:
        return False

    def register_dimension(self, dimension_identifier: Any):
        pass

    def _get_interface(self, raw_chunk_data: Optional[Any] = None) -> "Interface":
        raise Exception("If this is called something is wrong")

    def _encode(
        self,
        interface: api_wrapper.Interface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ) -> Any:
        raise Exception("If this is called something is wrong")

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs
    ):
        pass

    def _open(self):
        pass

    def _save(self):
        pass

    def _close(self):
        pass

    def unload(self):
        pass

    def all_chunk_coords(self, dimension: Dimension) -> Iterable[ChunkCoordinates]:
        yield from ()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return False

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        pass

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        pass

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        raise ChunkDoesNotExist

    def all_player_ids(self) -> Iterable[str]:
        yield from ()

    def has_player(self, player_id: str) -> bool:
        return False

    def _load_player(self, player_id: str) -> Player:
        raise PlayerDoesNotExist

    def _get_raw_player_data(self, player_id: str) -> Any:
        raise PlayerDoesNotExist
