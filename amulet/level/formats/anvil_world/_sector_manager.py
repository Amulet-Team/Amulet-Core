from __future__ import annotations

from typing import NamedTuple, List
import threading
import sys

if sys.version_info >= (3, 10):
    # bisect only supports key as of 3.10
    from bisect import bisect_left, bisect_right

else:

    def bisect_left(a, x, lo=0, hi=None, *, key=None):
        """Return the index where to insert item x in list a, assuming a is sorted.
        The return value i is such that all e in a[:i] have e < x, and all e in
        a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
        insert just before the leftmost x already there.
        Optional args lo (default 0) and hi (default len(a)) bound the
        slice of a to be searched.
        """

        if lo < 0:
            raise ValueError("lo must be non-negative")
        if hi is None:
            hi = len(a)
        # Note, the comparison uses "<" to match the
        # __lt__() logic in list.sort() and in heapq.
        if key is None:
            while lo < hi:
                mid = (lo + hi) // 2
                if a[mid] < x:
                    lo = mid + 1
                else:
                    hi = mid
        else:
            while lo < hi:
                mid = (lo + hi) // 2
                if key(a[mid]) < x:
                    lo = mid + 1
                else:
                    hi = mid
        return lo

    def bisect_right(a, x, lo=0, hi=None, *, key=None):
        """Return the index where to insert item x in list a, assuming a is sorted.
        The return value i is such that all e in a[:i] have e <= x, and all e in
        a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
        insert just after the rightmost x already there.
        Optional args lo (default 0) and hi (default len(a)) bound the
        slice of a to be searched.
        """

        if lo < 0:
            raise ValueError("lo must be non-negative")
        if hi is None:
            hi = len(a)
        # Note, the comparison uses "<" to match the
        # __lt__() logic in list.sort() and in heapq.
        if key is None:
            while lo < hi:
                mid = (lo + hi) // 2
                if x < a[mid]:
                    hi = mid
                else:
                    lo = mid + 1
        else:
            while lo < hi:
                mid = (lo + hi) // 2
                if x < key(a[mid]):
                    hi = mid
                else:
                    lo = mid + 1
        return lo


class NoValidSector(Exception):
    """An error for when there is no sector large enough and the region cannot be resized."""

    pass


class Sector(NamedTuple):
    start: int
    stop: int

    @property
    def length(self) -> int:
        return self.stop - self.start

    def intersects(self, other: Sector):
        """Do the two sectors intersect each other."""
        return not (other.stop <= self.start or self.stop <= other.start)

    def contains(self, other: Sector):
        """Is the other sector entirely within this sector."""
        return self.start <= other.start and other.stop <= self.stop

    def neighbours(self, other: Sector):
        """Do the two sectors neighbour but not intersect."""
        return other.stop == self.start or self.stop == other.start

    def split(self, other: Sector) -> List[Sector]:
        """
        Split this sector around another sector.
        The other sector must be contained within this sector

        :param other: The other sector to split around.
        :return: A list of 0-2 sectors
        """
        sectors = []
        if self.start < other.start:
            sectors.append(Sector(self.start, other.start))
        if other.stop < self.stop:
            sectors.append(Sector(other.stop, self.stop))
        return sectors


