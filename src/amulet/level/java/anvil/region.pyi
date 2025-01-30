from __future__ import annotations

import typing

import amulet.utils.lock
import amulet_nbt

__all__ = ["AnvilRegion", "RegionDoesNotExist"]

class AnvilRegion:
    """
    A class to read and write Minecraft Java Edition Region files.
    Only one instance should exist per region file at any given time otherwise bad things may happen.
    This class is internally thread safe but a public lock is provided to enable external synchronisation.
    Upstream locks from the level must also be adhered to.
    """

    class FileCloser:
        pass

    @typing.overload
    def __init__(
        self, directory: str, file_name: str, rx: int, rz: int, mcc: bool = False
    ) -> None: ...
    @typing.overload
    def __init__(self, directory: str, rx: int, rz: int, mcc: bool = False) -> None: ...
    @typing.overload
    def __init__(self, path: str, mcc: bool = False) -> None: ...
    def close(self) -> None:
        """
        Close the file object if open.
        This is automatically called when the instance is destroyed but may be called earlier.
        Thread safe.
        """

    def compact(self) -> None:
        """
        Compact the region file.
        Defragments the file and deletes unused space.
        If there are no chunks remaining in the region file it will be deleted.
        Thread safe.
        """

    def contains(self, cx: int, cz: int) -> bool:
        """
        Is the coordinate in the region.
        This returns true even if there is no value for the coordinate.
        Coordinates are in world space.
        Thread safe.
        """

    def delete_batch(self, coords: list[tuple[int, int]]) -> None:
        """
        Delete multiple chunk's data.
        Coordinates are in world space.
        Thread safe.
        """

    def delete_value(self, cx: int, cz: int) -> None:
        """
        Delete the chunk data.
        Coordinates are in world space.
        Thread safe.
        """

    def destroy(self) -> None:
        """
        Destroy the instance.
        Calls made after this will fail.
        This may only be called by the owner of the instance.
        Thread safe.
        """

    def get_coords(self) -> list[tuple[int, int]]:
        """
        Get the coordinates of all values in the region file.
        Coordinates are in world space.
        External lock optional.
        """

    def get_file_closer(self) -> AnvilRegion.FileCloser:
        """
        Get the object responsible for closing the region file.
        When this object is deleted it will close the region file
        This means that holding a reference to this will delay when the region file is closed.
        The region file may still be closed manually before this object is deleted.
        Thread safe.
        """

    def get_value(self, cx: int, cz: int) -> amulet_nbt.NamedTag:
        """
        Get the value for this coordinate.
        Coordinates are in world space.
        Thread safe.
        """

    def has_value(self, cx: int, cz: int) -> bool:
        """
        Is there a value stored for this coordinate.
        Coordinates are in world space.
        External lock optional.
        """

    def set_value(self, cx: int, cz: int, tag: amulet_nbt.NamedTag) -> None:
        """
        Set the value for this coordinate.
        Coordinates are in world space.
        Thread safe.
        """

    @property
    def lock(self) -> amulet.utils.lock.RLock:
        """
        A mutex which can be used to synchronise calls.
        Thread safe.
        """

    @property
    def path(self) -> str:
        """
        The path of the region file.
        Thread safe.
        """

    @property
    def rx(self) -> int:
        """
        The region x coordinate of the file.
        """

    @property
    def rz(self) -> int:
        """
        The region z coordinate of the file.
        """

class RegionDoesNotExist(RuntimeError):
    pass
