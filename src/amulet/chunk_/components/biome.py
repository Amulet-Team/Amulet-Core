# from __future__ import annotations
#
# from typing import Union, Iterable
# from collections.abc import Mapping
#
# import numpy
# from numpy.typing import ArrayLike
#
# from amulet.version import VersionRange
# from amulet.biome import Biome
# from amulet.palette import BiomePalette
# from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
# from amulet.utils.typed_property import TypedProperty
#
# from .abc import ChunkComponent
#
#
# class Biome2DComponentData:
#     _array: numpy.ndarray
#
#     def __init__(
#         self,
#         version_range: VersionRange,
#         array_shape: tuple[int, int],
#         default_biome: Biome,
#     ):
#         if (
#             not isinstance(array_shape, tuple)
#             and len(array_shape) == 2
#             and all(isinstance(s, int) for s in array_shape)
#         ):
#             raise TypeError
#
#         self._array_shape = array_shape
#         self._palette = BiomePalette(version_range)
#         self._palette.biome_to_index(default_biome)
#         self._set_biome(0)
#
#     def __getstate__(self) -> tuple[tuple[int, int], BiomePalette, numpy.ndarray]:
#         return self._array_shape, self._palette, self._array
#
#     def __setstate__(
#         self, state: tuple[tuple[int, int], BiomePalette, numpy.ndarray]
#     ) -> None:
#         self._array_shape, self._palette, self._array = state
#
#     @property
#     def array_shape(self) -> tuple[int, int]:
#         return self._array_shape
#
#     @TypedProperty[numpy.ndarray, Union[int, ArrayLike]]
#     def array(self) -> numpy.ndarray:
#         return self._array
#
#     @array.setter
#     def _set_biome(
#         self,
#         array: Union[int, ArrayLike],
#     ) -> None:
#         if isinstance(array, int):
#             self._array = numpy.full(self._array_shape, array, dtype=numpy.uint32)
#         else:
#             array = numpy.asarray(array)
#             if not isinstance(array, numpy.ndarray):
#                 raise TypeError
#             if array.shape != self._array_shape or array.dtype != numpy.uint32:
#                 raise ValueError
#             self._array = numpy.array(array)
#
#     @property
#     def palette(self) -> BiomePalette:
#         return self._palette
#
#
# class Biome2DComponent(ChunkComponent[Biome2DComponentData, Biome2DComponentData]):
#     storage_key = b"b2d"
#
#     @staticmethod
#     def fix_set_data(
#         old_obj: Biome2DComponentData, new_obj: Biome2DComponentData
#     ) -> Biome2DComponentData:
#         if not isinstance(new_obj, Biome2DComponentData):
#             raise TypeError
#         assert isinstance(old_obj, Biome2DComponentData)
#         if (
#             old_obj.array.shape != new_obj.array.shape
#             or old_obj.array_shape != new_obj.array_shape
#         ):
#             raise ValueError("New array shape does not match old array shape.")
#         elif old_obj.palette.version_range != new_obj.palette.version_range:
#             raise ValueError("New version range does not match old version range.")
#         return new_obj
#
#
# class Biome3DComponentData:
#     def __init__(
#         self,
#         version_range: VersionRange,
#         array_shape: tuple[int, int, int],
#         default_biome: Biome,
#     ):
#         self._palette = BiomePalette(version_range)
#         self._palette.biome_to_index(default_biome)
#         self._sections = SubChunkArrayContainer(array_shape, 0)
#
#     def __getstate__(self) -> tuple[BiomePalette, SubChunkArrayContainer]:
#         return self._palette, self._sections
#
#     def __setstate__(self, state: tuple[BiomePalette, SubChunkArrayContainer]) -> None:
#         self._palette, self._sections = state
#
#     @TypedProperty[
#         SubChunkArrayContainer,
#         SubChunkArrayContainer
#         | Mapping[int, numpy.ndarray]
#         | Iterable[tuple[int, numpy.ndarray]],
#     ]
#     def sections(self) -> SubChunkArrayContainer:
#         return self._sections
#
#     @sections.setter
#     def _set_biome(
#         self,
#         sections: (
#             SubChunkArrayContainer
#             | Mapping[int, numpy.ndarray]
#             | Iterable[tuple[int, numpy.ndarray]]
#         ),
#     ) -> None:
#         if sections is not self._sections:
#             self._sections.clear()
#             self._sections.update(sections)
#             if isinstance(sections, SubChunkArrayContainer):
#                 self._sections.default_array = sections.default_array
#
#     @property
#     def palette(self) -> BiomePalette:
#         return self._palette
#
#
# class Biome3DComponent(ChunkComponent[Biome3DComponentData, Biome3DComponentData]):
#     storage_key = b"b3d"
#
#     @staticmethod
#     def fix_set_data(
#         old_obj: Biome3DComponentData, new_obj: Biome3DComponentData
#     ) -> Biome3DComponentData:
#         if not isinstance(new_obj, Biome3DComponentData):
#             raise TypeError
#         assert isinstance(old_obj, Biome3DComponentData)
#         if old_obj.sections.array_shape != new_obj.sections.array_shape:
#             raise ValueError("New array shape does not match old array shape.")
#         elif old_obj.palette.version_range != new_obj.palette.version_range:
#             raise ValueError("New version range does not match old version range.")
#         return new_obj
