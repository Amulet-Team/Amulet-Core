import unittest
import time

from amulet.api.errors import ChunkLoadError
from amulet.world_interface import load_world
from tests.test_utils import create_temp_world, clean_temp_world


class WorldTestBaseCases:
    # Wrapped in another class, so it isn't executed on it's own.

    class WorldTestCase(unittest.TestCase):
        def _setUp(self, world_name):
            self._world_name = world_name
            self.world = load_world(create_temp_world(world_name))

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
        self._setUp("Java 1.12.2")


class Anvil2WorldTestCase(WorldTestBaseCases.WorldTestCase):
    def setUp(self):
        self._setUp("Java 1.13")


# class BedrockWorldTestCase(WorldTestBaseCases.WorldTestCase):
#     def setUp(self):
#         self._setUp("Bedrock 1.16")


if __name__ == "__main__":
    unittest.main()
