from __future__ import annotations

import itertools

from typing import Sequence, List, Iterator, Tuple, Union, cast, Iterable

from .minecraft_types import Point


class SubSelectionBox:
    """
    A SubSelectionBox is a box that can represent the entirety of a Selection or just a subsection
    of one. This allows for non-rectangular and non-contiguous selections.

    The both the minimum and  maximum coordinate points are inclusive.
    """

    def __init__(self, min_point: Point, max_point: Point):
        self.min = tuple(int(p) for p in min_point)
        self.max = tuple(int(p) for p in max_point)

    def __iter__(self):
        return itertools.product(
            range(self.min[0], self.max[0]),
            range(self.min[1], self.max[1]),
            range(self.min[2], self.max[2]),
        )

    def __str__(self):
        return f"({self.min}, {self.max})"

    def __contains__(self, item: Union[Point, Tuple[int, int, int], Tuple[float, float, float]]):
        return (
            self.min[0] <= item[0] <= self.max[0]
            and self.min[1] <= item[1] <= self.max[1]
            and self.min[2] <= item[2] <= self.max[2]
        )

    def to_slice(self) -> List[slice]:
        """
        Converts the SubSelectionBoxes minimum/maximum coordinates into slice arguments

        :return: The SubSelectionBoxes coordinates as slices in (x,y,z) order
        """
        return [
            slice(self.min[0], self.max[0]),
            slice(self.min[1], self.max[1]),
            slice(self.min[2], self.max[2]),
        ]

    @property
    def min_x(self):
        return self.min[0]

    @property
    def min_y(self):
        return self.min[1]

    @property
    def min_z(self):
        return self.min[2]

    @property
    def max_x(self):
        return self.max[0]

    @property
    def max_y(self):
        return self.max[1]

    @property
    def max_z(self):
        return self.max[2]

    @property
    def shape(self):
        return self.max_x - self.min_x, self.max_y - self.min_y, self.max_z - self.min_z

    def intersects(self, other: SubSelectionBox) -> bool:
        """
        Method to check whether this instance of SubSelectionBox intersects another SubSelectionBox

        :param other: The other SubSelectionBox to check for intersection
        :return: True if the two SubSelectionBoxes intersect, False otherwise
        """
        return not (
            self.min_x >= other.max_x
            or self.min_y >= other.max_y
            or self.min_z >= other.max_z
            or self.max_x <= other.min_x
            or self.max_y <= other.min_y
            or self.max_z <= other.min_z
        )


class Selection:
    """
    Holding class for multiple SubSelectionBoxes which allows for non-rectangular and non-contiguous selections
    """

    def __init__(self, boxes: Sequence[SubSelectionBox] = None):
        self._boxes = []
        if not boxes:
            boxes = []

        for box in boxes:
            self.add_box(box)

    def __iter__(self) -> Iterable[SubSelectionBox]:
        return itertools.chain.from_iterable(sorted(self._boxes, key=hash))

    def __len__(self):
        return len(self._boxes)

    def __contains__(self, item: Union[Point, Tuple[int, int, int]]):
        for subbox in self._boxes:
            if item in subbox:
                return True

        return False

    def add_box(self, other: SubSelectionBox, do_merge_check: bool = True):
        """
        Adds a SubSelectionBox to the selection box. If `other` is next to another SubSelectionBox in the selection, matches in any 2 dimensions, and
        `do_merge_check` is True, then the 2 boxes will be combined into 1 box.

        :param other: The box to add
        :param do_merge_check: Boolean flag to merge boxes if able
        """
        if do_merge_check:
            boxes_to_remove = None
            new_box = None
            for box in self._boxes:
                x_dim = box.min_x == other.min_x and box.max_x == other.max_x
                y_dim = box.min_y == other.min_y and box.max_y == other.max_y
                z_dim = box.min_z == other.min_z and box.max_z == other.max_z

                x_border = box.max_x == other.min_x or other.max_x == box.min_x
                y_border = box.max_y == other.min_y or other.max_y == box.min_y
                z_border = box.max_z == other.min_z or other.max_z == box.min_z

                if (
                    (x_dim and y_dim and z_border)
                    or (x_dim and z_dim and y_border)
                    or (y_dim and z_dim and x_border)
                ):
                    boxes_to_remove = box
                    new_box = SubSelectionBox(box.min, other.max)
                    break

            if new_box:
                self._boxes.remove(boxes_to_remove)
                self.add_box(new_box)
            else:
                self._boxes.append(other)
        else:
            self._boxes.append(other)

    def is_contiguous(self) -> bool:
        """Does the Selection represent one connected region (True) or multiple separated regions (False)"""
        if len(self._boxes) == 1:
            return True

        for i in range(len(self._boxes) - 1):
            sub_box = self._boxes[i]
            next_box = self._boxes[i + 1]
            if (
                abs(sub_box.max[0] - next_box.min[0])
                and abs(sub_box.max[1] - next_box.min[1])
                and abs(sub_box.max[2] - next_box.min[2])
            ):
                return False

        return True

    def is_rectangular(self) -> bool:
        """
        Checks if the Selection is a rectangle

        :return: True is the selection is a rectangle, False otherwise
        """
        return len(self._boxes) == 1

    def subboxes(self) -> Iterator[SubSelectionBox]:
        """
        Returns an iterator of the SubSelectionBoxes in the Selection

        :return: An iterator of the SubSelectionBoxes
        """
        return cast(Iterator[SubSelectionBox], iter(sorted(self._boxes, key=hash)))


if __name__ == "__main__":
    b1 = SubSelectionBox((0, 0, 0), (4, 4, 4))
    b2 = SubSelectionBox((7, 7, 7), (10, 10, 10))
    sel_box = Selection((b1, b2))

    # for obj in sel_box:
    #    for x, y, z in obj:
    #        print(x,y,z)

    for x, y, z in sel_box:
        print(x, y, z)
