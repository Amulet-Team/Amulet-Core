from __future__ import annotations
from typing import Any, overload, Callable
from collections.abc import Sequence
from weakref import WeakValueDictionary


class VersionNumber(Sequence[int]):
    """
    This class is designed to store semantic versions and data versions and allow comparisons between them.

    >>> v1 = VersionNumber(1, 0, 0)
    >>> v2 = VersionNumber(1, 0)
    >>> assert v2 == v1

    This class should also be used to store single number data versions.
    >>> v3 = VersionNumber(3578)
    """

    _cache: WeakValueDictionary[tuple[int, ...], VersionNumber] = WeakValueDictionary()

    _v: tuple[int, ...]
    _last_non_zero: None | int

    def __new__(cls, *v: int) -> VersionNumber:
        self = cls._cache.get(v)
        if self is not None:
            return self

        self = super().__new__(cls)
        self._v = v
        for i, el in enumerate(v):
            if not isinstance(el, int):
                raise TypeError(
                    f"All elements in the version must be ints. Index {i} is {el}."
                )
        self._last_non_zero = None
        self._cache[v] = self
        return self

    def __getnewargs__(self) -> tuple[int, ...]:
        return self._v

    def __getstate__(self) -> None:
        return None

    def __setstate__(self, state: None) -> None:
        pass

    def cropped_version(self) -> tuple[int, ...]:
        """The version number with trailing zeros cut off."""
        if self._last_non_zero is None:
            self._last_non_zero = (
                next((i for i in range(len(self._v) - 1, -1, -1) if self._v[i]), -1) + 1
            )
        return self._v[: self._last_non_zero]

    def padded_version(self, length: int) -> tuple[int, ...]:
        """Get the version number padded with zeros to the given length."""
        if length < 0:
            raise ValueError("Length must be at least 0.")
        return self._v[:length] + (0,) * (length - len(self))

    @overload
    def __getitem__(self, index: int) -> int: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[int]: ...

    def __getitem__(self, index: int | slice) -> int | Sequence[int]:
        return self._v[index]

    def __len__(self) -> int:
        return len(self._v)

    def __hash__(self) -> int:
        return hash(self.cropped_version())

    @staticmethod
    def _op(
        a: tuple[int, ...], b: tuple[int, ...], func: Callable[[Any, Any], bool]
    ) -> bool:
        len_dif = len(a) - len(b)
        if len_dif > 0:
            b += (0,) * len_dif
        elif len_dif < 0:
            a += (0,) * abs(len_dif)
        return func(a, b)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VersionNumber):
            return False
        return self.cropped_version() == other.cropped_version()

    def __lt__(self, other: VersionNumber) -> bool:
        length = max(len(self), len(other))
        return self.padded_version(length) < other.padded_version(length)

    def __gt__(self, other: VersionNumber) -> bool:
        length = max(len(self), len(other))
        return self.padded_version(length) > other.padded_version(length)

    def __le__(self, other: VersionNumber) -> bool:
        length = max(len(self), len(other))
        return self.padded_version(length) <= other.padded_version(length)

    def __ge__(self, other: VersionNumber) -> bool:
        length = max(len(self), len(other))
        return self.padded_version(length) >= other.padded_version(length)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(str, self._v))})"

    def __str__(self) -> str:
        return ".".join(map(str, self._v))


class PlatformVersionContainer:
    __slots__ = ("_platform", "_version")

    def __init__(self, platform: str, version: VersionNumber) -> None:
        self._platform = platform
        self._version = version

    def __getstate__(self) -> tuple[Any, ...]:
        return self._platform, self._version

    def __setstate__(self, state: tuple[Any, ...]) -> tuple[Any, ...]:
        self._platform, self._version, *state = state
        return state

    @property
    def platform(self) -> str:
        """The platform this object is defined in."""
        return self._platform

    @property
    def version(self) -> VersionNumber:
        """The version this object is defined in."""
        return self._version


class VersionRange:
    _cache: WeakValueDictionary[
        tuple[str, VersionNumber, VersionNumber], VersionRange
    ] = WeakValueDictionary()

    _platform: str
    _min: VersionNumber
    _max: VersionNumber

    def __new__(
        cls, platform: str, min_version: VersionNumber, max_version: VersionNumber
    ) -> VersionRange:
        key = (platform, min_version, max_version)
        self = cls._cache.get(key)
        if self is not None:
            return self

        self = super().__new__(cls)
        if min_version > max_version:
            raise ValueError(min_version, max_version)
        self._platform = platform
        self._min = min_version
        self._max = max_version
        self._cache[key] = self
        return self

    def __getnewargs__(
        self,
    ) -> tuple[str, VersionNumber, VersionNumber]:
        return self._platform, self._min, self._max

    def __getstate__(self) -> None:
        return None

    def __setstate__(self, state: None):
        pass

    def __repr__(self) -> str:
        return f"VersionRangeContainer({self._min!r}, {self._max!r})"

    @property
    def platform(self) -> str:
        """The platform string the object is defined in"""
        return self._platform

    @property
    def min(self) -> VersionNumber:
        """The minimum version this range supports"""
        return self._min

    @property
    def max(self) -> VersionNumber:
        """The maximum version this range supports"""
        return self._max

    def contains(self, platform: str, version: VersionNumber) -> bool:
        return platform == self.platform and self.min <= version <= self.max


class VersionRangeContainer:
    def __init__(self, version_range: VersionRange) -> None:
        self._version_range = version_range

    @property
    def version_range(self) -> VersionRange:
        return self._version_range

    def __getstate__(self) -> tuple[Any, ...]:
        return (self._version_range,)

    def __setstate__(self, state: tuple[Any, ...]) -> tuple[Any, ...]:
        self._version_range, *state = state
        return state
