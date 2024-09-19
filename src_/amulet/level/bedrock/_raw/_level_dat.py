from __future__ import annotations

import struct
from typing import BinaryIO, Any
from copy import deepcopy

from amulet_nbt import (
    read_nbt,
    NamedTag,
    utf8_escape_encoding,
    AnyNBT,
    EncodingPreset,
    StringEncoding,
)
from amulet.errors import LevelReadError


class BedrockLevelDAT(NamedTag):
    _level_dat_version: int

    def __init__(
        self,
        tag: AnyNBT | None = None,
        name: str | bytes = "",
        level_dat_version: int | None = None,
    ) -> None:
        if not isinstance(level_dat_version, int):
            raise TypeError(
                "level_dat_version must be specified when constructing a BedrockLevelDAT instance."
            )
        super().__init__(tag, name)
        self._level_dat_version = level_dat_version

    def __reduce__(self) -> Any:
        return BedrockLevelDAT, (self.tag, self.name, self.level_dat_version)

    def __copy__(self) -> BedrockLevelDAT:
        return BedrockLevelDAT(self.tag, self.name, self.level_dat_version)

    def __deepcopy__(self, memo: dict) -> BedrockLevelDAT:
        return BedrockLevelDAT(
            deepcopy(self.tag, memo=memo), self.name, self.level_dat_version
        )

    @property
    def level_dat_version(self) -> int:
        return self._level_dat_version

    @classmethod
    def from_file(cls, path: str) -> BedrockLevelDAT:
        with open(path, "rb") as f:
            level_dat_version = struct.unpack("<i", f.read(4))[0]
            if 4 <= level_dat_version <= 10:
                data_length = struct.unpack("<i", f.read(4))[0]
                root_tag = read_nbt(
                    f.read(data_length),
                    compressed=False,
                    little_endian=True,
                    string_encoding=utf8_escape_encoding,
                )
                name = root_tag.name
                tag = root_tag.tag
            else:
                # TODO: handle other versions
                raise LevelReadError(
                    f"Unsupported level.dat version {level_dat_version}"
                )
        return cls(tag, name, level_dat_version)

    def save_to(
        self,
        filename_or_buffer: str | BinaryIO | None = None,
        *,
        preset: EncodingPreset | None = None,
        compressed: bool = False,
        little_endian: bool = True,
        string_encoding: StringEncoding = utf8_escape_encoding,
    ) -> bytes:
        payload = super().save_to(
            compressed=compressed,
            little_endian=little_endian,
            string_encoding=string_encoding,
        )
        dat = struct.pack("<ii", self._level_dat_version, len(payload)) + payload
        if isinstance(filename_or_buffer, str):
            with open(filename_or_buffer, "wb") as f:
                f.write(dat)
        elif filename_or_buffer is not None:
            filename_or_buffer.write(dat)
        return dat
