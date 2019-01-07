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


class NBTTemplateTestBaseCases:
    class NBTTemplateTestCase(unittest.TestCase):
        def _setUp(self, template_dir):
            self.template_engine = TemplateLoader(template_dir)

        def test_load_template(self):
            item_template = self.template_engine.load_template("item")
            self.assertIsInstance(item_template, NBTCompoundStructure)

            bat_template = self.template_engine.load_template("bat")
            self.assertIsInstance(bat_template, NBTCompoundStructure)

        def test_any_tag(self):  # Reminder test since any tags aren't supported yet!
            self.assertFalse(True)

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


class Java113NBTTemplateTestCase(NBTTemplateTestBaseCases.NBTTemplateTestCase):
    def setUp(self):
        self._setUp(os.path.join("..", "src", "version_definitions", "java_1_13"))


if __name__ == "__main__":
    unittest.main()
