import os
import time
from contextlib import contextmanager


def get_world_path(name: str) -> str:
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tests_dir, "worlds", name)


@contextmanager
def timeout(test_instance, time_constraint: float):
    start = time.time()
    yield

    end = time.time()
    delta = end - start
    if delta > time_constraint:
        test_instance.fail(
            f"Test execution didn't meet desired run time of {time_constraint}, ran in {delta} instead"
        )
