import unittest

from test_utils import get_world_path

import api.world_loader
from api import world


class DefinitionBasedLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = api.world_loader.loader
        print(self.loader._identifiers)

    def test_identifing(self):
        name, _format = self.loader.identify(get_world_path("1.12.2 World"))
        self.assertEqual(name, "1_12")
        self.assertEqual(_format, "anvil")

        name, _format = self.loader.identify(get_world_path("1.13 World"))
        self.assertEqual(name, "1_13")
        self.assertEqual(_format, "anvil2")

    def test_loading(self):
        world_obj = self.loader.load_world(get_world_path("1.12.2 World"))
        self.assertIsInstance(world_obj, world.World)

        world_obj = self.loader.load_world(get_world_path("1.13 World"))
        self.assertIsInstance(world_obj, world.World)


if __name__ == "__main__":
    unittest.main()
