from collections.abc import Collection
from typing import TypeVar

import numpy

T = TypeVar("T")

def brute_sort_objects_no_hash(
    data: Collection[T],
) -> tuple[list[T], numpy.ndarray]: ...
