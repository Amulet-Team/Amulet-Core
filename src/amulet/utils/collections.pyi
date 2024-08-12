from __future__ import annotations
import typing

__all__ = ["PySequenceIterator"]

class PySequenceIterator:
    def __iter__(self) -> PySequenceIterator: ...
    def __next__(self) -> typing.Any: ...
