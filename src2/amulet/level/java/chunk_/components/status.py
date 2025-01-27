# from amulet.chunk.components.abc import ChunkComponent
#
#
# class StatusComponent(ChunkComponent[str, str]):
#     storage_key = b"jst"
#
#     @staticmethod
#     def fix_set_data(old_obj: str, new_obj: str) -> str:
#         if not isinstance(new_obj, str):
#             raise TypeError
#         return new_obj
