import unittest
from amulet.block import Block, BlockStack
from amulet.palette import BlockPalette
from amulet.version import VersionNumber, VersionRange


dirt = Block.from_java_blockstate("java", VersionNumber(3578), "minecraft:dirt")
stone = Block.from_java_blockstate("java", VersionNumber(3578), "minecraft:stone")
granite = Block.from_java_blockstate("java", VersionNumber(3578), "minecraft:granite")
water = Block.from_java_blockstate("java", VersionNumber(3578), "minecraft:water")
waterlogged_dirt = BlockStack(dirt, water)


class BlockPaletteTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.palette = BlockPalette(
            VersionRange("java", VersionNumber(3578), VersionNumber(3578))
        )

        # Partially populate the palette
        self.palette.block_stack_to_index(BlockStack(dirt))
        self.palette.block_stack_to_index(BlockStack(stone))
        self.palette.block_stack_to_index(BlockStack(granite))
        self.palette.block_stack_to_index(BlockStack(water))
        self.palette.block_stack_to_index(waterlogged_dirt)

    def test_get_item(self) -> None:
        self.assertEqual(BlockStack(dirt), self.palette[0])
        self.assertEqual(BlockStack(stone), self.palette[1])
        self.assertEqual(BlockStack(granite), self.palette[2])
        self.assertEqual(BlockStack(water), self.palette[3])
        self.assertEqual(waterlogged_dirt, self.palette[4])
        with self.assertRaises(IndexError):
            self.palette[5]

    def test_index_to_block_stack(self) -> None:
        self.assertEqual(BlockStack(dirt), self.palette.index_to_block_stack(0))
        self.assertEqual(BlockStack(stone), self.palette.index_to_block_stack(1))
        self.assertEqual(BlockStack(granite), self.palette.index_to_block_stack(2))
        self.assertEqual(BlockStack(water), self.palette.index_to_block_stack(3))
        self.assertEqual(waterlogged_dirt, self.palette.index_to_block_stack(4))
        with self.assertRaises(IndexError):
            self.palette.index_to_block_stack(5)

    def test_block_stack_to_index(self) -> None:
        self.assertEqual(0, self.palette.block_stack_to_index(BlockStack(dirt)))
        self.assertEqual(1, self.palette.block_stack_to_index(BlockStack(stone)))
        self.assertEqual(2, self.palette.block_stack_to_index(BlockStack(granite)))
        self.assertEqual(3, self.palette.block_stack_to_index(BlockStack(water)))
        self.assertEqual(4, self.palette.block_stack_to_index(waterlogged_dirt))
        self.assertEqual(
            5,
            self.palette.block_stack_to_index(
                BlockStack(
                    Block.from_java_blockstate(
                        "java", VersionNumber(3578), "a:b[c=d]"
                    )
                )
            ),
        )

    def test_len(self) -> None:
        palette = BlockPalette(
            VersionRange("java", VersionNumber(3578), VersionNumber(3578))
        )

        # Partially populate the palette
        palette.block_stack_to_index(BlockStack(dirt))
        palette.block_stack_to_index(BlockStack(stone))
        palette.block_stack_to_index(BlockStack(granite))
        palette.block_stack_to_index(BlockStack(water))
        palette.block_stack_to_index(waterlogged_dirt)

        self.assertEqual(5, len(palette))

    def test_errors(self) -> None:
        with self.assertRaises(ValueError):
            self.palette.block_stack_to_index(
                BlockStack(
                    Block.from_java_blockstate("java", VersionNumber(3579), "a:b")
                )
            )
        with self.assertRaises(ValueError):
            self.palette.block_stack_to_index(
                BlockStack(
                    Block.from_java_blockstate("java", VersionNumber(3577), "a:b")
                )
            )


if __name__ == "__main__":
    unittest.main()
