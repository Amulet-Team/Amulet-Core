from test_utils import modify_py_path

modify_py_path()

import unittest

from version_definitions import definition_manager


class TestPrototypeBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class TestPrototype(unittest.TestCase):
        def _setUp(self, version):
            self.proto = definition_manager.DefinitionManager(version)

        def test_get_internal_block(self):
            stone_def = self.proto.get_internal_block(basename="stone")
            granite_def = self.proto.get_internal_block(basename="granite")
            oak_log_axis_x = self.proto.get_internal_block(
                basename="oak_log", properties={"axis": "x"}
            )

            self.assertIsInstance(stone_def, dict)
            self.assertEqual("Stone", stone_def["name"])

            self.assertIsInstance(granite_def, dict)
            self.assertEqual("Granite", granite_def["name"])
            self.assertNotEqual(granite_def, stone_def)

            self.assertIsInstance(oak_log_axis_x, dict)
            self.assertEqual("Oak Log (East/West)", oak_log_axis_x["name"])
            self.assertNotEqual(
                oak_log_axis_x,
                self.proto.get_internal_block(
                    basename="oak_log", properties={"axis": "y"}
                ),
            )

            with self.assertRaises(KeyError):
                self.proto.get_internal_block(
                    resource_location="unknown", basename="stone"
                )
                self.proto.get_internal_block(
                    basename="stone", properties={"variant": "chiseled"}
                )
                self.proto.get_internal_block(basename="laterite")


class TestPrototype112(TestPrototypeBaseCases.TestPrototype):
    def setUp(self):
        self._setUp("java_1_12")

    def test_direct_access(self):
        self.assertEqual([1, 0], self.proto.blocks["minecraft:stone"])


class TestPrototype113(TestPrototypeBaseCases.TestPrototype):
    def setUp(self):
        self._setUp("java_1_13")

    def test_direct_access(self):
        self.assertEqual("minecraft:stone", self.proto.blocks["minecraft:stone"])


if __name__ == "__main__":
    unittest.main()
