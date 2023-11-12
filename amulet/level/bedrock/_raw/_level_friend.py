from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._level import BedrockRawLevelPrivate


class BedrockRawLevelFriend:
    _r: BedrockRawLevelPrivate

    __slots__ = ("_r",)

    def __init__(self, raw_data: BedrockRawLevelPrivate) -> None:
        self._r = raw_data
