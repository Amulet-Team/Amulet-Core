import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class CompactableLevel(ABC, metaclass=abc.ABCMeta):
    __slots__: Incomplete
    @abstractmethod
    def compact(self) -> None:
        """Compact level data to reduce file size."""
