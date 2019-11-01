import unittest

from test_utils import get_world_path

from amulet.world_interface import load_world
from amulet.api import world


@unittest.skip
class DefinitionBasedLoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.loader = world_loader

    def test_identifing(self):
        name, _format = self.loader.identify(get_world_path("1.12.2 World"))
        self.assertEqual("java_1_12", name)
        self.assertEqual("anvil", _format)

        name, _format = self.loader.identify(get_world_path("1.13 World"))
        self.assertEqual("java_1_13", name)
        self.assertEqual("anvil2", _format)

    def test_loading(self):
        # world_obj = self.loader.load_world(get_world_path("1.12.2 World"))
        world_obj = load_world(get_world_path("1.12.2 World"))
        self.assertIsInstance(world_obj, world.World)

        # world_obj = self.loader.load_world(get_world_path("1.13 World"))
        world_obj = load_world(get_world_path("1.13 World"))
        self.assertIsInstance(world_obj, world.World)


if __name__ == "__main__":
    unittest.main()
