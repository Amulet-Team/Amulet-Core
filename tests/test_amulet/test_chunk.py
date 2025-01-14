import unittest

from amulet.chunk import ChunkLoadError, ChunkDoesNotExist


class ChunkTestCase(unittest.TestCase):
    def test_exceptions(self) -> None:
        with self.assertRaises(ChunkDoesNotExist):
            raise ChunkDoesNotExist
        with self.assertRaises(ChunkLoadError):
            raise ChunkLoadError
        with self.assertRaises(ChunkLoadError):
            raise ChunkDoesNotExist

        try:
            raise ChunkLoadError
        except ChunkDoesNotExist:
            self.assertTrue(False)
        except ChunkLoadError:
            self.assertTrue(True)

        try:
            raise ChunkDoesNotExist
        except ChunkDoesNotExist:
            self.assertTrue(True)
        except ChunkLoadError:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
