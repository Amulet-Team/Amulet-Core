from amulet.level.abc import Dimension as Dimension

from ._chunk_handle import JavaChunkHandle as JavaChunkHandle
from ._level import JavaLevel as JavaLevel
from ._raw import JavaRawDimension as JavaRawDimension

class JavaDimension(Dimension["JavaLevel", "JavaRawDimension", JavaChunkHandle]): ...
