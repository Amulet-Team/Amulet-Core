import unittest

from amulet.chunk import ChunkLoadError, ChunkDoesNotExist
from tests.test_amulet.test_chunk_ import throw_chunk_load_error, throw_chunk_does_not_exist


class ChunkTestCase(unittest.TestCase):
    def test_exceptions(self) -> None:
        with self.assertRaises(RuntimeError):
            raise ChunkLoadError
        with self.assertRaises(RuntimeError):
            raise ChunkDoesNotExist
        with self.assertRaises(ChunkLoadError):
            raise ChunkLoadError
        # with self.assertRaises(ChunkLoadError):
        #     raise ChunkDoesNotExist
        with self.assertRaises(ChunkDoesNotExist):
            raise ChunkDoesNotExist

        with self.assertRaises(RuntimeError):
            throw_chunk_load_error()
        with self.assertRaises(RuntimeError):
            throw_chunk_does_not_exist()
        with self.assertRaises(ChunkLoadError):
            throw_chunk_load_error()
        # with self.assertRaises(ChunkLoadError):
        #     throw_chunk_does_not_exist()
        with self.assertRaises(ChunkDoesNotExist):
            throw_chunk_does_not_exist()

        # try:
        #     raise ChunkLoadError
        # except ChunkDoesNotExist:
        #     self.assertTrue(False)
        # except ChunkLoadError:
        #     self.assertTrue(True)
        #
        # try:
        #     raise ChunkDoesNotExist
        # except ChunkDoesNotExist:
        #     self.assertTrue(True)
        # except ChunkLoadError:
        #     self.assertTrue(False)
        #
        # try:
        #     throw_chunk_load_error()
        # except ChunkDoesNotExist:
        #     self.assertTrue(False)
        # except ChunkLoadError:
        #     self.assertTrue(True)
        #
        # try:
        #     throw_chunk_does_not_exist()
        # except ChunkDoesNotExist:
        #     self.assertTrue(True)
        # except ChunkLoadError:
        #     self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
