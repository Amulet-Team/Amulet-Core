from _typeshed import Incomplete
from amulet.api.errors import ObjectReadError as ObjectReadError
from amulet_nbt import NamedTag
from typing import BinaryIO, Optional, Union

class BedrockLevelDAT(NamedTag):
    _level_dat_version: int
    def __init__(self, tag: Incomplete | None = ..., name: str = ..., level_dat_version: int = ...) -> None: ...
    @classmethod
    def from_file(cls, path: str): ...
    def save_to(self, filename_or_buffer: Union[str, BinaryIO] = ..., *, compressed: bool = ..., little_endian: bool = ..., string_encoder=...) -> Optional[bytes]: ...
