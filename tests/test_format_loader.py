import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import unittest
from test_utils import get_world_path
from types import ModuleType

from formats import format_loader


class FormatLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.formats = format_loader.loader.get_loaded_formats()

    def test_has_anvil(self):
        self.assertTrue("anvil" in self.formats)
        self.assertIsInstance(self.formats["anvil"], ModuleType)

    def test_identify_anvil_world(self):
        self.assertTrue(self.formats["anvil"].identify(get_world_path("1.12.2 World")))
        self.assertFalse(self.formats["anvil"].identify(get_world_path("1.13 World")))

    def test_identify_anvil2_world(self):
        self.assertFalse(self.formats["anvil"].identify(get_world_path("1.13 World")))
        self.assertTrue(self.formats["anvil2"].identify(get_world_path("1.13 World")))

    def test_format_loader_identify(self):
        self.assertEqual(
            format_loader.loader.identify_world_format_str(
                get_world_path("1.12.2 World")
            ),
            "anvil",
        )
        self.assertEqual(
            format_loader.loader.identify_world_format_str(
                get_world_path("1.13 World")
            ),
            "anvil2",
        )


if __name__ == "__main__":
    unittest.main()
