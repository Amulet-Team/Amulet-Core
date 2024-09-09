from __future__ import annotations

import abc
import json as json
import os as os
import re as re
import typing
from abc import ABC, abstractmethod
from builtins import traceback as TracebackType
from typing import Protocol
from zipfile import ZipFile

__all__ = [
    "ABC",
    "BaseWrapper",
    "DataPack",
    "DirWrapper",
    "Protocol",
    "Readable",
    "TracebackType",
    "ZipFile",
    "ZipWrapper",
    "abstractmethod",
    "json",
    "os",
    "re",
]

class BaseWrapper(abc.ABC):
    @staticmethod
    def is_valid(path: str) -> bool:
        """

        Is the given path valid for this class.

        :param path: The path to test.

        """

    def __init__(self, path: str): ...
    def all_files_match(self, match: str) -> typing.Iterable[str]:
        """

        The relative paths of all files contained within that match the given regex.

        :param match: The regex string to match again.
        :return: An iterable of file paths that match the given regex.

        """

    def close(self) -> None:
        """
        Close the contents.
        """

    def has_file(self, relative_path: str) -> bool:
        """

        Does the requested file exist.

        :param relative_path:
        :return:

        """

    def open(self, relative_path: str) -> Readable:
        """

        Get the contents of the file.

        :param relative_path:
        :return:

        """

    @property
    def all_files(self) -> typing.Iterable[str]:
        """

        The relative paths of all files contained within.

        :return: An iterable of paths.

        """

    @property
    def path(self) -> str:
        """
        The path to the data.
        """

class DataPack:
    """
    The DataPack class wraps a single data pack.
    """

    @staticmethod
    def is_path_valid(path: str) -> bool:
        """

        Check if the given path is a valid data pack.

        :param path: The path to the data pack. Can be a zip file or directory.
        :return: True if the path is a valid data pack, False otherwise.

        """

    @staticmethod
    def is_wrapper_valid(wrapper: BaseWrapper) -> bool: ...
    def __init__(self, path: str): ...
    def all_files_match(self, match: str) -> typing.Iterable[str]:
        """

        The relative paths of all files contained within that match the given regex.

        :param match: The regex string to match again.
        :return: An iterable of file paths that match the given regex.

        """

    def close(self) -> None:
        """
        Close the contents.
        """

    def has_file(self, relative_path: str) -> bool:
        """

        Does the requested file exist.

        :param relative_path:
        :return:

        """

    def open(self, relative_path: str) -> Readable:
        """

        Get the contents of the file.

        :param relative_path:
        :return:

        """

    @property
    def all_files(self) -> typing.Iterable[str]:
        """

        The relative paths of all files contained within.

        :return: An iterable of paths.

        """

    @property
    def is_valid(self) -> bool: ...
    @property
    def path(self) -> str:
        """
        The path to the data.
        """

class DirWrapper(BaseWrapper):
    @staticmethod
    def is_valid(path: str) -> bool: ...
    def __init__(self, path: str): ...
    def close(self) -> None: ...
    def has_file(self, relative_path: str) -> bool: ...
    def open(self, relative_path: str) -> Readable: ...
    @property
    def all_files(self) -> typing.Iterable[str]: ...

class Readable(typing.Protocol):
    @classmethod
    def __subclasshook__(cls, other): ...
    def __enter__(self) -> Readable: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def __init__(self, *args, **kwargs): ...
    def read(self, n: int = -1) -> bytes: ...

class ZipWrapper(BaseWrapper):
    @staticmethod
    def is_valid(path: str) -> bool: ...
    def __init__(self, path: str): ...
    def close(self) -> None: ...
    def has_file(self, relative_path: str) -> bool: ...
    def open(self, name: str) -> Readable: ...
    @property
    def all_files(self) -> typing.Iterable[str]: ...

def _open_wrapper(path: str) -> BaseWrapper: ...
