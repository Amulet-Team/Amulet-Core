import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import unittest

from version_definitions import definition_manager


class TestPrototype112(unittest.TestCase):

    def setUp(self):
        self.proto = definition_manager.DefinitionManager("1.12")

    def test_direct_access(self):
        self.assertEqual(self.proto.blocks["minecraft:stone"], [1, 0])

    def test_get_internal_block(self):
        stone_def = self.proto.get_internal_block(basename="stone")
        granite_def = self.proto.get_internal_block(basename="granite")
        oak_log_axis_x = self.proto.get_internal_block(
            basename="oak_log", properties={"axis": "x"}
        )

        self.assertIsInstance(stone_def, dict)
        self.assertEqual(stone_def["name"], "Stone")

        self.assertIsInstance(granite_def, dict)
        self.assertEqual(granite_def["name"], "Granite")
        self.assertNotEqual(granite_def, stone_def)

        self.assertIsInstance(oak_log_axis_x, dict)
        self.assertEqual(oak_log_axis_x["name"], "Oak Log (East/West)")
        self.assertNotEqual(
            oak_log_axis_x,
            self.proto.get_internal_block(basename="oak_log", properties={"axis": "y"}),
        )

        with self.assertRaises(KeyError):
            self.proto.get_internal_block(resource_location="unknown", basename="stone")
            self.proto.get_internal_block(
                basename="stone", properties={"variant": "chiseled"}
            )
            self.proto.get_internal_block(basename="laterite")


class TestPrototype113(unittest.TestCase):

    def setUp(self):
        self.proto = definition_manager.DefinitionManager("1.13")

    def test_direct_access(self):
        self.assertEqual(self.proto.blocks["minecraft:stone"], "minecraft:stone")

    def test_get_internal_block(self):
        stone_def = self.proto.get_internal_block(basename="stone")
        granite_def = self.proto.get_internal_block(basename="granite")
        oak_log_axis_x = self.proto.get_internal_block(
            basename="oak_log", properties={"axis": "x"}
        )

        self.assertIsInstance(stone_def, dict)
        self.assertEqual(stone_def["name"], "Stone")

        self.assertIsInstance(granite_def, dict)
        self.assertEqual(granite_def["name"], "Granite")
        self.assertNotEqual(granite_def, stone_def)

        self.assertIsInstance(oak_log_axis_x, dict)
        self.assertEqual(oak_log_axis_x["name"], "Oak Log (East/West)")
        self.assertNotEqual(
            oak_log_axis_x,
            self.proto.get_internal_block(basename="oak_log", properties={"axis": "y"}),
        )

        with self.assertRaises(KeyError):
            self.proto.get_internal_block(resource_location="unknown", basename="stone")
            self.proto.get_internal_block(
                basename="stone", properties={"variant": "chiseled"}
            )
            self.proto.get_internal_block(basename="laterite")


if __name__ == "__main__":
    unittest.main()
