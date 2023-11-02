import unittest
from amulet.block import Block, BlockStack
from amulet.palette import BlockPalette
from amulet.game_version import JavaGameVersion, GameVersionRange


dirt = Block.from_string_blockstate(JavaGameVersion(3578), "minecraft:dirt")
stone = Block.from_string_blockstate(JavaGameVersion(3578), "minecraft:stone")
granite = Block.from_string_blockstate(JavaGameVersion(3578), "minecraft:granite")
water = Block.from_string_blockstate(JavaGameVersion(3578), "minecraft:water")
waterlogged_dirt = BlockStack(dirt, water)


class BlockManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.palette = BlockPalette(
            GameVersionRange(JavaGameVersion(3578), JavaGameVersion(3578))
        )

        # Partially populate the manager
        self.palette.block_stack_to_index(BlockStack(dirt))
        self.palette.block_stack_to_index(BlockStack(stone))
        self.palette.block_stack_to_index(BlockStack(granite))
        self.palette.block_stack_to_index(BlockStack(water))
        self.palette.block_stack_to_index(waterlogged_dirt)

    def test_get_item(self):
        self.assertEqual(BlockStack(dirt), self.palette[0])
        self.assertEqual(BlockStack(stone), self.palette[1])
        self.assertEqual(BlockStack(granite), self.palette[2])
        self.assertEqual(BlockStack(water), self.palette[3])
        self.assertEqual(waterlogged_dirt, self.palette[4])

    def test_index_to_block_stack(self):
        self.assertEqual(BlockStack(dirt), self.palette.index_to_block_stack(0))
        self.assertEqual(BlockStack(stone), self.palette.index_to_block_stack(1))
        self.assertEqual(BlockStack(granite), self.palette.index_to_block_stack(2))
        self.assertEqual(BlockStack(water), self.palette.index_to_block_stack(3))
        self.assertEqual(waterlogged_dirt, self.palette.index_to_block_stack(4))

    def test_block_stack_to_index(self):
        self.assertEqual(0, self.palette.block_stack_to_index(BlockStack(dirt)))
        self.assertEqual(1, self.palette.block_stack_to_index(BlockStack(stone)))
        self.assertEqual(2, self.palette.block_stack_to_index(BlockStack(granite)))
        self.assertEqual(3, self.palette.block_stack_to_index(BlockStack(water)))
        self.assertEqual(4, self.palette.block_stack_to_index(waterlogged_dirt))
        self.assertEqual(
            5,
            self.palette.block_stack_to_index(
                BlockStack(
                    Block.from_string_blockstate(JavaGameVersion(3578), "a:b[c=d]")
                )
            ),
        )

    def test_len(self):
        self.assertEqual(5, len(self.palette))


if __name__ == "__main__":
    unittest.main()
