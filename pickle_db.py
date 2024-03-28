"""
Pickle is great for converting an object to a binary representation and vice versa.
However successive calls will re-pickle the object even if the data is constant.
I would like to only pickle mutable objects and leave all constant objects in memory.

When unpickling if the instance exists we should just return that instead of creating a new object.
These objects will only be valid within the same session.
"""

from __future__ import annotations

import copyreg
from typing import Any
from threading import Lock
from collections.abc import Sequence
import pickle
import io
from bytesio_test import FastWritable
from weakref import WeakValueDictionary


class Constant:
    pass


_index = 0
lock = Lock()
_instances = WeakValueDictionary[int, Constant]()


def get_const(index: int) -> Constant:
    return _instances[index]


class CustomPickler(pickle.Pickler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.constants = list[Constant]()
        # dispatch_table = copyreg.dispatch_table.copy()
        #
        # from amulet.block import Block, BlockStack
        # dispatch_table[BlockStack] = self._store_const
        # dispatch_table[Block] = self._store_const
        #
        # self.dispatch_table = dispatch_table

    @classmethod
    def dumps(cls, obj: Any) -> tuple[bytes, tuple[Constant, ...]]:
        file = FastWritable()
        self = cls(file)
        self.dump(obj)
        return file.getvalue(), tuple(self.constants)

    def persistent_id(self, obj: Any) -> tuple[str, int] | None:
        if isinstance(obj, Constant):
            self.constants.append(obj)
            return "Const", len(self.constants) - 1
        return None

    # def _store_const(self, obj: Constant) -> Any:
    #     global _index
    #     with lock:
    #         index = _index
    #         _index += 1
    #     _instances[index] = obj
    #     self.constants.append(obj)
    #     return get_const, (index,)


class CustomUnpickler(pickle.Unpickler):
    def __init__(self, file: Any, constants: Sequence[Constant], *args: Any, **kwargs: Any) -> None:
        super().__init__(file, *args, **kwargs)
        self.constants = constants

    @classmethod
    def loads(cls, data: bytes, constants: Sequence[Constant]) -> Any:
        file = io.BytesIO(data)
        return cls(file, constants).load()

    def persistent_load(self, pid: tuple[str, int]) -> Any:
        tag_type, index = pid
        if tag_type == "Const":
            return self.constants[index]
        raise pickle.UnpicklingError
