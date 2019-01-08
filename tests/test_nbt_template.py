import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)), "src")

import unittest
from api.nbt_template import (
    TemplateLoader,
    NBTStructure,
    NBTRangeStructure,
    NBTListStructure,
    NBTCompoundStructure,
)
from test_utils import TESTS_DIR


class NBTTemplateTestBaseCases:
    class NBTTemplateTestCase(unittest.TestCase):
        def _setUp(self, template_dir):
            self.template_engine = TemplateLoader(template_dir)

        def test_equality(self):

            self.assertNotEqual(
                NBTStructure("string", "test"), NBTStructure("int", "test")
            )
            self.assertNotEqual(
                NBTStructure("string", "test"), NBTStructure("string", "test1")
            )

        def test_load_template(self):
            item_template = self.template_engine.load_template("item")
            self.assertIsInstance(item_template, NBTCompoundStructure)

            bat_template = self.template_engine.load_template("bat")
            self.assertIsInstance(bat_template, NBTCompoundStructure)

        def test_any_tag(self):  # Reminder test since any tags aren't supported yet!
            template = NBTCompoundStructure(None, {"any_tag": NBTStructure("any")})

            mock_1 = NBTCompoundStructure(
                None, {"any_tag": NBTStructure("string", "string_test")}
            )
            mock_2 = NBTCompoundStructure(
                None, {"any_tag": NBTStructure("int", "int_test")}
            )
            mock_3 = NBTCompoundStructure(
                None,
                {
                    "any_tag": NBTListStructure(
                        NBTStructure("float"),
                        [NBTStructure("float", 1.0), NBTStructure("double", 2.0)],
                    )
                },
            )
            mock_4 = NBTCompoundStructure(
                None,
                {
                    "any_tag": NBTCompoundStructure(
                        None,
                        {
                            "id": NBTStructure("string", "minecraft:cow"),
                            "CustomName": NBTStructure("string", "Kev"),
                        },
                    )
                },
            )

            mock_1.apply_template(template)
            mock_2.apply_template(template)
            mock_3.apply_template(template)
            mock_4.apply_template(template)

            print(mock_4)

            self.assertEqual(mock_1["any_tag"], NBTStructure("string", "string_test"))
            self.assertEqual(mock_2["any_tag"], NBTStructure("int", "int_test"))
            self.assertEqual(
                mock_3["any_tag"],
                NBTListStructure(
                    NBTStructure("float"),
                    [NBTStructure("float", 1.0), NBTStructure("double", 2.0)],
                ),
            )
            self.assertEqual(
                mock_4["any_tag"],
                NBTCompoundStructure(
                    None,
                    {
                        "id": NBTStructure("string", "minecraft:cow"),
                        "CustomName": NBTStructure("string", "Kev"),
                    },
                ),
            )

        def test_item_apply_template(self):
            item_template = self.template_engine.load_template("item")

            mock_item_1 = NBTCompoundStructure(
                {"id": NBTStructure("string", "minecraft:stone_shovel")}
            )
            mock_item_1_expected = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:stone_shovel"),
                    "Count": NBTStructure("byte", 1),
                    "Slot": NBTStructure("byte", 0),
                }
            )

            mock_item_1.apply_template(item_template)
            self.assertEqual(mock_item_1_expected, mock_item_1)

            mock_item_2 = NBTCompoundStructure(
                {
                    "id": NBTStructure("int", "minecraft:diamond_pickaxe"),
                    "Count": NBTStructure("byte", 1),
                    "Slot": NBTStructure("string", 0),
                }
            )
            mock_item_2_expected = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:diamond_pickaxe"),
                    "Count": NBTStructure("byte", 1),
                    "Slot": NBTStructure("byte", 0),
                }
            )

            mock_item_2.apply_template(item_template)
            self.assertEqual(mock_item_2_expected, mock_item_2)

            mock_item_3 = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:wood_axe"),
                    "tag": NBTCompoundStructure(
                        {"Unbreakable": NBTStructure("byte", 0)}
                    ),
                }
            )
            mock_item_3_expected = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:wood_axe"),
                    "Count": NBTStructure("byte", 1),
                    "Slot": NBTStructure("byte", 0),
                    "tag": NBTCompoundStructure(
                        {"Unbreakable": NBTRangeStructure("byte", 0, [0, 1])}
                    ),
                }
            )

            mock_item_3.apply_template(item_template)
            self.assertEqual(mock_item_3_expected, mock_item_3)

            mock_item_4 = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:diamond_shovel"),
                    "tag": NBTCompoundStructure(
                        {
                            "CanDestroy": NBTListStructure(
                                NBTStructure("string"),
                                [
                                    NBTStructure("string", "minecraft:dirt"),
                                    NBTStructure("int", "minecraft:obsidian"),
                                ],
                            )
                        }
                    ),
                }
            )
            mock_item_4_expected = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:diamond_shovel"),
                    "tag": NBTCompoundStructure(
                        {
                            "CanDestroy": NBTListStructure(
                                NBTStructure("string"),
                                [
                                    NBTStructure("string", "minecraft:dirt"),
                                    NBTStructure("string", "minecraft:obsidian"),
                                ],
                            )
                        }
                    ),
                }
            )

            mock_item_4.apply_template(item_template)
            self.assertEqual(mock_item_4_expected, mock_item_4)

            mock_item_5 = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:diamond_shovel"),
                    "tag": NBTCompoundStructure(
                        {
                            "Enchantments": NBTListStructure(
                                NBTCompoundStructure(
                                    {
                                        "id": NBTStructure("string"),
                                        "lvl": NBTStructure("short", 1),
                                    }
                                ),
                                [
                                    NBTCompoundStructure(
                                        {
                                            "id": NBTStructure(
                                                "string", "minecraft:knockback"
                                            ),
                                            "lvl": NBTStructure("short", 3),
                                        }
                                    ),
                                    NBTCompoundStructure(
                                        {
                                            "id": NBTStructure(
                                                "float", "minecraft:sharpness"
                                            ),
                                            "lvl": NBTStructure("int", 1),
                                        }
                                    ),
                                ],
                            )
                        }
                    ),
                }
            )
            mock_item_5_expected = NBTCompoundStructure(
                {
                    "id": NBTStructure("string", "minecraft:diamond_shovel"),
                    "tag": NBTCompoundStructure(
                        {
                            "Enchantments": NBTListStructure(
                                NBTCompoundStructure(
                                    {
                                        "id": NBTStructure("string"),
                                        "lvl": NBTStructure("short", 1),
                                    }
                                ),
                                [
                                    NBTCompoundStructure(
                                        {
                                            "id": NBTStructure(
                                                "string", "minecraft:knockback"
                                            ),
                                            "lvl": NBTStructure("short", 3),
                                        }
                                    ),
                                    NBTCompoundStructure(
                                        {
                                            "id": NBTStructure(
                                                "string", "minecraft:sharpness"
                                            ),
                                            "lvl": NBTStructure("short", 1),
                                        }
                                    ),
                                ],
                            )
                        }
                    ),
                }
            )

            mock_item_5.apply_template(item_template)
            self.assertEqual(mock_item_5_expected, mock_item_5)


class Java113NBTTemplateTestCase(NBTTemplateTestBaseCases.NBTTemplateTestCase):
    def setUp(self):
        self._setUp(
            os.path.join(
                os.path.dirname(TESTS_DIR), "src", "version_definitions", "java_1_13"
            )
        )


if __name__ == "__main__":
    unittest.main()
