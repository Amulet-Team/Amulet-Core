from unittest import TestCase

from amulet.utils.lock import OrderedLock
from amulet.block import Block, BlockStack
from amulet.chunk import ChunkDoesNotExist
from amulet.chunk_components import BlockComponent
from amulet.level.java import (
    JavaLevel,
    JavaDimension,
    JavaChunkHandle,
)
from amulet.level.java.chunk import JavaChunk

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp


class JavaChunkHandleTestCase(TestCase):
    def test_exists_chunk(self) -> None:
        input("Press Enter to continue...")
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
                self.assertEqual(
                    "minecraft:overworld", chunk_handle.dimension_id
                )

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
                chunk.block.palette.block_stack_to_index(block_stack)
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
                self.assertEqual(block_stack, chunk_3.block.palette.index_to_block_stack(67))

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
                self.assertEqual(block_stack, chunk_4.block.palette.index_to_block_stack(67))

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
                self.assertEqual(
                    "minecraft:overworld", chunk_handle.dimension_id
                )

                self.assertIsInstance(chunk_handle.cx, int)
                self.assertEqual(100, chunk_handle.cx)

                self.assertIsInstance(chunk_handle.cz, int)
                self.assertEqual(200, chunk_handle.cz)

                self.assertFalse(chunk_handle.exists())


            finally:
                level.close()
