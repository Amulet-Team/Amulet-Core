from __future__ import annotations

from typing import TYPE_CHECKING
from threading import RLock

from amulet_nbt import LongTag

if TYPE_CHECKING:
    from ._level import BedrockRawLevel


class ActorCounter:
    _lock: RLock
    _session: int
    _count: int

    def __init__(self) -> None:
        self._lock = RLock()
        self._session = -1
        self._count = 0

    @classmethod
    def from_level(cls, raw: BedrockRawLevel) -> ActorCounter:
        level_dat = raw.level_dat
        session = level_dat.compound.get_long(
            "worldStartCount", LongTag(0xFFFFFFFF)
        ).py_int
        # for some reason this is a signed int stored in a signed long. Manually apply the sign correctly
        session -= (session & 0x80000000) << 1

        # create the counter object and set the session
        counter = ActorCounter()
        counter._session = session

        # increment and write back so there are no conflicts
        session -= 1
        if session < 0:
            session += 0x100000000
        level_dat.compound["worldStartCount"] = LongTag(session)
        raw.level_dat = level_dat

        return counter

    def next(self) -> tuple[int, int]:
        """
        Get the next unique session id and actor counter.
        Session id is usually negative

        :return: Tuple[session id, actor id]
        """
        with self._lock:
            count = self._count
            self._count += 1
        return self._session, count
