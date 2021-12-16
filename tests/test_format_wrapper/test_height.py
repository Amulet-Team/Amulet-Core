import os.path
import unittest
import json

from tests.data.util import WorldTemp

from amulet import load_format
from tests.data import worlds_src
from tests.data.util import for_each_world, BaseWorldTest


@for_each_world(globals(), worlds_src.levels)
class TestWorldHeight(BaseWorldTest, unittest.TestCase):
    def test_height(self):
        with WorldTemp(self.WorldPath) as world_temp:
            test_data_path = os.path.join(world_temp.temp_path, "world_test_data.json")
            self.assertTrue(
                os.path.isfile(test_data_path),
                msg=f"Could not find world_test_data.json for world {self.WorldPath}",
            )
            with open(test_data_path) as f:
                test_data = json.load(f)
            self.assertIn("dim_height", test_data, msg=self.WorldPath)
            self.assertIsInstance(test_data["dim_height"], dict, msg=self.WorldPath)
            height_data = test_data["dim_height"]
            world_wrapper = load_format(world_temp.temp_path)
            world_wrapper.open()
            self.assertEqual(
                sorted(test_data["dim_height"]),
                sorted(world_wrapper.dimensions),
                msg=self.WorldPath,
            )
            for dim in world_wrapper.dimensions:
                box = world_wrapper.bounds(dim).to_box()
                self.assertEqual(
                    height_data[dim], [list(box.min), list(box.max)], msg=self.WorldPath
                )
            world_wrapper.close()


if __name__ == "__main__":
    unittest.main()
