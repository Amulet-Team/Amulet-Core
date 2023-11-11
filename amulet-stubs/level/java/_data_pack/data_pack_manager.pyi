from .data_pack import DataPack as DataPack
from _typeshed import Incomplete
from typing import BinaryIO, Iterable

class DataPackManager:
    """
    The DataPackManager class contains one or more data packs.
    It manages loading them so that the stacking order is maintained.
    """
    _data_packs: Incomplete
    def __init__(self, data_packs: Iterable[DataPack]) -> None:
        """
        Construct a new DataPackManager class.

        :param data_packs: The data packs to load from. Later in the list get higher priority.
        """
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
    def open(self, relative_path: str) -> BinaryIO:
        """
        Get the contents of the file.

        :param relative_path:
        :return:
        """
    def close(self) -> None:
        """Close the contents."""
