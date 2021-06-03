from typing import Iterable, BinaryIO
from .data_pack import DataPack


class DataPackManager:
    """
    The DataPackManager class contains one or more data packs.
    It manages loading them so that the stacking order is maintained.
    """

    def __init__(self, data_packs: Iterable[DataPack]):
        """
        Construct a new DataPackManager class.

        :param data_packs: The data packs to load from. Later in the list get higher priority.
        """
        self._data_packs = tuple(
            reversed(
                tuple(
                    pack
                    for pack in data_packs
                    if isinstance(pack, DataPack) and pack.is_valid
                )
            )
        )

    @property
    def all_files(self) -> Iterable[str]:
        """
        The relative paths of all files contained within.

        :return: An iterable of paths.
        """
        all_files = set()
        for pack in self._data_packs:
            all_files.update(pack.all_files)
        return all_files

    def all_files_match(self, match: str) -> Iterable[str]:
        """
        The relative paths of all files contained within that match the given regex.

        :param match: The regex string to match again.
        :return: An iterable of file paths that match the given regex.
        """
        all_files = set()
        for pack in self._data_packs:
            all_files.update(pack.all_files_match(match))
        return all_files

    def has_file(self, relative_path: str) -> bool:
        """
        Does the requested file exist.

        :param relative_path:
        :return:
        """
        return any(pack.has_file(relative_path) for pack in self._data_packs)

    def open(self, relative_path: str) -> BinaryIO:
        """
        Get the contents of the file.

        :param relative_path:
        :return:
        """
        for pack in self._data_packs:
            if pack.has_file(relative_path):
                return pack.open(relative_path)
        raise FileNotFoundError(
            f"The requested path {relative_path} could not be found."
        )

    def close(self):
        """Close the contents."""
        for pack in self._data_packs:
            pack.close()
