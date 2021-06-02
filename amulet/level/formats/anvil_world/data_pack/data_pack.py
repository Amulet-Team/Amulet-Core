from abc import ABC, abstractmethod
from typing import Iterable
import os
import json
from zipfile import ZipFile
import io


class BaseWrapper(ABC):
    def __init__(self, path: str):
        self._path = path

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
        return self._path

    @property
    @abstractmethod
    def all_files(self) -> Iterable[str]:
        """
        The relative paths of all files contained within.

        :return: An iterable of paths.
        """
        raise NotImplementedError

    @abstractmethod
    def has_file(self, relative_path: str) -> bool:
        """
        Does the requested file exist.

        :param relative_path:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def open(self, relative_path: str, mode="rb", **kwargs) -> io.BytesIO:
        """
        Get the contents of the file.

        :param relative_path:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the contents."""
        raise NotImplementedError


class ZipWrapper(BaseWrapper, ZipFile):
    def __init__(self, path: str):
        BaseWrapper.__init__(self, path)
        ZipFile.__init__(self, path)

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isfile(path) and path.endswith(".zip")

    @property
    def all_files(self) -> Iterable[str]:
        for path in self.NameToInfo:
            if not path.endswith("/"):
                yield path

    def has_file(self, relative_path: str) -> bool:
        if relative_path.endswith("/"):
            # is a directory
            return False
        else:
            return relative_path in self.NameToInfo

    open = ZipFile.open
    close = ZipFile.close


class DirWrapper(BaseWrapper):
    def __init__(self, path: str):
        BaseWrapper.__init__(self, path)

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isdir(path)

    @property
    def all_files(self) -> Iterable[str]:
        for abs_path, _, files in os.walk(self.path):
            rel_path = os.path.normpath(os.path.relpath(abs_path, self.path)).replace(os.sep, "/")
            if rel_path == ".":
                yield from files
            else:
                for f in files:
                    yield f"{rel_path}/{f}"

    def has_file(self, relative_path: str) -> bool:
        return os.path.isfile(os.path.join(self.path, relative_path))

    def open(self, relative_path: str, mode="rb", **kwargs) -> io.BytesIO:
        return open(os.path.join(self.path, relative_path), mode, **kwargs)

    def close(self):
        pass


def _open_wrapper(path: str) ->BaseWrapper:
    for cls in (ZipWrapper, DirWrapper):
        if cls.is_valid(path):
            return cls(path)
    raise ValueError(f"The given path {path} is not valid.")


class DataPack:
    def __init__(self, path: str):
        assert self.is_valid(path), "The given path is not a valid data pack."

    @staticmethod
    def is_valid(path: str):
        """
        Check if the given path is a valid data pack.

        :param path: The path to the data pack. Can be a zip file or directory.
        :return: True if the path is a valid data pack, False otherwise.
        """
        wrapper = _open_wrapper(path)
        if wrapper.has_file("pack.mcmeta"):
            with wrapper.open("pack.mcmeta") as m:
                try:
                    meta_file = json.load(m)
                except json.JSONDecodeError:
                    pass
                else:
                    if isinstance(meta_file, dict) and isinstance(meta_file.get("pack", {}).get("pack_format", None), int):
                        # TODO: check the actual value
                        wrapper.close()
                        return True
        wrapper.close()
        return False
