import unittest

from amulet.api.errors import PlayerDoesNotExist
from amulet.api.player import Player
from amulet import load_level
from tests.data.util import create_temp_world, clean_temp_world
from tests.data import worlds_src


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):
        def _setUp(self, world_name):
            self._world_name = world_name
            self.world = load_level(create_temp_world(world_name))

        def tearDown(self):
            self.world.close()
            clean_temp_world(self._world_name)

        def test_get_players(self):
            player_ids = list(self.world.all_player_ids())
            self.assertGreaterEqual(len(player_ids), 1)
            for player_id in player_ids:
                self.assertTrue(self.world.has_player(player_id))
                player = self.world.get_player(player_id)
                self.assertIsInstance(player, Player)

            with self.assertRaises(PlayerDoesNotExist):
                self.world.get_player("test")


def _create_test(path):
    cls_name = f"Test{path}"

    class TestCase(WorldTestBaseCases.WorldTestCase):
        def setUp(self):
            self._setUp(path)

    globals()[cls_name] = TestCase


for _path in worlds_src.levels:
    _create_test(_path)


if __name__ == "__main__":
    unittest.main()
