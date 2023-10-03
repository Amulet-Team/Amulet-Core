import unittest

from amulet.utils.shareable_lock import ShareableRLock


class TestShareableRLock(unittest.TestCase):
    def test_lock(self):
        lock = ShareableRLock()

        with lock.unique():
            pass

        with lock.shared():
            pass

        with lock.unique():
            with lock.unique():
                pass

        with lock.unique():
            with lock.shared():
                pass

        with lock.shared():
            with lock.unique():
                pass

        with lock.shared():
            with lock.shared():
                pass

    def test_deadlock(self):
        pass


if __name__ == "__main__":
    unittest.main()
