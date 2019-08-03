from __future__ import annotations

from ...api.chunk import Chunk

class Format:
  def __init__(self, directory: str):
    self._directory = directory

  def get_chunk(self, cx: int, cz: int) -> Chunk:
    raise NotImplementedError()

  @staticmethod
  def identify(directory: str) -> bool:
    raise NotImplementedError()
