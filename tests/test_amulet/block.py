import unittest
from amulet.block import Block, BlockStack

from amulet.game_version import JavaGameVersion


from amulet_nbt import (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
)


def get_test_block() -> Block:
    return Block(
        JavaGameVersion(3578),
        "namespace",
        "basename",
        {
            "ByteTag": ByteTag(1),
            "ShortTag": ShortTag(2),
            "IntTag": IntTag(4),
            "LongTag": LongTag(8),
            "StringTag": StringTag("hi"),
        },
    )


def get_test_block_variants() -> tuple[Block, ...]:
    return (
        Block(
            JavaGameVersion(3579),
            "namespace",
            "basename",
            {
                "ByteTag": ByteTag(1),
                "ShortTag": ShortTag(2),
                "IntTag": IntTag(4),
                "LongTag": LongTag(8),
                "StringTag": StringTag("hi"),
            },
        ),
        Block(
            JavaGameVersion(3578),
            "namespace2",
            "basename",
            {
                "ByteTag": ByteTag(1),
                "ShortTag": ShortTag(2),
                "IntTag": IntTag(4),
                "LongTag": LongTag(8),
                "StringTag": StringTag("hi"),
            },
        ),
        Block(
            JavaGameVersion(3578),
            "namespace",
            "basename2",
            {
                "ByteTag": ByteTag(1),
                "ShortTag": ShortTag(2),
                "IntTag": IntTag(4),
                "LongTag": LongTag(8),
                "StringTag": StringTag("hi"),
            },
        ),
        Block(
            JavaGameVersion(3578),
            "namespace",
            "basename",
            {
                "ByteTag": ByteTag(2),
                "ShortTag": ShortTag(2),
                "IntTag": IntTag(4),
                "LongTag": LongTag(8),
                "StringTag": StringTag("hi"),
            },
        ),
    )


class BlockTestCase(unittest.TestCase):
    def test_construct(self):
        block = get_test_block()
        self.assertEqual(JavaGameVersion(3578), block.version)
        self.assertEqual("namespace:basename", block.namespaced_name)
        self.assertEqual("namespace", block.namespace)
        self.assertEqual("basename", block.base_name)
        self.assertEqual(
            {
                "ByteTag": ByteTag(1),
                "ShortTag": ShortTag(2),
                "IntTag": IntTag(4),
                "LongTag": LongTag(8),
                "StringTag": StringTag("hi"),
            },
            block.properties,
        )

    def test_equal(self):
        self.assertEqual(get_test_block(), get_test_block())
        for block in get_test_block_variants():
            with self.subTest(repr(block)):
                self.assertNotEqual(get_test_block(), block)

    def test_hash(self):
        self.assertEqual(hash(get_test_block()), hash(get_test_block()))
        for block in get_test_block_variants():
            with self.subTest(repr(block)):
                self.assertNotEqual(hash(get_test_block()), hash(block))

    def test_blockstate_constructor(self):
        self.assertEqual(
            Block(JavaGameVersion(3578), "minecraft", "air"),
            Block.from_string_blockstate(JavaGameVersion(3578), "air"),
        )
        self.assertEqual(
            Block(JavaGameVersion(3578), "minecraft", "air"),
            Block.from_string_blockstate(JavaGameVersion(3578), "minecraft:air"),
        )
        self.assertEqual(
            Block(JavaGameVersion(3578), "a", "b"),
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b[]"),
        )
        self.assertEqual(
            Block(JavaGameVersion(3578), "a", "b", {"c": StringTag("d")}),
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b[c=d]"),
        )
        self.assertEqual(
            Block(
                JavaGameVersion(3578),
                "a",
                "b",
                {"c": StringTag("d"), "e": StringTag("f")},
            ),
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b[c=d,e=f]"),
        )

        with self.assertRaises(ValueError):
            Block.from_string_blockstate(JavaGameVersion(3578), "a:")
        with self.assertRaises(ValueError):
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b[")
        with self.assertRaises(ValueError):
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b]")
        with self.assertRaises(ValueError):
            Block.from_string_blockstate(JavaGameVersion(3578), "a:b[c]")
        with self.assertRaises(ValueError):
            Block.from_string_blockstate(JavaGameVersion(3578), "[a=b]")

    def test_snbt_blockstate_constructor(self):
        self.assertEqual(
            Block(JavaGameVersion(3578), "minecraft", "air"),
            Block.from_snbt_blockstate(JavaGameVersion(3578), "air"),
        )
        self.assertEqual(
            Block(JavaGameVersion(3578), "minecraft", "air"),
            Block.from_snbt_blockstate(JavaGameVersion(3578), "minecraft:air"),
        )
        self.assertEqual(
            Block(JavaGameVersion(3578), "a", "b"),
            Block.from_snbt_blockstate(JavaGameVersion(3578), "a:b[]"),
        )
        self.assertEqual(
            Block(
                JavaGameVersion(3578),
                "a",
                "b",
                {
                    "ByteTag": ByteTag(1),
                    "ShortTag": ShortTag(2),
                    "IntTag": IntTag(4),
                    "LongTag": LongTag(8),
                    "StringTag": StringTag("hi"),
                },
            ),
            Block.from_snbt_blockstate(
                JavaGameVersion(3578),
                'a:b[ByteTag=1b,ShortTag=2s,IntTag=4,LongTag=8l,StringTag="hi"]',
            ),
        )

        with self.assertRaises(ValueError):
            Block.from_snbt_blockstate(JavaGameVersion(3578), "a:")
        with self.assertRaises(ValueError):
            Block.from_snbt_blockstate(JavaGameVersion(3578), "a:b[")
        with self.assertRaises(ValueError):
            Block.from_snbt_blockstate(JavaGameVersion(3578), "a:b]")
        with self.assertRaises(ValueError):
            Block.from_snbt_blockstate(JavaGameVersion(3578), "a:b[c]")
        with self.assertRaises(ValueError):
            Block.from_snbt_blockstate(JavaGameVersion(3578), "[a=b]")


class BlockStackTestCase(unittest.TestCase):
    def test_constructor(self):
        block_stack_1 = BlockStack(get_test_block())
        block_stack_2 = BlockStack(get_test_block())
        self.assertEqual(block_stack_1, block_stack_1)
        self.assertEqual(block_stack_1, block_stack_2)
        self.assertEqual(block_stack_2, block_stack_1)
        self.assertEqual(1, len(block_stack_1))
        self.assertEqual(get_test_block(), block_stack_1[0])
        self.assertEqual(get_test_block(), block_stack_1.base_block)

        block_variants = get_test_block_variants()
        block_stack_3 = BlockStack(*block_variants)
        block_stack_4 = BlockStack(*block_variants)
        self.assertEqual(block_stack_3, block_stack_3)
        self.assertEqual(block_stack_3, block_stack_4)
        self.assertEqual(block_stack_4, block_stack_3)
        for block_1, block_2 in zip(block_variants, block_stack_3):
            self.assertEqual(block_1, block_2)
        self.assertEqual(block_variants[0], block_stack_3.base_block)
        self.assertEqual(block_variants[1:], block_stack_3.extra_blocks)

        self.assertNotEqual(block_stack_1, block_stack_3)


if __name__ == "__main__":
    unittest.main()
