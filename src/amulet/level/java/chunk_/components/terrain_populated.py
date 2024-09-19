# from __future__ import annotations
# from amulet.chunk.components.abc import ChunkComponent
#
#
# class TerrainPopulatedComponent(ChunkComponent[bool, bool]):
#     storage_key = b"jtp"
#
#     @staticmethod
#     def fix_set_data(old_obj: bool, new_obj: bool) -> bool:
#         if not isinstance(new_obj, bool):
#             raise TypeError
#         return new_obj
