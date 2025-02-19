from unittest import TestCase
from tempfile import TemporaryDirectory
import os
from multiprocessing import Queue, Process

from test_amulet.test_util.test_lock_file_ import (
    test_lock_file,
    create_test_file,
    unlock_test_file,
)


def write_file(path: str, queue: Queue):
    with open(path) as f:
        queue.put(f.read())

    try:
        create_test_file(path)
    except:
        queue.put(True)
    else:
        queue.put(False)


class LockFileTestCase(TestCase):
    def test_cpp(self) -> None:
        with TemporaryDirectory() as temp_dir:
            test_lock_file(os.path.join(temp_dir, "test.lock"))

    def test_py(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lock_path = os.path.join(temp_dir, "test.lock")
            create_test_file(lock_path)

            queue = Queue()
            p = Process(target=write_file, args=(lock_path, queue))
            p.start()
            p.join()

            self.assertEqual("Hello World", queue.get())
            self.assertTrue(queue.get())

            unlock_test_file()
