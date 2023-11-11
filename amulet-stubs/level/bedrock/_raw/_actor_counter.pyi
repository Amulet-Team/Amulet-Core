from ._level import BedrockRawLevel as BedrockRawLevel
from threading import RLock

class ActorCounter:
    _lock: RLock
    _session: int
    _count: int
    def __init__(self) -> None: ...
    @classmethod
    def from_level(cls, raw: BedrockRawLevel): ...
    def next(self) -> tuple[int, int]:
        """
        Get the next unique session id and actor counter.
        Session id is usually negative

        :return: Tuple[session id, actor id]
        """
