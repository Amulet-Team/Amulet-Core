import unittest
from amulet.block import Block, BlockStack

from amulet.version import VersionNumber

from amulet_nbt import (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
)


def get_test_block() -> Block:
    return Block(
        "java",
        VersionNumber(3578),
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
            "java",
            VersionNumber(3579),
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
            "java",
            VersionNumber(3578),
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
            "java",
            VersionNumber(3578),
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
            "java",
            VersionNumber(3578),
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
    def test_construct(self) -> None:
        block = get_test_block()
        self.assertEqual("java", block.platform)
        self.assertEqual(VersionNumber(3578), block.version)
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

    def test_equal(self) -> None:
        self.assertEqual(get_test_block(), get_test_block())
        for block in get_test_block_variants():
            with self.subTest(repr(block)):
                self.assertNotEqual(get_test_block(), block)

    def test_hash(self) -> None:
        self.assertEqual(hash(get_test_block()), hash(get_test_block()))
        for block in get_test_block_variants():
            with self.subTest(repr(block)):
                self.assertNotEqual(hash(get_test_block()), hash(block))

    def test_java_blockstate(self) -> None:
        self.assertEqual(
            "namespace:basename",
            Block("platform", VersionNumber(), "namespace", "basename").java_blockstate,
        )
        self.assertEqual(
            "namespace:basename[g=helloworld]",
            Block(
                "platform",
                VersionNumber(),
                "namespace",
                "basename",
                {
                    "g": StringTag("helloworld"),
                    "f": LongTag(0),
                    "e": IntTag(0),
                    "d": ShortTag(0),
                    "c": ByteTag(2),
                    "b": ByteTag(1),
                    "a": ByteTag(0),
                },
            ).java_blockstate,
        )

    def test_bedrock_blockstate(self) -> None:
        self.assertEqual(
            "namespace:basename",
            Block(
                "platform", VersionNumber(), "namespace", "basename"
            ).bedrock_blockstate,
        )
        self.assertEqual(
            'namespace:basename["a"=false,"b"=true,"c"=2b,"d"=0s,"e"=0,"f"=0L,"g"="helloworld"]',
            Block(
                "platform",
                VersionNumber(),
                "namespace",
                "basename",
                {
                    "g": StringTag("helloworld"),
                    "f": LongTag(0),
                    "e": IntTag(0),
                    "d": ShortTag(0),
                    "c": ByteTag(2),
                    "b": ByteTag(1),
                    "a": ByteTag(0),
                },
            ).bedrock_blockstate,
        )

    def test_java_blockstate_constructor(self) -> None:
        self.assertEqual(
            Block("java", VersionNumber(3578), "minecraft", "air"),
            Block.from_java_blockstate("java", VersionNumber(3578), "air"),
        )
        self.assertEqual(
            Block("java", VersionNumber(3578), "minecraft", "air"),
            Block.from_java_blockstate("java", VersionNumber(3578), "minecraft:air"),
        )
        self.assertEqual(
            Block("java", VersionNumber(3578), "a", "b"),
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b[]"),
        )
        self.assertEqual(
            Block("java", VersionNumber(3578), "minecraft", "b"),
            Block.from_java_blockstate("java", VersionNumber(3578), "b[]"),
        )
        self.assertEqual(
            Block(
                "java",
                VersionNumber(3578),
                "a",
                "b",
                {"c": StringTag("d")},
            ),
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b[c=d]"),
        )
        self.assertEqual(
            Block(
                "java",
                VersionNumber(3578),
                "a",
                "b",
                {"c": StringTag("d"), "e": StringTag("f")},
            ),
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b[c=d,e=f]"),
        )

        with self.assertRaises(ValueError):
            Block.from_java_blockstate("java", VersionNumber(3578), "a:")
        with self.assertRaises(ValueError):
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b[")
        with self.assertRaises(ValueError):
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b]")
        with self.assertRaises(ValueError):
            Block.from_java_blockstate("java", VersionNumber(3578), "a:b[c]")
        with self.assertRaises(ValueError):
            Block.from_java_blockstate("java", VersionNumber(3578), "[a=b]")

    def test_bedrock_blockstate_constructor(self) -> None:
        self.assertEqual(
            Block("java", VersionNumber(3578), "minecraft", "air"),
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "air"),
        )
        self.assertEqual(
            Block("java", VersionNumber(3578), "minecraft", "air"),
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "minecraft:air"),
        )
        self.assertEqual(
            Block("java", VersionNumber(3578), "a", "b"),
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "a:b[]"),
        )
        self.assertEqual(
            Block(
                "java",
                VersionNumber(3578),
                "a",
                "b",
                {
                    "ByteTag": ByteTag(1),
                    "false": ByteTag(0),
                    "true": ByteTag(1),
                    "ShortTag": ShortTag(2),
                    "IntTag": IntTag(4),
                    "LongTag": LongTag(8),
                    "StringTag": StringTag("hi"),
                },
            ),
            Block.from_bedrock_blockstate(
                "java",
                VersionNumber(3578),
                'a:b["false"=false,"true"=true,"ByteTag"=1b,"ShortTag"=2s,"IntTag"=4,"LongTag"=8l,"StringTag"="hi"]',
            ),
        )

        with self.assertRaises(ValueError):
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "a:")
        with self.assertRaises(ValueError):
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "a:b[")
        with self.assertRaises(ValueError):
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "a:b]")
        with self.assertRaises(ValueError):
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "a:b[c]")
        with self.assertRaises(ValueError):
            Block.from_bedrock_blockstate("java", VersionNumber(3578), "[a=b]")


class BlockStackTestCase(unittest.TestCase):
    def test_constructor(self) -> None:
        block_stack_1 = BlockStack(get_test_block())
        block_stack_2 = BlockStack(get_test_block())
        self.assertEqual(block_stack_1, block_stack_1)
        self.assertEqual(block_stack_1, block_stack_2)
        self.assertEqual(block_stack_2, block_stack_1)
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

    def test_get_item(self) -> None:
        block1 = Block("java", VersionNumber(3578), "namespace", "block1")
        block2 = Block("java", VersionNumber(3578), "namespace", "block2")
        block_stack = BlockStack(block1, block2)

        self.assertEqual(block1, block_stack[0])
        self.assertEqual(block2, block_stack[1])
        self.assertEqual(block1, block_stack[-2])
        self.assertEqual(block2, block_stack[-1])
        with self.assertRaises(IndexError):
            block_stack[-3]
        with self.assertRaises(IndexError):
            block_stack[2]

        self.assertIsInstance(block_stack[:], list)
        self.assertEqual([block1, block2], block_stack[:])

    def test_len(self) -> None:
        self.assertEqual(
            1,
            len(BlockStack(Block("java", VersionNumber(3578), "namespace", "block1"))),
        )
        self.assertEqual(
            2,
            len(
                BlockStack(
                    Block("java", VersionNumber(3578), "namespace", "block1"),
                    Block("java", VersionNumber(3578), "namespace", "block2"),
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
