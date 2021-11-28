import unittest
import time

from amulet.api.errors import ChunkLoadError
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

        def test_chunk_speed(self):
            chunk_count = 0
            start_time = time.time()
            for dimension in self.world.dimensions:
                for cx, cz in self.world.all_chunk_coords(dimension):
                    try:
                        chunk = self.world.get_chunk(cx, cz, dimension)
                    except ChunkLoadError:
                        pass
                    else:
                        chunk_count += 1
            end_time = time.time()
            print((end_time - start_time) / chunk_count)


class AnvilWorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp(worlds_src.java_vanilla_1_12_2)


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp(worlds_src.java_vanilla_1_13)


# class BedrockWorldTestCase(WorldTestBaseCases.WorldTestCase):
#     def setUp(self):
#         self._setUp(worlds_src.bedrock_vanilla_1_16)


if __name__ == "__main__":
    unittest.main()
