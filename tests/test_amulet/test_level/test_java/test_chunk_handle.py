from unittest import TestCase

from amulet.utils.lock import OrderedLock
from amulet.version import VersionNumber
from amulet.block import Block, BlockStack
from amulet.biome import Biome
from amulet.chunk import ChunkDoesNotExist
from amulet.chunk import Chunk
from amulet.chunk_components import BlockComponent
from amulet.level.java import (
    JavaLevel,
    JavaDimension,
    JavaChunkHandle,
)
from amulet.level.java.chunk import JavaChunk, JavaChunk1444, JavaChunk1466

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp


class JavaChunkHandleTestCase(TestCase):
    def test_exists_chunk(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                overworld = level.get_dimension("minecraft:overworld")
                self.assertIsInstance(overworld, JavaDimension)

                chunk_handle = overworld.get_chunk_handle(1, 2)
                self.assertIsInstance(chunk_handle, JavaChunkHandle)

                self.assertIsInstance(chunk_handle.lock, OrderedLock)

                self.assertIsInstance(chunk_handle.dimension_id, str)
                self.assertEqual("minecraft:overworld", chunk_handle.dimension_id)

                self.assertIsInstance(chunk_handle.cx, int)
                self.assertEqual(1, chunk_handle.cx)

                self.assertIsInstance(chunk_handle.cz, int)
                self.assertEqual(2, chunk_handle.cz)

                self.assertTrue(chunk_handle.exists())

                # load the first time
                chunk = chunk_handle.get_chunk()
                self.assertIsInstance(chunk, JavaChunk)
                self.assertIsInstance(chunk, BlockComponent)
                assert isinstance(chunk, BlockComponent)
                self.assertEqual(67, len(chunk.block.palette))

                # modify the chunk
                block_stack = BlockStack(
                    Block(
                        "java",
                        chunk.block.palette.version_range.max_version,
                        "my_namespace",
                        "my_basename",
                    )
                )
                self.assertEqual(
                    67, chunk.block.palette.block_stack_to_index(block_stack)
                )
                self.assertEqual(68, len(chunk.block.palette))

                # reload it from the cache
                chunk_2 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_2, JavaChunk)
                self.assertIs(chunk_2.__class__, chunk.__class__)
                self.assertIsInstance(chunk_2, BlockComponent)
                assert isinstance(chunk_2, BlockComponent)
                self.assertEqual(67, len(chunk_2.block.palette))

                # override it
                chunk_handle.set_chunk(chunk)

                chunk_3 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_3, JavaChunk)
                self.assertIs(chunk_3.__class__, chunk.__class__)
                assert isinstance(chunk_3, BlockComponent)
                self.assertEqual(68, len(chunk_3.block.palette))
                self.assertEqual(
                    block_stack, chunk_3.block.palette.index_to_block_stack(67)
                )

                # delete it
                chunk_handle.delete_chunk()
                self.assertFalse(chunk_handle.exists())
                with self.assertRaises(ChunkDoesNotExist):
                    chunk_handle.get_chunk()

                # set it again
                chunk_handle.set_chunk(chunk)
                chunk_4 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_4, JavaChunk)
                self.assertIs(chunk_4.__class__, chunk.__class__)
                assert isinstance(chunk_4, BlockComponent)
                self.assertEqual(68, len(chunk_4.block.palette))
                self.assertEqual(
                    block_stack, chunk_4.block.palette.index_to_block_stack(67)
                )

            finally:
                level.close()

    def test_not_exists_chunk(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                overworld = level.get_dimension("minecraft:overworld")
                self.assertIsInstance(overworld, JavaDimension)

                chunk_handle = overworld.get_chunk_handle(100, 200)
                self.assertIsInstance(chunk_handle, JavaChunkHandle)

                self.assertIsInstance(chunk_handle.lock, OrderedLock)

                self.assertIsInstance(chunk_handle.dimension_id, str)
                self.assertEqual("minecraft:overworld", chunk_handle.dimension_id)

                self.assertIsInstance(chunk_handle.cx, int)
                self.assertEqual(100, chunk_handle.cx)

                self.assertIsInstance(chunk_handle.cz, int)
                self.assertEqual(200, chunk_handle.cz)

                # Make sure the chunk doesn't exist
                self.assertFalse(chunk_handle.exists())
                with self.assertRaises(ChunkDoesNotExist):
                    chunk_handle.get_chunk()

                # Make sure the level supports the chunk we are using
                self.assertLessEqual(VersionNumber(1466), level.max_game_version)

                # Create the chunk
                chunk = JavaChunk1466(
                    1466,
                    BlockStack(Block("java", VersionNumber(1466), "minecraft", "air")),
                    Biome("java", VersionNumber(1466), "minecraft", "plains"),
                )
                self.assertEqual(1, len(chunk.block.palette))

                # Set the chunk
                chunk_handle.set_chunk(chunk)

                self.assertTrue(chunk_handle.exists())
                chunk_2 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_2, JavaChunk1466)
                self.assertEqual(1, len(chunk_2.block.palette))
                self.assertEqual(
                    BlockStack(Block("java", VersionNumber(1466), "minecraft", "air")),
                    chunk_2.block.palette.index_to_block_stack(0),
                )

                # Delete the chunk
                chunk_handle.delete_chunk()
                self.assertFalse(chunk_handle.exists())
                with self.assertRaises(ChunkDoesNotExist):
                    chunk_handle.get_chunk()

            finally:
                level.close()

    def test_undo_redo(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                overworld = level.get_dimension("minecraft:overworld")
                chunk_handle = overworld.get_chunk_handle(1, 2)
                self.assertTrue(chunk_handle.exists())

                # Create a new restore point
                self.assertEqual(0, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                level.create_restore_point()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())

                # load the chunk
                chunk = chunk_handle.get_chunk()
                self.assertIsInstance(chunk, JavaChunk1466)

                def validate_original_chunk(original_chunk: Chunk) -> None:
                    self.assertIsInstance(original_chunk, JavaChunk1466)
                    self.assertEqual(67, len(original_chunk.block.palette))

                validate_original_chunk(chunk)

                # modify the chunk
                block_stack = BlockStack(
                    Block(
                        "java",
                        chunk.block.palette.version_range.max_version,
                        "my_namespace",
                        "my_basename",
                    )
                )
                self.assertEqual(
                    67, chunk.block.palette.block_stack_to_index(block_stack)
                )

                def validate_edited_1(edited_chunk: Chunk) -> None:
                    self.assertIsInstance(edited_chunk, JavaChunk1466)
                    self.assertEqual(68, len(edited_chunk.block.palette))
                    self.assertEqual(
                        block_stack, edited_chunk.block.palette.index_to_block_stack(67)
                    )

                validate_edited_1(chunk)

                # set the chunk
                chunk_handle.set_chunk(chunk)
                validate_edited_1(chunk_handle.get_chunk())

                # undo changes and validate original state
                level.undo()
                self.assertEqual(0, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_original_chunk(chunk_handle.get_chunk())

                # redo changes and validate edited state
                level.redo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                validate_edited_1(chunk_handle.get_chunk())

                # make another change in the same undo bin
                block_stack_2 = BlockStack(
                    Block(
                        "java",
                        chunk.block.palette.version_range.max_version,
                        "my_namespace",
                        "my_basename_2",
                    )
                )
                self.assertEqual(
                    68, chunk.block.palette.block_stack_to_index(block_stack_2)
                )

                def validate_edited_2(edited_chunk: Chunk) -> None:
                    self.assertIsInstance(edited_chunk, JavaChunk1466)
                    self.assertEqual(69, len(edited_chunk.block.palette))
                    self.assertEqual(
                        block_stack, edited_chunk.block.palette.index_to_block_stack(67)
                    )
                    self.assertEqual(
                        block_stack_2,
                        edited_chunk.block.palette.index_to_block_stack(68),
                    )

                validate_edited_2(chunk)
                chunk_handle.set_chunk(chunk)

                # validate the set chunk
                validate_edited_2(chunk_handle.get_chunk())

                # undo changes and validate original state
                level.undo()
                self.assertEqual(0, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_original_chunk(chunk_handle.get_chunk())

                # redo changes and validate edited state
                level.redo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                validate_edited_2(chunk_handle.get_chunk())

                # create a new restore point and make another change
                level.create_restore_point()
                self.assertEqual(2, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                block_stack_3 = BlockStack(
                    Block(
                        "java",
                        chunk.block.palette.version_range.max_version,
                        "my_namespace",
                        "my_basename_3",
                    )
                )
                self.assertEqual(
                    69, chunk.block.palette.block_stack_to_index(block_stack_3)
                )

                def validate_edited_3(edited_chunk: Chunk) -> None:
                    self.assertIsInstance(edited_chunk, JavaChunk1466)
                    self.assertEqual(70, len(edited_chunk.block.palette))
                    self.assertEqual(
                        block_stack, edited_chunk.block.palette.index_to_block_stack(67)
                    )
                    self.assertEqual(
                        block_stack_2,
                        edited_chunk.block.palette.index_to_block_stack(68),
                    )

                validate_edited_3(chunk)
                chunk_handle.set_chunk(chunk)
                validate_edited_3(chunk_handle.get_chunk())

                level.undo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_edited_2(chunk_handle.get_chunk())
                level.undo()
                self.assertEqual(0, level.get_undo_count())
                self.assertEqual(2, level.get_redo_count())
                validate_original_chunk(chunk_handle.get_chunk())
                level.redo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_edited_2(chunk_handle.get_chunk())
                level.redo()
                self.assertEqual(2, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                validate_edited_3(chunk_handle.get_chunk())

                # undo and invalidate the newer undo point
                level.undo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_edited_2(chunk_handle.get_chunk())
                chunk_handle.set_chunk(chunk)
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                validate_edited_3(chunk_handle.get_chunk())
                level.undo()
                self.assertEqual(0, level.get_undo_count())
                self.assertEqual(1, level.get_redo_count())
                validate_original_chunk(chunk_handle.get_chunk())
                level.redo()
                self.assertEqual(1, level.get_undo_count())
                self.assertEqual(0, level.get_redo_count())
                validate_edited_3(chunk_handle.get_chunk())

            finally:
                level.close()

    def test_history_enabled(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                # Create a restore point.
                level.create_restore_point()

                # Get the chunk handle.
                overworld = level.get_dimension("minecraft:overworld")
                chunk_handle = overworld.get_chunk_handle(1, 2)

                # Create and set the chunk.
                chunk = JavaChunk1444(
                    1444,
                    BlockStack(Block("java", VersionNumber(1444), "minecraft", "air")),
                    Biome("java", VersionNumber(1444), "minecraft", "plains"),
                )
                chunk_handle.set_chunk(chunk)

                # History is enabled so the original state should have been loaded when setting.
                level.undo()
                chunk_2 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_2, JavaChunk1466)
                self.assertEqual(67, len(chunk_2.block.palette))

            finally:
                level.close()

    def test_history_disabled(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                # Create a restore point.
                level.create_restore_point()

                # Disable history.
                # Changes from this point will overwrite the previous state.
                # The original state won't be loaded if the chunk is set before being loaded.
                level.history_enabled = False

                # Get the chunk handle.
                overworld = level.get_dimension("minecraft:overworld")
                chunk_handle = overworld.get_chunk_handle(1, 2)

                # Create and set the chunk.
                chunk = JavaChunk1444(
                    1444,
                    BlockStack(Block("java", VersionNumber(1444), "minecraft", "air")),
                    Biome("java", VersionNumber(1444), "minecraft", "plains"),
                )
                chunk_handle.set_chunk(chunk)

                # This chunk wasn't loaded before it was set so this should be set as the original state.
                level.undo()
                chunk_2 = chunk_handle.get_chunk()
                self.assertIsInstance(chunk_2, JavaChunk1444)
                self.assertEqual(1, len(chunk_2.block.palette))

            finally:
                level.close()
