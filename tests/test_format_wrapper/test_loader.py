import unittest

from tests.data.util import WorldTemp

from amulet import load_level, load_format
from amulet.level.formats.anvil_world import AnvilFormat
from amulet.api.level import World
from tests.data import worlds_src


class DefinitionBasedLoaderTestCase(unittest.TestCase):
    def test_identify(self):
        for path in worlds_src.JavaVanillaLevels:
            with WorldTemp(path) as world_temp:
                java_format = load_format(world_temp.temp_path)
                self.assertIsInstance(java_format, AnvilFormat)

    def test_loading(self):
        for path in worlds_src.levels:
            with WorldTemp(path) as world_temp:
                numerical_java_world = load_level(world_temp.temp_path)
                self.assertIsInstance(numerical_java_world, World)
                numerical_java_world.close()


if __name__ == "__main__":
    unittest.main()
