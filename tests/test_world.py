import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import unittest

import json
import numpy

from api.selection import SubBox, SelectionBox
from api.chunk import SubChunk
from api import world_loader
from utils.world_utils import decode_long_array, encode_long_array
from test_utils import get_world_path, get_data_path


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):

        def _setUp(self, world_name):
            self.world = world_loader.loader.load_world(get_world_path(world_name))

        def tearDown(self):
            self.world.exit()

        def test_get_block(self):
            self.assertEqual("minecraft:air", self.world.get_block(0, 0, 0))
            self.assertEqual("minecraft:stone", self.world.get_block(1, 70, 3))
            self.assertEqual("minecraft:granite", self.world.get_block(1, 70, 5))
            self.assertEqual(
                "minecraft:polished_granite", self.world.get_block(1, 70, 7)
            )

            with self.assertRaises(IndexError):
                self.world.get_block(300, 300, 300)

        def test_get_blocks(self):
            self.assertIsInstance(
                next(
                    self.world.get_sub_chunks(slice(0, 10), slice(0, 10), slice(0, 10))
                ),
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
                "minecraft:stone", self.world.get_block(1, 70, 3)
            )  # Sanity check
            self.assertEqual("minecraft:granite", self.world.get_block(1, 70, 5))

            self.world.run_operation_from_operation_name("clone", src_box, target_box)

            self.assertEqual("minecraft:stone", self.world.get_block(1, 70, 5))

            self.world.undo()

            self.assertEqual("minecraft:granite", self.world.get_block(1, 70, 5))

            self.world.redo()

            self.assertEqual("minecraft:stone", self.world.get_block(1, 70, 5))

            self.world.undo()

            self.assertEqual("minecraft:granite", self.world.get_block(1, 70, 5))

        def test_fill_operation(self):
            subbox_1 = SubBox((1, 70, 3), (5, 71, 5))
            box = SelectionBox((subbox_1,))

            self.world.run_operation_from_operation_name("fill", box, "minecraft:stone")

            for x, y, z in box:
                self.assertEqual(
                    "minecraft:stone",
                    self.world.get_block(x, y, z),
                    f"Failed at coordinate ({x},{y},{z})",
                )

            self.world.undo()

            self.assertEqual("minecraft:stone", self.world.get_block(1, 70, 3))
            self.assertEqual("minecraft:granite", self.world.get_block(1, 70, 5))


class AnvilWorldTestCase(WorldTestBaseCases.WorldTestCase):

    def setUp(self):
        self._setUp("1.12.2 World")


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):

    def setUp(self):
        self._setUp("1.13 World")

    def test_longarray(self):

        with open(get_data_path("longarraytest.json")) as json_data:
            test_data = json.load(json_data)

        test_ran = 0
        for test_entry in test_data["tests"]:
            test_ran += 1
            block_array = test_entry["block_array"]
            long_array = test_entry["long_array"]
            palette_size = test_entry["palette_size"]

            self.assertTrue(
                numpy.array_equal(
                    block_array, decode_long_array(long_array, len(block_array))
                )
            )

            self.assertTrue(
                numpy.array_equal(
                    long_array, encode_long_array(block_array, palette_size)
                )
            )

        #Make sure some test are ran in case the data file failed to load or has a wrong format.
        self.assertTrue(test_ran > 0)


if __name__ == "__main__":
    unittest.main()
