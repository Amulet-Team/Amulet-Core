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
        if isinstance(boxes, tuple):
            boxes = list(boxes)
        self._boxes = boxes

    def __iter__(self):
        return itertools.chain.from_iterable(self._boxes)

    def add_box(self, other: SubBox):
        self._boxes.append(other)

    def is_contiguous(self) -> bool:
        if len(self._boxes) == 1:
            return True

        for i in range(len(self._boxes) - 1):
            sub_box = self._boxes[i]
            next_box = self._boxes[i + 1]
            if abs(sub_box.max[0] - next_box.min[0]) > 1 and abs(sub_box.max[1] - next_box.min[1]) > 1 and abs(sub_box.max[2] - next_box.min[2]) > 1:
                return False

        return True


if __name__ == "__main__":
    b1 = SubBox((0, 0, 0), (4, 4, 4))
    b2 = SubBox((7, 7, 7), (10, 10, 10))
    sel_box = SelectionBox((b1, b2))

    # for obj in sel_box:
    #    for x, y, z in obj:
    #        print(x,y,z)

    for x, y, z in sel_box:
        print(x, y, z)
