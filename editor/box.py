from collections import namedtuple
import itertools

from typing import Sequence


Point = namedtuple("Point", ("x", "y", "z"))


class SubBox:

    def __init__(self, min_point: Point, max_point: Point):
        self.min = min_point
        self.max = max_point

    def __iter__(self):
        return itertools.product(
            range(self.min[0], self.max[0]),
            range(self.min[1], self.max[1]),
            range(self.min[2], self.max[2]),
        )


class SelectionBox:

    def __init__(self, boxes: Sequence[SubBox]):
        self._boxes = boxes
        self.__step = 1

    def __iter__(self):
        return itertools.chain.from_iterable(self._boxes)


if __name__ == "__main__":
    b1 = SubBox((0, 0, 0), (4, 4, 4))
    b2 = SubBox((7, 7, 7), (10, 10, 10))
    sel_box = SelectionBox((b1, b2))

    # for obj in sel_box:
    #    for x, y, z in obj:
    #        print(x,y,z)

    for x, y, z in sel_box:
        print(x, y, z)
