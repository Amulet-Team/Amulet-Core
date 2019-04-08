import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import unittest

import json
import numpy

from api.block import Block
from api.errors import ChunkDoesntExistException
from api.selection import SubBox, SelectionBox
from api.chunk import SubChunk
from api import world_loader
from api.nbt_template import NBTEntry, NBTCompoundEntry, NBTListEntry
from formats.anvil2.anvil2_world import _decode_long_array, _encode_long_array
from test_utils import get_world_path, get_data_path, timeout


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):
        def _setUp(self, world_name):
            self.world = world_loader.loader.load_world(get_world_path(world_name))

        def tearDown(self):
            self.world.exit()

        def test_get_block(self):
            self.assertEqual("minecraft:air", self.world.get_block(0, 0, 0).blockstate)
            self.assertEqual(
                "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
            )
            self.assertEqual(
                "minecraft:polished_granite", self.world.get_block(1, 70, 7).blockstate
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
            with timeout(self, 0.5, show_completion_time=True):
                subbx1 = SubBox((1, 70, 3), (1, 70, 4))
                src_box = SelectionBox((subbx1,))

                subbx2 = SubBox((1, 70, 5), (1, 70, 6))
                target_box = SelectionBox((subbx2,))

                self.assertEqual(
                    "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
                )  # Sanity check
                self.assertEqual(
                    "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
                )

                self.world.run_operation_from_operation_name(
                    "clone", src_box, target_box
                )

                self.assertEqual(
                    "minecraft:stone", self.world.get_block(1, 70, 5).blockstate
                )

                self.world.undo()

                self.assertEqual(
                    "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
                )

                self.world.redo()

                self.assertEqual(
                    "minecraft:stone", self.world.get_block(1, 70, 5).blockstate
                )

                self.world.undo()

                self.assertEqual(
                    "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
                )

        def test_fill_operation(self):
            with timeout(self, 0.5, show_completion_time=True):
                subbox_1 = SubBox((1, 70, 3), (5, 71, 5))
                box = SelectionBox((subbox_1,))

                # Start sanity check
                self.assertEqual(
                    "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
                )
                self.assertEqual(
                    "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
                )
                # End sanity check

                self.world.run_operation_from_operation_name(
                    "fill", box, Block("minecraft:stone")
                )

                for x, y, z in box:
                    self.assertEqual(
                        "minecraft:stone",
                        self.world.get_block(x, y, z).blockstate,
                        f"Failed at coordinate ({x},{y},{z})",
                    )

                self.world.undo()

                self.assertEqual(
                    "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
                )

                self.assertEqual(
                    "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
                )

                self.world.redo()

                for x, y, z in box:
                    self.assertEqual(
                        "minecraft:stone",
                        self.world.get_block(x, y, z).blockstate,
                        f"Failed at coordinate ({x},{y},{z})",
                    )

        def test_delete_chunk(self):
            subbox1 = SubBox((1, 1, 1), (5, 5, 5))
            box1 = SelectionBox((subbox1,))

            self.assertEqual(
                "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
            )

            self.world.run_operation_from_operation_name("delete_chunk", box1)

            with self.assertRaises(ChunkDoesntExistException):
                _ = self.world.get_block(1, 70, 3).blockstate

            self.assertEqual(
                0, len([x for x in self.world.get_sub_chunks(*subbox1.to_slice())])
            )

            self.world.undo()

            self.assertEqual(
                "minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "minecraft:granite", self.world.get_block(1, 70, 5).blockstate
            )

            self.world.redo()

            with self.assertRaises(ChunkDoesntExistException):
                _ = self.world.get_block(1, 70, 3).blockstate

            self.assertEqual(
                0, len([x for x in self.world.get_sub_chunks(*subbox1.to_slice())])
            )

        @unittest.skip
        def test_get_entities(
            self
        ):  # TODO: Make a more complete test once we figure out what get_entities() returns
            box1 = SelectionBox((SubBox((0, 0, 0), (16, 16, 16)),))

            print("--" * 16)
            result = self.world.get_entities_in_box(box1)
            with result as entities:
                self.assertEqual(
                    entities, {}
                )  # TODO: Change this when we use a better test world

                ent = {"Pos": [10.0, 3.0, 10.0], "id": "test"}
                entities.add_entity(ent)
                self.assertEqual(1, len(entities[(0, 0)]))
                # self.assertNotIn((1, 1), entities)
                ent["Pos"] = [20.42, 5.79, 20.5]
                self.assertEqual(
                    1, len(entities[(0, 0)])
                )  # Hasn't been re-organized yet
                # self.assertNotIn((1, 1), entities)
                print(entities)
                ent["test"] = False
                print(entities)
                # entities.remove_entity(ent)
                print(entities)
            print(result._entities)

            # All entities have now been re-organized into their proper chunks
            self.assertEqual(0, len(entities[(0, 0)]))
            self.assertEqual(1, len(entities[(1, 1)]))


class AnvilWorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("1.12.2 World")


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("1.13 World")

    def test_longarray(self):

        with open(get_data_path("longarraytest.json")) as json_data:
            test_data = json.load(json_data)

        test_ran = False
        for test_entry in test_data["tests"]:
            test_ran = True
            block_array = test_entry["block_array"]
            long_array = test_entry["long_array"]
            palette_size = test_entry["palette_size"]

            self.assertTrue(
                numpy.array_equal(
                    block_array, _decode_long_array(long_array, len(block_array))
                )
            )

            self.assertTrue(
                numpy.array_equal(
                    long_array, _encode_long_array(block_array, palette_size)
                )
            )

        # Make sure some test are ran in case the data file failed to load or has a wrong format.
        self.assertTrue(test_ran)


if __name__ == "__main__":
    unittest.main()
