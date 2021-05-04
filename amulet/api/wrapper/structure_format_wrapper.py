from abc import abstractmethod
from typing import BinaryIO, List, Any, Tuple
import os

from .format_wrapper import FormatWrapper
from amulet.api.data_types import Dimension
from amulet.api.errors import ObjectReadError, ObjectReadWriteError


class StructureFormatWrapper(FormatWrapper):
    """A base FormatWrapper for all structures that only have one dimension."""

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`StructureFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        if self.extensions:
            ext = os.path.splitext(self._path)[1]
            if ext not in self.extensions:
                raise ObjectReadWriteError(
                    f"The given file does not have a valid file extension. Must be one of {self.extensions}"
                )

    @property
    def level_name(self) -> str:
        return os.path.basename(self.path)

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
        return True

    @property
    @abstractmethod
    def extensions(self) -> Tuple[str, ...]:
        """
        The extension the file can have to be valid.

        eg (".schematic",)
        """
        raise NotImplementedError

    @abstractmethod
    def open_from(self, f: BinaryIO):
        """
        Load from a file like object. Useful to load from RAM rather than disk.

        :param f: The file like object to read data from.
        """
        raise NotImplementedError

    def _open(self):
        if not os.path.isfile(self._path):
            raise ObjectReadError(f"There is no file to read at {self._path}")
        with open(self._path, "rb") as f:
            self.open_from(f)

    @abstractmethod
    def save_to(self, f: BinaryIO):
        """
        Write to a file like object. Useful to write to RAM rather than disk.

        :param f: The file like object to write data to.
        """
        raise NotImplementedError

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "wb") as f:
            self.save_to(f)
