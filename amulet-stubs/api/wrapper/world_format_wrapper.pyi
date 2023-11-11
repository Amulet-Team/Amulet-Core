import abc
from .format_wrapper import DiskFormatWrapper as DiskFormatWrapper, StorageType as StorageType, VersionNumberT as VersionNumberT
from _typeshed import Incomplete
from abc import abstractmethod
from amulet import IMG_DIRECTORY as IMG_DIRECTORY
from amulet.api.wrapper import Interface as Interface
from typing import Any, Optional

missing_world_icon: Incomplete

class WorldFormatWrapper(DiskFormatWrapper[VersionNumberT], metaclass=abc.ABCMeta):
    _missing_world_icon = missing_world_icon
    _world_image_path: Incomplete
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`WorldFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    @staticmethod
    def storage_type() -> StorageType: ...
    @property
    @abstractmethod
    def level_name(self) -> str: ...
    @level_name.setter
    @abstractmethod
    def level_name(self, value: str): ...
    @property
    @abstractmethod
    def last_played(self) -> int: ...
    @property
    @abstractmethod
    def game_version_string(self) -> str: ...
    @property
    def world_image_path(self) -> str:
        """The path to the world icon."""
    @property
    def can_add_dimension(self) -> bool: ...
    def register_dimension(self, dimension_identifier: Any): ...
    def _get_interface(self, raw_chunk_data: Optional[Any] = ...) -> Interface: ...
