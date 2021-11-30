import unittest

from tests.data.util import WorldTemp

from amulet import load_level, load_format
from amulet.level.formats.anvil_world import AnvilFormat
from amulet.api.level import World
from tests.data import worlds_src


class DefinitionBasedLoaderTestCase(unittest.TestCase):
    def test_identify(self):
        with WorldTemp(worlds_src.java_vanilla_1_12_2) as world_temp:
            numerical_java_format = load_format(world_temp.temp_path)
            self.assertIsInstance(numerical_java_format, AnvilFormat)

        with WorldTemp(worlds_src.java_vanilla_1_13) as world_temp:
            blockstate_java_format = load_format(world_temp.temp_path)
            self.assertIsInstance(blockstate_java_format, AnvilFormat)

    def test_loading(self):
        with WorldTemp(worlds_src.java_vanilla_1_12_2) as world_temp:
            numerical_java_world = load_level(world_temp.temp_path)
            self.assertIsInstance(numerical_java_world, World)
            numerical_java_world.close()

        with WorldTemp(worlds_src.java_vanilla_1_13) as world_temp:
            blocksate_java_world = load_level(world_temp.temp_path)
            self.assertIsInstance(blocksate_java_world, World)
            blocksate_java_world.close()


if __name__ == "__main__":
    unittest.main()
