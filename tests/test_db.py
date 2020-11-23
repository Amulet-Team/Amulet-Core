import unittest
from amulet.libs.leveldb import LevelDB


class BlockTestCase(unittest.TestCase):
    def test_create_ldb(self):
        db = LevelDB("./worlds_temp/leveldb", True)
        db.close()


if __name__ == "__main__":
    unittest.main()
