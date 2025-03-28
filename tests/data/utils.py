import sys
import os
import time
import shutil
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import atexit
from typing import Generator

import tests.data

DATA_DIR = os.path.realpath(tests.data.__path__[0])
TEMP_DIR = TemporaryDirectory()
atexit.register(TEMP_DIR.cleanup)


def get_data_dir() -> str:
    return DATA_DIR


def get_temp_dir() -> str:
    return TEMP_DIR.name


def get_data_path(name: str) -> str:
    return os.path.join(DATA_DIR, name)


def clean_path(path: str) -> None:
    """Clean a given path removing all data at that path."""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        os.remove(path)


@contextmanager
def timeout(test_instance, time_constraint: float, show_completion_time=False) -> Generator[None, None, None]:
    start = time.time()
    yield

    end = time.time()
    delta = end - start
    if delta > time_constraint:
        test_instance.fail(
            f"Test execution didn't meet desired run time of {time_constraint}, ran in {delta} instead"
        )
    elif show_completion_time:
        print(
            f"Test ran in {delta} seconds, was required to run in {time_constraint} seconds",
            file=sys.stderr,
        )
