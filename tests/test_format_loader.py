import unittest
from types import ModuleType

from formats import format_loader


class FormatLoaderTestCase(unittest.TestCase):

    def test_has_anvil(self):
        print(format_loader._formats)
        self.assertIsInstance(format_loader._formats['anvil'], ModuleType)
        print(format_loader._formats['anvil'].AnvilWorld)


if __name__ == '__main__':
    unittest.main()
