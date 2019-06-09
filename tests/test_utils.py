import sys
import os
import time
from contextlib import contextmanager

TESTS_DIR = os.path.dirname(__file__)


def modify_py_path():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    if path not in sys.path:
        sys.path.insert(0, path)


try:
    import api
except ModuleNotFoundError:
    modify_py_path()


def get_world_path(name: str) -> str:
    return os.path.join(TESTS_DIR, "worlds", name)


def get_data_path(name: str) -> str:
    return os.path.join(TESTS_DIR, "data", name)


@contextmanager
def timeout(test_instance, time_constraint: float, show_completion_time=False):
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
