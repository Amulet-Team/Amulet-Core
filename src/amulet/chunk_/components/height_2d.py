# import numpy
# from numpy.typing import ArrayLike
# from .abc import ChunkComponent
#
#
# class Height2DComponent(ChunkComponent[numpy.ndarray, ArrayLike]):
#     storage_key = b"h2d"
#
#     @staticmethod
#     def fix_set_data(old_obj: numpy.ndarray, new_obj: ArrayLike) -> numpy.ndarray:
#         new_obj = numpy.asarray(new_obj, numpy.int64)
#         if not isinstance(new_obj, numpy.ndarray):
#             raise TypeError
#         if new_obj.shape != old_obj.shape or new_obj.dtype != numpy.int64:
#             raise ValueError
#         return new_obj
