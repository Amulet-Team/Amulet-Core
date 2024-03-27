import unittest

from amulet.level.formats.anvil_world._sector_manager import (
    Sector,
    SectorManager,
    NoValidSector,
)


SectorSize = 4096

sector_0 = Sector(0 * SectorSize, 1 * SectorSize)
sector_1 = Sector(1 * SectorSize, 2 * SectorSize)
sector_2_9 = Sector(2 * SectorSize, 9 * SectorSize)
sector_2_10 = Sector(2 * SectorSize, 10 * SectorSize)
sector_9_10 = Sector(9 * SectorSize, 10 * SectorSize)
sector_10 = Sector(10 * SectorSize, 11 * SectorSize)
sector_11_21 = Sector(11 * SectorSize, 21 * SectorSize)
sector_21_23 = Sector(21 * SectorSize, 23 * SectorSize)


class JavaSectorManagerTestCase(unittest.TestCase):
    def test_init_sector_manager(self) -> None:
        manager = SectorManager(0, 0)
        self.assertEqual([], manager.sectors)

    def test_reserve_free(self) -> None:
        # Create the manager
        manager = SectorManager(0, 0)
        self.assertEqual([], manager.sectors)

        # Reserve a sector
        manager.reserve_space(SectorSize)
        self.assertEqual([sector_0], manager.sectors)

        # Reserve another sector
        manager.reserve_space(SectorSize)
        self.assertEqual([sector_0, sector_1], manager.sectors)

        # Free the first sector
        manager.free(sector_0)
        self.assertEqual([sector_1], manager.sectors)

        # Reserve the first sector again
        manager.reserve_space(SectorSize)
        self.assertEqual([sector_0, sector_1], manager.sectors)

        # Reserve a third sector at a set location
        manager.reserve(sector_10)
        self.assertEqual([sector_0, sector_1, sector_10], manager.sectors)

        # Reserve another sector with a size larger than the gap
        manager.reserve_space(10 * SectorSize)
        self.assertEqual([sector_0, sector_1, sector_10, sector_11_21], manager.sectors)

        # Reserve part of the gap
        manager.reserve_space(7 * SectorSize)
        self.assertEqual(
            [sector_0, sector_1, sector_2_9, sector_10, sector_11_21], manager.sectors
        )

        # Reserve another space too large for the gap
        manager.reserve_space(2 * SectorSize)
        self.assertEqual(
            [sector_0, sector_1, sector_2_9, sector_10, sector_11_21, sector_21_23],
            manager.sectors,
        )

        # Reserve the last part of the gap
        manager.reserve_space(1 * SectorSize)
        self.assertEqual(
            [
                sector_0,
                sector_1,
                sector_2_9,
                sector_9_10,
                sector_10,
                sector_11_21,
                sector_21_23,
            ],
            manager.sectors,
        )

    def test_sector_merge(self) -> None:
        # Create the manager
        manager = SectorManager(0, 0)
        self.assertEqual([], manager.sectors)

        manager.reserve(sector_1)
        manager.reserve(sector_2_9)
        manager.reserve(sector_9_10)
        manager.reserve(sector_10)
        self.assertEqual(
            [sector_1, sector_2_9, sector_9_10, sector_10], manager.sectors
        )

        # Free and merge
        manager.free(sector_2_9)
        manager.free(sector_9_10)
        self.assertEqual([sector_1, sector_10], manager.sectors)
        manager.reserve_space(8 * SectorSize)
        self.assertEqual([sector_1, sector_2_10, sector_10], manager.sectors)

        # reset
        manager.free(sector_2_10)
        manager.reserve(sector_2_9)
        manager.reserve(sector_9_10)
        self.assertEqual(
            [sector_1, sector_2_9, sector_9_10, sector_10], manager.sectors
        )

        # Repeat with reserve
        manager.free(sector_2_9)
        manager.free(sector_9_10)
        self.assertEqual([sector_1, sector_10], manager.sectors)
        manager.reserve(sector_2_10)
        self.assertEqual([sector_1, sector_2_10, sector_10], manager.sectors)

    def test_free_unreserved(self) -> None:
        manager = SectorManager(0, 0)
        with self.assertRaises(ValueError):
            manager.free(sector_0)

    def test_reserve_error(self) -> None:
        # Create the manager
        manager = SectorManager(0, 0)
        self.assertEqual([], manager.sectors)

        manager.reserve_space(SectorSize)
        with self.assertRaises(NoValidSector):
            manager.reserve(sector_0)

        manager = SectorManager(0, SectorSize, False)
        with self.assertRaises(NoValidSector):
            manager.reserve_space(2 * SectorSize)


if __name__ == "__main__":
    unittest.main()
