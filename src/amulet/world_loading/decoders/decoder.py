from __future__ import annotations

from typing import Tuple

from ...api.chunk import Chunk


class Decoder:
    def decode(self, data) -> Chunk:
        raise NotImplementedError()

    @staticmethod
    def identify(key: Tuple) -> bool:
        raise NotImplementedError()
