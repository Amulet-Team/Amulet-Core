import copy
import unittest

from amulet import load_format
from tests.data.util import WorldTemp


class WrapBaseTestDecodeEncode:
    # Wrapped in another class, so it isn't executed on it's own.

    class BaseTestDecodeEncode(unittest.TestCase):
        WorldName = None

        def test_decode_encode(self):
            """Test decoding chunk data and then encoding it again to make sure it matches."""
            with WorldTemp(self.WorldName) as world_temp:
                level = load_format(world_temp.temp_path)
                level.open()
                for dimension in level.dimensions:
                    for cx, cz in level.all_chunk_coords(dimension):
                        raw_chunk_data_in = level._get_raw_chunk_data(cx, cz, dimension)
                        raw_chunk_data = copy.deepcopy(raw_chunk_data_in)
                        interface = level._get_interface(raw_chunk_data)

                        # decode the raw chunk data into the universal format
                        chunk, chunk_palette = level._decode(
                            interface, dimension, cx, cz, raw_chunk_data
                        )
                        raw_chunk_data_out = level._encode(
                            interface, chunk, dimension, chunk_palette
                        )
                level.close()
