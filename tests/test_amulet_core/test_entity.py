import unittest

from amulet.nbt import NamedTag, CompoundTag, IntTag, StringTag

from amulet.core.entity import Entity
from amulet.core.version import VersionNumber


def get_test_entity() -> Entity:
    return Entity(
        "java",
        VersionNumber(3578),
        "namespace",
        "basename",
        1.0,
        2.0,
        3.0,
        NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
    )


def get_test_entity_variants() -> tuple[Entity, ...]:
    return (
        Entity(
            "bedrock",
            VersionNumber(3578),
            "namespace",
            "basename",
            1.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3579),
            "namespace",
            "basename",
            1.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace1",
            "basename",
            1.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace",
            "basename1",
            1.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace",
            "basename",
            0.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace",
            "basename",
            1.0,
            0.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace",
            "basename",
            1.0,
            2.0,
            0.0,
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
        ),
        Entity(
            "java",
            VersionNumber(3578),
            "namespace",
            "basename",
            1.0,
            2.0,
            3.0,
            NamedTag(CompoundTag({"int": IntTag(0), "str": StringTag("hi")})),
        ),
    )


class EntityTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_entity_ import test_entity

        test_entity()

    def test_construct(self) -> None:
        entity = get_test_entity()
        self.assertEqual("java", entity.platform)
        self.assertEqual(VersionNumber(3578), entity.version)
        self.assertEqual("namespace", entity.namespace)
        self.assertEqual("basename", entity.base_name)
        self.assertEqual(1.0, entity.x)
        self.assertEqual(2.0, entity.y)
        self.assertEqual(3.0, entity.z)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(1), "str": StringTag("hi")})),
            entity.nbt,
        )

    def test_edit(self) -> None:
        entity = get_test_entity()
        entity.namespace = "namespace2"
        self.assertEqual("namespace2", entity.namespace)
        entity.base_name = "basename2"
        self.assertEqual("basename2", entity.base_name)
        entity.x = 10
        self.assertEqual(10, entity.x)
        entity.y = 20
        self.assertEqual(20, entity.y)
        entity.z = 30
        self.assertEqual(30, entity.z)
        entity.nbt.compound["int"] = IntTag(2)
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(2), "str": StringTag("hi")})),
            entity.nbt,
        )
        old_nbt = entity.nbt
        entity.nbt = NamedTag(CompoundTag({"int": IntTag(3), "str": StringTag("hi")}))
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(2), "str": StringTag("hi")})),
            old_nbt,
        )
        self.assertEqual(
            NamedTag(CompoundTag({"int": IntTag(3), "str": StringTag("hi")})),
            entity.nbt,
        )

    def test_equal(self) -> None:
        self.assertEqual(get_test_entity(), get_test_entity())
        for entity in get_test_entity_variants():
            with self.subTest(repr(entity)):
                self.assertNotEqual(get_test_entity(), entity)


if __name__ == "__main__":
    unittest.main()
