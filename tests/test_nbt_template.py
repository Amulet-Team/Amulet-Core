from test_utils import modify_py_path

modify_py_path()

import os

import unittest
from amulet.api.nbt_template import (
    TemplateLoader,
    NBTStructure,
    NBTListStructure,
    NBTCompoundStructure,
    NBTEntry,
    NBTListEntry,
    NBTCompoundEntry,
    nbt_template_to_entry,
)
from test_utils import TESTS_DIR

# noinspection PyUnresolvedReferences
class NBTTemplateTestBase:
    """
    Tests for NBTEntry apply_template()
    """

    def _setUp(self, template_dir):
        self.template_engine = TemplateLoader(template_dir)

    def test_equality(self):

        self.assertNotEqual(NBTStructure("string", "test"), NBTStructure("int", "test"))
        self.assertNotEqual(
            NBTStructure("string", "test"), NBTStructure("string", "test1")
        )

    def test_compound_update(self):
        original = NBTCompoundEntry({"id": NBTStructure("string", "minecraft:cow")})
        new = NBTCompoundEntry({"CustomName": NBTStructure("string", "Test")})

        self.assertNotIn("CustomName", original)
        original.update(new)
        self.assertIn("CustomName", original)

    def test_load_template(self):
        item_template = self.template_engine.load_template("item_entry")
        self.assertIsInstance(item_template, NBTCompoundStructure)

        bat_template = self.template_engine.load_template("bat")
        self.assertIsInstance(bat_template, NBTCompoundStructure)

    def test_any_tag(self):  # Reminder test since any tags aren't supported yet!
        template = NBTCompoundStructure({"any_tag": NBTStructure("any")})

        mock_1 = NBTCompoundEntry({"any_tag": NBTEntry("string", "string_test")})
        mock_2 = NBTCompoundEntry({"any_tag": NBTEntry("int", "int_test")})
        mock_3 = NBTCompoundEntry(
            {"any_tag": NBTListEntry([NBTEntry("float", 1.0), NBTEntry("double", 2.0)])}
        )
        mock_4 = NBTCompoundEntry(
            {
                "any_tag": NBTCompoundEntry(
                    {
                        "id": NBTEntry("string", "minecraft:cow"),
                        "CustomName": NBTEntry("string", "Kev"),
                    }
                )
            }
        )

        result_1 = mock_1.apply_template(template)
        result_2 = mock_2.apply_template(template)
        result_3 = mock_3.apply_template(template)
        result_4 = mock_4.apply_template(template)

        self.assertEqual(result_1["any_tag"], NBTEntry("string", "string_test"))
        self.assertEqual(result_2["any_tag"], NBTEntry("int", "int_test"))
        self.assertEqual(
            result_3["any_tag"],
            NBTListEntry([NBTEntry("float", 1.0), NBTEntry("double", 2.0)]),
        )
        self.assertEqual(
            result_4["any_tag"],
            NBTCompoundEntry(
                {
                    "id": NBTEntry("string", "minecraft:cow"),
                    "CustomName": NBTEntry("string", "Kev"),
                }
            ),
        )

    def test_item_apply_template(self):
        item_template = self.template_engine.load_template("item_entry")

        mock_item_1 = NBTCompoundEntry(
            {"id": NBTEntry("string", "minecraft:stone_shovel")}
        )
        mock_item_1_expected = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:stone_shovel"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("byte", 0),
            }
        )

        result_item_1 = mock_item_1.apply_template(item_template)
        self.assertNotEqual(mock_item_1_expected, mock_item_1)
        self.assertNotEqual(mock_item_1, result_item_1)
        self.assertEqual(mock_item_1_expected, result_item_1)

        mock_item_2 = NBTCompoundEntry(
            {
                "id": NBTEntry("int", "minecraft:diamond_pickaxe"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("string", 0),
            }
        )
        mock_item_2_expected = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:diamond_pickaxe"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("byte", 0),
            }
        )

        result_item_2 = mock_item_2.apply_template(item_template)
        self.assertNotEqual(mock_item_2_expected, mock_item_2)
        self.assertNotEqual(mock_item_2, result_item_2)
        self.assertEqual(mock_item_2_expected, result_item_2)

        mock_item_3 = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:wood_axe"),
                "tag": NBTCompoundEntry({"Unbreakable": NBTEntry("byte", 0)}),
            }
        )
        mock_item_3_expected = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:wood_axe"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("byte", 0),
                "tag": NBTCompoundEntry({"Unbreakable": NBTEntry("byte", 0)}),
            }
        )

        result_item_3 = mock_item_3.apply_template(item_template)
        self.assertNotEqual(mock_item_3_expected, mock_item_3)
        self.assertNotEqual(mock_item_3, result_item_3)
        self.assertEqual(mock_item_3_expected, result_item_3)

        mock_item_4 = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:diamond_shovel"),
                "tag": NBTCompoundEntry(
                    {
                        "CanDestroy": NBTListEntry(
                            [
                                NBTEntry("string", "minecraft:dirt"),
                                NBTEntry("int", "minecraft:obsidian"),
                            ]
                        )
                    }
                ),
            }
        )
        mock_item_4_expected = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:diamond_shovel"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("byte", 0),
                "tag": NBTCompoundEntry(
                    {
                        "CanDestroy": NBTListEntry(
                            [
                                NBTEntry("string", "minecraft:dirt"),
                                NBTEntry("string", "minecraft:obsidian"),
                            ]
                        )
                    }
                ),
            }
        )

        result_item_4 = mock_item_4.apply_template(item_template)
        self.assertNotEqual(mock_item_4_expected, mock_item_4)
        self.assertNotEqual(mock_item_4, result_item_4)
        self.assertEqual(mock_item_4_expected, result_item_4)

        mock_item_5 = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:diamond_shovel"),
                "tag": NBTCompoundEntry(
                    {
                        "Enchantments": NBTListEntry(
                            [
                                NBTCompoundEntry(
                                    {
                                        "id": NBTEntry("string", "minecraft:knockback"),
                                        "lvl": NBTEntry("short", 3),
                                    }
                                ),
                                NBTCompoundEntry(
                                    {
                                        "id": NBTEntry("float", "minecraft:sharpness"),
                                        "lvl": NBTEntry("int", 1),
                                    }
                                ),
                            ]
                        )
                    }
                ),
            }
        )
        mock_item_5_expected = NBTCompoundEntry(
            {
                "id": NBTEntry("string", "minecraft:diamond_shovel"),
                "Count": NBTEntry("byte", 1),
                "Slot": NBTEntry("byte", 0),
                "tag": NBTCompoundEntry(
                    {
                        "Enchantments": NBTListEntry(
                            [
                                NBTCompoundEntry(
                                    {
                                        "id": NBTEntry("string", "minecraft:knockback"),
                                        "lvl": NBTEntry("short", 3),
                                    }
                                ),
                                NBTCompoundEntry(
                                    {
                                        "id": NBTEntry("string", "minecraft:sharpness"),
                                        "lvl": NBTEntry("short", 1),
                                    }
                                ),
                            ]
                        )
                    }
                ),
            }
        )

        result_item_5 = mock_item_5.apply_template(item_template)
        self.assertNotEqual(mock_item_5_expected, mock_item_5)
        self.assertNotEqual(mock_item_5, result_item_5)
        self.assertEqual(mock_item_5_expected, result_item_5)

    def test_nbt_template_to_entry(self):
        entry_1 = nbt_template_to_entry("creeper", self.template_engine)
        self.assertEqual("minecraft:creeper", entry_1["id"].value)


class Java113NBTTemplateTestCase(NBTTemplateTestBase, unittest.TestCase):
    def setUp(self):
        self._setUp(
            os.path.join(
                os.path.dirname(TESTS_DIR), "src", "amulet", "version_definitions", "java_1_13"
            )
        )


if __name__ == "__main__":
    unittest.main()
