import abc
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Iterable, Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...
    def __enter__(self) -> Readable: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

class BaseWrapper(ABC, metaclass=abc.ABCMeta):
    def __init__(self, path: str) -> None: ...
    @staticmethod
    @abstractmethod
    def is_valid(path: str) -> bool:
        """
        Is the given path valid for this class.

        :param path: The path to test.
        """

    @property
    def path(self) -> str:
        """The path to the data."""

    @property
    @abstractmethod
    def all_files(self) -> Iterable[str]:
        """
        The relative paths of all files contained within.

        :return: An iterable of paths.
        """

    def all_files_match(self, match: str) -> Iterable[str]:
        """
        The relative paths of all files contained within that match the given regex.

        :param match: The regex string to match again.
        :return: An iterable of file paths that match the given regex.
        """

    @abstractmethod
    def has_file(self, relative_path: str) -> bool:
        """
        Does the requested file exist.

        :param relative_path:
        :return:
        """

    @abstractmethod
    def open(self, relative_path: str) -> Readable:
        """
        Get the contents of the file.

        :param relative_path:
        :return:
        """

    @abstractmethod
    def close(self) -> None:
        """Close the contents."""

class ZipWrapper(BaseWrapper):
    def __init__(self, path: str) -> None: ...
    @staticmethod
    def is_valid(path: str) -> bool: ...
    @property
    def all_files(self) -> Iterable[str]: ...
    def has_file(self, relative_path: str) -> bool: ...
    def open(self, name: str) -> Readable: ...
    def close(self) -> None: ...

class DirWrapper(BaseWrapper):
    def __init__(self, path: str) -> None: ...
    @staticmethod
    def is_valid(path: str) -> bool: ...
    @property
    def all_files(self) -> Iterable[str]: ...
    def has_file(self, relative_path: str) -> bool: ...
    def open(self, relative_path: str) -> Readable: ...
    def close(self) -> None: ...

class DataPack:
    """The DataPack class wraps a single data pack."""

    def __init__(self, path: str) -> None: ...
    @property
    def path(self) -> str:
        """The path to the data."""

    @staticmethod
    def is_path_valid(path: str) -> bool:
        """
        Check if the given path is a valid data pack.

        :param path: The path to the data pack. Can be a zip file or directory.
        :return: True if the path is a valid data pack, False otherwise.
        """

    @property
    def is_valid(self) -> bool: ...
    @staticmethod
    def is_wrapper_valid(wrapper: BaseWrapper) -> bool: ...
    @property
    def all_files(self) -> Iterable[str]:
        """
        The relative paths of all files contained within.

        :return: An iterable of paths.
        """

    def all_files_match(self, match: str) -> Iterable[str]:
        """
        The relative paths of all files contained within that match the given regex.

        :param match: The regex string to match again.
        :return: An iterable of file paths that match the given regex.
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

    def close(self) -> None:
        """Close the contents."""
