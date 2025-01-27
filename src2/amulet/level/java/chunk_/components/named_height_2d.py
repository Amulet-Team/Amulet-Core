# import numpy
# from amulet.chunk.components.abc import ChunkComponent
#
#
# class NamedHeight2DData:
#     arrays: dict[str, numpy.ndarray]
#
#     def __init__(
#         self, shape: tuple[int, int], arrays: dict[str, numpy.ndarray]
#     ) -> None:
#         self._shape = shape
#         self.arrays = arrays
#
#     @property
#     def shape(self) -> tuple[int, int]:
#         return self._shape
#
#
# class NamedHeight2DComponent(ChunkComponent[NamedHeight2DData, NamedHeight2DData]):
#     storage_key = b"nh2d"
#
#     @staticmethod
#     def fix_set_data(
#         old_obj: NamedHeight2DData, new_obj: NamedHeight2DData
#     ) -> NamedHeight2DData:
#         if not isinstance(new_obj, NamedHeight2DData):
#             raise TypeError
#         if new_obj.shape != old_obj.shape:
#             raise ValueError
#         for key, value in new_obj.arrays.items():
#             if not isinstance(key, str):
#                 raise TypeError
#             if not isinstance(value, numpy.ndarray):
#                 raise TypeError
#             if value.shape != old_obj.shape:
#                 raise ValueError
#         return new_obj
