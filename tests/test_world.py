import unittest

import json
import numpy

from amulet.api.block import Block
from amulet.api.errors import ChunkDoesNotExist
from amulet.api.selection import SubBox, SelectionBox
from amulet.api.chunk import SubChunk
from amulet.world_interface import load_world, load_format
from test_utils import get_world_path, get_data_path, timeout

import os.path as op


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):
        def _setUp(self, world_name):
            self.world = load_world(get_world_path(world_name))

        def tearDown(self):
            self.world.close()

        def test_get_block(self):
            self.assertEqual(
                "universal_minecraft:air", self.world.get_block(0, 0, 0).blockstate
            )
            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=true]",
                self.world.get_block(1, 70, 7).blockstate,
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
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )  # Sanity check
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.run_operation_from_operation_name("clone", src_box, target_box)

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 5).blockstate
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.redo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 5).blockstate
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

        def test_fill_operation(self):
            subbox_1 = SubBox((1, 70, 3), (5, 71, 5))
            box = SelectionBox((subbox_1,))

            # Start sanity check
            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )
            # End sanity check

            self.world.run_operation_from_operation_name(
                "fill", box, Block("universal_minecraft:stone")
            )

            for x, y, z in box:
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(x, y, z).blockstate,
                    f"Failed at coordinate ({x},{y},{z})",
                )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )

            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.redo()

            for x, y, z in box:
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(x, y, z).blockstate,
                    f"Failed at coordinate ({x},{y},{z})",
                )

        def test_replace_single_block(self):
            subbox1 = SubBox((1, 70, 3), (5, 71, 5))
            box1 = SelectionBox((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.run_operation_from_operation_name(
                "replace",
                box1,
                [Block("universal_minecraft:granite[polished=false]")],
                [Block("universal_minecraft:stone")],
            )

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 5).blockstate
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.redo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 5).blockstate
            )

        def test_replace_multiblock(self):
            subbox1 = SubBox((1, 70, 3), (1, 75, 3))
            box1 = SelectionBox((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            for i in range(1, 5):
                self.assertEqual(
                    "universal_minecraft:air",
                    self.world.get_block(1, 70 + i, 3).blockstate,
                    f"Failed at coordinate (1,i,3)",
                )

            self.world.run_operation_from_operation_name(
                "replace",
                box1,
                [Block("universal_minecraft:stone"), Block("universal_minecraft:air")],
                [
                    Block("universal_minecraft:granite[polished=false]"),
                    Block("universal_minecraft:stone"),
                ],
            )

            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 3).blockstate,
            )

            for i in range(1, 5):
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(1, 70 + i, 3).blockstate,
                    f"Failed at coordinate (1,i,3)",
                )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            for i in range(1, 5):
                self.assertEqual(
                    "universal_minecraft:air",
                    self.world.get_block(1, 70 + i, 3).blockstate,
                    f"Failed at coordinate (1,i,3)",
                )

            self.world.redo()

            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 3).blockstate,
            )

            for i in range(1, 5):
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(1, 70 + i, 3).blockstate,
                    f"Failed at coordinate (1,i,3)",
                )

        def test_delete_chunk(self):
            subbox1 = SubBox((1, 1, 1), (5, 5, 5))
            box1 = SelectionBox((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.run_operation_from_operation_name("delete_chunk", box1)

            with self.assertRaises(ChunkDoesNotExist):
                _ = self.world.get_block(1, 70, 3).blockstate

            self.assertEqual(
                0, len([x for x in self.world.get_sub_chunks(*subbox1.to_slice())])
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone", self.world.get_block(1, 70, 3).blockstate
            )
            self.assertEqual(
                "universal_minecraft:granite[polished=false]",
                self.world.get_block(1, 70, 5).blockstate,
            )

            self.world.redo()

            with self.assertRaises(ChunkDoesNotExist):
                _ = self.world.get_block(1, 70, 3).blockstate

            self.assertEqual(
                0, len([x for x in self.world.get_sub_chunks(*subbox1.to_slice())])
            )

        @unittest.skipUnless(
            op.exists(get_world_path("1.12.2 World to 1.13 World"))
            and op.exists(get_world_path("1.13 World to 1.12.2 World")),
            reason="Output worlds do not exist",
        )
        def test_save(self):
            output_wrapper = None
            version_string = self.world.world_wrapper.game_version_string

            if "1.12.2" in version_string:
                output_wrapper = load_format(
                    get_world_path("1.12.2 World to 1.13 World")
                )
            else:
                output_wrapper = load_format(
                    get_world_path("1.13 World to 1.12.2 World")
                )
            output_wrapper.open()

            self.world.save(output_wrapper)
            self.world.close()
            output_wrapper.close()

        @unittest.skip("Entity API currently being rewritten")
        def test_get_entities(
            self
        ):  # TODO: Make a more complete test once we figure out what get_entities() returns
            box1 = SelectionBox((SubBox((0, 0, 0), (17, 20, 17)),))

            test_entity = {
                "id": "universal_minecraft:cow",
                "CustomName": "TestName",
                "Pos": [1.0, 4.0, 1.0],
            }

            entity_iter = self.world.get_entities_in_box(box1)
            for chunk_coords, entities in entity_iter:
                self.assertEqual(0, len(entities))

            self.world.add_entities([test_entity])

            entity_iter = self.world.get_entities_in_box(box1)
            for chunk_coords, entities in entity_iter:
                if chunk_coords == (0, 0):
                    self.assertEqual(1, len(entities))
                    test_entity["Pos"] = entities[0]["Pos"] = [17.0, 20.0, 17.0]
                else:
                    self.assertEqual(0, len(entities))

            entity_iter = self.world.get_entities_in_box(box1)
            for chunk_coords, entities in entity_iter:
                if chunk_coords == (1, 1):
                    self.assertEqual(1, len(entities))
                else:
                    self.assertEqual(0, len(entities))

            self.world.delete_entities([test_entity])

            entity_iter = self.world.get_entities_in_box(box1)
            for chunk_coords, entities in entity_iter:
                self.assertEqual(0, len(entities))


class AnvilWorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("1.12.2 World")


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("1.13 World")

    @unittest.skip
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
