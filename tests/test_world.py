from typing import Union, Sequence

import unittest
from unittest import mock

import numpy


class World(object):
    pass


class MCEditWorldTestCase(unittest.TestCase):

    def setUp(self):

        def get_block_side_effect(x: int, y: int, z: int) -> str:
            if not (0 <= y <= 255):
                raise IndexError()

            return "minecraft:dirt"

        def get_blocks_side_effects(
            *args: Union[Sequence[slice], Sequence[int]]
        ) -> numpy.ndarray:
            _blocks = numpy.full((16, 16, 16), "minecraft:air", dtype=str)
            """

            :param args:
            :return:
            """
            length = len(args)
            if 3 <= length < 6:
                slice_x, slice_y, slice_z = args[0:3]
                if not (
                    isinstance(slice_x, slice)
                    or isinstance(slice_y, slice)
                    or isinstance(slice_z, slice)
                ):
                    raise IndexError()

                return _blocks[slice_x, slice_y, slice_z]

            elif 6 <= length < 9:
                start_x, start_y, start_z, end_x, end_y, end_z = args[0:6]
                return _blocks[start_x:end_x, start_y:end_y, start_z:end_z]

            elif length >= 9:
                start_x, start_y, start_z, end_x, end_y, end_z, step_x, step_y, step_z = args[
                    0:9
                ]
                return _blocks[
                    start_x:end_x:step_x, start_y:end_y:step_y, start_z:end_z:step_z
                ]

            else:
                raise IndexError()

        self.world = World()
        self.world.get_block = mock.MagicMock(return_value="minecraft:dirt")
        self.world.get_block.side_effect = get_block_side_effect

        self.world.get_blocks = mock.MagicMock(
            return_value=numpy.full((16, 16, 16), "minecraft:air", dtype=str)
        )
        self.world.get_blocks.side_effect = get_blocks_side_effects

    def test_get_block(self):
        self.assertEqual(self.world.get_block(0, 0, 0), "minecraft:dirt")
        self.assertEqual(self.world.get_block(16, 16, 16), "minecraft:dirt")
        with self.assertRaises(IndexError):
            self.world.get_block(300, 300, 300)

    def test_get_blocks(self):
        self.assertIsInstance(
            self.world.get_blocks(slice(0, 10), slice(0, 10), slice(0, 10)),
            numpy.ndarray,
        )
        self.assertIsInstance(self.world.get_blocks(0, 0, 0, 10, 10, 10), numpy.ndarray)
        self.assertIsInstance(
            self.world.get_blocks(0, 0, 0, 10, 10, 10, 2, 2, 2), numpy.ndarray
        )

        with self.assertRaises(IndexError):
            self.world.get_blocks()

            self.world.get_blocks(slice(0, 10, 2))
            self.world.get_blocks(slice(0, 10, 2), slice(0, 10, 2))

            self.world.get_blocks(0)
            self.world.get_blocks(0, 0)
            self.world.get_blocks(0, 0, 0)


if __name__ == "__main__":
    unittest.main()
