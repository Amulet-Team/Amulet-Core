import unittest
from tests.test_utils import get_world_path

from formats import format_loader


class UnifiedWorldTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = format_loader.loader

    def test_load_anvil(self):
        world = self.loader.load_world(get_world_path("1.12.2 World"))
