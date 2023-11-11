from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from collections.abc import Container


class AbstractVersion(ABC):
    def __init__(self, platform: str) -> None:
        self._platform = str(platform)

    @property
    def platform(self) -> str:
        return self._platform

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __gt__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __ge__(self, other: Any) -> bool:
        raise NotImplementedError

    def is_compatible(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.platform == other.platform

    def _check_compatible(self, other: Any) -> None:
        if not isinstance(other, self.__class__):
            raise TypeError(f"other must be a {self.__class__.__name__} instance.")
        if self.platform != other.platform:
            raise ValueError(f"Version {other!r} is not compatible with {self!r}")


class DataVersion(AbstractVersion):
    def __init__(self, platform: str, data_version: int) -> None:
        super().__init__(platform)
        if not isinstance(data_version, int):
            raise TypeError
        self._data_version = data_version

    @property
    def data_version(self) -> int:
        return self._data_version

    def __hash__(self) -> int:
        return hash((self.platform, self.data_version))

    def __eq__(self, other: Any) -> bool:
        return self.is_compatible(other) and self.data_version == other.data_version

    def __lt__(self, other: DataVersion) -> bool:
        self._check_compatible(other)
        return self.data_version < other.data_version

    def __gt__(self, other: DataVersion) -> bool:
        self._check_compatible(other)
        return self.data_version > other.data_version

    def __le__(self, other: DataVersion) -> bool:
        self._check_compatible(other)
        return self.data_version <= other.data_version

    def __ge__(self, other: DataVersion) -> bool:
        self._check_compatible(other)
        return self.data_version >= other.data_version

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.platform}, {self.data_version})"


class SemanticVersion(AbstractVersion):
    def __init__(self, platform: str, semantic_version: tuple[int, ...]) -> None:
        super().__init__(platform)
        semantic_version = tuple(semantic_version)
        if not all(isinstance(v, int) for v in semantic_version):
            raise TypeError
        self._semantic_version = semantic_version

    @property
    def semantic_version(self) -> tuple[int, ...]:
        return self._semantic_version

    def __hash__(self) -> int:
        return hash((self.platform, self.semantic_version))

    @staticmethod
    def _pad(
        a: tuple[int, ...], b: tuple[int, ...]
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        len_dif = len(a) - len(b)
        if len_dif > 0:
            b += (0,) * len_dif
        elif len_dif < 0:
            a += (0,) * abs(len_dif)
        return a, b

    def __eq__(self, other: Any) -> bool:
        if not self.is_compatible(other):
            return False
        a, b = self._pad(self.semantic_version, other.semantic_version)
        return a == b

    def __lt__(self, other: SemanticVersion) -> bool:
        self._check_compatible(other)
        a, b = self._pad(self.semantic_version, other.semantic_version)
        return a < b

    def __gt__(self, other: SemanticVersion) -> bool:
        self._check_compatible(other)
        a, b = self._pad(self.semantic_version, other.semantic_version)
        return a > b

    def __le__(self, other: SemanticVersion) -> bool:
        self._check_compatible(other)
        a, b = self._pad(self.semantic_version, other.semantic_version)
        return a <= b

    def __ge__(self, other: SemanticVersion) -> bool:
        self._check_compatible(other)
        a, b = self._pad(self.semantic_version, other.semantic_version)
        return a >= b

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.platform}, {self.semantic_version})"


class VersionContainer:
    __slots__ = ("_version",)

    def __init__(self, version: AbstractVersion) -> None:
        if not isinstance(version, AbstractVersion):
            raise TypeError("Invalid version", version)
        self._version = version

    @property
    def version(self) -> AbstractVersion:
        """
        The version this object is defined in.
        """
        return self._version


VersionT = TypeVar("VersionT", bound=AbstractVersion)


class VersionRange(Generic[VersionT]):
    def __init__(self, min_version: VersionT, max_version: VersionT) -> None:
        if min_version > max_version:
            raise ValueError(min_version, max_version)
        self._min = min_version
        self._max = max_version

    def __repr__(self) -> str:
        return f"VersionRangeContainer({self._min!r}, {self._max!r})"

    @property
    def min(self) -> VersionT:
        return self._min

    @property
    def max(self) -> VersionT:
        return self._max

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, AbstractVersion):
            return False
        return self.min <= item <= self.max


VersionRangeT = TypeVar("VersionRangeT", bound=VersionRange)


class VersionRangeContainer(Generic[VersionRangeT]):
    def __init__(self, version_range: VersionRangeT) -> None:
        if not isinstance(version_range, VersionRange):
            raise TypeError
        self._version_range = version_range

    @property
    def version_range(self) -> VersionRangeT:
        return self._version_range
