import unittest

import json
import numpy
import os

from amulet.api.block import Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from amulet.api.selection import SelectionBox, SelectionGroup
from amulet import load_level, load_format
from tests.test_utils import (
    get_world_path,
    get_data_path,
    create_temp_world,
    clean_temp_world,
)
from amulet.operations.clone import clone
from amulet.operations.delete_chunk import delete_chunk
from amulet.operations.fill import fill
from amulet.operations.replace import replace


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):
        def _setUp(self, world_name):
            self._world_name = world_name
            self.world = load_level(create_temp_world(world_name))

        def tearDown(self):
            self.world.close()
            clean_temp_world(self._world_name)

        def test_get_block(self):
            self.assertEqual(
                "universal_minecraft:air",
                self.world.get_block(0, 0, 0, "overworld").blockstate,
            )
            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=true]',
                self.world.get_block(1, 70, 7, "overworld").blockstate,
            )

        def test_get_blocks(self):
            selection_box = SelectionBox((0, 0, 0), (10, 10, 10))
            for selection in [SelectionGroup(selection_box), selection_box]:
                chunk, box = next(self.world.get_chunk_boxes("overworld", selection))
                self.assertIsInstance(chunk, Chunk)
                self.assertIsInstance(box, SelectionBox)

                chunk, slices, _ = next(
                    self.world.get_chunk_slice_box("overworld", selection)
                )
                self.assertIsInstance(chunk, Chunk)
                self.assertIsInstance(slices, tuple)
                for s in slices:
                    self.assertIsInstance(s, slice)

        def test_clone_operation(self):
            subbx1 = SelectionBox((1, 70, 3), (2, 71, 4))
            src_box = SelectionGroup((subbx1,))

            target = {"x": 1, "y": 70, "z": 5}

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )  # Sanity check
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.run_operation(clone, "overworld", src_box, target)

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.undo()

            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.redo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.undo()

            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

        def test_fill_operation(self):
            subbox_1 = SelectionBox((1, 70, 3), (5, 71, 5))
            box = SelectionGroup((subbox_1,))

            # Start sanity check
            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )
            # End sanity check

            self.world.run_operation(
                fill, "overworld", box, Block.from_string_blockstate("universal_minecraft:stone")
            )

            for x, y, z in box:
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(x, y, z, "overworld").blockstate,
                    f"Failed at coordinate ({x},{y},{z})",
                )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )

            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.redo()

            for x, y, z in box:
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(x, y, z, "overworld").blockstate,
                    f"Failed at coordinate ({x},{y},{z})",
                )

        def test_replace_single_block(self):
            subbox1 = SelectionBox((1, 70, 3), (5, 71, 6))
            box1 = SelectionGroup((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.run_operation(
                replace,
                "overworld",
                box1,
                {
                    "original_blocks": [
                        Block.from_string_blockstate(
                            "universal_minecraft:granite[polished=false]"
                        )
                    ],
                    "replacement_blocks": [
                        Block.from_string_blockstate("universal_minecraft:stone")
                    ],
                },
            )

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.redo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

        def test_replace_multiblock(self):
            subbox1 = SelectionBox((1, 70, 3), (2, 75, 4))
            box1 = SelectionGroup((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            for y in range(71, 75):
                self.assertEqual(
                    "universal_minecraft:air",
                    self.world.get_block(1, y, 3, "overworld").blockstate,
                    f"Failed at coordinate (1,{y},3)",
                )

            self.world.run_operation(
                replace,
                "overworld",
                box1,
                {
                    "original_blocks": [
                        Block.from_string_blockstate("universal_minecraft:stone"),
                        Block.from_string_blockstate("universal_minecraft:air"),
                    ],
                    "replacement_blocks": [
                        Block.from_string_blockstate(
                            "universal_minecraft:granite[polished=false]"
                        ),
                        Block.from_string_blockstate("universal_minecraft:stone"),
                    ],
                },
            )

            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )

            for y in range(71, 75):
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(1, y, 3, "overworld").blockstate,
                    f"Failed at coordinate (1,{y},3)",
                )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            for y in range(71, 75):
                self.assertEqual(
                    "universal_minecraft:air",
                    self.world.get_block(1, y, 3, "overworld").blockstate,
                    f"Failed at coordinate (1,{y},3)",
                )

            self.world.redo()

            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )

            for y in range(71, 75):
                self.assertEqual(
                    "universal_minecraft:stone",
                    self.world.get_block(1, y, 3, "overworld").blockstate,
                    f"Failed at coordinate (1,{y},3)",
                )

        def test_delete_chunk(self):
            subbox1 = SelectionBox((1, 1, 1), (5, 5, 5))
            box1 = SelectionGroup((subbox1,))

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.run_operation(delete_chunk, "overworld", box1)

            with self.assertRaises(ChunkDoesNotExist):
                _ = self.world.get_block(1, 70, 3, "overworld").blockstate

            self.assertEqual(
                0,
                len([x for x in self.world.get_chunk_slice_box("overworld", subbox1)]),
            )

            self.world.undo()

            self.assertEqual(
                "universal_minecraft:stone",
                self.world.get_block(1, 70, 3, "overworld").blockstate,
            )
            self.assertEqual(
                'universal_minecraft:granite[polished=false]',
                self.world.get_block(1, 70, 5, "overworld").blockstate,
            )

            self.world.redo()

            with self.assertRaises(ChunkDoesNotExist):
                _ = self.world.get_block(1, 70, 3, "overworld").blockstate

            self.assertEqual(
                0,
                len([x for x in self.world.get_chunk_slice_box("overworld", subbox1)]),
            )

        @unittest.skipUnless(
            os.path.exists(get_world_path("Java 1.12.2"))
            and os.path.exists(get_world_path("Java 1.13")),
            reason="Output worlds do not exist",
        )
        def test_save(self):
            version_string = self.world.level_wrapper.game_version_string

            if "1.12.2" in version_string:
                world_name = "Java 1.13"
                world_name_temp = "Java 1.12.2 to Java 1.13"
            else:
                world_name = "Java 1.12.2"
                world_name_temp = "Java 1.13 to Java 1.12.2"

            output_wrapper = load_format(create_temp_world(world_name, world_name_temp))
            output_wrapper.open()

            self.world.save(output_wrapper)
            self.world.close()
            output_wrapper.close()

            clean_temp_world(world_name_temp)

        @unittest.skip("Entity API currently being rewritten")
        def test_get_entities(
            self,
        ):  # TODO: Make a more complete test once we figure out what get_entities() returns
            box1 = SelectionGroup((SelectionBox((0, 0, 0), (17, 20, 17)),))

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
        self._setUp("Java 1.12.2")


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("Java 1.13")


if __name__ == "__main__":
    unittest.main()
