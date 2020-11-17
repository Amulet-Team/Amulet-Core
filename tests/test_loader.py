import unittest

from tests.test_utils import get_world_path, create_temp_world, clean_temp_world

from amulet.world_interface import load_world, load_format
from amulet.world_interface.formats.anvil.anvil_format import AnvilFormat
from amulet.api.level import World


class DefinitionBasedLoaderTestCase(unittest.TestCase):
    @unittest.skip
    def test_identify(self):
        numerical_java_format = load_format(get_world_path("Java 1.12.2"))
        self.assertIsInstance(numerical_java_format, AnvilFormat)

        blockstate_java_format = load_format(get_world_path("Java 1.13"))
        self.assertIsInstance(blockstate_java_format, AnvilFormat)

    def test_loading(self):
        numerical_java_world = load_world(create_temp_world("Java 1.12.2"))
        self.assertIsInstance(numerical_java_world, World)
        numerical_java_world.close()
        clean_temp_world("Java 1.12.2")

        blocksate_java_world = load_world(create_temp_world("Java 1.13"))
        self.assertIsInstance(blocksate_java_world, World)
        blocksate_java_world.close()
        clean_temp_world("Java 1.13")


if __name__ == "__main__":
    unittest.main()
