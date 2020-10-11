from typing import BinaryIO, List, Any, Generator, Tuple, Dict, TYPE_CHECKING
import os

from .format_wrapper import FormatWrapper
from amulet.api.data_types import Dimension, PlatformType
from amulet.api.errors import ObjectReadError, ObjectReadWriteError
from amulet import ChunkCoordinates

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface


class StructureFormatWrapper(FormatWrapper):
    """A base FormatWrapper for all structures that only have one dimension."""

    def __init__(self, path: str):
        """Set up the StructureFormatWrapper ready for accessing.

        :param path: The location of the file to read from and write to.
        """
        if type(self) is StructureFormatWrapper:
            raise Exception(
                "StructureFormatWrapper is not directly usable. One of its subclasses must be used."
            )
        super().__init__(path)
        if self.extensions:
            ext = os.path.splitext(self._path)[1]
            if ext not in self.extensions:
                raise ObjectReadWriteError(f"The given file does not have a valid file extension. Must be one of {self.extensions}")

    @property
    def dimensions(self) -> List[Dimension]:
        return ["main"]

    @property
    def can_add_dimension(self) -> bool:
        return False

    def register_dimension(self, dimension_internal: Any, dimension_name: Dimension):
        pass

    @property
    def requires_selection(self) -> bool:
        """Does this object require that a selection be defined when creating it from scratch?"""
        return True

    @staticmethod
    def is_valid(path: str) -> bool:
        raise NotImplementedError

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        raise NotImplementedError

    @property
    def extensions(self) -> Tuple[str, ...]:
        """The extension the file can have to be valid.
        eg (".schematic",)"""
        raise NotImplementedError

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> "Interface":
        raise NotImplementedError

    def _create(self):
        raise NotImplementedError

    def open_from(self, f: BinaryIO):
        """Load from a file like object. Useful to load from RAM rather than disk."""
        raise NotImplementedError

    def _open(self):
        if not os.path.isfile(self._path):
            raise ObjectReadError(f"There is no file to read at {self._path}")
        with open(self._path, "rb") as f:
            self.open_from(f)

    def save_to(self, f: BinaryIO):
        """Write to a file like object. Useful to write to RAM rather than disk.
        _save should open the file on disk and give it to this method."""
        raise NotImplementedError

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "wb") as f:
            self.save_to(f)

    def _close(self):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def all_chunk_coords(
        self, dimension: Dimension
    ) -> Generator[ChunkCoordinates, None, None]:
        raise NotImplementedError

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        raise NotImplementedError

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        raise NotImplementedError
