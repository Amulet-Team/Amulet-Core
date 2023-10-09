from abc import ABC, abstractmethod


class CompactableLevel(ABC):
    __slots__ = ()

    @abstractmethod
    def compact(self):
        """Compact level data to reduce file size."""
        raise NotImplementedError
