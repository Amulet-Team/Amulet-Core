from typing import TYPE_CHECKING, Callable
from weakref import ref

if TYPE_CHECKING:
    from ._level import BedrockRawLevel


class BedrockRawLevelFriend:
    _r_ref: Callable[[], BedrockRawLevel | None]

    __slots__ = ("_r",)

    def __init__(self, raw_level: BedrockRawLevel) -> None:
        self._r_ref = ref(raw_level)

    @property
    def _r(self) -> BedrockRawLevel:
        r = self._r_ref()
        if r is None:
            raise RuntimeError("Cannot access raw level")
        return r

    def _invalidate_r(self) -> None:
        self._r_ref = lambda: None
