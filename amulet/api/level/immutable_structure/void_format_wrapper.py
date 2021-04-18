from typing import Any, Generator, List, Dict, Tuple, Optional, TYPE_CHECKING

from amulet.api.data_types import Dimension, PlatformType, ChunkCoordinates
from amulet.api.wrapper import FormatWrapper
from amulet.api.errors import ChunkDoesNotExist

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface


class VoidFormatWrapper(FormatWrapper):
    """There is no actual database here for chunks to be read from or written to. This is just here to make the world happy."""

    @property
    def world_name(self) -> str:
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

    def register_dimension(self, dimension_internal: Any, dimension_name: Dimension):
        pass

    def _get_interface(self, raw_chunk_data: Optional[Any] = None) -> "Interface":
        raise Exception("If this is called something is wrong")

    def _create(self, overwrite: bool, **kwargs):
        pass

    def _open(self):
        pass

    def _save(self):
        pass

    def _close(self):
        pass

    def unload(self):
        pass

    def all_chunk_coords(
        self, dimension: Dimension
    ) -> Generator[ChunkCoordinates, None, None]:
        yield from ()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return False

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        pass

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        pass

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        raise ChunkDoesNotExist
