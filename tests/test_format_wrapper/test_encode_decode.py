import copy
import unittest

from amulet_nbt import TAG_Compound
from amulet import load_format
from tests.data.util import WorldTemp, for_each_world, BaseWorldTest
from tests.data.worlds_src import levels


@for_each_world(globals(), levels)
class BaseTestDecodeEncode(BaseWorldTest, unittest.TestCase):
    def test_decode_encode(self):
        """Test decoding chunk data and then encoding it again to make sure it matches."""
        with WorldTemp(self.WorldPath) as world_temp:
            level = load_format(world_temp.temp_path)
            level.open()
            chunk_count = 0
            for dimension in level.dimensions:
                for cx, cz in level.all_chunk_coords(dimension):
                    raw_chunk_data_in = level._get_raw_chunk_data(cx, cz, dimension)
                    raw_chunk_data = copy.deepcopy(raw_chunk_data_in)
                    interface = level._get_interface(raw_chunk_data)

                    if (
                        world_temp.metadata["world_data"]["platform"] == "java"
                        and world_temp.metadata["world_data"]["origin"] == "vanilla"
                    ):
                        # store references to the data
                        level_tag = raw_chunk_data.get("Level", TAG_Compound())

                    # decode the raw chunk data
                    chunk, chunk_palette = level._decode(
                        interface, dimension, cx, cz, raw_chunk_data
                    )

                    # TODO: uncomment this when the last few things in the Java format are sorted
                    # if (
                    #     world_temp.metadata["world_data"]["platform"] == "java"
                    #     and world_temp.metadata["world_data"]["origin"] == "vanilla"
                    # ):
                    #     self.assertFalse(raw_chunk_data, msg=self.WorldPath)
                    #     self.assertFalse(level_tag, msg=self.WorldPath)

                    raw_chunk_data_out = level._encode(
                        interface, chunk, dimension, chunk_palette
                    )
                    if chunk_count > 100:
                        break
                    chunk_count += 1
                    # if raw_chunk_data_in != raw_chunk_data_out:
                    #     print("Difference")
                    #     print(raw_chunk_data_in.value.find_diff(raw_chunk_data_out.value))
                    # print(raw_chunk_data_in.to_snbt())
                    # print(raw_chunk_data_out.to_snbt())

                    # self.assertEqual(raw_chunk_data_in, raw_chunk_data_out)

                    raw_chunk_data2 = copy.deepcopy(raw_chunk_data_out)
                    if world_temp.metadata["world_data"]["platform"] == "bedrock":
                        raw_chunk_data2 = {
                            key: val
                            for key, val in raw_chunk_data2.items()
                            if val is not None
                        }
                    level._decode(interface, dimension, cx, cz, raw_chunk_data2)
            level.close()


if __name__ == "__main__":
    unittest.main()
