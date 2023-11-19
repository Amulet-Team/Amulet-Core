import unittest

from amulet_nbt import NamedTag, CompoundTag, IntTag, StringTag

from amulet.entity import Entity
from amulet.version import PlatformVersion, VersionNumber


def get_test_entity() -> Entity:
    return Entity(
        PlatformVersion("java", VersionNumber(3578)),
        "namespace",
        "basename",
        1,
        2,
        3,
        NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
    )


def get_test_entity_variants() -> tuple[Entity, ...]:
    return (
        Entity(
            PlatformVersion("java", VersionNumber(3579)),
            "namespace",
            "basename",
            1,
            2,
            3,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace1",
            "basename",
            1,
            2,
            3,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename1",
            1,
            2,
            3,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename",
            0,
            2,
            3,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename",
            1,
            0,
            3,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename",
            1,
            2,
            0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            PlatformVersion("java", VersionNumber(3578)),
            "namespace",
            "basename",
            1,
            2,
            3,
            NamedTag(CompoundTag({"int": IntTag(0), "str": StringTag("hi")})),
        ),
    )


class EntityTestCase(unittest.TestCase):
    def test_construct(self):
        entity = get_test_entity()
        self.assertEqual(PlatformVersion("java", VersionNumber(3578)), entity.version)
        self.assertEqual("namespace", entity.namespace)
        self.assertEqual("basename", entity.base_name)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
            entity.nbt,
        )

    def test_edit(self):
        entity = get_test_entity()
        entity.namespace = "namespace2"
        self.assertEqual("namespace2", entity.namespace)
        entity.base_name = "basename2"
        self.assertEqual("basename2", entity.base_name)
        entity.nbt.compound["int"] = IntTag(2)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(2), "str": StringTag("hi")})),
            entity.nbt,
        )
        entity.x = 5
        entity.y = 6
        entity.z = 7
        self.assertEqual((5, 6, 7), entity.location)

    def test_equal(self):
        self.assertEqual(get_test_entity(), get_test_entity())
        for entity in get_test_entity_variants():
            with self.subTest(repr(entity)):
                self.assertNotEqual(get_test_entity(), entity)

    def test_hash(self):
        entity_1 = get_test_entity()
        entity_2 = get_test_entity()
        self.assertEqual(hash(entity_1), hash(entity_1))
        self.assertEqual(hash(entity_2), hash(entity_2))
        self.assertNotEqual(hash(entity_1), hash(entity_2))


if __name__ == "__main__":
    unittest.main()
