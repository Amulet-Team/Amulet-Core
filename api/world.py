from typing import Tuple

import numpy


class WorldFormat(object):
    """
    Base class for World objects
    """

    @classmethod
    def load(cls, directory: str) -> object:
        raise NotImplementedError()

    def d_load_chunk(self, cx: int, cz: int) -> Tuple[numpy.ndarray, dict, dict]:
        raise NotImplementedError()

    @classmethod
    def fromUnifiedFormat(cls, unified: object) -> "WorldFormat":
        """
        Converts the passed object to the specific implementation

        :param unified: The object to convert
        :return object: The result of the conversion, None if not successful
        """
        raise NotImplementedError()

    def toUnifiedFormat(self) -> object:
        """
        Converts the current object to the Unified format
        """
        raise NotImplementedError()

    def save(self) -> None:
        """
        Saves the current WorldFormat to disk
        """
        raise NotImplementedError()
