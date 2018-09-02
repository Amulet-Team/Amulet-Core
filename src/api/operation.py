from abc import abstractmethod

from typing import Union

import numpy

from api.types import Point


class Operation:
    @abstractmethod
    def run_operation(self, world):
        pass

class BlockChange:

    def __init__(self, start_point: Point, change: Union[numpy.ndarray, str]):
        self.start = start_point
        self.change = change

    def __contains__(self, item: Point):
        if isinstance(self.changes, numpy.ndarray):
            return self.start <= item <= self.start + self.changes.shape
        return item == self.start

    @property
    def start_point(self) -> Point:
        return self.start

    @property
    def changes(self) -> Union[numpy.ndarray, str]:
        return self.change
