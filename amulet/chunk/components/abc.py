from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, ClassVar
from enum import Enum

GetT = TypeVar("GetT")
SetT = TypeVar("SetT")


class UnloadedComponent(Enum):
    value = 0


_storage_keys = set[str]()


class ChunkComponent(ABC, Generic[T]):
    storage_key: ClassVar[bytes] = b""

    @staticmethod
    @abstractmethod
    def fix_set_data(old_obj: GetT, new_obj: SetT) -> GetT:
        """Validate and fix the data being set.

        This is run when the component is set.

        :param old_obj: The old component state
        :param new_obj: The new component state
        :return: The new component state to set.
        """
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert isinstance(cls.storage_key, bytes) and cls.storage_key and cls.storage_key not in _storage_keys, "Suffix must be a unique identifier."