class SectorManager:
    """A class to manage a sequence of memory."""

    def __init__(self, start: int, stop: int, resizable: bool = True):
        """
        :param start: The start of the memory region
        :param stop: The end of the memory region
        :param resizable: Can the region be resized
        """
        if stop < start:
            raise ValueError("stop must be at least start")
        self._lock = threading.RLock()
        self._stop = stop
        self._resizable = resizable

        # A list of free sectors ordered by start location
        self._free_start = [Sector(start, stop)]
        # A list of free sectors ordered by (length, start).
        # This makes it easier to find the first sector large enough
        self._free_size = [Sector(start, stop)]

        # A set of reserved sectors
        self._reserved = set()

    @property
    def sectors(self) -> List[Sector]:
        """A list of reserved sectors"""
        with self._lock:
            return list(self._reserved)

    def reserve_space(self, length: int) -> Sector:
        """
        Find and reserve a memory location large enough to fit the requested memory.

        :param length: The length of the memory region to reserve
        :return: The index of the start of the reserved memory region
        """
        if not length:
            raise ValueError("Cannot reserve a sector with zero length.")
        with self._lock:
            # find the index of the first element with a larger or equal length prioritising the ones closer to the start
            index = bisect_left(
                self._free_size, (length, 0), key=lambda k: (k.length, k.start)
            )
            if index < len(self._free_size):
                # if there exists a section large enough to fit the length
                free_sector = self._free_size.pop(index)
                start_index = self._free_start.index(free_sector)
                sector = Sector(free_sector.start, free_sector.start + length)
                if free_sector.length > length:
                    free_sector = Sector(sector.stop, free_sector.stop)
                    self._add_size_sector(free_sector)
                    self._free_start[start_index] = free_sector
                else:
                    del self._free_start[start_index]
                return sector
            elif self._resizable:
                sector = Sector(self._stop, self._stop + length)
                self._stop = sector.stop
                self._reserved.add(sector)
                return sector
            else:
                raise NoValidSector(
                    "There is not enough contiguous space to allocate the length."
                )

    def reserve(self, sector: Sector):
        """
        Mark a section as reserved.
        If you don't know exactly where the sector is use `reserve_space` to find and reserve a new sector

        :param sector: The sector to reserve
        """
        if not sector.length:
            raise ValueError("Cannot reserve a sector with zero length.")
        with self._lock:
            if sector.start >= self._stop and (
                not self._free_start or self._free_start[-1].stop != self._stop
            ):
                if self._resizable:
                    # if the last sector has been reserved or did not exist then create a new one
                    s = Sector(self._stop, sector.stop)
                    self._free_start.append(s)
                    self._add_size_sector(s)
                    self._stop = sector.stop
                else:
                    raise NoValidSector("The sector starts outside of the region.")

            # Get the index of the segment with the latest start point that is
            # less than or equal to the start point of the sector being reserved.
            index = (
                bisect_right(self._free_start, sector.start, key=lambda k: k.start) - 1
            )

            if index < 0:
                raise NoValidSector(
                    "No free sectors that start at or before the one being reserved."
                )

            free_sector = self._free_start[index]

            if sector.stop <= free_sector.stop:
                # The sector fits within the contained sector
                # remove the contained sector from the lists
                del self._free_start[index]
                self._free_size.remove(free_sector)
            elif free_sector.stop == self._stop:
                if self._resizable:
                    # The sector is the last one and the memory region is resizable
                    del self._free_start[index]
                    self._free_size.remove(free_sector)
                    free_sector = Sector(free_sector.start, sector.stop)
                    self._stop = sector.stop
                else:
                    raise NoValidSector(
                        "The sector is outside the defined region and the region is not resizable."
                    )
            else:
                raise NoValidSector("The requested sector is not free to be reserved.")

            # split around the reserved sector
            sectors = free_sector.split(sector)
            # add the results back
            self._free_start[index:index] = sectors
            for s in sectors:
                self._add_size_sector(s)
            self._reserved.add(sector)

    def _add_size_sector(self, sector: Sector):
        self._free_size.insert(
            bisect_left(
                self._free_size,
                (sector.length, sector.start),
                key=lambda k: (k.length, k.start),
            ),
            sector,
        )

    def free(self, sector: Sector):
        """
        Free a reserved sector.
        The sector must match exactly a sector previously reserved.

        :param sector: The sector to free
        """
        with self._lock:
            # remove the sector from the reserved storage
            self._reserved.remove(sector)

            # Add it back to the free storage
            # find the position where it would be placed in the list ordered by start location
            index = bisect_right(self._free_start, sector.start, key=lambda k: k.start)

            # merge with the right neighbour
            if (
                index < len(self._free_start)
                and self._free_start[index].start == sector.stop
            ):
                right_sector = self._free_start.pop(index)
                self._free_size.remove(right_sector)
                sector = Sector(sector.start, right_sector.stop)

            # merge with the left neighbour
            if index > 0 and self._free_start[index - 1].stop == sector.start:
                left_sector = self._free_start.pop(index - 1)
                self._free_size.remove(left_sector)
                sector = Sector(left_sector.start, sector.stop)
                index -= 1

            self._free_start.insert(index, sector)
            self._add_size_sector(sector)


def validate(m):
    assert set(m._free_start) == set(m._free_size)
    free = sorted(list(m._free_start) + list(m._reserved), key=lambda k: k.start)
    if free:
        for i in range(len(free) - 1):
            assert free[i].stop == free[i + 1].start
        assert free[-1].stop == m._stop


def test1():
    m = SectorManager(2, 3)
    validate(m)
    m.reserve(Sector(2, 3))
    validate(m)
    m.reserve(Sector(3, 4))
    validate(m)
    print(m.sectors)


def test2():
    m = SectorManager(2, 102)

    m.reserve(Sector(5, 6))
    validate(m)
    m.reserve(Sector(6, 7))
    validate(m)
    # m.reserve(Sector(7, 8))
    m.reserve(Sector(8, 9))
    validate(m)

    try:
        m.reserve(Sector(6, 8))
    except NoValidSector:
        pass
    else:
        raise Exception

    validate(m)

    try:
        m.reserve(Sector(7, 9))
    except NoValidSector:
        pass
    else:
        raise Exception

    validate(m)
    m.free(Sector(5, 6))
    validate(m)
    m.free(Sector(6, 7))
    validate(m)
    m.free(Sector(8, 9))
    validate(m)

    m.reserve(Sector(6, 8))
    validate(m)
    m.free(Sector(6, 8))
    validate(m)

    m.reserve(Sector(7, 9))
    validate(m)
    m.free(Sector(7, 9))

    validate(m)

    assert len(m._free_start) == 1


# def test3():
# reserve a number of single length units
# for _ in range(20):
#     i = free_indexes.pop(random.randrange(len(free_indexes)))
#     m.reserve(Sector(i, i+1))
#     validate(m)
#     reserved_indexes.append(i)
#
# for _ in range(20):
#     index = random.randrange(len(free_indexes))
#     di = 1
#     i = free_indexes.pop(index)
#
# for _ in range(10_000):
#     m.reserve(Sector(i, i+1))
#     validate(m)
# print(m.sectors)


def test():
    test1()
    test2()


if __name__ == "__main__":
    test()
