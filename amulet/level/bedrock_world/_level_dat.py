from __future__ import annotations

import os
import struct
import warnings
from typing import Tuple, Union, Optional, BinaryIO
from io import BytesIO

from amulet_nbt import (
    AbstractBaseTag,
    load as load_nbt,
    NamedTag,
    utf8_escape_decoder,
    utf8_escape_encoder,
)
from amulet.api.errors import (
    ObjectReadError,
)


class BedrockLevelDAT(NamedTag):
    _path: str
    _level_dat_version: int

    def __init__(
        self, tag=None, name: str = "", path: str = None, level_dat_version: int = None
    ):
        if isinstance(tag, str):
            warnings.warn(
                "You must use BedrockLevelDAT.from_file to load from a file.",
                FutureWarning,
            )
            super().__init__()
            self._path = path = tag
            self._level_dat_version = 8
            if os.path.isfile(path):
                self.load_from(path)
            return
        else:
            if not (isinstance(path, str) and isinstance(level_dat_version, int)):
                raise TypeError(
                    "path and level_dat_version must be specified when constructing a BedrockLevelDAT instance."
                )
            super().__init__(tag, name)
            self._path = path
            self._level_dat_version = level_dat_version

    @classmethod
    def from_file(cls, path: str):
        level_dat_version, name, tag = cls._read_from(path)
        return cls(tag, name, path, level_dat_version)

    @property
    def path(self) -> Optional[str]:
        return self._path

    @staticmethod
    def _read_from(path: str) -> Tuple[int, str, AbstractBaseTag]:
        with open(path, "rb") as f:
            level_dat_version = struct.unpack("<i", f.read(4))[0]
            if 4 <= level_dat_version <= 10:
                data_length = struct.unpack("<i", f.read(4))[0]
                root_tag = load_nbt(
                    f.read(data_length),
                    compressed=False,
                    little_endian=True,
                    string_decoder=utf8_escape_decoder,
                )
                name = root_tag.name
                value = root_tag.tag
            else:
                # TODO: handle other versions
                raise ObjectReadError(
                    f"Unsupported level.dat version {level_dat_version}"
                )
        return level_dat_version, name, value

    def load_from(self, path: str):
        self._level_dat_version, self.name, self.tag = self._read_from(path)

    def reload(self):
        self.load_from(self.path)

    def save(self, path: str = None):
        self.save_to(path or self._path)

    def save_to(
        self,
        filename_or_buffer: Union[str, BinaryIO] = None,
        *,
        compressed=False,
        little_endian=True,
        string_encoder=utf8_escape_encoder,
    ) -> Optional[bytes]:
        payload = super().save_to(
            compressed=compressed,
            little_endian=little_endian,
            string_encoder=string_encoder,
        )
        buffer = BytesIO()
        buffer.write(struct.pack("<ii", self._level_dat_version, len(payload)))
        buffer.write(payload)
        if filename_or_buffer is None:
            return buffer.getvalue()
        elif isinstance(filename_or_buffer, str):
            with open(filename_or_buffer, "wb") as f:
                f.write(buffer.getvalue())
        else:
            filename_or_buffer.write(buffer.getvalue())
