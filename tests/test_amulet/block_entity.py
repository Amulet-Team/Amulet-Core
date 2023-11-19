import unittest

from amulet_nbt import NamedTag, CompoundTag, IntTag, StringTag

from amulet.block_entity import BlockEntity
from amulet.version import VersionNumber, PlatformVersion


def get_test_block_entity() -> BlockEntity:
    return BlockEntity(
        PlatformVersion("java", VersionNumber(3578)),
        "namespace",
        "basename",
        NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
    )


def get_test_block_entity_variants() -> tuple[BlockEntity, ...]:
    return (
        BlockEntity(
            PlatformVersion("java", VersionNumber(3579)),
            "namespace",
            "basename",
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        BlockEntity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace1",
            "basename",
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        BlockEntity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename1",
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        BlockEntity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename",
            NamedTag(CompoundTag({"int": IntTag(0), "str": StringTag("hi")})),
        ),
    )


class BlockEntityTestCase(unittest.TestCase):
    def test_construct(self):
        block_entity = get_test_block_entity()
        self.assertEqual(
            PlatformVersion("java", VersionNumber(3578)), block_entity.version
        )
        self.assertEqual("namespace", block_entity.namespace)
        self.assertEqual("basename", block_entity.base_name)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
            block_entity.nbt,
        )

    def test_edit(self):
        block_entity = get_test_block_entity()
        block_entity.namespace = "namespace2"
        self.assertEqual("namespace2", block_entity.namespace)
        block_entity.base_name = "basename2"
        self.assertEqual("basename2", block_entity.base_name)
        block_entity.nbt.compound["int"] = IntTag(2)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(2), "str": StringTag("hi")})),
            block_entity.nbt,
        )

    def test_equal(self):
        self.assertEqual(get_test_block_entity(), get_test_block_entity())
        for block_entity in get_test_block_entity_variants():
            with self.subTest(repr(block_entity)):
                self.assertNotEqual(get_test_block_entity(), block_entity)


if __name__ == "__main__":
    unittest.main()
