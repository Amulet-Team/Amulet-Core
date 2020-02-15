import numpy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class ChunkArray(numpy.ndarray):
    def __new__(cls, parent_chunk: "Chunk", input_array):
        obj = numpy.asarray(input_array).view(cls)
        obj._parent_chunk = parent_chunk
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._parent_chunk = getattr(obj, "_parent_chunk", None)

    def _dirty(self):
        self._parent_chunk.changed = True

    def byteswap(self, inplace=False):
        if inplace:
            self._dirty()
        numpy.ndarray.byteswap(self, inplace)

    def fill(self, value):
        self._dirty()
        numpy.ndarray.fill(self, value)

    def itemset(self, *args):
        self._dirty()
        numpy.ndarray.itemset(*args)

    def partition(self, kth, axis=-1, kind="introselect", order=None):
        self._dirty()
        numpy.ndarray.partition(self, kth, axis, kind, order)

    def put(self, indices, values, mode="raise"):
        self._dirty()
        numpy.ndarray.put(self, indices, values, mode)

    def resize(self, *new_shape, refcheck=True):
        self._dirty()
        numpy.ndarray.resize(self, *new_shape, refcheck=refcheck)

    def sort(self, axis=-1, kind="quicksort", order=None):
        self._dirty()
        numpy.ndarray.sort(self, axis, kind, order)

    def squeeze(self, axis=None):
        self._dirty()
        numpy.ndarray.squeeze(self, axis)

    def __iadd__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__iadd__(self, *args, **kwargs)

    def __iand__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__iand__(self, *args, **kwargs)

    def __ifloordiv__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ifloordiv__(self, *args, **kwargs)

    def __ilshift__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ilshift__(self, *args, **kwargs)

    def __imatmul__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imatmul__(self, *args, **kwargs)

    def __imod__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imod__(self, *args, **kwargs)

    def __imul__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imul__(self, *args, **kwargs)

    def __ior__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ior__(self, *args, **kwargs)

    def __ipow__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ipow__(self, *args, **kwargs)

    def __irshift__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__irshift__(self, *args, **kwargs)

    def __isub__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__isub__(self, *args, **kwargs)

    def __itruediv__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__itruediv__(self, *args, **kwargs)

    def __ixor__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ixor__(self, *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__setitem__(self, *args, **kwargs)
