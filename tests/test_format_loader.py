import unittest
from types import ModuleType
import os

from formats import format_loader


def get_world_path(name: str) -> str:
    return os.path.join("worlds", name)


class FormatLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.formats = format_loader.loader.get_loaded_formats()

    def test_has_anvil(self):
        self.assertTrue("anvil" in self.formats)
        self.assertIsInstance(self.formats["anvil"], ModuleType)

    def test_has_unified(self):
        self.assertTrue("unified" in self.formats)
        self.assertIsInstance(self.formats["unified"], ModuleType)

    def test_identify_anvil_world(self):
        self.assertTrue(self.formats["anvil"].identify(get_world_path("1.12.2 World")))
        self.assertFalse(self.formats["anvil"].identify(get_world_path("1.13 World")))

    def test_identify_anvil2_world(self):
        self.assertFalse(self.formats["anvil"].identify(get_world_path("1.13 World")))
        self.assertTrue(self.formats["anvil2"].identify(get_world_path("1.13 World")))


if __name__ == "__main__":
    unittest.main()
