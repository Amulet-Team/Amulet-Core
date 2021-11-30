import os.path
import unittest
import json

from tests.data.util import WorldTemp

from amulet import load_format
from tests.data import worlds_src


class TestWorldHeight(unittest.TestCase):
    def test_height(self):
        for world_name in worlds_src.levels:
            with WorldTemp(world_name) as world_temp:
                test_data_path = os.path.join(world_temp.temp_path, "world_test_data.json")
                self.assertTrue(os.path.isfile(test_data_path), msg=f"Could not find world_test_data.json for world {world_name}")
                with open(test_data_path) as f:
                    test_data = json.load(f)
                self.assertIn("dim_height", test_data)
                self.assertIsInstance(test_data["dim_height"], dict)
                height_data = test_data["dim_height"]
                world_wrapper = load_format(world_temp.temp_path)
                world_wrapper.open()
                for dim in world_wrapper.dimensions:
                    self.assertIn(dim, height_data, msg=world_name)
                    box = world_wrapper.bounds(dim).to_box()
                    self.assertEqual(
                        height_data[dim],
                        [
                            list(box.min),
                            list(box.max)
                        ],
                        msg=world_name
                    )
                world_wrapper.close()


if __name__ == "__main__":
    unittest.main()
