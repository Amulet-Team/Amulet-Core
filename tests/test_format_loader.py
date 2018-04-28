import unittest
from types import ModuleType

from formats import format_loader


class FormatLoaderTestCase(unittest.TestCase):

    def test_has_anvil(self):
        formats = format_loader.loader.get_loaded_formats()

        self.assertTrue("anvil" in formats)
        self.assertIsInstance(formats["anvil"], ModuleType)


if __name__ == "__main__":
    unittest.main()
