import abc
from abc import ABC, abstractmethod

class CompactableLevel(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def compact(self) -> None:
        """Compact level data to reduce file size."""
