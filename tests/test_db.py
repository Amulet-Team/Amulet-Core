import unittest
from amulet.libs.leveldb import LevelDB
import os
import shutil

DB_PATH = "./worlds_temp/leveldb"


class LevelDBTestCase(unittest.TestCase):
    def _clear_db(self):
        if os.path.isdir(DB_PATH):
            shutil.rmtree(DB_PATH)

    def test_create_ldb(self):
        self._clear_db()
        db = LevelDB(DB_PATH, True)
        db.close()

    def test_read_write(self):
        self._clear_db()
        db = LevelDB(DB_PATH, True)

        with self.assertRaises(KeyError):
            db.get(b"random_key")

        key1 = b"key"
        value1 = b"value"
        db.put(key1, value1)
        self.assertEqual(db.get(key1), value1)

        key2 = key1 * 1000
        value2 = value1 * 1000
        db.put(key2, value2)
        self.assertEqual(db.get(key2), value2)

        db.close()

    def test_put_batch(self):
        self._clear_db()
        db = LevelDB(DB_PATH, True)

        batch = {
            f"key{i}".encode("utf-8"): f"val{i}".encode("utf-8") for i in range(100)
        }
        db.putBatch(batch)

        self.assertEqual(dict(db.iterate()), batch)
        self.assertEqual(set(db.keys()), batch.keys())
        self.assertEqual(set(db), batch.keys())

        db.close()

    def test_contains(self):
        self._clear_db()
        db = LevelDB(DB_PATH, True)

        self.assertFalse(b"test_key2" in db)

        db.put(b"test_key2", b"test")

        self.assertTrue(b"test_key2" in db)

        db.close()

    def test_delete(self):
        self._clear_db()
        db = LevelDB(DB_PATH, True)

        self.assertFalse(b"test_key3" in db)

        db.put(b"test_key3", b"test")

        self.assertTrue(b"test_key3" in db)

        db.delete(b"test_key3")

        self.assertFalse(b"test_key3" in db)

        db.close()


if __name__ == "__main__":
    unittest.main()
