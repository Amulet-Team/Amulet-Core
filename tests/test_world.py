import unittest

from api.box import SubBox, SelectionBox
from api.chunk import SubChunk
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
            next(self.world.get_sub_chunks(slice(0, 10), slice(0, 10), slice(0, 10))),
            SubChunk,
        )
        self.assertIsInstance(
            next(self.world.get_sub_chunks(0, 0, 0, 10, 10, 10)), SubChunk
        )
        self.assertIsInstance(
            next(self.world.get_sub_chunks(0, 0, 0, 10, 10, 10, 2, 2, 2)), SubChunk
        )

        with self.assertRaises(IndexError):
            next(self.world.get_sub_chunks())

            next(self.world.get_sub_chunks(slice(0, 10, 2)))
            next(self.world.get_sub_chunks(slice(0, 10, 2), slice(0, 10, 2)))

            next(self.world.get_sub_chunks(0))
            next(self.world.get_sub_chunks(0, 0))
            next(self.world.get_sub_chunks(0, 0, 0))


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
            next(self.world.get_sub_chunks(slice(0, 10), slice(0, 10), slice(0, 10))),
            SubChunk,
        )
        self.assertIsInstance(
            next(self.world.get_sub_chunks(0, 0, 0, 10, 10, 10)), SubChunk
        )
        self.assertIsInstance(
            next(self.world.get_sub_chunks(0, 0, 0, 10, 10, 10, 2, 2, 2)), SubChunk
        )

        with self.assertRaises(IndexError):
            next(self.world.get_sub_chunks())

            next(self.world.get_sub_chunks(slice(0, 10, 2)))
            next(self.world.get_sub_chunks(slice(0, 10, 2), slice(0, 10, 2)))

            next(self.world.get_sub_chunks(0))
            next(self.world.get_sub_chunks(0, 0))
            next(self.world.get_sub_chunks(0, 0, 0))

    def test_clone_operation(self):

        subbx1 = SubBox((1, 70, 3), (1, 70, 4))
        src_box = SelectionBox((subbx1,))

        subbx2 = SubBox((1, 70, 5), (1, 70, 6))
        target_box = SelectionBox((subbx2,))

        self.assertEqual(
            self.world.get_block(1, 70, 3), "minecraft:stone"
        )  # Sanity check
        self.assertEqual(self.world.get_block(1, 70, 5), "minecraft:granite")

        self.world.run_operation("clone", src_box, target_box)

        self.assertEqual("minecraft:stone", self.world.get_block(1, 70, 5))


if __name__ == "__main__":
    unittest.main()
