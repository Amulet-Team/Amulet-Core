import os
import unittest

from formats import format_loader

def get_world_path(name: str) -> str:
    return os.path.join("worlds", name)

class UnifiedWorldTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = format_loader.loader

    def test_load_anvil(self):
        world = self.loader.load_world(get_world_path("1.12.2 World"))
