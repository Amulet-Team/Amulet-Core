from typing import TYPE_CHECKING

from amulet.level.abc import Dimension
from ._chunk_handle import JavaChunkHandle

if TYPE_CHECKING:
    from ._level import JavaLevel
    from ._raw import JavaRawDimension


class JavaDimension(Dimension["JavaLevel", "JavaRawDimension", JavaChunkHandle]):
    def _create_chunk_handle(self, cx: int, cz: int) -> JavaChunkHandle:
        return JavaChunkHandle(
            self._l_ref,
            self._chunk_history,
            self._chunk_data_history,
            self.dimension_id,
            cx,
            cz,
        )
