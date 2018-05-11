import unittest

from version_definitions import format_proto_1


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.proto112 = format_proto_1.Prototype1("1.12")
        self.proto113 = format_proto_1.Prototype1("1.13")

    def test_direct_access(self):
        self.assertEqual(self.proto112.blocks["minecraft:stone"], [1,0])
        self.assertEqual(self.proto113.blocks["minecraft:stone"], "minecraft:stone")

    def test_get_internal_block(self):
        stone_def = self.proto112.get_internal_block(basename="stone")
        oak_log_axis_x = self.proto112.get_internal_block(basename="oak_log", properties={"axis": "x"})

        self.assertIsInstance(stone_def, dict)
        self.assertEqual(stone_def["name"], "Stone")

        self.assertIsInstance(oak_log_axis_x, dict)
        self.assertEqual(oak_log_axis_x["name"], "Oak Log (East/West)")
        self.assertNotEqual(oak_log_axis_x, self.proto112.get_internal_block(basename="oak_log", properties={"axis": "y"}))

        with self.assertRaises(KeyError):
            self.proto112.get_internal_block(resource_location="unknown", basename="stone")
            self.proto112.get_internal_block(basename="stone", properties={"variant": "chiseled"})
            self.proto112.get_internal_block(basename="laterite")


if __name__ == '__main__':
    unittest.main()
