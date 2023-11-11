import abc
from .format_wrapper import DiskFormatWrapper as DiskFormatWrapper, StorageType as StorageType, VersionNumberT as VersionNumberT
from _typeshed import Incomplete
from abc import abstractmethod
from amulet.api.data_types import Dimension as Dimension
from amulet.api.errors import ObjectReadError as ObjectReadError, ObjectReadWriteError as ObjectReadWriteError, PlayerDoesNotExist as PlayerDoesNotExist
from amulet.player import Player as Player
from amulet.selection import SelectionGroup as SelectionGroup
from typing import Any, BinaryIO, Dict, Iterable, List, Optional, Tuple, Union

class StructureFormatWrapper(DiskFormatWrapper[VersionNumberT], metaclass=abc.ABCMeta):
    """A base FormatWrapper for all structures that only have one dimension."""
    _has_disk_data: bool
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`StructureFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    @staticmethod
    def storage_type() -> StorageType: ...
    @property
    def level_name(self) -> str: ...
    @property
    def dimensions(self) -> List[Dimension]: ...
    @property
    def can_add_dimension(self) -> bool: ...
    def register_dimension(self, dimension_identifier: Any): ...
    @staticmethod
    def requires_selection() -> bool: ...
    @property
    @abstractmethod
    def extensions(self) -> Tuple[str, ...]:
        '''
        The extension the file can have to be valid.

        eg (".schematic",)
        '''
    _bounds: Incomplete
    def _set_selection(self, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None]): ...
    @abstractmethod
    def open_from(self, f: BinaryIO):
        """
        Load from a file like object. Useful to load from RAM rather than disk.

        :param f: The file like object to read data from.
        """
    _is_open: bool
    _has_lock: bool
    def _open(self) -> None: ...
    @abstractmethod
    def save_to(self, f: BinaryIO):
        """
        Write to a file like object. Useful to write to RAM rather than disk.

        :param f: The file like object to write data to.
        """
    def _save(self) -> None: ...
    def all_player_ids(self) -> Iterable[str]: ...
    def has_player(self, player_id: str) -> bool: ...
    def _load_player(self, player_id: str) -> Player: ...
    def _get_raw_player_data(self, player_id: str) -> Any: ...
