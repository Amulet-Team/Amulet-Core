import unittest

from api.selection import AbstractSelection
from test_utils import get_world_path

from formats import format_loader


class AnvilWorldTestCase(unittest.TestCase):

    def setUp(self):
        self.world = format_loader.loader.load_world(get_world_path("1.12.2 World"))

    def test_get_block(self):
        self.assertEqual(self.world.get_block(0, 0, 0), "minecraft:air")
        self.assertEqual(self.world.get_block(1, 70, 3), "minecraft:stone")
        self.assertEqual(self.world.get_block(1, 70, 5), "minecraft:granite")
        self.assertEqual(self.world.get_block(1, 70, 7), "minecraft:polished_granite")

        with self.assertRaises(IndexError):
            self.world.get_block(300, 300, 300)

    def test_get_blocks(self):
        self.assertIsInstance(
            next(self.world.get_blocks(slice(0, 10), slice(0, 10), slice(0, 10))),
            AbstractSelection
        )
        self.assertIsInstance(next(self.world.get_blocks(0, 0, 0, 10, 10, 10)), AbstractSelection)
        self.assertIsInstance(
            next(self.world.get_blocks(0, 0, 0, 10, 10, 10, 2, 2, 2)), AbstractSelection
        )

        with self.assertRaises(IndexError):
            self.world.get_blocks()

            self.world.get_blocks(slice(0, 10, 2))
            self.world.get_blocks(slice(0, 10, 2), slice(0, 10, 2))

            self.world.get_blocks(0)
            self.world.get_blocks(0, 0)
            self.world.get_blocks(0, 0, 0)


class Anvil2WorldTestCase(unittest.TestCase):

    def setUp(self):
        self.world = format_loader.loader.load_world(get_world_path("1.13 World"))

    def test_get_block(self):
        self.assertEqual(self.world.get_block(0, 0, 0), "minecraft:air")
        self.assertEqual(self.world.get_block(1, 70, 3), "minecraft:stone")
        self.assertEqual(self.world.get_block(1, 70, 5), "minecraft:granite")
        self.assertEqual(self.world.get_block(1, 70, 7), "minecraft:polished_granite")

        with self.assertRaises(IndexError):
            self.world.get_block(300, 300, 300)

    def test_get_blocks(self):
        self.assertIsInstance(
            next(self.world.get_blocks(slice(0, 10), slice(0, 10), slice(0, 10))),
            AbstractSelection
        )
        self.assertIsInstance(next(self.world.get_blocks(0, 0, 0, 10, 10, 10)), AbstractSelection)
        self.assertIsInstance(
            next(self.world.get_blocks(0, 0, 0, 10, 10, 10, 2, 2, 2)), AbstractSelection
        )

        with self.assertRaises(IndexError):
            self.world.get_blocks()

            self.world.get_blocks(slice(0, 10, 2))
            self.world.get_blocks(slice(0, 10, 2), slice(0, 10, 2))

            self.world.get_blocks(0)
            self.world.get_blocks(0, 0)
            self.world.get_blocks(0, 0, 0)


if __name__ == "__main__":
    unittest.main()
