from __future__ import annotations

import types
import typing
from builtins import str as PlatformType

__all__ = [
    "PlatformType",
    "PlatformVersionContainer",
    "VersionNumber",
    "VersionRange",
    "VersionRangeContainer",
]

class PlatformVersionContainer:
    """
    A class storing platform identifier and version number.
    Thread safe.
    """

    def __init__(self, platform: str, version: VersionNumber) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def platform(self) -> str:
        """
        Get the platform identifier.
        """

    @property
    def version(self) -> VersionNumber:
        """
        Get the version number.
        """

class VersionNumber:
    """
    This class is designed to store semantic versions and data versions and allow comparisons between them.
    It is a wrapper around std::vector<std::int64_t> with special comparison handling.
    The version can contain zero to max(int64) values.
    Undefined trailing values are implied zeros. 1.1 == 1.1.0
    All methods are thread safe.

    >>> v1 = VersionNumber(1, 0, 0)
    >>> v2 = VersionNumber(1, 0)
    >>> assert v2 == v1

    This class should also be used to store single number data versions.
    >>> v3 = VersionNumber(3578)
    """

    def __contains__(self, arg0: int) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: VersionNumber) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __ge__(self, arg0: VersionNumber) -> bool: ...
    @typing.overload
    def __getitem__(self, item: typing.SupportsInt) -> int: ...
    @typing.overload
    def __getitem__(self, item: slice) -> list[int]: ...
    def __gt__(self, arg0: VersionNumber) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(self, *args: typing.SupportsInt) -> None: ...
    def __iter__(self) -> typing.Iterator[int]: ...
    def __le__(self, arg0: VersionNumber) -> bool: ...
    def __len__(self) -> int: ...
    def __lt__(self, arg0: VersionNumber) -> bool: ...
    def __repr__(self) -> str: ...
    def __reversed__(self) -> typing.Iterator[int]: ...
    def __str__(self) -> str: ...
    def count(self, value: int) -> int: ...
    def cropped_version(self) -> list[int]:
        """
        The version number with trailing zeros cut off.
        """

    def index(
        self, value: int, start: int = 0, stop: int = 18446744073709551615
    ) -> int: ...
    def padded_version(self, len: int) -> list[int]:
        """
        Get the version number cropped or padded with zeros to the given length.
        """

class VersionRange:
    """
    A class storing platform identifier and minimum and maximum version numbers.
    Thread safe.
    """

    __hash__: typing.ClassVar[None] = None  # type: ignore
    @typing.overload
    def __eq__(self, arg0: VersionRange) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __init__(
        self, platform: str, min_version: VersionNumber, max_version: VersionNumber
    ) -> None: ...
    def __repr__(self) -> str: ...
    def contains(self, arg0: str, arg1: VersionNumber) -> bool:
        """
        Check if the platform is equal and the version number is within the range.
        """

    @property
    def max_version(self) -> VersionNumber:
        """
        The maximum version number
        """

    @property
    def min_version(self) -> VersionNumber:
        """
        The minimum version number
        """

    @property
    def platform(self) -> str:
        """
        The platform identifier.
        """

class VersionRangeContainer:
    """
    A class that contains a version range.
    """

    def __init__(self, version_range: VersionRange) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def version_range(self) -> VersionRange:
        """
        The version range.
        """
