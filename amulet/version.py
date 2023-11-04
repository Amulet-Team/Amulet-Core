from abc import ABC, abstractmethod
from typing import TypeVar, Generic


class AbstractVersion(ABC):
    def __init__(self, platform: str):
        self._platform = str(platform)

    @property
    def platform(self) -> str:
        return self._platform

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

    def _check_compatible(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"other must be a {self.__class__.__name__} instance.")
        if self.platform != other.platform:
            raise ValueError(
                f"other has platform {other.platform} which does not match {self.platform}"
            )


class DataVersion(AbstractVersion):
    def __init__(self, platform: str, data_version: int):
        super().__init__(platform)
        if not isinstance(data_version, int):
            raise TypeError
        self._data_version = data_version

    @property
    def data_version(self) -> int:
        return self._data_version

    def __hash__(self):
        return hash(self._data_version)

    def __eq__(self, other):
        self._check_compatible(other)
        return self.data_version == other.data_version

    def __lt__(self, other):
        self._check_compatible(other)
        return self.data_version < other.data_version

    def __gt__(self, other):
        self._check_compatible(other)
        return self.data_version > other.data_version

    def __le__(self, other):
        self._check_compatible(other)
        return self.data_version <= other.data_version

    def __ge__(self, other):
        self._check_compatible(other)
        return self.data_version >= other.data_version

    def __repr__(self):
        return f"{self.__class__.__name__}({self.platform}, {self.data_version})"


class SemanticVersion(AbstractVersion):
    def __init__(self, platform: str, semantic_version: tuple[int, ...]):
        super().__init__(platform)
        semantic_version = tuple(semantic_version)
        if not all(isinstance(v, int) for v in semantic_version):
            raise TypeError
        self._semantic_version = semantic_version

    @property
    def semantic_version(self) -> tuple[int, ...]:
        return self._semantic_version

    def __hash__(self):
        return hash(self._semantic_version)

    def __eq__(self, other):
        self._check_compatible(other)
        return self.semantic_version == other.semantic_version

    def __lt__(self, other):
        self._check_compatible(other)
        return self.semantic_version < other.semantic_version

    def __gt__(self, other):
        self._check_compatible(other)
        return self.semantic_version > other.semantic_version

    def __le__(self, other):
        self._check_compatible(other)
        return self.semantic_version <= other.semantic_version

    def __ge__(self, other):
        self._check_compatible(other)
        return self.semantic_version >= other.semantic_version

    def __repr__(self):
        return f"{self.__class__.__name__}({self.platform}, {self.semantic_version})"


class VersionContainer:
    __slots__ = ("_version",)

    def __init__(self, version: AbstractVersion):
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
    def __init__(self, min_version: AbstractVersion, max_version: AbstractVersion):
        if not max_version >= min_version:
            raise ValueError(min_version, max_version)
        self._min = min_version
        self._max = max_version

    def __repr__(self):
        return f"VersionRangeContainer({self._min!r}, {self._max!r})"

    @property
    def min(self) -> VersionT:
        return self._min

    @property
    def max(self) -> VersionT:
        return self._max

    def __contains__(self, item):
        return self.min <= item <= self.max


class VersionRangeContainer:
    def __init__(self, version_range: VersionRange):
        if not isinstance(version_range, VersionRange):
            raise TypeError
        self._version_range = version_range

    @property
    def version_range(self) -> VersionRange:
        return self._version_range
