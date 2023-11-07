from __future__ import annotations

import struct
from typing import Union, Optional, BinaryIO
from io import BytesIO

from amulet_nbt import (
    load as load_nbt,
    NamedTag,
    utf8_escape_decoder,
    utf8_escape_encoder,
)
from amulet.api.errors import (
    ObjectReadError,
)


class BedrockLevelDAT(NamedTag):
    _level_dat_version: int

    def __init__(self, tag=None, name: str = "", level_dat_version: int = None):
        if not isinstance(level_dat_version, int):
            raise TypeError(
                "path and level_dat_version must be specified when constructing a BedrockLevelDAT instance."
            )
        super().__init__(tag, name)
        self._level_dat_version = level_dat_version

    @classmethod
    def from_file(cls, path: str):
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
                tag = root_tag.tag
            else:
                # TODO: handle other versions
                raise ObjectReadError(
                    f"Unsupported level.dat version {level_dat_version}"
                )
        return cls(tag, name, level_dat_version)

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
