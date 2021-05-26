import unittest

from tests.test_utils import get_world_path, create_temp_world, clean_temp_world

from amulet import load_level, load_format
from amulet.level.formats.anvil_world import AnvilFormat
from amulet.api.level import World
from . import worlds_src


class DefinitionBasedLoaderTestCase(unittest.TestCase):
    @unittest.skip
    def test_identify(self):
        numerical_java_format = load_format(get_world_path(worlds_src.java_vanilla_1_12_2))
        self.assertIsInstance(numerical_java_format, AnvilFormat)

        blockstate_java_format = load_format(get_world_path(worlds_src.java_vanilla_1_13))
        self.assertIsInstance(blockstate_java_format, AnvilFormat)

    def test_loading(self):
        numerical_java_world = load_level(create_temp_world(worlds_src.java_vanilla_1_12_2))
        self.assertIsInstance(numerical_java_world, World)
        numerical_java_world.close()
        clean_temp_world(worlds_src.java_vanilla_1_12_2)

        blocksate_java_world = load_level(create_temp_world(worlds_src.java_vanilla_1_13))
        self.assertIsInstance(blocksate_java_world, World)
        blocksate_java_world.close()
        clean_temp_world(worlds_src.java_vanilla_1_13)


if __name__ == "__main__":
    unittest.main()
