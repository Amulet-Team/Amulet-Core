from __future__ import annotations

import amulet.level.java._raw._data_pack.data_pack
from amulet.level.java._raw._data_pack.data_pack import DataPack, Readable

__all__ = ["DataPack", "DataPackManager", "Readable"]

class DataPackManager:
    """

    The DataPackManager class contains one or more data packs.
    It manages loading them so that the stacking order is maintained.

    """

    def __init__(
        self,
        data_packs: typing.Iterable[
            amulet.level.java._raw._data_pack.data_pack.DataPack
        ],
    ):
        """

        Construct a new DataPackManager class.

        :param data_packs: The data packs to load from. Later in the list get higher priority.

        """

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

    def open(
        self, relative_path: str
    ) -> amulet.level.java._raw._data_pack.data_pack.Readable:
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
