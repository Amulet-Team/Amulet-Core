from abc import ABC, abstractmethod
from typing import TypeVar, Generic


class AbstractGameVersion(ABC):
    @staticmethod
    @abstractmethod
    def platform_str() -> str:
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __gt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ge__(self, other):
        raise NotImplementedError


GameVersionT = TypeVar("GameVersionT", bound=AbstractGameVersion)


class GameVersionRange(Generic[GameVersionT]):
    def __init__(
        self, min_version: AbstractGameVersion, max_version: AbstractGameVersion
    ):
        if not max_version >= min_version:
            raise ValueError(min_version, max_version)
        self._min = min_version
        self._max = max_version

    @property
    def min(self) -> GameVersionT:
        return self._min

    @property
    def max(self) -> GameVersionT:
        return self._max

    def __contains__(self, item):
        return self.min <= item <= self.max


class AbstractBaseIntVersion(AbstractGameVersion):
    def __init__(self, data_version: int):
        """Constructor subject to change"""
        self._data_version = data_version

    @property
    def data_version(self) -> int:
        return self._data_version

    def __hash__(self):
        return hash(self._data_version)

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return NotImplemented
        return self.data_version == other.data_version

    def __lt__(self, other):
        if type(other) is not self.__class__:
            return NotImplemented
        return self.data_version < other.data_version

    def __gt__(self, other):
        if type(other) is not self.__class__:
            return NotImplemented
        return self.data_version > other.data_version

    def __le__(self, other):
        if type(other) is not self.__class__:
            return NotImplemented
        return self.data_version <= other.data_version

    def __ge__(self, other):
        if type(other) is not self.__class__:
            return NotImplemented
        return self.data_version >= other.data_version


class JavaGameVersion(AbstractBaseIntVersion):
    @staticmethod
    def platform_str() -> str:
        return "java"


class BedrockGameVersion(AbstractBaseIntVersion):
    @staticmethod
    def platform_str() -> str:
        return "bedrock"
