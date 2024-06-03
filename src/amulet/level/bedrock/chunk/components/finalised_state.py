from amulet.chunk.components.abc import ChunkComponent


class FinalisedStateComponent(ChunkComponent[int, int]):
    storage_key = b"bfs"

    @staticmethod
    def fix_set_data(old_obj: int, new_obj: int) -> int:
        if not isinstance(new_obj, int):
            raise TypeError
        if new_obj < 0:
            raise ValueError
        return new_obj
